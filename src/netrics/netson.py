""" Measurements
    Records selected network measurements
"""

from subprocess import Popen, PIPE
import time
import re

import os, sys, logging, traceback
from speedtest import Speedtest
from pathlib import Path
from tinydb import TinyDB, where
from tinydb.operations import increment
from tinydb.operations import set as tdb_set

log = logging.getLogger(__name__)

class Measurements:
    """ Take network measurements """

    def __init__(self, args, nmxperimentctrl):
        self.nma = nmxperimentctrl
        if self.nma.conf is None:
            log.error("No toml configuration.")
            os.exit(1)
        self.results = {}
        self.quiet = args.quiet
        self.sites = list(self.nma.conf['reference_site_dict'].keys())
        self.labels = self.nma.conf['reference_site_dict']
        if self.nma.conf['databases']['tinydb_enable']:
            try:
                Path(Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'])).mkdir(parents=True, exist_ok=True)
                speedtest_json = Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'], 'speedtest.json')
                seen_devices_json = Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'], 'seen_devices.json')

                if not speedtest_json.exists():
                    speedtest_json.touch()
                if not seen_devices_json.exists():
                    seen_devices_json.touch()

                self.speed_db = TinyDB(speedtest_json)
                self.dev_db = TinyDB(seen_devices_json)

                log.info("using {0}".format(speedtest_json))
                log.info("using {0}".format(seen_devices_json))

            except Exception as e:
                log.error("tinydb continuing without tinydb ({0} / {1})".
                    format(self.nma.conf['databases']['tinydb_path'], "{}".format(e)))
                self.nma.conf['databases']['tinydb_enable'] = False
        else:
            log.info("tinydb disabled")

        if self.nma.conf['databases']['tinydb_enable'] and (len(self.speed_db.all()) == 0):
            self.speed_db.insert(
                {'download': 600, 'upload': 50, 'test': False})

        if not self.quiet:
            print("\n --- NETWORK MEASUREMENTS ---")

    def update_sites(self, sites):
        """
        Method updates sites to visit during latency sites. Takes text file
        containing websites as input
        """

        self.labels = {}

        with open(sites) as f:
            for line in f:
                (website, label) = line.split()
                self.labels[website] = label

        self.sites = list(self.labels.keys())

    def update_max_speed(self, measured_down, measured_up):
        """
        Method updates the maximum measured upload and downlaod bandwidth
        from either the iperf3 test or the ookla speed test. This value
        is used as the guess for the iperf3 test
        """

        max_speed = self.speed_db.all()
        max_down = max(measured_down, max_speed[0]['download'])
        max_up = max(measured_up, max_speed[0]['upload'])

        if max_speed[0]['test']:
            self.speed_db.update({'download': max_down})
            self.speed_db.update({'upload': max_up})
        else:
            self.speed_db.update({'download': measured_down})
            self.speed_db.update({'upload': measured_up})

        self.speed_db.update({'test': True})

    def speed(self, run_test):
        """ Test runs Ookla Speed test """

        if not run_test:
            return

        s = Speedtest()
        s.get_best_server()
        s.download()
        s.upload()
        test_results = s.results.dict()

        download_speed = test_results["download"] / 1e6
        upload_speed = test_results["upload"] / 1e6

        self.update_max_speed(float(download_speed), float(upload_speed))

        self.results["speedtest_download"] = download_speed
        self.results["speedtest_upload"] = upload_speed

        if not self.quiet:
            print('\n --- Ookla speed tests ---')
            print(f'Download: {download_speed} Mb/s')
            print(f'Upload:   {upload_speed} Mb/s')
        return test_results

    def ping_latency(self, run_test):
        """
        Method records ping latency to self.sites
        """

        if not run_test:
            return

        ping_res = None

        for site in self.sites:
            ping_cmd = "ping -i {:.2f} -c {:d} -w {:d} {:s}".format(
                0.25, 10, 5, site)
            ping_res = Popen(ping_cmd, shell=True,
                             stdout=PIPE).stdout.read().decode('utf-8')

            ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                             ping_res, re.MULTILINE)[0])

            ping_rtt_ms = re.findall(
                'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                , ping_res)[0]

            ping_rtt_ms = [float(v) for v in ping_rtt_ms]

            label = self.labels[site]

            self.results[label + "_packet_loss_pct"] = ping_pkt_loss
            self.results[label + "_rtt_min_ms"] = ping_rtt_ms[0]
            self.results[label + "_rtt_max_ms"] = ping_rtt_ms[2]
            self.results[label + "_rtt_avg_ms"] = ping_rtt_ms[1]
            self.results[label + "_rtt_mdev_ms"] = ping_rtt_ms[3]

            if not self.quiet:
                print(f'\n --- {label} ping latency ---')
                print(f'Packet Loss: {ping_pkt_loss}%')
                print(f'Average RTT: {ping_rtt_ms[0]} (ms)')
                print(f'Minimum RTT: {ping_rtt_ms[1]} (ms)')
                print(f'Maximum RTT: {ping_rtt_ms[2]} (ms)')
                print(f'RTT Std Dev: {ping_rtt_ms[3]} (ms)')
        
        return ping_res

    def dns_latency(self, run_test):
        """
        Method records dig latency for each site in self.sites
        """

        if not run_test:
            return

        dig_res = None

        target = '8.8.8.8'

        if 'target' in self.nma.conf['dns_latency'].keys():
            target = self.nma.conf['dns_latency']['target']

        dig_delays = []

        for site in self.sites:
            dig_cmd = f'dig @{target} {site}'
            dig_res = Popen(dig_cmd, shell=True,
                            stdout=PIPE).stdout.read().decode('utf-8')

            dig_res_qt = re.findall('Query time: ([0-9]*) msec',
                                 dig_res, re.MULTILINE)[0]
            dig_delays.append(int(dig_res_qt))

        self.results["dns_query_avg_ms"] = sum(dig_delays) / len(dig_delays)
        self.results["dns_query_max_ms"] = max(dig_delays)

        if not self.quiet:
            print(f'\n --- DNS Delays (n = {len(dig_delays)}) ---')
            print(f'Avg DNS Query Time: {self.results["dns_query_avg_ms"]} ms')
            print(f'Max DNS Query Time: {self.results["dns_query_max_ms"]} ms')

        return dig_res

    def hops_to_backbone(self, run_test):
        """
        Method counts hops to 'ibone', center that all data leaving Chicago
        travels through
        """

        if not run_test:
            return

        tr_res = None

        target = 'www.google.com'

        if 'target' in self.nma.conf['hops_to_backbone']:
            target = self.nma.conf['hops_to_backbone']['target']

        tr_cmd = 'traceroute -m 15 -N 32 -w3 {0} | grep -m 1 ibone'.format(target)
        tr_res = Popen(tr_cmd, shell=True,
                       stdout=PIPE).stdout.read().decode('utf-8')

        tr_res_s = tr_res.strip().split(" ")

        if len(tr_res_s):
            hops = int(tr_res_s[0])
        else:
            hops = -1

        self.results["hops_to_backbone"] = hops

        if not self.quiet:
            print('\n --- Hops to Backbone ---')
            print(f'Hops: {self.results["hops_to_backbone"]}')
        
        return tr_res

    def hops_to_target(self, site):
        """
        Method counts the number of hops to the target site
        """

        if not site:
            return

        tr_res = None

        target = 'www.google.com'

        if 'target' in self.nma.conf['hops_to_target']:
            target = self.nma.conf['hops_to_target']['target']

        tr_cmd = f'traceroute -m 20 -q 5 -w 2 {target} | tail -1 | awk "{{print $1}}"'
        tr_res = Popen(tr_cmd, shell=True,
                       stdout=PIPE).stdout.read().decode('utf-8')

        tr_res_s = tr_res.strip().split(" ")

        hops = -1

        if len(tr_res_s):
            hops = int(tr_res_s[0])

        label = self.labels[target]

        self.results[f'hops_to_{label}'] = hops

        if not self.quiet:
            print('\n --- Hops to Target ---')
            print("Hops to {}: {}".format(target,
                                          self.results[f'hops_to_{label}']))
        return tr_res

    def connected_devices_arp(self, run_test):
        """
        Method counts the number of active devices on the network.
        """


        if not run_test:
            return

        res = {}

        ts = int(time.time())

        route_cmd = "ip r | grep /24 | awk '{print $1;}'"
        subnet = Popen(route_cmd, shell=True,
                       stdout=PIPE).stdout.read().decode('utf-8')

        nmap_cmd = f'nmap -sn {subnet}'
        Popen(nmap_cmd, shell=True, stdout=PIPE)

        arp_cmd = ("/usr/sbin/arp -i eth0 -n | grep : |"
                   "grep -v '_gateway' | tr -s ' ' | "
                   "cut -f3 -d' ' | sort | uniq")

        arp_res = Popen(arp_cmd, shell=True,
                        stdout=PIPE).stdout.read().decode('utf-8')
        res['arp'] = arp_res

        devices = set(arp_res.strip().split("\n"))
        active_devices = [[dev, ts, 1] for dev in devices]

        for device in active_devices:
            if self.dev_db.contains(where('mac_addr') == device[0]):
                self.dev_db.update(increment("n"),
                                   where('mac_addr') == device[0])
                self.dev_db.update(tdb_set('last_seen', device[1]),
                                   where('mac_addr') == device[0])
            else:
                self.dev_db.insert({'mac_addr': device[0],
                                    'last_seen': device[1],
                                    'n': device[2]})

        print(self.dev_db.all())
        ndev_past_day = len(self.dev_db.search(
            where('last_seen') > (ts - 86400)))
        ndev_past_week = len(self.dev_db.search(
            where('last_seen') > (ts - 86400*7)))

        print(ndev_past_day)
        self.results["devices_active"] = len(active_devices)
        self.results["devices_total"] = self.dev_db.count(where('n') >= 1)
        self.results["devices_1day"] = ndev_past_day
        self.results["devices_1week"] = ndev_past_week

        if not self.quiet:
            print('\n --- Number of Devices ---')
            print(f'Number of active devices: '
                  f'{self.results["devices_active"]}')
            print(f'Number of total devices: '
                  f'{self.results["devices_total"]}')
            print(f'Number of devices in last 1 day:'
                  f' {self.results["devices_1day"]}')
            print(f'Number of devices in last week:'
                  f' {self.results["devices_1week"]}')
        return res

    def iperf3_bandwidth(self, client, port):
        """
        Method for recorded results of iperf3 bandwidth tests
        """

        if not client:
            return

        iperf_res = None

        if self.nma.conf['databases']['tinydb_enable']:
            speed = self.speed_db.all()

        measured_bw = {'upload': 0, 'download': 0}
        measured_jitter = {'upload': 0, 'download': 0}

        for direction, value in measured_bw.items():
            reverse = False

            bandwidth = 0

            if self.nma.conf['databases']['tinydb_enable']:
                bandwidth = speed[0][direction] + 10
                if direction == 'download':
                    bandwidth += 40
                    reverse = True

            iperf_cmd = "/usr/local/bin/iperf3 -c {} -p {} -u -i 0 -b {}M {} | awk 'NR=={}'"\
                .format(client, port, bandwidth,
                        '-R' if reverse else "", 10 if reverse else 8)
            iperf_res = Popen(iperf_cmd, shell=True,
                              stdout=PIPE).stdout.read().decode('utf-8')

            measured_bw[direction] = iperf_res.split()[6]
            measured_jitter[direction] = iperf_res.split()[8]

            self.results[f'iperf_udp_{direction}'] = float(
                measured_bw[direction])
            self.results[f'iperf_udp_{direction}_jitter_ms'] = float(
                measured_jitter[direction])

            if not self.quiet:
                if direction == 'upload':
                    print('\n --- iperf Bandwidth and Jitter ---')
                print(f'{direction} bandwidth: {measured_bw[direction]} Mb/s')
                print(f'{direction} jitter: {measured_jitter[direction]} ms')

        if self.nma.conf['databases']['tinydb_enable']:
            self.update_max_speed(float(measured_bw['download']),
                              float(measured_bw['upload']))
        return iperf_res
