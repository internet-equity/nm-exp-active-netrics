from .. utils import popen_exec
import logging
import re 

log = logging.getLogger(__name__)


def test_ping_latency(key, measurement, args, results, quiet):
    """
    Method records ping latency to sites given
    """

    ping_res = {}
    error_found = False
    ping_failure_count = 0

    sites = args["sites"]
    labels = args["labels"]

    for site in sites:
        ping_cmd = "ping -i {:.2f} -c {:d} -w {:d} {:s}".format(
            0.25, 10, 5, site)

        try:
            label = labels[site]
        except KeyError:
            label = site

        ping_res[label] = {}

        ping_res[label], err = popen_exec(ping_cmd)
        if len(err) > 0:
            print(f"ERROR: {err}")
            log.error(err)
            results[key][label + "_error"] = err.strip()
            ping_res[label] = { 'error' : f'{err}' }
            error_found = True

            if "Name or service not known" in err or \
                "Temporary failure in name resolution" in err:
                ping_failure_count += 1

            if ping_failure_count >= 5:
                log.error("Aborting additional pings: 5 failures.")
                break

            continue

        try:
            ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                            ping_res[label], re.MULTILINE)[0])
        except IndexError:
            results[key][label + "_error"] = 'Packet Loss IndexError'
            ping_res[label] = {'error': 'Packet Loss IndexErorr'}
            log.error('Packet Loss IndexErorr: Unexpected output from ping')
            error_found = True
            continue

        try:
            ping_rtt_ms = re.findall(
                'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                , ping_res[label])[0]
        except IndexError:
            results[key][label + "_error"] = 'Probe IndexError'
            ping_res[label] = {'error': 'Probe IndexErorr'}
            log.error('Probe IndexErorr: Unexpected output from ping')
            error_found = True
            continue


        ping_rtt_ms = [float(v) for v in ping_rtt_ms]

        results[key][label + "_packet_loss_pct"] = ping_pkt_loss
        results[key][label + "_rtt_min_ms"] = ping_rtt_ms[0]
        results[key][label + "_rtt_max_ms"] = ping_rtt_ms[2]
        results[key][label + "_rtt_avg_ms"] = ping_rtt_ms[1]
        results[key][label + "_rtt_mdev_ms"] = ping_rtt_ms[3]

        if not quiet:
            print(f'\n --- {label} ping latency (MANDATORY) ---')
            print(f'Packet Loss: {ping_pkt_loss}%')
            print(f'Average RTT: {ping_rtt_ms[0]} (ms)')
            print(f'Minimum RTT: {ping_rtt_ms[1]} (ms)')
            print(f'Maximum RTT: {ping_rtt_ms[2]} (ms)')
            print(f'RTT Std Dev: {ping_rtt_ms[3]} (ms)')

    results[key]["error"] = error_found
    return ping_res