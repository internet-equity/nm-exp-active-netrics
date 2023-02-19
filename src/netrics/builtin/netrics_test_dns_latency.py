import json
from .. utils import popen_exec
import logging
import re

log = logging.getLogger(__name__)

def test_dns_latency(key, measurement, args, results, quiet):
    """Method returns dig latency for each site in args["sites"]
    """

    conf = args["conf"]
    sites = args["sites"]
    labels = args["labels"]

    dig_res = None
    error_found = False
    target = '8.8.8.8'

    if 'target' in conf['dns_latency'].keys():
        target = conf['dns_latency']['target']

    dig_delays = []
    dig_res = {}
    for site in sites:
        
        if valid_ip(site):
            continue

        try:
            label = labels[site]
        except KeyError:
            label = site
        dig_cmd = f'dig @{target} {site}'
        dig_res[label], err = popen_exec(dig_cmd)
        if len(err) > 0:
            print(f"ERROR: {err}")
            results[key][f'{label}_error'] = f'{err}'
            dig_res[label] = { 'error': f'{err}' }
            log.error(err)
            error_found = True
            continue

        dig_res_qt = re.findall('Query time: ([0-9]*) msec',
                                dig_res[label], re.MULTILINE)[0]
        dig_delays.append(int(dig_res_qt))

    results[key] = {}
    results[key]["dns_query_avg_ms"] = sum(dig_delays) / len(dig_delays)
    results[key]["dns_query_max_ms"] = max(dig_delays)
    results[key]["error"] = error_found

    if not quiet:
        print(f'\n --- DNS Delays (n = {len(dig_delays)}) ---')
        print(f'Avg DNS Query Time: {results[key]["dns_query_avg_ms"]} ms')
        print(f'Max DNS Query Time: {results[key]["dns_query_max_ms"]} ms')

    return dig_res

# function taken from
# https://stackoverflow.com/questions/11264005/using-a-regex-to-match-ip-addresses
def valid_ip(address):
    """
    Check if a site in sites is an IP address
    """
    try:
        host_bytes = address.split('.')
        valid = [int(b) for b in host_bytes]
        valid = [b for b in valid if b >=0 and b<=255]
        return len(host_bytes) == 4 and len(valid) == 4
    except:
        return False