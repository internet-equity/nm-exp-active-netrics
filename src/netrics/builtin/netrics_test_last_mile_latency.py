from .. utils import popen_exec
import logging
import re
import ipaddress

log = logging.getLogger(__name__)

def test_last_mile_latency(key, measurement, conf, results, quiet):
    """Method records RTT to earliest node with public IP Address along path
    to 8.8.8.8 by default.
    """

    sites = list(conf['last_mile_latency'].keys())
    labels = conf['last_mile_latency']

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

    for line in out:
        if 'traceroute' not in line and countOccurrences(line, '*') < 3:
            ipv4_extract_pattern = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
            ip_addr = re.findall(ipv4_extract_pattern, line)[0]
            try:
                if not ipaddress.ip_address(ip_addr).is_private:
                    ping_cmd = "ping -i {:.2f} -c {:d} -w {:d} {:s}".format(
                        0.25, 10, 5, ip_addr)
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

                    results[key][labels[site] + "_last_mile_ping_packet_loss_pct"] = ping_pkt_loss
                    results[key][labels[site] + "_last_mile_ping_rtt_min_ms"] = ping_rtt_ms[0]
                    results[key][labels[site] + "_last_mile_ping_rtt_max_ms"] = ping_rtt_ms[2]
                    results[key][labels[site] + "_last_mile_ping_rtt_avg_ms"] = ping_rtt_ms[1]
                    results[key][labels[site] + "_last_mile_ping_rtt_mdev_ms"] = ping_rtt_ms[3]
                    break
            except ValueError:
                continue
    
    if res:
        try:
            res.sort()
            results[key][f'{labels[site]}_last_mile_tr_rtt_min_ms'] = float(res[0])
            results[key][f'{labels[site]}_last_mile_tr_rtt_median_ms'] = float(get_median(res))
            results[key][f'{labels[site]}_last_mile_tr_rtt_max_ms'] = float(res[-1])
        except Exception as e:
            return e


def countOccurrences(s, ch):
        return sum(1 for i, letter in enumerate(s) if letter == ch)

def get_median(x):
    n = len(x)
    if n % 2 == 0: # even
        return 0.5 * (x[n//2 -1] + x[n//2])
    else: # odd
        return x[(n+1)//2 -1]