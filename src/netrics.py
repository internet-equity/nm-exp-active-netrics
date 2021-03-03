#!/usr/bin/env python3
import os, sys
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
__version__ = "0.1.10"
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
            '-d', '--dns',
            default=False,
            action='store_true',
            help='Measure DNS latency'
    )

    parser.add_argument(
            '-b', '--backbone',
            default=False,
            #const='www.google.com',
            #nargs='?',
            action='store_true',
            help='Count hops to Chicago backbone (ibone)'
    )

    parser.add_argument(
            '-t', '--target',
            default=False,
            #const='www.google.com',
            #nargs='?',
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
            '-s', '--ookla',
            default=False,
            action='store_true',
            help='Measure up/down using Ookla'
    )

    parser.add_argument(
            '-i', '--iperf',
            #default=[False, False],    #conf moved to toml
            #nargs = 2,                 #conf moved to toml
            action='store_true',
            help='Measure connection with remote server. Needs [client] [port]',
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
            help='Check dependencies and overall health parameters.'
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

    ret = creds.write_points([{"measurement": "networks",
                         "tags"        : {"install": installid},
                         "fields"      : measurements,
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

""" Run ookla speed test """
output['ookla'] = test.speed(args.ookla)

""" Measure ping latency to list of websites """
output['ping_latency'] = test.ping_latency(args.ping)

""" Measure DNS latency """
output['dns_latency'] = test.dns_latency(args.dns)

""" Count hops to local backbone """
output['hops_to_backbone'] = test.hops_to_backbone(args.backbone)

""" Count hops to target website """
output['hops_to_target'] = test.hops_to_target(args.target)

""" Count number of devices on network """
output['connected_devices_arp'] = test.connected_devices_arp(args.ndev)

""" Run iperf3 bandwidth test """
if args.iperf:
  if nma.conf['iperf']['targets'][0] == "":
    log.error("[iperf][targets] not properly set")
    print("[iperf][targets] not properly set")
    sys.exit(1)
    
  for target in nma.conf['iperf']['targets']:
    server=target.split(':')[0]
    port=target.split(':')[1]
    output['iperf'] = test.iperf3_bandwidth(client=server, port=port)

if not args.quiet:
  print(test.results)
  #print(output)

nma.save_str(test.results, 'netrics_results')
nma.save_pkl(output, 'netrics_output')

if args.upload:
  upload(test.results, test.results)

