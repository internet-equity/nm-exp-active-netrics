""" Measurements
    Records selected network measurements
"""

from subprocess import Popen, PIPE
import time
import re
import json
import random
import ipaddress
import urllib.request
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
        self.results = { 'total_bytes_consumed' : 0 }
        self.quiet = args.quiet

        self.sites = list(self.nma.conf['reference_site_dict'].keys())
        self.labels = self.nma.conf['reference_site_dict']
#        self.resolvers = self.nma.conf['dns_latency']['encrypted_dns_targets']
        self.resolvers = list(self.nma.conf['resolver_dict'].keys())
        self.res_labels = self.nma.conf['resolver_dict']
        self.measured_down = 5
        self.max_monthly_consumption_gb = 200
        self.max_monthly_tests = 200

        if 'limit_consumption' in self.nma.conf.keys():
            if 'measured_down' in self.nma.conf['limit_consumption']:
                if self.nma.conf['limit_consumption']['measured_down'] > 0:
                    self.measured_down = self.nma.conf['limit_consumption']['measured_down']
            if 'max_monthly_consumption_gb' in self.nma.conf['limit_consumption']:
                if self.nma.conf['limit_consumption']['max_monthly_consumption_gb'] is not None:
                    self.max_monthly_consumption_gb = int(self.nma.conf['limit_consumption']['max_monthly_consumption_gb'])
            if 'max_monthly_tests' in self.nma.conf['limit_consumption']:
                if self.nma.conf['limit_consumption']['max_monthly_tests'] is not None:
                    self.max_monthly_tests = int(self.nma.conf['limit_consumption']['max_monthly_tests'])

        if self.nma.conf['databases']['tinydb_enable']:
            try:
                Path(Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'])).mkdir(parents=True, exist_ok=True)
                speedtest_json = Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'], 'speedtest.json')
                seen_devices_json = Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'], 'seen_devices.json')
                consumption_json = Path.cwd().joinpath(self.nma.conf['databases']['tinydb_path'], 'consumption.json')
                if not speedtest_json.exists():
                    speedtest_json.touch()
                if not seen_devices_json.exists():
                    seen_devices_json.touch()
                if not consumption_json.exists():
                    consumption_json.touch()

                self.speed_db = TinyDB(speedtest_json)
                self.dev_db = TinyDB(seen_devices_json)
                self.consumption_db = TinyDB(consumption_json)

                log.info("DB using {0}".format(speedtest_json))
                log.info("DB using {0}".format(seen_devices_json))
                log.info("DB using {0}".format(consumption_json))

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

    def popen_exec(self, cmd):
        pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out = pipe.stdout.read().decode('utf-8')
        err = pipe.stderr.read().decode('utf-8')
        return out, err

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

    def ipquery(self, key="ipquery", run_test=True):
        j4 = None
        #j6 = None
        try:
           req = urllib.request.Request("https://api.ipify.org?format=json")
           with urllib.request.urlopen(req) as response:
             if response.getcode()!=200:
                log.warn('Ip Query Unexpected:'+str(response.getcode()))
             else:
                j4 = json.loads(response.read().decode())
           #req = urllib.request.Request("https://api64.ipify.org?format=json")
           #with urllib.request.urlopen(req) as response:
           #  if response.getcode()!=200:
           #     log.warn('Ip Query Unexpected:'+str(response.getcode()))
           #  else:
           #     j6 = json.loads(response.read().decode())

           if 'ip' in j4.keys(): j4 = j4['ip']
           #if 'ip' in j6.keys(): j6 = j6['ip'] #TODO: make ipv6 to work?
           #self.results[key] = { 'ipv4': j4, 'ipv6': j6 }
           self.results[key] = { 'ipv4': j4 }
        except Exception as err:
           self.results[key] = { 'error': f'{err}' }
        #res = { 'ipv4': j4, 'ipv6': j6 }
        res = { 'ipv4': j4 }
        if 'error' in self.results[key].keys():
           res = { 'error': self.results[key]['error'] }
        return res

    def speed_ookla(self, key, run_test):
        """ Test runs Ookla Speed test """
        """ key: test name """

        if not run_test:
            return

        self.results[key] = {}
        error_found = False
        output, err = self.popen_exec("timeout 35 /usr/local/src/nm-exp-active-netrics/bin/speedtest --accept-license -p no -f json -u kbps")
        if len(err) > 0:
             self.results[key]["error"] = f'{err}'
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
                self.results[key]["ookla_error"] = error_found 
                return f'{err}'

        try:
            res_json = json.loads(output)
        except Exception as err:
            self.results[key]["ookla_json_error"] = f'{err}'
            error_found = True
            self.results[key]["ookla_error"] = error_found
            log.exception('Ookla JSON failed to load. Aborting test.')
            return output
        download_ookla = res_json["download"]['bandwidth'] * 8 / 1e6
        upload_ookla = res_json["upload"]['bandwidth'] * 8 / 1e6
        jitter_ookla = res_json['ping']['jitter']
        latency_ookla = res_json['ping']['latency']

        # Calculating data transferred 
        ul_bw_used = int(res_json['upload']['bytes']) 
        dl_bw_used = int(res_json['download']['bytes']) 
        self.results['total_bytes_consumed'] += ul_bw_used + dl_bw_used

        pktloss_ookla = None
        if 'packetLoss' in res_json.keys():
            pktloss_ookla = res_json['packetLoss']
        if self.nma.conf['databases']['tinydb_enable']:
            self.update_max_speed(float(download_ookla), float(upload_ookla))

        self.results[key]["speedtest_ookla_download"] = float(download_ookla)
        self.results[key]["speedtest_ookla_upload"] = float(upload_ookla)
        self.results[key]["speedtest_ookla_jitter"] = float(jitter_ookla)
        self.results[key]["speedtest_ookla_latency"] = float(latency_ookla)

        self.results[key]["speedtest_ookla_server_host"] = res_json["server"]["host"]
        self.results[key]["speedtest_ookla_server_name"] = res_json["server"]["name"]
        self.results[key]["speedtest_ookla_server_id"]   = res_json["server"]["id"] 

        if pktloss_ookla is not None:
            self.results[key]["speedtest_ookla_pktloss2"] = float(pktloss_ookla)

        if not self.quiet:
            print('\n --- Ookla speed tests ---')
            print(f'Download:\t{download_ookla} Mb/s')
            print(f'Upload:\t\t{upload_ookla} Mb/s')
            print(f'Latency:\t{latency_ookla} ms')
            print(f'Jitter:\t\t{jitter_ookla} ms')
            
            if pktloss_ookla is not None:
                print(f'PktLoss:\t{pktloss_ookla}%')
            else:
                print(f'PktLoss:\tnot returned by test.')
        
        self.results[key]["ookla_error"] = error_found

        return output #res_json

    def parse_ndt7_output(self, output):
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


    def speed_ndt7(self, key, run_test):
        """ Test runs NDT7 Speed test """
        """ key: test name """

        if not run_test:
            return

        self.results[key] = {}
        error_found = False
        output, err = self.popen_exec("/usr/local/src/nm-exp-active-netrics/bin/ndt7-client -scheme ws -format 'json' | grep -i 'numbytes\|FQDN'")
        if len(err) > 0:
             self.results[key]["error"] = f'{err}'
             print(f"ERROR: {err}")
             log.error(err)
             error_found = True
             self.results[key]["ndt_error"] = error_found
             return f'{err}'

        res_json, res_text, total_bytes = self.parse_ndt7_output(output)

        download_speed = float(res_json["Download"]["Value"])
        upload_speed = float(res_json["Upload"]["Value"])
        download_retrans = float(res_json["DownloadRetrans"]["Value"])
        minrtt = float(res_json['MinRTT']['Value'])

        self.results[key]["speedtest_ndt7_download"] = download_speed
        self.results[key]["speedtest_ndt7_upload"] = upload_speed
        self.results[key]["speedtest_ndt7_downloadretrans"] = download_retrans
        self.results[key]["speedtest_ndt7_minrtt"] = minrtt
        self.results[key]["speedtest_ndt7_server"] = res_json['ServerFQDN']
        self.results["total_bytes_consumed"] += total_bytes
        
        if not self.quiet:
            print('\n --- NDT7 speed tests ---')
            print(f'Download:\t{download_speed} Mb/s')
            print(f'Upload:\t\t{upload_speed} Mb/s')
            print(f'DownloadRetrans:{download_retrans} %')
            print(f'MinRTT:\t\t{minrtt} ms')
 
        self.results[key]["ndt_error"] = error_found

        return res_text #res_json

    def bandwidth_test_stochastic_limit(self, measured_down=5,
                                        max_monthly_consumption_gb=200,
                                        max_monthly_tests=200):
        max_speed = self.speed_db.all()
        speed = max(measured_down, max_speed[0]['download'])  # should be Mbps

        print("speed", speed)
        # This assumes 1GB per test, for a gig link.
        # The factor of 4 is for ndt7, iperf3, speedtest, and latency under load
        monthly_tests = (max_monthly_consumption_gb / 4) * (1000 / speed)

        print("monthly_tests", monthly_tests)
        log.info(f"bandwidth_test_stochastic_limit: monthly_tests={monthly_tests} max_monthly_tests={max_monthly_tests}"\
                f" max_speed={max_speed[0]['download']} measured_down:{measured_down}")
        print(f"bandwidth_test_stochastic_limit: monthly_tests={monthly_tests} max_monthly_tests={max_monthly_tests}"\
                f" max_speed={max_speed[0]['download']} measured_down={measured_down}")
        if monthly_tests > max_monthly_tests:
            monthly_tests = max_monthly_tests

        rand = random.random()
        run_test = (monthly_tests / (24 * 30)) > rand
        print("bandwidth_test_stochastic_limit: measured_down={0}, max_monthly_consumption_gb={1}, "\
                "max_monthly_tests={2}".format(measured_down, max_monthly_consumption_gb, max_monthly_tests))
        print("bandwidth_test_stochastic_limit: {0} > {1} (speed: {2})".format(monthly_tests / (24 * 30), rand, speed))
        return run_test

    def speed(self, key_ookla, key_ndt7, limit_consumption):
        """ Test runs Ookla and NDT7 Speed tests in sequence """
        if limit_consumption:
            if not self.bandwidth_test_stochastic_limit(measured_down = self.measured_down,
                    max_monthly_consumption_gb = self.max_monthly_consumption_gb,
                    max_monthly_tests = self.max_monthly_tests):
                log.info("limit_consumption applied, skipping test: speedtest")
                print("limit_consumption applied, skipping test: speedtest")
                return None, None
        return self.speed_ookla(key_ookla, True), self.speed_ndt7(key_ndt7, True)

    def ping_latency(self, key, run_test):
        """
        Method records ping latency to self.sites
        """
        """ key: test name """

        ###
        # WARNING: this test is mandatory, for Chicago Deployment
        ##
        sites = self.sites
        if not run_test:
            sites = [self.sites[0]]

        ping_res = {}
        error_found = False
        ping_failure_count = 0

        self.results[key] = {}
        for site in sites:
            ping_cmd = "ping -i {:.2f} -c {:d} -w {:d} {:s}".format(
                0.25, 10, 5, site)

            try:
                label = self.labels[site]
            except KeyError:
                label = site

            ping_res[label] = {}

            ping_res[label], err = self.popen_exec(ping_cmd)
            if len(err) > 0:
                print(f"ERROR: {err}")
                log.error(err)
                self.results[key][label + "_error"] = err.strip()
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
                self.results[key][label + "_error"] = 'Packet Loss IndexError'
                ping_res[label] = {'error': 'Packet Loss IndexErorr'}
                error_found = True
                continue

            try:
                ping_rtt_ms = re.findall(
                    'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                    , ping_res[label])[0]
            except IndexError:
                self.results[key][label + "_error"] = 'Probe IndexError'
                ping_res[label] = {'error': 'Probe IndexErorr'}
                error_found = True
                continue


            ping_rtt_ms = [float(v) for v in ping_rtt_ms]

            self.results[key][label + "_packet_loss_pct"] = ping_pkt_loss
            self.results[key][label + "_rtt_min_ms"] = ping_rtt_ms[0]
            self.results[key][label + "_rtt_max_ms"] = ping_rtt_ms[2]
            self.results[key][label + "_rtt_avg_ms"] = ping_rtt_ms[1]
            self.results[key][label + "_rtt_mdev_ms"] = ping_rtt_ms[3]

            if not self.quiet:
                print(f'\n --- {label} ping latency (MANDATORY) ---')
                print(f'Packet Loss: {ping_pkt_loss}%')
                print(f'Average RTT: {ping_rtt_ms[0]} (ms)')
                print(f'Minimum RTT: {ping_rtt_ms[1]} (ms)')
                print(f'Maximum RTT: {ping_rtt_ms[2]} (ms)')
                print(f'RTT Std Dev: {ping_rtt_ms[3]} (ms)')

        self.results[key]["error"] = error_found
        return ping_res

    def last_mile_latency(self, key, run_test):
        """
        Method records RTT to earliest node with public IP Address along path
        to 8.8.8.8 by default.
        """
        """ key : test name """

        if not run_test:
            return

        sites = list(self.nma.conf['last_mile_latency'].keys())
        labels = self.nma.conf['last_mile_latency']

        if len(sites) == 0:
            return

        output = {}
        res = None
        for site in sites:
            tr_cmd = f'traceroute {site}'

            out, err = self.popen_exec(tr_cmd)
            output[site] = out
            self.results[key] = {}

            if len(err) > 0:
                self.results[key]["error"] = f'{err}'
                print(f'ERROR: {err}')
                log.error(err)
                return f'{err}'

            out = out.split('\n')
            for line in out:
                hop_stats = line.split(' ')
                if len(hop_stats) > 5:
                    ip_addr = hop_stats[4].strip('()')
                    try:
                        if not ipaddress.ip_address(ip_addr).is_private:
                            ping_cmd = "ping -i {:.2f} -c {:d} -w {:d} {:s}".format(
                                0.25, 10, 5, ip_addr)
                            output[site], err = self.popen_exec(ping_cmd)
                            if len(err) > 0:
                                print(f"ERROR: {err}")
                                log.error(err)
                                self.results[key][site + "_error"] = f'{err}'
                                output[site] = { 'error' : f'{err}' }
                                error_found = True
                                return

                            try:
                                ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                                                output[site], re.MULTILINE)[0])
                            except IndexError:
                                self.results[key][site + "_error"] = 'Packet Loss IndexError'
                                output[site] = {'error': 'Packet Loss IndexErorr'}
                                error_found = True
                                continue

                            try:
                                ping_rtt_ms = re.findall(
                                    'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                                    , output[site])[0]
                            except IndexError:
                                self.results[key][site + "_error"] = 'Probe IndexError'
                                output[site] = {'error': 'Probe IndexErorr'}
                                error_found = True
                                continue
                            res = [hop_stats[6], hop_stats[9], hop_stats[12]]
                            ping_rtt_ms = [float(v) for v in ping_rtt_ms]

                            self.results[key][labels[site] + "_last_mile_ping_packet_loss_pct"] = ping_pkt_loss
                            self.results[key][labels[site] + "_last_mile_ping_rtt_min_ms"] = ping_rtt_ms[0]
                            self.results[key][labels[site] + "_last_mile_ping_rtt_max_ms"] = ping_rtt_ms[2]
                            self.results[key][labels[site] + "_last_mile_ping_rtt_avg_ms"] = ping_rtt_ms[1]
                            self.results[key][labels[site] + "_last_mile_ping_rtt_mdev_ms"] = ping_rtt_ms[3]
                            break
                    except ValueError:
                        continue

            if res:
                res.sort()
                self.results[key][f'{labels[site]}_last_mile_tr_rtt_min_ms'] = float(res[0])
                self.results[key][f'{labels[site]}_last_mile_tr_rtt_median_ms'] = float(res[1])
                self.results[key][f'{labels[site]}_last_mile_tr_rtt_max_ms'] = float(res[2])
        return output

    def oplat(self, key, run_test, client, port, limit):

        if not run_test: return
        if not client: return

        if limit:
            if not self.bandwidth_test_stochastic_limit(measured_down=self.measured_down,
                                                        max_monthly_consumption_gb=self.max_monthly_consumption_gb,
                                                        max_monthly_tests=self.max_monthly_tests):
                log.info("limit_consumption applied, skipping test: OpLat")
                print("limit_consumption applied, skipping test: OpLat")
                return

        if 'targets' in self.nma.conf['oplat']:
            targets = self.nma.conf['oplat']['targets']
        else:
            return

        res = {}
        self.results[key] = {}

        error = False
        oplat_out = {}
        for upload in [True, False]:

            ul_dl = "ul" if upload else "dl"

            for dst in targets:
                cmd = "/usr/local/src/nm-exp-active-netrics/bin/oplat " \
                        "-s /usr/local/src/nm-exp-active-netrics/bin/iperf3.sh " \
                        "-c {} -p {} -d {} -i 0.25 -n 10 -m 'tcp icmp' -J {}".format(
                    client, port, dst, "" if upload else "-R")
                oplat_out[ul_dl], err = self.popen_exec(cmd)
                if len(err) > 0:
                    print(f'ERROR: {err}')
                    log.error(err)
                    self.results[key][f'{dst}_{ul_dl}_error'] = f'{err}'
                    oplat_out[ul_dl] = {'error': f'{err}'}
                    error = True
                    continue

                res = json.loads(oplat_out[ul_dl])
                if ul_dl == "ul":
                    sum_sent = res["SumSent"]
                    self.results[key]['avg_sum_sent'] = float(sum_sent) / 13
                    self.results['total_bytes_consumed'] += int(sum_sent)
                else:
                    sum_recv = res["SumRecv"]
                    self.results[key]['avg_sum_recv'] = float(sum_recv) / 13
                    self.results['total_bytes_consumed'] += int(sum_recv)

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

                self.results[key][f'avg_rate_tcp_probes_{ul_dl}'] = tcp_sum / len(set(tcp_rates))
                self.results[key][f'avg_rate_icmp_probes_{ul_dl}'] = icmp_sum / len(set(icmp_rates))
                self.results[key][f'unloaded_icmp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["PacketLoss"])
                self.results[key][f'unloaded_icmp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["MinRtt"]) * 1e-6
                self.results[key][f'unloaded_icmp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["MaxRtt"]) * 1e-6
                self.results[key][f'unloaded_icmp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["UnloadedStats"]["AvgRtt"]) * 1e-6
                self.results[key][f'loaded_icmp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["PacketLoss"])
                self.results[key][f'loaded_icmp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["MinRtt"]) * 1e-6
                self.results[key][f'loaded_icmp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["MaxRtt"]) * 1e-6
                self.results[key][f'loaded_icmp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["ICMPinger"]["LoadedStats"]["AvgRtt"]) * 1e-6

                self.results[key][f'unloaded_tcp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["PacketLoss"])
                self.results[key][f'unloaded_tcp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["MinRtt"]) * 1e-6
                self.results[key][f'unloaded_tcp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["MaxRtt"]) * 1e-6
                self.results[key][f'unloaded_tcp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["UnloadedStats"]["AvgRtt"]) * 1e-6
                self.results[key][f'loaded_tcp_{field_dst}_pkt_loss_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["PacketLoss"])
                self.results[key][f'loaded_tcp_{field_dst}_min_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["MinRtt"]) * 1e-6
                self.results[key][f'loaded_tcp_{field_dst}_max_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["MaxRtt"]) * 1e-6
                self.results[key][f'loaded_tcp_{field_dst}_avg_rtt_ms_{ul_dl}'] = float(res["TCPinger"]["LoadedStats"]["AvgRtt"]) * 1e-6


                #res[ul_dl] = out

        self.results[key]['error'] = error
        return oplat_out


    def latency_under_load(self, key, run_test, client, port):
        """
        Method records ping latency under load to self.sites_load
        """
        """ key: test name """

        if not run_test: return
        if not client:   return

        if 'targets' in self.nma.conf['latency_under_load']:
            targets = self.nma.conf['latency_under_load']['targets']
        else:
            return

        ping_res = {}
        self.results[key] = {}

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
                  label = self.labels[site]
                except KeyError:
                  label = site

                ping_cmd = "ping -i 0.25 -c 10 -w 5 {:s}".format(site)
                
                start = time.time()
                ping_res[direction][label], err = self.popen_exec(load + ping_cmd)
                if len(err) > 0:
                    print(f"ERROR: {err}")
                    log.error(err)
                    self.results[key][f'{label}_{ul_dl}_error'] = f'{err}'
                    ping_res[direction][label] = { 'error': f'{err}' }
                    error_found = True
                    continue

                ping_pkt_loss = float(re.findall(', ([0-9.]*)% packet loss',
                                                 ping_res[direction][label], re.MULTILINE)[0])
                
                ping_rtt_ms = re.findall(
                    'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                    , ping_res[direction][label])[0]

                ping_rtt_ms = [float(v) for v in ping_rtt_ms]

                self.results[key][f"{label}_packet_loss_pct_under_{ul_dl}"] = ping_pkt_loss
                self.results[key][f"{label}_rtt_min_ms_under_{ul_dl}"] = ping_rtt_ms[0]
                self.results[key][f"{label}_rtt_max_ms_under_{ul_dl}"] = ping_rtt_ms[2]
                self.results[key][f"{label}_rtt_avg_ms_under_{ul_dl}"] = ping_rtt_ms[1]
                self.results[key][f"{label}_rtt_mdev_ms_under_{ul_dl}"] = ping_rtt_ms[3]

                if not self.quiet:
                    print(f'\n --- {label} ping latency under load ---')
                    print(f'Packet Loss Under Load: {ping_pkt_loss}%')
                    print(f'Average RTT Under Load: {ping_rtt_ms[1]} (ms)')
                    print(f'Minimum RTT Under Load: {ping_rtt_ms[0]} (ms)')
                    print(f'Maximum RTT Under Load: {ping_rtt_ms[2]} (ms)')
                    print(f'RTT Std Dev Under Load: {ping_rtt_ms[3]} (ms)')

                if (time.time() - start) < 11:
                    time.sleep(11 - (time.time() - start))

        self.results[key]['error'] = error_found
        return ping_res

    # function taken from
    # https://stackoverflow.com/questions/11264005/using-a-regex-to-match-ip-addresses
    def valid_ip(self, address):
        """
        Check if a site in self.sites is an IP address
        """
        try:
            host_bytes = address.split('.')
            valid = [int(b) for b in host_bytes]
            valid = [b for b in valid if b >=0 and b<=255]
            return len(host_bytes) == 4 and len(valid) == 4
        except:
            return False


    def dns_latency(self, key, run_test):
        """
        Method records dig latency for each site in self.sites
        """
        """ key: test name """

        if not run_test:
            return

        dig_res = None
        error_found = False
        target = '8.8.8.8'

        if 'target' in self.nma.conf['dns_latency'].keys():
            target = self.nma.conf['dns_latency']['target']

        dig_delays = []
        dig_res = {}
        for site in self.sites:
            
            if self.valid_ip(site):
                continue

            try:
               label = self.labels[site]
            except KeyError:
               label = site
            dig_cmd = f'/usr/local/dig/bin/dig @{target} {site}'
            dig_res[label], err = self.popen_exec(dig_cmd)
            if len(err) > 0:
               print(f"ERROR: {err}")
               self.results[key][f'{label}_error'] = f'{err}'
               dig_res[label] = { 'error': f'{err}' }
               log.error(err)
               error_found = True
               continue

            dig_res_qt = re.findall('Query time: ([0-9]*) msec',
                                 dig_res[label], re.MULTILINE)[0]
            dig_delays.append(int(dig_res_qt))

        self.results[key] = {}
        self.results[key]["dns_query_avg_ms"] = sum(dig_delays) / len(dig_delays)
        self.results[key]["dns_query_max_ms"] = max(dig_delays)
        self.results[key]["error"] = error_found

        if not self.quiet:
            print(f'\n --- DNS Delays (n = {len(dig_delays)}) ---')
            print(f'Avg DNS Query Time: {self.results[key]["dns_query_avg_ms"]} ms')
            print(f'Max DNS Query Time: {self.results[key]["dns_query_max_ms"]} ms')

        return dig_res


    def encrypted_dns_latency(self, key, run_test):
        """
        Method records dig latency for each site in self.sites
        """
        """ key: test name """

        if not run_test:
            return

        error_found = False

        dig_delays = []
        dig_res = {}
        self.results[key] = {}
        
        for site in self.sites:

            if self.valid_ip(site):
                continue

            try:
                label = self.labels[site]
            except KeyError:
                label = site

            for resolver in self.resolvers:
                try:
                    res_label = self.res_labels[resolver]
                except KeyError:
                    res_label = resolver
                print(f'RUNNING: {resolver} {site}')
                dig_cmd = f'/usr/local/dig/bin/dig +https @{resolver} {site}'
                dig_res[f'{res_label}_{label}'], err = self.popen_exec(dig_cmd)
                if len(err) > 0:
                    print(f"ERROR: {err}")
                    self.results[key][f'{res_label}_{label}_error'] = f'{err}'
                    dig_res[f'{res_label}_{label}'] = { 'error': f'{err}' }
                    log.error(err)
                    error_found = True
                    continue
                try:
                    dig_res_qt = re.findall('Query time: ([0-9]*) msec',dig_res[f'{res_label}_{label}'], re.MULTILINE)[0]
                except IndexError as e:
                    print(f"ERROR: encrypted DNS lookup failed for {resolver} {site}")
                    continue
                print(f"RESULT: {dig_res_qt}")
                self.results[key][f'{res_label}_{label}_encrypted_dns_latency'] = int(dig_res_qt)

        # if not self.quiet:
        #     print(f'\n --- Encrypted DNS Delays (n = {len(dig_delays)}) ---')
        #     print(f'Avg DNS Query Time: {self.results[key]["dns_query_avg_ms"]} ms')
        #     print(f'Max DNS Query Time: {self.results[key]["dns_query_max_ms"]} ms')

        return dig_res


    def hops_to_target(self, key, site):
        """
        Method counts the number of hops to the target site
        """
        """ key: test name """

        if not site:
            return

        tr_res = None
        error_found = False

        self.results[key] = {}
        targets = ['www.google.com']

        if 'targets' in self.nma.conf['hops_to_target']:
            targets = self.nma.conf['hops_to_target']['targets']

        tr_res = {}
        for target in targets:
            try:
                label = self.labels[target]
            except KeyError:
                label = target

            tr_cmd = f'traceroute -m 20 -q 5 -w 2 {target} | tail -1 | awk "{{print $1}}"'
            tr_res[label], err = self.popen_exec(tr_cmd)
            if len(err) > 0:
                print(f"ERROR: {err}")
                log.error(err)
                self.results[key][f'{label}_error'] = f'{err}'
                #TODO: save the output regardless?
                #tr_res[label] = { f'{label}': tr_res[label], 'error' : f'{err}' }
                tr_res[label] = { 'error' : f'{err}' }
                error_found = True
                continue

            tr_res_s = tr_res
            tr_res_s = tr_res_s[label].strip().split(" ")

            hops = -1

            if len(tr_res_s):
                hops = int(tr_res_s[0])

            self.results[key][f'hops_to_{label}'] = hops

        self.results[key]["error"] = error_found

        if not self.quiet:
            print('\n --- Hops to Target ---')
            for target in targets:
              try:
                label = self.labels[target]
              except KeyError:
                label = target
              if f'{label}_error' in self.results[key]:
                print("Hops to {}: {}".format(target,
                                          self.results[key][f'{label}_error']))
              else:
                print("Hops to {}: {}".format(target,
                                          self.results[key][f'hops_to_{label}']))

        return tr_res

    def connected_devices_arp(self, key, run_test):
        """
        Method counts the number of active devices on the network.
        """
        """ key: test name """


        if not run_test:
            return

        res = {}

        ts = int(time.time())
        iface = 'eth0'

        if 'nmap_dev_scan' in self.nma.conf.keys():
            if 'iface' in self.nma.conf['nmap_dev_scan']:
                iface = self.nma.conf['nmap_dev_scan']['iface']

        route_cmd = f"ip r | grep -v default | grep src | grep {iface} | head -n 1 | awk '{{print $1;}}'"
        subnet = Popen(route_cmd, shell=True,
                       stdout=PIPE).stdout.read().decode('utf-8').strip(" \n")
        nmap_cmd = f'nmap -sn {subnet}'
        Popen(nmap_cmd, shell=True, stdout=PIPE).stdout.read()

        arp_cmd = (f"/usr/sbin/arp -i {iface} -n | grep : |"
                   "grep -v '_gateway' | tr -s ' ' | "
                   "cut -f3 -d' ' | sort | uniq")

        arp_res, err = self.popen_exec(arp_cmd)
        if len(err) > 0:
            print(f"ERROR: {err}")
            log.error(err)
            return None

        ## use arp_res to collect device mac address, it's disabled for now
        res['arp'] = "[REDACTED]"

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

        self.results[key] = {}
        self.results[key]["devices_active"] = len(active_devices)
        self.results[key]["devices_total"] = self.dev_db.count(where('n') >= 1)
        self.results[key]["devices_1day"] = ndev_past_day
        self.results[key]["devices_1week"] = ndev_past_week

        if not self.quiet:
            print('\n --- Number of Devices ---')
            print(f'Number of active devices: '
                  f'{self.results[key]["devices_active"]}')
            print(f'Number of total devices: '
                  f'{self.results[key]["devices_total"]}')
            print(f'Number of devices in last 1 day:'
                  f' {self.results[key]["devices_1day"]}')
            print(f'Number of devices in last week:'
                  f' {self.results[key]["devices_1week"]}')
        return res

    def iperf3_bandwidth(self, key, client, port, limit):
        """
        Method for recorded results of iperf3 bandwidth tests
        """
        """ key: test name """

        if not client:
            return

        if limit:
            if not self.bandwidth_test_stochastic_limit(measured_down = self.measured_down,
                    max_monthly_consumption_gb = self.max_monthly_consumption_gb,
                    max_monthly_tests = self.max_monthly_tests):
                log.info("limit_consumption applied, skipping test: iperf")
                print("limit_consumption applied, skipping test: iperf")
                return

        iperf_res = {}
        error_found = False
        
        if self.nma.conf['databases']['tinydb_enable']:
            speed = self.speed_db.all()

        measured_bw = {'upload': 0, 'download': 0}
        measured_jitter = {'upload': 0, 'download': 0}
        
        length = None ##default
        if 'buffer_length' in self.nma.conf['iperf'].keys():
            length = self.nma.conf['iperf']['buffer_length']

        self.results[key] = {}
        for direction, value in measured_bw.items():
            reverse = False

            bandwidth = 0

            if self.nma.conf['databases']['tinydb_enable']:
                bandwidth = speed[0][direction] * 1.05
                if direction == 'download':
                    reverse = True
             
            #log.info(f"iperf using buffer_length: {length}")
            iperf_cmd = "/usr/local/src/nm-exp-active-netrics/bin/iperf3.sh" \
                        " -c {} -p {} -u -P 4 -b {:.2f}M {} {} --json"\
                        .format(client, port, bandwidth/4, 
                                f'-l {length}' if length is not None else '',
                                '-t 5 -R -i 1' if reverse else "-t 20 -i 0")
            # print(iperf_cmd)
            for attempt_num in range(1, 5):
                (output, err) = self.popen_exec(iperf_cmd)
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
                self.results[key][f'iperf_{direction}_error'] = f'{err}'
                iperf_res[direction] = { f'output' : output, 'error' : err }
                log.error(err)
                error_found = True
                continue

            try:
                iperf_res[direction] = output
                json_res = json.loads(output)
            except Exception as err:
                log.error(f'{err}')
                self.results[key] = { f'iperf_{direction}_error' : f'{err}' }
                iperf_res[direction] = { f'output' : output, 'error' : f'{err}' }
                continue

            if direction == "upload":
                lost_pct = json_res["end"]["sum"]["lost_percent"]
                frac_recvd = (100 - lost_pct) / 100
                measured_bw[direction] = frac_recvd * float(json_res["end"]["sum"]["bits_per_second"]) / 1e6

                self.results['total_bytes_consumed'] += json_res['end']['sum']['bytes']

            else:

                seconds     = sum([i["sum"]["seconds"] for i in json_res["intervals"]])
                total_bytes = sum([i["sum"]["bytes"]   for i in json_res["intervals"]])

                measured_bw[direction] = total_bytes * 8. / seconds / 1e6
                self.results['total_bytes_consumed'] += total_bytes

                for i in range(5):

                    interval_seconds = json_res["intervals"][i]["sum"]["seconds"]
                    interval_bytes   = json_res["intervals"][i]["sum"]["bytes"]
                    self.results[key][f'iperf_udp_download_i{i}'] = interval_bytes * 8 / interval_seconds / 1e6

            self.results[key][f'iperf_udp_{direction}'] = measured_bw[direction]


            measured_jitter[direction] = float(json_res['end']['sum']['jitter_ms'])
            self.results[key][f'iperf_udp_{direction}_jitter_ms'] = measured_jitter[direction]

            if not self.quiet:
                if direction == 'upload':
                    print('\n --- iperf Bandwidth ---')
                print(f'{direction} bandwidth: {measured_bw[direction]} Mb/s')
                print(f'{direction} jitter: {measured_jitter[direction]} ms')

        self.results[key]['error'] = error_found
        if self.nma.conf['databases']['tinydb_enable']:
            self.update_max_speed(measured_bw['download'],
                                  measured_bw['upload'])

        return iperf_res


    def tshark_eth_consumption(self, key, run_test, dur = 60):
        """ key: test name """

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
        self.results[key] = {}
        self.results[key]["consumption_download"] = dl * 8 / 1e6 / duration
        self.results[key]["consumption_upload"]   = ul * 8 / 1e6 / duration

        return tshark_res


    def consumption_reset(self):
       if self.nma.conf['databases']['tinydb_enable']:
            if (len(self.consumption_db.all()) == 0):
                self.consumption_db.insert({'total_bytes_consumed' : 0})
            consumption = self.consumption_db.all()
            total_bytes_consumed = consumption[0]['total_bytes_consumed']
            self.consumption_db.update({'total_bytes_consumed' : 0})
            return total_bytes_consumed
       return 0

    def consumption_update(self, totalbytes):
       if self.nma.conf['databases']['tinydb_enable']:
            if (len(self.consumption_db.all()) == 0):
                self.consumption_db.insert({'total_bytes_consumed' : totalbytes})
            consumption = self.consumption_db.all()
            total_bytes_consumed = consumption[0]['total_bytes_consumed'] + totalbytes
            self.consumption_db.update({'total_bytes_consumed' : total_bytes_consumed})
            return total_bytes_consumed
       return 0
