from genericpath import exists
import os, sys
import logging, logging.handlers
import traceback
import toml
import random
from dotenv import load_dotenv
from pathlib import Path
import urllib, json
import urllib.parse
import urllib.request
from datetime import datetime
import pickle
from subprocess import Popen, PIPE

project = "netrics"

log = logging.getLogger(__name__)

projectname = "nm-exp-active-{0}".format(project)
EXP = Path(projectname)
ETC = Path("/etc") / EXP
ETC_ENV = ETC / ".env"
TMP = Path("/tmp/nm/") / EXP
TMP_LOG = TMP / "log"
TMP_LOG_FILE = TMP_LOG / (projectname + ".log")
TMP_CACHE = TMP / "cache"

UPLOAD_PENDING = TMP / "upload" / "pending"
UPLOAD_ARCHIVE = TMP / "upload" / "archive"

CFG = projectname + ".toml"
ETC_CFG = ETC / CFG

def which(pgm):
    path=os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p=os.path.join(p,pgm)
        if os.path.exists(p) and os.access(p,os.X_OK):
            return p

class NetMicroscopeControl:
    global log
    def __init__(self, args):

        self.conf = {}

        Path(TMP_LOG).mkdir(parents=True, exist_ok=True)
        Path(UPLOAD_PENDING).mkdir(parents=True, exist_ok=True)
        Path(UPLOAD_ARCHIVE).mkdir(parents=True, exist_ok=True)


        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', 
          datefmt='%Y-%m-%dT%H:%M:%S',
          filename=TMP_LOG_FILE,
          #filemode='w', 
          level=logging.INFO)

        handler = logging.handlers.TimedRotatingFileHandler(TMP_LOG_FILE,
                                       when="d",
                                       interval=1,
                                       backupCount=30)
        log.addHandler(handler)

        ## try to use your local .env
        #env_path = Path('.').absolute() / 'env' / '.env'
        #if os.path.exists(env_path):
        #    load_dotenv(env_path)
        #    log.info("ENV using {0}".format(env_path))
        if os.path.exists(ETC_ENV):
            load_dotenv(ETC_ENV)
            log.info("ENV using {0}".format(ETC_ENV))
        else:
            log.warn("ENV not set: ({0},{1}).".format(env_path, ETC_ENV))
        
        cfg_path = Path('.').absolute() / 'conf' / CFG
        try: 
            if os.path.exists(cfg_path):
                self.conf = toml.load(cfg_path)
                log.info("CONF using {0}".format(cfg_path))
            elif os.path.exists(ETC_CFG):
                self.conf = toml.load(ETC_CFG)
                log.info("CONF using {0}".format(ETC_CFG))
            else:
                log.warn("CONF not set.")
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.error("TOML Load Exception: ({0}) {1} {2} {3}".format(str(e), exc_type, fname, exc_tb.tb_lineno))
            traceback.print_exc()
            log.info('Existing...')
            sys.exit(1)

    def get_times(self):
        deployment = None
        deployment_etc = Path(ETC) / "deployment"
        deployment_tmp = Path(TMP_CACHE) / "deployment"

        Path(TMP_CACHE).mkdir(parents=True, exist_ok=True)

        if 'deployment' in self.conf.keys():
            deployment = self.conf['deployment']
        elif deployment_etc.exists():
            with open(deployment_etc, 'r') as dfile:
                deployment = dfile.read()
                dfile.close()
        elif deployment_tmp.exists():
            with open(deployment_tmp, 'r') as dfile:
                deployment = dfile.read()
                dfile.close()

        req = urllib.request.Request(self.conf['deployment_json_url'])
        with urllib.request.urlopen(req) as response:
            if response.getcode()!=200:
                log.info('Unexpected:'+str(response.getcode()))
                sys.exit(1)
            else:
                j = None
                p = None
                
                if deployment_etc.exists():
                    p = deployment_etc
                else:
                    p = deployment_tmp
                netrics_json_path = Path(TMP_CACHE) / "netrics.json"
                with open(netrics_json_path, 'w') as nj:
                    j = response.read().decode()
                    nj.write(j)
                    nj.close()
                    log.info('OK')
                netrics_json = json.loads(j)

                randprofile = False
                ## if user don't have a profile defined, pick one as a baseline
                ## and rand -3 + 3
                if deployment is None:
                  randprofile = True
                  rlen = len(netrics_json['schedule'])
                  r = random.randrange(0, rlen)
                  with open(p, 'w') as dfile:
                      dfile.write(netrics_json['schedule'][r]['deployment'])
                      dfile.close()
                  with open(p, 'r') as dfile:
                      deployment = dfile.read()
                      dfile.close()
                for i in netrics_json['schedule']:
                    if i['deployment'] == deployment:
                        for k in i['times']:
                            if randprofile: ## this will apply to anonymous (user w no profile def) 
                               print("{0} {1}".format(k, i['times'][k] + random.randrange(-3,3)))
                            else:
                               print("{0} {1}".format(k, i['times'][k]))
    def get_logs(self):
        print("{0}\n...".format(TMP_LOG_FILE))
        cat_log_cmd = "cat {0}".format(TMP_LOG_FILE)
        loglines = Popen(cat_log_cmd, shell=True,
                             stdout=PIPE).stdout.readlines()
        l = len(loglines)
        if l < 10: l = 0
        for i in range(l - 10, l):
            print(loglines[i].decode('utf-8'), end = '')
        
        log_from_cron = TMP_LOG / "log.txt"
        if Path(log_from_cron).exists():
            cat_log_cmd = "cat {0}".format(TMP_LOG_FILE)
            loglines = Popen(cat_log_cmd, shell=True,
                                stdout=PIPE).stdout.readlines()
            l = len(loglines)
            for i in range(l - 10, l):
                print(loglines[i].decode('utf-8'), end = '')

    def get_checks(self):
        r = {
            'ip': which("ip"),
            'arp': which("arp"),
            'nmap': which("nmap"),
            'iperf3': "/usr/local/src/nm-exp-active-netrics/iperf3.sh" 
                if os.path.exists("/usr/local/src/nm-exp-active-netrics/bin/iperf3.sh") else None,
            'ping': which("ping"),
            'dig': which("dig"),
            'tshark': which("tshark"),
            'traceroute': which("traceroute"),
            'speedtest': which("speedtest"),
        }

        print("ip: {0}".format((r['ip'], "OK") if r['ip'] is not None else None))
        print("arp: {0}".format((r['arp'], "OK") if r['arp'] is not None else None))
        print("nmap: {0}".format((r['nmap'], "OK") if r['nmap'] is not None else None))
        print("iperf3: {0}".format((r['iperf3'], "OK") if r['iperf3'] is not None else None))
        print("ping: {0}".format((r['ping'], "OK") if r['ping'] is not None else None))
        print("dig: {0}".format((r['dig'], "OK") if r['dig'] is not None else None))
        print("tshark: {0}".format((r['dig'], "OK") if r['tshark'] is not None else None))
        print("traceroute: {0}".format((r['traceroute'], "OK") if r['traceroute'] is not None else None))
        print("speedtest: {0}".format((r['speedtest'], "OK") if r['speedtest'] is not None else None))
        cat_log_cmd = "cat {0}".format(TMP_LOG_FILE)
        loglines = Popen(cat_log_cmd, shell=True,
                             stdout=PIPE).stdout.readlines()
        l = len(loglines)
        r['log_lines'] = l
        r['log_lines_cron'] = None
        r['log_lines_error'] = 0
        r['log_lines_warns'] = 0
        for i in range(0, l):
            if loglines[i].find(b'ERROR') != -1:
                r['log_lines_error'] += 1
            if loglines[i].find(b'WARN') != -1:
                r['log_lines_warns'] += 1
        print("log_lines: {0}".format(r['log_lines']))
        print("log_lines_error: {0}".format(r['log_lines_error']))
        print("log_lines_warns: {0}".format(r['log_lines_warns']))
        log_from_cron = TMP_LOG / "log.txt"
        if Path(log_from_cron).exists():
            cat_log_cmd = "cat {0}".format(TMP_LOG_FILE)
            loglines = Popen(cat_log_cmd, shell=True,
                                stdout=PIPE).stdout.readlines()
            r['log_lines_cron'] = len(loglines)
        print("log_lines_cron: {0}".format(r['log_lines_cron']))
        return r


    def save_str(self, data, cmd, topic = "default"):
        p = UPLOAD_PENDING / topic / "out"
        Path(p).mkdir(parents=True, exist_ok=True)
        d = datetime.now().strftime("nm_data_%Y%m%d_%H%M%S")
        d = "{0}_{1}.out".format(d, cmd)
        output = p / d
        with open(p / d, 'w') as f:
            f.write("{}".format(data))
            f.close()
            os.sync()
        log.info("pending {0}".format(output))

    def save_pkl(self, data, cmd, topic = "default"):
        p = UPLOAD_PENDING / topic / "pkl"
        Path(p).mkdir(parents=True, exist_ok=True)
        d = datetime.now().strftime("nm_data_%Y%m%d_%H%M%S")
        d = "{0}_{1}.pkl".format(d, cmd)
        output = p / d
        with open(output, 'wb') as f:
            f.write(pickle.dumps(data))
            f.close()
            os.sync()
        log.info("pending {0}".format(output))
                  



        
