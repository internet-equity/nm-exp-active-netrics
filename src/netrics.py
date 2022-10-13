#!/usr/bin/env python3
import os, sys, pwd
sys.path.append("venv/lib/python3.8/site-packages/")
sys.path.append("venv/lib64/python3.8/site-packages/")
import argparse
import logging
from datetime import datetime
from netrics.netson import Measurements
from nmexpactive.experiment import NetMicroscopeControl

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError


log = logging.getLogger(__name__)

#TODO: move this to setup.py
__name__ = "nm-exp-active-netrics"
__version__ = "1.0.2"
__author__ = "Kyle-MacMillan, James Saxon, Guilherme Martins,"\
             "Marc Richardson, Nick Feamster"

#Used for Annotations
class keyvalue(argparse.Action):
    def __call__( self , parser, namespace,
                 values, option_string = None):
        setattr(namespace, self.dest, dict())
        keyop = None 
        for value in values:
            try:
              key, value = value.split('=')
              keyop = key
              getattr(namespace, self.dest)[key] = value
            except:
              if keyop is None:
                  keyop = 'default'
                  getattr(namespace, self.dest)[keyop] = ""
              getattr(namespace, self.dest)[keyop] = \
                (getattr(namespace, self.dest)[keyop] + " " + value).strip()

