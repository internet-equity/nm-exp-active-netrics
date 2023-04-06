from .. utils import popen_exec
import logging
import re
from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

def test_httping(key, conf, results, quiet=False):

    #read the sites from conf
    #TODO
    sites = [("www.wikipedia.com","wikipedia"),("www.google.com","google")]

    #take argument how many times to run from conf
    #TODO
    c = 2

    ping_res = {}

    for site,label in sites:
        
        ping_cmd = f"httping {site} -c {c}"
        ping_res[label], err = popen_exec(ping_cmd)

        if len(err) > 0:            
            print(f"ERROR: {err}")
            results[key][label][f'error'] = f'{err}'
            log.error(err)
            continue
            
        pattern = r"round-trip min/avg/max = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+) ms"
        match = re.search(pattern, ping_res[label])

        if match:
        # Extract the min, avg, and max values
            min_value = match.group(1)
            avg_value = match.group(2)
            max_value = match.group(3)

        else:
            err = "Metrics not found in httping output"
            print(f"ERROR: {err}")
            results[key][label][f'error'] = f'{err}'
            log.error(err)            
            continue

        if not quiet:
            print(f'\n --- {label} httping latency ---')
            print(f'Minimum value: {min_value} (ms)')
            print(f'Average value: {avg_value} (ms)')
            print(f'Maximum value: {max_value} (ms)')

        results[key][f'{label}_min_value'] = min_value
        results[key][f'{label}_avg_value'] = avg_value
        results[key][f'{label}_max_value'] = max_value

    return ping_res


