from .. utils import popen_exec
import logging
import re
from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

def test_httping(key, conf, results, quiet=False):

    #read the sites from conf
    try:
        labels = conf['reference_site_dict']
        sites = conf['httping']['targets']
    except Exception as err:
        print("config file not configured correctly for httping: ",err)
        results[key][f'error'] = f'{err}'
        log.error(err)
        return

    #take argument how many times to run from conf
    c = conf['httping']['c']

    ping_res = {}

    for site in sites:

        label = labels[site]
        
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

        results[key][f'{label}_httping_min_value'] = min_value
        results[key][f'{label}_httping_avg_value'] = avg_value
        results[key][f'{label}_httping_max_value'] = max_value

    return ping_res


