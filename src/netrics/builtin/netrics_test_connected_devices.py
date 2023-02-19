from .. utils import popen_exec
import logging
import time
from subprocess import Popen, PIPE
from tinydb import where
from tinydb.operations import increment
from tinydb.operations import set as tdb_set

log = logging.getLogger(__name__)


def test_connected_devices(key, measurement, dev_db, conf, results, quiet):
    """
    Method counts the number of active devices on the network.
    """

    res = {}

    ts = int(time.time())
    iface = 'eth0'

    if 'nmap_dev_scan' in conf.keys():
        if 'iface' in conf['nmap_dev_scan']:
            iface = conf['nmap_dev_scan']['iface']

    route_cmd = f"ip r | grep -v default | grep src | grep {iface} | head -n 1 | awk '{{print $1;}}'"
    subnet = Popen(route_cmd, shell=True,
                    stdout=PIPE).stdout.read().decode('utf-8').strip(" \n")
    nmap_cmd = f'nmap -sn {subnet}'
    Popen(nmap_cmd, shell=True, stdout=PIPE).stdout.read()

    arp_cmd = (f"/usr/sbin/arp -i {iface} -n | grep : |"
                "grep -v '_gateway' | tr -s ' ' | "
                "cut -f3 -d' ' | sort | uniq")

    arp_res, err = popen_exec(arp_cmd)
    if len(err) > 0:
        print(f"ERROR: {err}")
        log.error(err)
        return None

    ## use arp_res to collect device mac address, it's disabled for now
    res['arp'] = "[REDACTED]"

    devices = set(arp_res.strip().split("\n"))
    active_devices = [[dev, ts, 1] for dev in devices]

    for device in active_devices:
        if dev_db.contains(where('mac_addr') == device[0]):
            dev_db.update(increment("n"),
                                where('mac_addr') == device[0])
            dev_db.update(tdb_set('last_seen', device[1]),
                                where('mac_addr') == device[0])
        else:
            dev_db.insert({'mac_addr': device[0],
                                'last_seen': device[1],
                                'n': device[2]})

    print(dev_db.all())
    ndev_past_day = len(dev_db.search(
        where('last_seen') > (ts - 86400)))
    ndev_past_week = len(dev_db.search(
        where('last_seen') > (ts - 86400*7)))

    print(ndev_past_day)

    results[key]["devices_active"] = len(active_devices)
    results[key]["devices_total"] = dev_db.count(where('n') >= 1)
    results[key]["devices_1day"] = ndev_past_day
    results[key]["devices_1week"] = ndev_past_week

    if not quiet:
        print('\n --- Number of Devices ---')
        print(f'Number of active devices: '
                f'{results[key]["devices_active"]}')
        print(f'Number of total devices: '
                f'{results[key]["devices_total"]}')
        print(f'Number of devices in last 1 day:'
                f' {results[key]["devices_1day"]}')
        print(f'Number of devices in last week:'
                f' {results[key]["devices_1week"]}')
    return res