import json
from .. utils import popen_exec
import logging

log = logging.getLogger(__name__)

def test_ookla(key, measurement, conf, results, quiet):
    error_found = False
    timeout = 35
    try:
       timeout = conf['ookla']['timeout']
    except KeyError:
       print(f"WARN: Ookla timeout not set, default to {timeout}.")
       log.warn(f"Ookla timeout not set, default to {timeout}.")
    output, err = popen_exec(f"timeout {timeout} /usr/local/src/nm-exp-active-netrics/bin/speedtest --accept-license -p no -f json -u kbps")
    if len(err) > 0:
       results[key]["error"] = f'{err}'
       print(f"ERROR: {err}")
       log.error(err)

       results_available = False
       error_found = True
       if len(output) > 0:
          try:
             res_json = json.loads(output)
             if "download"  in res_json and \
                "bandwidth" in res_json["download"]:
                  results_available = True
          except ValueError:
            log.warn("Unable to parse output")

          if results_available and \
             "Timeout occurred in connect" in err:

             log.warn("Saving speedtest despite connect timeout error.")

          else:
             results[key]["ookla_error"] = error_found 
          return f'{err}'

    try:
        res_json = json.loads(output)
    except Exception as err:
        results[key]["ookla_json_error"] = f'{err}'
        error_found = True
        results[key]["ookla_error"] = error_found
        log.exception('Ookla JSON failed to load. Aborting test.')
        return output
    download_ookla = res_json["download"]['bandwidth'] * 8 / 1e6
    upload_ookla = res_json["upload"]['bandwidth'] * 8 / 1e6
    jitter_ookla = res_json['ping']['jitter']
    latency_ookla = res_json['ping']['latency']

    # Calculating data transferred 
    ul_bw_used = int(res_json['upload']['bytes']) 
    dl_bw_used = int(res_json['download']['bytes']) 
    results['total_bytes_consumed'] += ul_bw_used + dl_bw_used

    pktloss_ookla = None
    if 'packetLoss' in res_json.keys():
        pktloss_ookla = res_json['packetLoss']
    if conf['databases']['tinydb_enable']:
        measurement.update_max_speed(float(download_ookla), float(upload_ookla))

    results[key]["speedtest_ookla_download"] = float(download_ookla)
    results[key]["speedtest_ookla_upload"] = float(upload_ookla)
    results[key]["speedtest_ookla_jitter"] = float(jitter_ookla)
    results[key]["speedtest_ookla_latency"] = float(latency_ookla)

    results[key]["speedtest_ookla_server_host"] = res_json["server"]["host"]
    results[key]["speedtest_ookla_server_name"] = res_json["server"]["name"]
    results[key]["speedtest_ookla_server_id"]   = res_json["server"]["id"] 

    if pktloss_ookla is not None:
        results[key]["speedtest_ookla_pktloss2"] = float(pktloss_ookla)

    if not quiet:
        print('\n --- Ookla speed tests ---')
        print(f'Download:\t{download_ookla} Mb/s')
        print(f'Upload:\t\t{upload_ookla} Mb/s')
        print(f'Latency:\t{latency_ookla} ms')
        print(f'Jitter:\t\t{jitter_ookla} ms')
            
    if pktloss_ookla is not None:
        print(f'PktLoss:\t{pktloss_ookla}%')
    else:
        print(f'PktLoss:\tnot returned by test.')
        
    results[key]["ookla_error"] = error_found

    return output #res_json


def parse_ndt7_output(output):
    """Parse output of non-quiet ndt7-client JSON"""

    res_json = {}
    dl_bytes = 0
    ul_bytes = 0
    res_text = ''

    for obj in output.split("\n")[:-1]:
        r = json.loads(obj)
        if r.get("Value", 0):
            num_bytes = r["Value"]["AppInfo"]["NumBytes"]
            if r["Value"]["Test"] == "download":
                dl_bytes = num_bytes
            else:
                ul_bytes = num_bytes
        else:
            res_json = r
            res_text = obj

    total_bytes = dl_bytes + ul_bytes

    return (res_json, res_text, total_bytes)


def test_ndt7(key, measurement, conf, results, quiet):
    error_found = False
    output, err = popen_exec("/usr/local/src/nm-exp-active-netrics/bin/ndt7-client -scheme ws -format 'json' | grep -i 'numbytes\|FQDN'")
    if len(err) > 0:
        results[key]["error"] = f'{err}'
        print(f"ERROR: {err}")
        log.error(err)
        error_found = True
        results[key]["ndt_error"] = error_found
        return f'{err}'
    res_json, res_text, total_bytes = parse_ndt7_output(output)

    download_speed = float(res_json["Download"]["Throughput"]["Value"])
    download_latency = float(res_json["Download"]["Latency"]["Value"])
    upload_speed = float(res_json["Upload"]["Throughput"]["Value"])
    download_retrans = float(res_json["Download"]["Retransmission"]["Value"])
    # not in new json
    # minrtt = float(res_json['MinRTT']['Value'])

    results[key]["speedtest_ndt7_download"] = download_speed
    results[key]["speedtest_ndt7_upload"] = upload_speed
    results[key]["speedtest_ndt7_downloadretrans"] = download_retrans
    results[key]["speedtest_ndt7_downloadlatency"] = download_latency
    results[key]["speedtest_ndt7_server"] = res_json['ServerFQDN']
    # results[key]["speedtest_ndt7_minrtt"] = minrtt
    results["total_bytes_consumed"] += total_bytes
    if not quiet:
        print('\n --- NDT7 speed tests ---')
        print(f'Download:\t{download_speed} Mb/s')
        print(f'Upload:\t\t{upload_speed} Mb/s')
        print(f'DownloadRetrans:{download_retrans} %')
        print(f'Download Latency:{download_latency} ms')
        # print(f'MinRTT:\t\t{minrtt} ms')

    results[key]["ndt_error"] = error_found

    return res_text #res_json

