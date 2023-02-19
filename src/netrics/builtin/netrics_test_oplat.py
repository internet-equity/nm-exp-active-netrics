from .. utils import popen_exec
import logging
import json

log = logging.getLogger(__name__)


def test_oplat(key, measurement, args, results, quiet):

    limit = args["limit"]
    bandwidth_test_stochastic_limit = args["bandwidth_test_stochastic_limit"]
    measured_down = args["measured_down"]
    max_monthly_consumption_gb = args["max_monthly_consumption_gb"]
    max_monthly_tests = args["max_monthly_tests"]
    conf = args["conf"]
    client = args["client"]
    port = args["port"]

    if limit:
        if not bandwidth_test_stochastic_limit(measured_down=measured_down,
                                                    max_monthly_consumption_gb=max_monthly_consumption_gb,
                                                    max_monthly_tests=max_monthly_tests):
            log.info("limit_consumption applied, skipping test: OpLat")
            print("limit_consumption applied, skipping test: OpLat")
            return

    if 'targets' in conf['oplat']:
        targets = conf['oplat']['targets']
    else:
        return

    res = {}
    results[key] = {}

    error = False
    oplat_out = {}
    for upload in [True, False]:

        ul_dl = "ul" if upload else "dl"

        for dst in targets:
            cmd = "/usr/local/src/nm-exp-active-netrics/bin/oplat " \
                    "-s /usr/local/src/nm-exp-active-netrics/bin/iperf3.sh " \
                    "-c {} -p {} -d {} -i 0.25 -n 10 -m 'tcp icmp' -J {}".format(
                client, port, dst, "" if upload else "-R")
            oplat_out[ul_dl], err = popen_exec(cmd)
            if len(err) > 0:
                print(f'ERROR: {err}')
                log.error(err)
                results[key][f'{dst}_{ul_dl}_error'] = f'{err}'
                oplat_out[ul_dl] = {'error': f'{err}'}
                error = True
                continue

            res = json.loads(oplat_out[ul_dl])
            if ul_dl == "ul":
                sum_sent = res["SumSent"]
                results[key]['avg_sum_sent'] = float(sum_sent) / 13
                results['total_bytes_consumed'] += int(sum_sent)
            else:
                sum_recv = res["SumRecv"]
                results[key]['avg_sum_recv'] = float(sum_recv) / 13
                results['total_bytes_consumed'] += int(sum_recv)

            tcp_rates = []
            icmp_rates = []
            tcp_sum = 0
            icmp_sum = 0

            tcp_loads = res["TCPinger"]["PingLoads"]
            for probe in tcp_loads:
                tcp_rates.append(float(probe["Rate"]))

            for rate in set(tcp_rates):
                tcp_sum += rate

            icmp_loads = res["ICMPinger"]["PingLoads"]
            for probe in icmp_loads:
                icmp_rates.append(float(probe["Rate"]))

            for rate in set(icmp_rates):
                icmp_sum += rate

            field_dst = dst.split(":")[0]

            results[key][f'avg_rate_tcp_probes_{ul_dl}'] = tcp_sum / len(set(tcp_rates))
            results[key][f'avg_rate_icmp_probes_{ul_dl}'] = icmp_sum / len(set(icmp_rates))
            results[key][f'unloaded_icmp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["PacketLoss"])
            results[key][f'unloaded_icmp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["MinRtt"]) * 1e-6
            results[key][f'unloaded_icmp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["MaxRtt"]) * 1e-6
            results[key][f'unloaded_icmp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["AvgRtt"]) * 1e-6
            results[key][f'loaded_icmp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["PacketLoss"])
            results[key][f'loaded_icmp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["MinRtt"]) * 1e-6
            results[key][f'loaded_icmp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["MaxRtt"]) * 1e-6
            results[key][f'loaded_icmp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["AvgRtt"]) * 1e-6

            results[key][f'unloaded_tcp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["PacketLoss"])
            results[key][f'unloaded_tcp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["MinRtt"]) * 1e-6
            results[key][f'unloaded_tcp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["MaxRtt"]) * 1e-6
            results[key][f'unloaded_tcp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["AvgRtt"]) * 1e-6
            results[key][f'loaded_tcp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["PacketLoss"])
            results[key][f'loaded_tcp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["MinRtt"]) * 1e-6
            results[key][f'loaded_tcp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["MaxRtt"]) * 1e-6
            results[key][f'loaded_tcp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["AvgRtt"]) * 1e-6

    results[key]['error'] = error
    return oplat_out