import re
from subprocess import Popen, PIPE
import logging

log = logging.getLogger(__name__)


def test_tshark(key, measurement, results, quiet, dur):

    local_ip_cmd   = "ip a show dev eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'"
    gateway_ip_cmd = "ip r | grep default | cut -f3 -d' '"

    loc_ip = Popen(local_ip_cmd,   shell = True, stdout = PIPE).stdout.read().decode('utf-8').strip()
    gw_ip  = Popen(gateway_ip_cmd, shell = True, stdout = PIPE).stdout.read().decode('utf-8').strip()

    cap_filter = f"not broadcast and not multicast and not (ip src {loc_ip} or ip dst {loc_ip} or ip src {gw_ip} or ip dst {gw_ip})"

    tshark_cmd = f'tshark -f "{cap_filter}" -i eth0 -a duration:{dur} -Q -z conv,ip -z io,stat,{dur*2}'
    tshark_res = Popen(tshark_cmd, shell = True, stdout = PIPE).stdout.read().decode('utf-8')
    print(tshark_res)
    duration = float(re.findall("Duration: ([0-9.]*) secs", tshark_res, re.MULTILINE)[0])
    print("duration:{}".format(duration))

    columns = ["A", "B", "BA_fr", "BA_bytes", "AB_fr", "AB_bytes", "tot_fr", "to_bytes", "start", "duration"]

    tshark_conv = re.findall('(.*<->.*)', tshark_res, re.MULTILINE)
    tshark_list = [re.sub("<->", "", l).split() for l in tshark_conv]

    tshark_conn = [{c : conn[ci] for ci, c in enumerate(columns)}
                    for conn in tshark_list]

    dl, ul = 0, 0
    for conn in tshark_conn:
        if "192.168" in conn["A"]:
            dn, up = "BA", "AB"
        else:
            dn, up = "AB", "BA"

        dl += float(conn[f"{dn}_bytes"])
        ul += float(conn[f"{up}_bytes"])


    # Converts bytes to Mbps
    results[key]["consumption_download"] = dl * 8 / 1e6 / duration
    results[key]["consumption_upload"]   = ul * 8 / 1e6 / duration

    return tshark_res