from .. utils import popen_exec
import logging
import re
import time 

log = logging.getLogger(__name__)


def test_latunderload(key, measurement, args, conf, results, quiet):
    """
    Method records ping latency under load to sites_load
    """

    if 'targets' in conf['latency_under_load']:
        targets = conf['latency_under_load']['targets']
    else:
        return

    ping_res = {}
    client = args["client"]
    port = args["port"]
    labels = args["labels"]

    error_found = False

    for upload in [True, False]:

        ul_dl = "ul" if upload else "dl"

        load = "/usr/local/src/nm-exp-active-netrics/bin/iperf3.sh -c {} -p {} -i 0 -t 10 {}"\
                    .format(client, port, "" if upload else "-R" )

        load += " > /dev/null & sleep 2 && echo starting ping && "

        direction = ul_dl
        ping_res[direction] = {} 
        for site in targets:

            try:
                label = labels[site]
            except KeyError:
                label = site

            ping_cmd = "ping -i 0.25 -c 10 -w 5 {:s}".format(site)
            
            start = time.time()
            ping_res[direction][label], err = popen_exec(load + ping_cmd)
            if len(err) > 0:
                print(f"ERROR: {err}")
                log.error(err)
                results[key][f'{label}_{ul_dl}_error'] = f'{err}'
                ping_res[direction][label] = { 'error': f'{err}' }
                error_found = True
                continue

            ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                                ping_res[direction][label], re.MULTILINE)[0])
            
            ping_rtt_ms = re.findall(
                'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                , ping_res[direction][label])[0]

            ping_rtt_ms = [float(v) for v in ping_rtt_ms]

            results[key][f"{label}_packet_loss_pct_under_{ul_dl}"] = ping_pkt_loss
            results[key][f"{label}_rtt_min_ms_under_{ul_dl}"] = ping_rtt_ms[0]
            results[key][f"{label}_rtt_max_ms_under_{ul_dl}"] = ping_rtt_ms[2]
            results[key][f"{label}_rtt_avg_ms_under_{ul_dl}"] = ping_rtt_ms[1]
            results[key][f"{label}_rtt_mdev_ms_under_{ul_dl}"] = ping_rtt_ms[3]

            if not quiet:
                print(f'\n --- {label} ping latency under load ---')
                print(f'Packet Loss Under Load: {ping_pkt_loss}%')
                print(f'Average RTT Under Load: {ping_rtt_ms[1]} (ms)')
                print(f'Minimum RTT Under Load: {ping_rtt_ms[0]} (ms)')
                print(f'Maximum RTT Under Load: {ping_rtt_ms[2]} (ms)')
                print(f'RTT Std Dev Under Load: {ping_rtt_ms[3]} (ms)')

            if (time.time() - start) < 11:
                time.sleep(11 - (time.time() - start))

    results[key]['error'] = error_found
    return ping_res