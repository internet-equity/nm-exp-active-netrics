from .. utils import popen_exec
import logging
import json
import time
import random

log = logging.getLogger(__name__)


def test_iperf3(key, measurement, args, results, quiet):
    """
    Method to record results of iperf3 bandwidth tests
    """

    limit = args["limit"]
    bandwidth_test_stochastic_limit = args["bandwidth_test_stochastic_limit"]
    measured_down = args["measured_down"]
    max_monthly_consumption_gb = args["max_monthly_consumption_gb"]
    max_monthly_tests = args["max_monthly_tests"]
    conf = args["conf"]
    client = args["client"]
    port = args["port"]
    speed_db = args["speed_db"]
    update_max_speed = args["update_max_speed"]

    if limit:
        if not bandwidth_test_stochastic_limit(measured_down = measured_down,
                max_monthly_consumption_gb = max_monthly_consumption_gb,
                max_monthly_tests = max_monthly_tests):
            log.info("limit_consumption applied, skipping test: iperf")
            print("limit_consumption applied, skipping test: iperf")
            return

    iperf_res = {}
    error_found = False
    
    if conf['databases']['tinydb_enable']:
        speed = speed_db.all()

    measured_bw = {'upload': 0, 'download': 0}
    measured_jitter = {'upload': 0, 'download': 0}
    
    length = None ##default
    if 'buffer_length' in conf['iperf'].keys():
        length = conf['iperf']['buffer_length']

    for direction, value in measured_bw.items():
        reverse = False

        bandwidth = 0

        if conf['databases']['tinydb_enable']:
            bandwidth = speed[0][direction] * 1.05
        
        if direction == 'download':
            reverse = True
            
        #log.info(f"iperf using buffer_length: {length}")
        iperf_cmd = "/usr/local/src/nm-exp-active-netrics/bin/iperf3.sh" \
                    " -c {} -p {} -u -P 4 -b {:.2f}M {} {} --json"\
                    .format(client, port, bandwidth/4, 
                            f'-l {length}' if length is not None else '',
                            '-t 5 -R -i 1' if reverse else "-t 20 -i 0")

        for attempt_num in range(1, 5):
            (output, err) = popen_exec(iperf_cmd)
            if 'try again later' in err:
                if attempt_num < 4:
                    log.error(f'{attempt_num} / 4: {err}: Will try test again...')
                    time.sleep(30 + random.randint(1, 60))
                else:
                    log.error(f'{attempt_num} / 4: {err}: Will *not* try test again.')
            else:
                break
        if len(err) > 0:            
            print(f"ERROR: {err}")
            results[key][f'iperf_{direction}_error'] = f'{err}'
            iperf_res[direction] = { f'output' : output, 'error' : err }
            log.error(err)
            error_found = True
            continue
        
        try:
            iperf_res[direction] = output
            json_res = json.loads(output)
        except Exception as err:
            log.error(f'{err}')
            results[key] = { f'iperf_{direction}_error' : f'{err}' }
            iperf_res[direction] = { f'output' : output, 'error' : f'{err}' }
            continue

        if direction == "upload":
            lost_pct = json_res["end"]["sum"]["lost_percent"]
            frac_recvd = (100 - lost_pct) / 100
            measured_bw[direction] = frac_recvd * float(json_res["end"]["sum"]["bits_per_second"]) / 1e6

            results['total_bytes_consumed'] += json_res['end']['sum']['bytes']

        else:

            seconds     = sum([i["sum"]["seconds"] for i in json_res["intervals"]])
            total_bytes = sum([i["sum"]["bytes"]   for i in json_res["intervals"]])

            measured_bw[direction] = total_bytes * 8. / seconds / 1e6
            results['total_bytes_consumed'] += total_bytes

            for i in range(5):

                interval_seconds = json_res["intervals"][i]["sum"]["seconds"]
                interval_bytes   = json_res["intervals"][i]["sum"]["bytes"]
                results[key][f'iperf_udp_download_i{i}'] = interval_bytes * 8 / interval_seconds / 1e6

        results[key][f'iperf_udp_{direction}'] = measured_bw[direction]


        measured_jitter[direction] = float(json_res['end']['sum']['jitter_ms'])
        results[key][f'iperf_udp_{direction}_jitter_ms'] = measured_jitter[direction]

        if not quiet:
            if direction == 'upload':
                print('\n --- iperf Bandwidth ---')
            print(f'{direction} bandwidth: {measured_bw[direction]} Mb/s')
            print(f'{direction} jitter: {measured_jitter[direction]} ms')

    results[key]['error'] = error_found
    if conf['databases']['tinydb_enable']:
        update_max_speed(measured_bw['download'],
                                measured_bw['upload'])

    return iperf_res