class BatchingCallback(object):

    def success(self, conf: (str, str, str), data: str):
        print(f"Written batch: {conf}, data: {data}")
        log.info("influxdb write_api return: OK")

    def error(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        print(f"Cannot write batch: {conf}, data: {data} due: {exception}")
        log.error("influxdb write_api return: error")

    def retry(self, conf: (str, str, str), data: str, exception: InfluxDBError):
        print(f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}")
        log.error("influxdb write_api return: error")

#Used to report consumption (Human Readable)
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def build_parser():
    """ Construct parser to interpret command-line args """

    parser = argparse.ArgumentParser(
            description='measure network on jetson')

    parser.add_argument(
            '-u', '--upload',
            default=False,
            action='store_true',
            help=("Upload measurements to infux")
    )

    parser.add_argument(
            '-q', '--quiet',
            default=False,
            action='store_true',
            help="Suppress output"
    )

    parser.add_argument(
            '-p', '--ping',
            default=False,
            action='store_true',
            help='Measure ping latency'
    )

    parser.add_argument(
            '-b', '--last_mile_rtt',
            default=False,
            action='store_true',
            help='Measure last mile RTT'
    )

    parser.add_argument(
            '-l', '--latency_under_load',
            default=False,
            action='store_true',
            help='Measure ping latency under load'
    )

    parser.add_argument(
            '-d', '--dns',
            default=False,
            action='store_true',
            help='Measure DNS latency'
    )

    parser.add_argument(
            '-t', '--target',
            default=False,
            action='store_true',
            help='Count hops to target website'
    )

    parser.add_argument(
            '-n', '--ndev',
            default=False,
            action='store_true',
            help='Count number of connected devies'
    )

    parser.add_argument(
            '-k', '--ookla',
            default=False,
            action='store_true',
            help='Measure up/down network throughout using Ookla'
    )

    parser.add_argument(
            '-a', '--ndt7',
            default=False,
            action='store_true',
            help='Measure up/down network throughout using NDT7'
    )

    parser.add_argument(
            '-s', '--speed',
            default=False,
            action='store_true',
            help='Measure up/down network throughput using supported tools NDT7 and Ookla (in sequence)'
    )

    parser.add_argument(
            '-i', '--iperf',
            action='store_true',
            help='Measure up/down UDP throughout using standard iperf3',
    )

    parser.add_argument(
            '--tshark',
            #default=[False, False],    #conf moved to toml
            #nargs = 2,                 #conf moved to toml
            action='store_true',
            help='Measure on-going consumption using tshark (Passive HW setup required)'
    )

    parser.add_argument(
            '--limit-consumption',
            default=False,
            action='store_true',
            help='Apply stochastic limit to bandwidth tests'
    )

    parser.add_argument(
            '-c', '--config',
            default=None,
            action='store',
            help='Provide an alternative toml configuration file'
    )

    ## Non-test 
    parser.add_argument(
            '-R', '--reset-consumption',
            action='store_true',
            help='Reset consumption counter',
    )

    ## Non-test 
    parser.add_argument(
            '-A', '--annotate',
            metavar="key=value key=value",
            default=None,
            nargs='*', 
            action = keyvalue,
            help='Annotate the output JSON with a any key=value configuration (eg. -A isp=starlink desc="perf debugging")'
    )

    ## Non-test 
    parser.add_argument(
            '-G', '--get-times',
            default=False,
            action='store_true',
            help='Get test profiles and (netrics.json deployment_json_url from toml)'
    )

    ## Non-test
    parser.add_argument(
            '-L', '--logs',
            default=False,
            action='store_true',
            help='Tail logs and generate summary'
    )

    ## Non-test
    parser.add_argument(
            '-C', '--check',
            default=False,
            action='store_true',
            help='Check dependencies and overall health parameters'
    )

    return parser


def upload(upload_results, measurements):

    if not upload_results:
        return

    server = None
    port = 0
    token = None
    org = None
    installid = None

    server = os.getenv("INFLUXDB_SERVER")
    port = os.getenv("INFLUXDB_PORT")
    token = os.getenv("INFLUXDB_TOKEN")
    org = os.getenv("INFLUXDB_ORG")
    db = os.getenv("INFLUXDB_DATABASE")
    installid = os.getenv("INSTALL_ID")

    if server is None:
        log.error("Unable to insert data (influxdb), missing .env or INFLUXDB_* not set.")
        print(("Unable to insert data (influxdb), missing .env or INFLUXDB_* not set."))
        return
 
    with InfluxDBClient(url = "https://{0}:{1}".format(server, port), token = token,  org = org) as client:
        callback = BatchingCallback()
        write_api = client.write_api(write_options=SYNCHRONOUS,
                                    success_callback=callback.success,
                                    error_callback=callback.error,
                                    retry_callback=callback.retry)

        insert = {}
        for m in measurements.keys():
            if m != 'ipquery':
              if type(measurements[m]) is dict:
                for k in measurements[m].keys():
                    if k != 'error':
                        insert[k] = measurements[m][k]
              ## the below code address for measurements without keys
              ## like total_bytes_consumed,  
              else:
                insert[m] = measurements[m]

        #print("---> {}".format(insert))

        record = [
                {
                    "measurement": "networks",
                    "tags"       : {
                        "install": installid
                    },
                    "fields"      : insert,
                    "time"        : datetime.utcnow()
                }
        ]

        ret = write_api.write(bucket=db, record=record)

        return

        
        #if not ret:
        #    log.error("influxdb write_points return: false")
        #    return
        #log.info("influxdb write_points return: OK")
 

def check_connectivity(res, site):

    if "ping_latency" not in res:
        return None

    latency_res = res["ping_latency"]

    if f"{site}_rtt_avg_ms" in latency_res:
        return True

    offline_failures = ["Name or service not known",
                        "Temporary failure in name resolution"]

    if f"{site}_error" in latency_res:

        offline_failures = ["Name or service not known",
                            "Temporary failure in name resolution"]

        for mode in offline_failures:
            if mode in latency_res[f"{site}_error"]:
                return False


    return None


################################# MAIN #######################################

parser = build_parser()
args = parser.parse_args()

output = {} #raw output

try:
  userid=pwd.getpwuid(os.getuid())[0]
  if userid != 'netrics':
      raise Exception('User: {0}'.format(userid))
except (KeyError, PermissionError, Exception) as error:
  print("ERROR: run this command as using unprivileged user 'netrics' or root, message:({0})".format(error))
  sys.exit(1)

nma = NetMicroscopeControl(args)

if args.get_times:
  nma.get_times()
  sys.exit(0)

if args.logs:
  nma.get_logs()
  sys.exit(0)

if args.check:
  r = nma.get_checks()
  #TODO: upload r (health)
  sys.exit(0)

log.info("Initializing.")
test = Measurements(args, nma)

""" Run IPv4v6 query"""
output['ipquery']= test.ipquery()

""" Measure ping latency to list of websites """
if not args.tshark:
    output['ping_latency'] = test.ping_latency('ping_latency', args.ping)



# Check to see if we have connectivity failures on google, amazon, and wikipedia.
connectivity_status  = [check_connectivity(test.results, site)
                        for site in ["google", "amazon", "wikipedia"]]
# Values will be none if no ping test actually ran.
connectivity_status  = [stat for stat in connectivity_status if stat is not None]
# If any actual tests ran AND they ALL failed, then we have connectivity failure.
# print(connectivity_status, any(connectivity_status))
connectivity_failure = connectivity_status and not any(connectivity_status)

if not connectivity_failure:

    """ Measure last mile latency """
    output['last_mile_rtt'] = test.last_mile_latency('last_mile_rtt', args.last_mile_rtt)

    """ Measure DNS latency """
    output['dns_latency'] = test.dns_latency('dns_latency', args.dns)
    
    """ Count hops to target website """
    output['hops_to_target'] = test.hops_to_target('hops_to_target', args.target)

    """ Run ookla speed test """
    output['ookla'] = test.speed_ookla('ookla', args.ookla)
    
    """ Run ndt7 speed test """
    output['ndt7'] = test.speed_ndt7('ndt7', args.ndt7)

    """ Run speed tests in sequence ookla/ndt7 """
    if args.speed:
      output['ookla'], output['ndt7'] = test.speed('ookla', 'ndt7', args.limit_consumption)

    """ Run iperf3 bandwidth test """
    if args.iperf:
      if nma.conf['iperf']['targets'][0] == "":
        log.error("[iperf][targets] not properly set")
        print("[iperf][targets] not properly set")
        sys.exit(1)
    
      for target in nma.conf['iperf']['targets']:
        server=target.split(':')[0]
        port=target.split(':')[1]
        output['iperf'] = test.iperf3_bandwidth('iperf', client=server, port=port,
                limit=args.limit_consumption)
    
    """ Measure latency under load """
    if args.latency_under_load:
    
        if nma.conf['iperf']['targets'][0] == "":
            log.error("[iperf][targets] not properly set")
            print("[iperf][targets] not properly set -- needed for latency under load")
            sys.exit(1)
    
        target = nma.conf['iperf']['targets'][0]
        server = target.split(':')[0]
        port   = target.split(':')[1]
    
        output['latency_under_load'] = test.oplat('oplat', True, client=server,
                                                  port=port, limit=args.limit_consumption)

    
""" Count number of devices on network """
output['connected_devices_arp'] = test.connected_devices_arp('connected_devices_arp', args.ndev)

""" Measure consumption using tshark. """
output['tshark_eth_consumption'] = test.tshark_eth_consumption('tshark_eth_consumption', args.tshark)


if not args.quiet:
  print(test.results)

if args.reset_consumption:
  total_bytes_consumed = test.consumption_reset()
  msg = "Consumption RESET: Now 0 (zero) bytes, before: {0} bytes ({1}).".format(total_bytes_consumed,
          sizeof_fmt(total_bytes_consumed))
  print(msg)
  log.info(msg)
else:
  test_bytes_consumed = test.results['total_bytes_consumed']
  test.results['test_bytes_consumed'] = test_bytes_consumed
  test.results['total_bytes_consumed'] = test.consumption_update(test.results['total_bytes_consumed']) 
  msg = "Consumption UPDATE: {0} of {1} bytes ({2}).".format(test_bytes_consumed, 
         test.results['total_bytes_consumed'], sizeof_fmt(test.results['total_bytes_consumed']))
  print(msg)
  log.info(msg)

timenow = datetime.now()
nma.save_json(test.results, 'netrics_results', timenow, topic=nma.conf['topic'],
        extended = nma.conf['extended'] if 'extended' in nma.conf.keys() else None,
        annotation = args.annotate)
nma.save_zip(output, 'netrics_output', timenow, topic=nma.conf['topic'])


if args.upload and not connectivity_failure:

  upload(test.results, test.results)


