#!/usr/bin/env python3

import argparse
import logging
from netrics.netson import Measurements
from nmexpactive.experiment import NetMicroscopeControl

log = logging.getLogger(__name__)

#TODO: move this to setup.py
__name__ = "nm-exp-active-netrics"
__version__ = "0.0.1"
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
            const='www.google.com',
            nargs='?',
            action='store',
            help='Count hops to Chicago backbone (ibone)'
    )

    parser.add_argument(
            '-t', '--target',
            default=False,
            const='www.google.com',
            nargs='?',
            action='store',
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
            default=[False, False],
            nargs = 2,
            action='store',
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
            help='Provide toml configuration file'
    )

    return parser

parser = build_parser()
args = parser.parse_args()
parser.print_help()

nma = NetMicroscopeControl(args)
log.info("Initializing.")
test = Measurements(args, nma)





