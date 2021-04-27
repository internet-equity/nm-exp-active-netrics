""" Measurements
    Records selected network measurements
"""

from subprocess import Popen, PIPE
import time
import re
import json

import os, sys, logging, traceback
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

    def speed_ookla(self, run_test):
        """ Test runs Ookla Speed test """

        if not run_test:
            return

        # TODO: to account for errors/faults in the execution
        output = Popen('/usr/local/src/nm-exp-active-netrics/bin/speedtest --accept-license -p no -f json -u kbps',
                shell=True, stdout=PIPE).stdout.read().decode('utf-8')
        res_json = json.loads(output)
        download_ookla = res_json["download"]['bandwidth'] / 1e5 #TODO: why this is in 1e5 and not in 1e6?
        upload_ookla = res_json["upload"]['bandwidth'] / 1e5
        jitter_ookla = res_json['ping']['jitter']
        latency_ookla = res_json['ping']['latency']
        pktloss_ookla = None
        if 'packetLoss' in res_json.keys():
            pktloss_ookla = res_json['packetLoss']
        self.update_max_speed(float(download_ookla), float(upload_ookla))

        self.results["speedtest_ookla_download"] = download_ookla
        self.results["speedtest_ookla_upload"] = upload_ookla
        self.results["speedtest_ookla_jitter"] = jitter_ookla
        self.results["speedtest_ookla_latency"] = latency_ookla
        if pktloss_ookla is not None:
            self.results["speedtest_ookla_pktloss"] = pktloss_ookla

        if not self.quiet:
            print('\n --- Ookla speed tests ---')
            print(f'Download:\t{download_ookla} Mb/s')
            print(f'Upload:\t\t{upload_ookla} Mb/s')
            print(f'Latency:\t{latency_ookla} ms')
            print(f'Jitter:\t\t{jitter_ookla} ms')
            print(f'PktLoss:\t{pktloss_ookla} Total Count')
        return res_json

    def speed_ndt7(self, run_test):
        """ Test runs NDT7 Speed test """

        if not run_test:
            return

        # TODO: to account for errors/faults in the execution
        output = Popen("/usr/local/src/nm-exp-active-netrics/bin/ndt7-client -quiet -format 'json'",
                shell=True, stdout=PIPE).stdout.read().decode('utf-8')
        res_json = json.loads(output)

        download_speed = res_json["Download"]["Value"]
        upload_speed = res_json["Upload"]["Value"]
        download_retrans = float(res_json["DownloadRetrans"]["Value"])
        minrtt = res_json['MinRTT']['Value']

        self.results["speedtest_ndt7_download"] = download_speed
        self.results["speedtest_ndt7_upload"] = upload_speed
        self.results["speedtest_ndt7_downloadretrans"] = download_retrans
        self.results["speedtest_ndt7_minrtt"] = minrtt

        if not self.quiet:
            print('\n --- NDT7 speed tests ---')
            print(f'Download:\t{download_speed} Mb/s')
            print(f'Upload:\t\t{upload_speed} Mb/s')
            print(f'DownloadRetrans:{download_retrans} %')
            print(f'MinRTT:\t\t{minrtt} ms')
 
        return res_json

    def speed(self):
        return self.speed_ookla(True), self.speed_ndt7(True)

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

    def latency_under_load(self, run_test, client, port):
        """
        Method records ping latency under load to self.sites_load
        """

        if not run_test: return
        if not client:   return

        if 'targets' in self.nma.conf['latency_under_load']:
            targets = self.nma.conf['latency_under_load']['targets']
        else:
            return

        ping_res = None

        for upload in [True, False]:

            ul_dl = "ul" if upload else "dl"

            load = "/usr/local/src/nm-exp-active-netrics/bin/iperf3.sh -c {} -p {} -i 0 -t 10 {}"\
                       .format(client, port, "" if upload else "-R" )

            load += " > /dev/null & sleep 2 && echo starting ping && "

            for site in targets:

                ping_cmd = "ping -i 0.25 -c 10 -w 5 {:s}".format(site)
                
                start = time.time()
                ping_res = Popen(load + ping_cmd, shell=True,
                                 stdout=PIPE).stdout.read().decode('utf-8')

                ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                                 ping_res, re.MULTILINE)[0])

                ping_rtt_ms = re.findall(
                    'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                    , ping_res)[0]

                ping_rtt_ms = [float(v) for v in ping_rtt_ms]

                label = self.labels[site]

                self.results[f"{label}_packet_loss_pct_under_{ul_dl}"] = ping_pkt_loss
                self.results[f"{label}_rtt_min_ms_under_{ul_dl}"] = ping_rtt_ms[0]
                self.results[f"{label}_rtt_max_ms_under_{ul_dl}"] = ping_rtt_ms[2]
                self.results[f"{label}_rtt_avg_ms_under_{ul_dl}"] = ping_rtt_ms[1]
                self.results[f"{label}_rtt_mdev_ms_under_{ul_dl}"] = ping_rtt_ms[3]

                if not self.quiet:
                    print(f'\n --- {label} ping latency under load ---')
                    print(f'Packet Loss Under Load: {ping_pkt_loss}%')
                    print(f'Average RTT Under Load: {ping_rtt_ms[1]} (ms)')
                    print(f'Minimum RTT Under Load: {ping_rtt_ms[0]} (ms)')
                    print(f'Maximum RTT Under Load: {ping_rtt_ms[2]} (ms)')
                    print(f'RTT Std Dev Under Load: {ping_rtt_ms[3]} (ms)')

                if (time.time() - start) < 11:
                    time.sleep(11 - (time.time() - start))
        
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

        nmap_cmd = f'nmap --unprivileged -sn {subnet}'
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

            iperf_cmd = "/usr/local/src/nm-exp-active-netrics/bin/iperf3.sh -c {} -p {} -u -i 0 -b {}M {} | awk 'NR=={}'"\
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


    def tshark_eth_consumption(self, run_test, dur = 60):

        if not run_test:
            return

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
        self.results["consumption_download"] = dl * 8 / 1e6 / duration
        self.results["consumption_upload"]   = ul * 8 / 1e6 / duration

        return tshark_res


