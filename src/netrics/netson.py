""" Measurements
    Records selected network measurements
"""


from subprocess import Popen, PIPE
import json
import random
import urllib.request
import os, logging
from pathlib import Path
from tinydb import TinyDB, where
from tinydb.operations import increment
from tinydb.operations import set as tdb_set
from netrics.builtin.netrics_test_speedtests import test_ookla
from netrics.builtin.netrics_test_speedtests import test_ndt7
from tinydb import TinyDB
from netrics.builtin.netrics_test_speedtests import test_ookla
from netrics.builtin.netrics_test_speedtests import test_ndt7
from netrics.builtin.netrics_test_dns_latency import test_dns_latency
from netrics.builtin.netrics_test_last_mile_latency import test_last_mile_latency
from netrics.builtin.netrics_test_latunderload import test_latunderload
from netrics.builtin.netrics_test_ping_latency import test_ping_latency
from netrics.builtin.netrics_test_oplat import test_oplat
from netrics.builtin.netrics_test_hops_to_target import test_hops_to_target
from netrics.builtin.netrics_test_iperf3 import test_iperf3
from netrics.builtin.netrics_test_connected_devices import test_connected_devices


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
        self.enc_sites = list(self.nma.conf['encrypted_dns_reference_site_dict'].keys())
        self.labels = self.nma.conf['reference_site_dict']
        self.enc_labels = self.nma.conf['encrypted_dns_reference_site_dict']
        self.resolvers = self.nma.conf['dns_latency']['encrypted_dns_targets']
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

    def popen_exec_pipe(self, cmd):
        pipe = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        return pipe
 
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
        return test_ookla(key, self, self.nma.conf, self.results, self.quiet)

    def speed_ndt7(self, key, run_test):
        """ Test runs NDT7 Speed test """
        """ key: test name """

        if not run_test:
            return

        self.results[key] = {}
        return test_ndt7(key, self, self.nma.conf, self.results, self.quiet)

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

    def speed_ookla(self, key, run_test):
        """ Test runs Ookla Speed test """
        """ key: test name """
        if not run_test:
            return

        self.results[key] = {}
        return test_ookla(key, self, self.nma.conf, self.results, self.quiet)

    def speed_ndt7(self, key, run_test):
        """ Test runs NDT7 Speed test """
        """ key: test name """

        if not run_test:
            return

        self.results[key] = {}
        return test_ndt7(key, self, self.nma.conf, self.results, self.quiet)

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
        Records ping latency to self.sites
        """
        """ key: test name """

        ###
        # WARNING: this test is mandatory, for Chicago Deployment
        ##

        sites = self.sites
        if not run_test:
            sites = [self.sites[0]]

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
                log.error('Packet Loss IndexErorr: Unexpected output from ping')
                error_found = True
                continue

            try:
                ping_rtt_ms = re.findall(
                    'rtt [a-z/]* = ([0-9.]*)/([0-9.]*)/([0-9.]*)/([0-9.]*) ms'
                    , ping_res[label])[0]
            except IndexError:
                self.results[key][label + "_error"] = 'Probe IndexError'
                ping_res[label] = {'error': 'Probe IndexErorr'}
                log.error('Probe IndexErorr: Unexpected output from ping')
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
        args = { "sites" : sites,
                 "labels" : self.labels
                }
        return test_ping_latency(key, self, args, self.results, self.quiet)

    def last_mile_latency(self, key, run_test):
        """
        Records RTT to earliest node with public IP Address along path
        to 8.8.8.8 by default.
        """
        """ key : test name """

        def countOccurrences(s, ch):
            return sum(1 for i, letter in enumerate(s) if letter == ch)

        def get_median(x):
            n = len(x)
            if n % 2 == 0: # even
                return 0.5 * (x[n//2 -1] + x[n//2])
            else: # odd
                return x[(n+1)//2 -1]

        if not run_test:
            return

        def get_median(x):
            n = len(x)
            if n % 2 == 0: # even
                return 0.5 * (x[n//2 -1] + x[n//2])
            else: # odd
                return x[(n+1)//2 -1]

        if not run_test:
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
                if 'traceroute' not in line and countOccurrences(line, '*') < 3:
                    ipv4_extract_pattern = "(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
                    ip_addr = re.findall(ipv4_extract_pattern, line)[0]
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
                            res = re.findall('([0-9.]*) ms', line)
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
                self.results[key][f'{labels[site]}_last_mile_tr_rtt_median_ms'] = float(get_median(res))
                self.results[key][f'{labels[site]}_last_mile_tr_rtt_max_ms'] = float(res[-1])
        return output
        self.results[key] = {}

        return test_last_mile_latency(key, self, self.nma.conf, self.results, self.quiet)

    def oplat(self, key, run_test, client, port, limit):

        if not run_test: return
        if not client: return

        self.results[key] = {}
        args = { "limit" : limit,
                 "port" : port,
                 "client" : client,
                 "bandwidth_test_stochastic_limit" : self.bandwidth_test_stochastic_limit,
                 "measured_down" : self.measured_down,
                 "max_monthly_consumption_gb" : self.max_monthly_consumption_gb,
                 "max_monthly_tests" : self.max_monthly_tests,
                 "conf" : self.nma.conf
                }

        return test_oplat(key, self, args, self.results, self.quiet)

    def latency_under_load(self, key, run_test, client, port):
        """
        Method records ping latency under load to self.sites_load
        """
        """ key: test name """

        if not run_test: return
        if not client:   return

        self.results[key] = {}
        args = { "client" : client,
                 "port" : port,
                 "labels" : self.labels
            }

        return test_latunderload(key, self, args, self.nma.conf, self.results, self.quiet)

    def dns_latency(self, key, run_test):
        """ Records dig latency for each site in self.sites """
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
        for site in self.enc_sites:
            
            if self.valid_ip(site):
                continue

            try:
               label = self.labels[site]
            except KeyError:
               label = site
            dig_cmd = f'dig @{target} {site}'
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
        args = { "conf" : self.nma.conf,
                 "sites" : self.sites,
                 "labels" : self.labels
                }

        return test_dns_latency(key, self, args, self.results, self.quiet)


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
        dig_res_pipe = {}
        self.results[key] = {}
        
        for site in self.enc_sites:
            if self.valid_ip(site):
                continue

            try:
                label = self.labels[site]
            except KeyError:
                label = site

            for resolver in self.resolvers:
                print(f'RUNNING: {resolver} {site}')
                dig_cmd = f'timeout 5 /usr/local/src/nm-exp-active-netrics/bin/dig +https @{resolver} {site}'
                ping_cmd = f'ping -c 5 {resolver}'
                dig_res_pipe[f'{resolver}_{label}'] = self.popen_exec_pipe(dig_cmd)
                dig_res_pipe[f'ping_{resolver}_{label}'] = self.popen_exec_pip(ping_cmd)

        for site in self.enc_sites:
            if self.valid_ip(site):
                continue

            try:
                label = self.enc_labels[site]
            except KeyError:
                label = site

            for resolver in self.resolvers:
                out = dig_res_pipe[f'{resolver}_{label}'].stdout.read().decode('utf-8')
                ping_out = dig_res_pipe[f'ping_{resolver}_{label}'].stdout.read().decode('utf-8')
                err = dig_res_pipe[f'{resolver}_{label}'].stderr.read().decode('utf-8')
                if len(err) > 0:
                    print(f"ERROR: {err}")
                    self.results[key][f'{resolver}_{label}_error'] = f'{err}'
                    self.results[key][f'ping_{resolver}_{label}'] = f'{err}'
                    dig_res[f'{resolver}_{label}'] = { 'error': f'{err}' }
                    dig_res[f'ping_{resolver}_{label}'] = { 'error': f'{err}' }
                    log.error(err)
                    error_found = True
                    continue
                dig_res[f'{resolver}_{label}'] = out
                dig_res[f'ping_{resolver}_{label}'] = ping_out
                try:
                    dig_res_qt = re.findall('Query time: ([0-9]*) msec',dig_res[f'{resolver}_{label}'], re.MULTILINE)[0]
                    ping_time = re.findall('rtt min/avg/max/mdev = ([0-9]*)/([0-9]*)/([0-9]*)/([0-9]*) ms', ping[f'ping_{resolver}_{label}'], re.MULTILINE)[0]
                    self.results[key][f'{resolver}_{label}_encrypted_dns_latency'] = int(dig_res_qt)
                    self.results[key][f'ping_{resolver}_{label}_encrypted_dns_latency'] = int(ping_time)
                except IndexError as e:
                    print(f"ERROR: encrypted DNS lookup failed for {resolver} {site}")
                    continue

        # if not self.quiet:
        #     print(f'\n --- Encrypted DNS Delays (n = {len(dig_delays)}) ---')
        #     print(f'Avg DNS Query Time: {self.results[key]["dns_query_avg_ms"]} ms')
        #     print(f'Max DNS Query Time: {self.results[key]["dns_query_max_ms"]} ms')
        return dig_res


    def hops_to_target(self, key, site):
        """
        Counts the number of hops to the target site
        """
        """ key: test name """

        if not site:
            return

        self.results[key] = {}
        args = { "conf" : self.nma.conf,
                 "labels" : self.labels
                }

        return test_hops_to_target(key, self, args, self.results, self.quiet)

    def connected_devices_arp(self, key, run_test):
        """
        Method counts the number of active devices on the network.
        """
        """ key: test name """


        if not run_test:
            return

        self.results[key] = {}

        return test_connected_devices(key, self, self.dev_db, self.nma.conf, self.results, self.quiet)

    def iperf3_bandwidth(self, key, client, port, limit):
        """
        Records results of iperf3 bandwidth tests
        """
        """ key: test name """

        if not client and not self.nma.conf['databases']['tinydb_enable']:
            return

        if limit:
            if not self.bandwidth_test_stochastic_limit(measured_down = self.measured_down,
                    max_monthly_consumption_gb = self.max_monthly_consumption_gb,
                    max_monthly_tests = self.max_monthly_tests):
                log.info("limit_consumption applied, skipping test: iperf")
                print("limit_consumption applied, skipping test: iperf")
                return 

        self.results[key] = {}
        args = { "port" : port,
                 "client" : client,
                 "update_max_speed" : self.update_max_speed,
                 "speed_db" : self.speed_db,
                 "conf" : self.nma.conf
                }

        return test_iperf3(key, self, args, self.results, self.quiet)

    def tshark_eth_consumption(self, key, run_test, dur = 60):
        """DEPRECIATED"""
        """ key: test name """
        return

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
