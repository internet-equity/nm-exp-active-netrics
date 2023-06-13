from .. utils import popen_exec
import logging
import re
import os
from subprocess import Popen, PIPE
import json
from .. utils import valid_ip

log = logging.getLogger(__name__)

def test_encrypteddns(key, conf, results, quiet = False):

    try:
        enc_sites = list(conf['encrypted_dns_reference_site_dict'].keys())
        enc_labels = conf['encrypted_dns_reference_site_dict']
    except Exception as err:
        print("config file not configured correctly for go responsiveness: ",err)
        results[key][f'error'] = f'{err}'
        log.error(err)
        return

    dig_delays = []
    dig_res = {}
    dig_res_pipe = {}
    results[key] = {}

    for site in enc_sites:
        if site.valid_ip():
            continue
        try:
            label = enc_labels[site]
        except KeyError:
            label = site
        for resolver in resolvers:
            print(f'RUNNING: {resolver} {site}')
            dig_cmd = f'timeout 5 /usr/local/src/nm-exp-active-netrics/bin/dig +https @{resolver} {site}'
            dig_res_pipe[f'{resolver}_{label}'] = self.popen_exec_pipe(dig_cmd)
     for site in enc_sites:
         if site.valid_ip():
             continue
         try:
             label = enc_labels[site]
         except KeyError:
             label = site
         for resolver in resolvers:
             out = dig_res_pipe[f'{resolver}_{label}'].stdout.read().decode('utf-8')
             err = dig_res_pipe[f'{resolver}_{label}'].stderr.read().decode('utf-8')
             if len(err) > 0:
                 print(f"ERROR: {err}")
                 results[key][f'{resolver}_{label}_error'] = f'{err}'
                 dig_res[f'{resolver}_{label}'] = { 'error': f'{err}' }
                 log.error(err)
                 error_found = True
                 continue
             dig_res[f'{resolver}_{label}'] = out
             try:
                dig_res_qt = re.findall('Query time: ([0-9]*) msec',dig_res[f'{resolver}_{label}'], re.MULTILINE)[0]
                results[key][f'{resolver}_{label}_encrypted_dns_latency'] = int(dig_res_qt)
             except IndexError as e:
                 print(f"ERROR: encrypted DNS lookup failed for {resolver} {site}")
                 continue
    return dig_res
