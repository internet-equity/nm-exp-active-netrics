from .. utils import popen_exec
import logging
import re
import ipaddress

log = logging.getLogger(__name__)

def test_k_hop_latency(key, measurement, conf, results, quiet):
    """Method records RTT to k nodes with public IP Address along path
    to 8.8.8.8 by default.
    """

    sites = list(conf['k_hop_latency'].keys())
    labels = conf['k_hop_latency']

    if len(sites) == 0:
        return

    output = {}
    res = None
    for site in sites:
        tr_cmd = f'traceroute {site}'

        out, err = popen_exec(tr_cmd)
        output[site] = out
        results[key] = {}

        if len(err) > 0:
            results[key]["error"] = f'{err}'
            print(f'ERROR: {err}')
            log.error(err)
            return f'{err}'

        out = out.split('\n')
        parse_trace_output(out,output,site,results,key,labels)

    return output


def parse_trace_output(out,output,site,results,key,labels):
    print(out) 
    tr_out = {'index': [], 'hostname': [], 'ip_addr': []}
    for line in out:
        if 'traceroute' not in line and countOccurrences(line, '*') < 3:
            ipv4_extract_pattern = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
            hostname_extract_pattern = "[a-zA-Z0-9.-_]+"
            decimal_extract_pattern = "^\d*\.?\d*$" 
            
            line_split = [x.strip() for x in line.split()]
            if len(line_split) == 0:
                continue

            tr_out['index'].append(int(line_split[0]))
            tr_out['hostname'].append([])
            tr_out['ip_addr'].append([])
            
            for substr in line_split[1:]:
                for ch in ['(', ')']:
                    substr = substr.replace(ch, '')
                if re.match(ipv4_extract_pattern, substr):
                    tr_out['ip_addr'][-1] += [substr]
                elif re.match(hostname_extract_pattern, substr) and not (re.match(decimal_extract_pattern, substr) or substr in ['ms', '*']):
                    tr_out['hostname'][-1] += [substr]
                elif re.match(decimal_extract_pattern, substr) or substr in ['ms', '*']:
                    continue
    for rep in range(5):
        for count, ip_addr_list in enumerate(tr_out['ip_addr']):
            if count == 15:
                print('breaking')
                break
            try:
                for i, ip_addr in enumerate(ip_addr_list):
                    if ip_addr == 'missing':
                        continue
                    ping_cmd = "ping -i {:.2f} -c {:d} -w {:d} {:s}".format(
                        0.25, 1, 5, ip_addr)
                    output[site], err = popen_exec(ping_cmd)
                    if len(err) > 0:
                        print(f"ERROR: {err}")
                        log.error(err)
                        results[key][site + "_error"] = f'{err}'
                        output[site] = { 'error' : f'{err}' }
                        error_found = True
                        return

                    try:
                        ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                                        output[site], re.MULTILINE)[0])
                    except IndexError:
                        results[key][site + "_error"] = 'Packet Loss IndexError'
                        output[site] = {'error': 'Packet Loss IndexErorr'}
                        error_found = True
                        continue

                    try:
                        ping_rtt_ms = re.findall(
                            'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                            , output[site])[0]
                    except IndexError:
                        results[key][site + "_error"] = 'Probe IndexError'
                        output[site] = {'error': 'Probe IndexErorr'}
                        error_found = True
                        continue

                    res = re.findall('([0-9.]*) ms', line)
                    ping_rtt_ms = [float(v) for v in ping_rtt_ms]
                    
                    results[key][ip_addr + f"_k_hop_latency_rep_{rep}_index"] = tr_out['index'][count]
                    results[key][ip_addr + f"_k_hop_latency_rep_{rep}_hostname"] = tr_out['hostname'][count][i] if len(tr_out['hostname'][count]) > 0 else ""
                    results[key][ip_addr + f"_k_hop_latency_rep_{rep}_packet_loss_pct"] = ping_pkt_loss
                    results[key][ip_addr + f"_k_hop_latency_rep_{rep}_ping_rtt_ms"] = ping_rtt_ms[0]
                    break
            except ValueError as e:
                print(e)
                continue
            
def countOccurrences(s, ch):
        return sum(1 for i, letter in enumerate(s) if letter == ch)

def get_median(x):
    n = len(x)
    if n % 2 == 0: # even
        return 0.5 * (x[n//2 -1] + x[n//2])
    else: # odd
        return x[(n+1)//2 -1]
