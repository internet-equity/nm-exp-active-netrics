#!/usr/bin/env python3
import os, sys, pwd
sys.path.append("venv/lib/python3.8/site-packages/")
sys.path.append("venv/lib64/python3.8/site-packages/")
import argparse
import logging
from datetime import datetime
from netrics.netson import Measurements
from nmexpactive.experiment import NetMicroscopeControl

from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb import InfluxDBClient

log = logging.getLogger(__name__)

#TODO: move this to setup.py
__name__ = "nm-exp-active-netrics"
__version__ = "0.1.11"
__author__ = "Kyle-MacMillan, James Saxon, Guilherme Martins"

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
            '-b', '--backbone',
            default=False,
            action='store_true',
            help='Count hops to Chicago backbone (ibone)'
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
            '-f', '--sites',
            default=None,
            action='store',
            help='Text file containing sites to visit during test'
    )

    parser.add_argument(
            '-c', '--config',
            default=None,
            action='store',
            help='Provide an alternative toml configuration file'
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
    username = None
    password = None
    installid = None

    server = os.getenv("INFLUXDB_SERVER")
    port = os.getenv("INFLUXDB_PORT")
    username = os.getenv("INFLUXDB_USERNAME")
    password = os.getenv("INFLUXDB_PASSWORD")
    db = os.getenv("INFLUXDB_DATABASE")
    installid = os.getenv("INSTALL_ID")

    if server is None:
        log.error("Unable to insert data (influxdb), missing .env or INFLUXDB_* not set.")
        print(("Unable to insert data (influxdb), missing .env or INFLUXDB_* not set."))
        return
 
    creds = InfluxDBClient(host=server, port=port, username=username,
                password=password, database=db, ssl=True, verify_ssl=True)

    insert = {}
    for m in measurements.keys():
        if m != 'ipquery':
            for k in measurements[m].keys():
                insert[k] = measurements[m][k]
    #print("{}".format(insert))

    ret = creds.write_points([{"measurement": "networks",
                         "tags"        : {"install": installid},
                         "fields"      : insert,
                         "time"        : datetime.utcnow()}])
    if not ret:
        log.error("influxdb write_points return: false")
        print("influxdb write_points return: false")
        return
    log.info("influxdb write_points return: OK")
    

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

""" Run ookla speed test """
output['ookla'] = test.speed_ookla('ookla', args.ookla)

""" Run ndt7 speed test """
output['ndt7'] = test.speed_ndt7('ndt7', args.ndt7)

""" Run speed tests in sequence ookla/ndt7 """
if args.speed:
  output['ookla'], output['ndt7'] = test.speed('ookla', 'ndt7')

""" Measure ping latency to list of websites """
output['ping_latency'] = test.ping_latency('ping_latency', args.ping)

""" Measure latency under load """
if args.latency_under_load:

  if nma.conf['iperf']['targets'][0] == "":
    log.error("[iperf][targets] not properly set")
    print("[iperf][targets] not properly set -- needed for latency under load")
    sys.exit(1)
    
  target = nma.conf['iperf']['targets'][0]
  server = target.split(':')[0]
  port   = target.split(':')[1]

  output['latency_under_load'] = test.latency_under_load('latency_under_load', True, client = server, port = port)


""" Measure DNS latency """
output['dns_latency'] = test.dns_latency('dns_latency', args.dns)

""" Count hops to local backbone """
output['hops_to_backbone'] = test.hops_to_backbone('hops_to_backbone', args.backbone)

""" Count hops to target website """
output['hops_to_target'] = test.hops_to_target('hops_to_target', args.target)

""" Count number of devices on network """
output['connected_devices_arp'] = test.connected_devices_arp('connected_devices_arp', args.ndev)

""" Measure consumption using tshark. """
output['tshark_eth_consumption'] = test.tshark_eth_consumption('tshark_eth_consumption', args.tshark)


""" Run iperf3 bandwidth test """
if args.iperf:
  if nma.conf['iperf']['targets'][0] == "":
    log.error("[iperf][targets] not properly set")
    print("[iperf][targets] not properly set")
    sys.exit(1)
    
  for target in nma.conf['iperf']['targets']:
    server=target.split(':')[0]
    port=target.split(':')[1]
    output['iperf'] = test.iperf3_bandwidth('iperf', client=server, port=port)

if not args.quiet:
  print(test.results)
  #print(output)

timenow = datetime.now()
nma.save_json(test.results, 'netrics_results', timenow, topic=nma.conf['topic'])
nma.save_zip(output, 'netrics_output', timenow, topic=nma.conf['topic'])
if args.upload:
  upload(test.results, test.results)

