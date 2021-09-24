from genericpath import exists
import os, sys
import logging, logging.handlers, re
import traceback
import toml
import random
from dotenv import load_dotenv
from pathlib import Path
import urllib, json
import urllib.parse
import urllib.request
import pickle
from subprocess import Popen, PIPE
import getpass
from zipfile import ZipFile
from io import BytesIO

project = "netrics"

log = logging.getLogger(__name__)

projectname = "nm-exp-active-{0}".format(project)
EXP = Path(projectname)
ETC = Path("/etc") / EXP
ETC_ENV = ETC / ".env.netrics"
VAR_NM =  Path("/var/nm/")
VAR = Path("/var/nm/") / EXP
VAR_LOG = VAR / "log"
VAR_LOG_FILE = VAR_LOG / (projectname + ".log")
VAR_CACHE = VAR / "cache"
VAR_UPLOAD = VAR / "upload"
UPLOAD_PENDING = VAR_UPLOAD / "pending"
UPLOAD_ARCHIVE = VAR_UPLOAD / "archive"

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
        myuser = getpass.getuser()
        self.conf = {}
        if myuser != "netrics":
            print("WARN: running as {0}. Recommended: \"netrics\".".format(myuser))
        try:
          Path(VAR_NM).mkdir(parents=True, exist_ok=True)
          Path(VAR).mkdir(parents=True, exist_ok=True)
          Path(VAR_LOG).mkdir(parents=True, exist_ok=True)
          Path(VAR_UPLOAD).mkdir(parents=True, exist_ok=True)
          Path(UPLOAD_PENDING).mkdir(parents=True, exist_ok=True)
          Path(UPLOAD_ARCHIVE).mkdir(parents=True, exist_ok=True)
        except FileNotFoundError as fnfe:
          print("ERROR: NetMicroscopeControl.init FileNotFoundError {0}".format(fnfe))
          sys.exit(1)
        except PermissionError as pe:
          print("ERROR: NetMicroscopeControl.init {0} {1}".format(myuser, pe))
          sys.exit(1)

        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', 
          datefmt='%Y-%m-%dT%H:%M:%S',
          filename=VAR_LOG_FILE,
          #filemode='w', 
          level=logging.INFO)

        handler = logging.handlers.TimedRotatingFileHandler(VAR_LOG_FILE,
                                       when="d",
                                       interval=1,
                                       backupCount=30)
        log.addHandler(handler)

        if os.path.exists(ETC_ENV):
            load_dotenv(ETC_ENV)
            log.info("ENV using {0}".format(ETC_ENV))
        else:
            log.info("ENV not set: ({0}).".format(ETC_ENV))
        
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
        deployment_var = Path(VAR_CACHE) / "deployment"

        Path(VAR_CACHE).mkdir(parents=True, exist_ok=True)

        if 'deployment' in self.conf.keys():
            deployment = self.conf['deployment']
        elif deployment_etc.exists():
            with open(deployment_etc, 'r') as dfile:
                deployment = dfile.read()
                dfile.close()
        elif deployment_var.exists():
            with open(deployment_var, 'r') as dfile:
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
                    p = deployment_var
                netrics_json_path = Path(VAR_CACHE) / "netrics.json"
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
        print("{0}\n...".format(VAR_LOG_FILE))
        cat_log_cmd = "cat {0}".format(VAR_LOG_FILE)
        loglines = Popen(cat_log_cmd, shell=True,
                             stdout=PIPE).stdout.readlines()
        l = len(loglines)
        if l > 10:
            for i in range(l - 10, l):
                print(loglines[i].decode('utf-8'), end = '')
        
        log_from_cron = VAR_LOG / "log.txt"
        if Path(log_from_cron).exists():
            cat_log_cmd = "cat {0}".format(VAR_LOG_FILE)
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
            'ndt7-client': "/usr/local/src/nm-exp-active-netrics/bin/ndt7-client"
                if os.path.exists("/usr/local/src/nm-exp-active-netrics/bin/ndt7-client") else None,
            'ping': which("ping"),
            'dig': which("dig"),
            'tshark': which("tshark"),
            'traceroute': which("traceroute"),
            'speedtest': which("/usr/local/src/nm-exp-active-netrics/bin/speedtest"),
        }

        print("ip: {0}".format((r['ip'], "OK") if r['ip'] is not None else None))
        print("arp: {0}".format((r['arp'], "OK") if r['arp'] is not None else None))
        print("nmap: {0}".format((r['nmap'], "OK") if r['nmap'] is not None else None))
        print("iperf3: {0}".format((r['iperf3'], "OK") if r['iperf3'] is not None else None))
        print("ndt7-client: {0}".format((r['ndt7-client'], "OK") if r['ndt7-client'] is not None else None))
        print("ping: {0}".format((r['ping'], "OK") if r['ping'] is not None else None))
        print("dig: {0}".format((r['dig'], "OK") if r['dig'] is not None else None))
        print("tshark: {0}".format((r['dig'], "OK") if r['tshark'] is not None else None))
        print("traceroute: {0}".format((r['traceroute'], "OK") if r['traceroute'] is not None else None))
        print("speedtest: {0}".format((r['speedtest'], "OK") if r['speedtest'] is not None else None))
        cat_log_cmd = "cat {0}".format(VAR_LOG_FILE)
        loglines = Popen(cat_log_cmd, shell=True,
                             stdout=PIPE).stdout.readlines()
        l = len(loglines)
        r['log_lines'] = l
        r['log_lines_cron'] = None
        r['log_lines_error'] = 0
        r['log_lines_warns'] = 0
        for i in range(0, l):
            if loglines[i].find(b'ERROR') != -1:
                print(f"ERROR in {VAR_LOG_FILE}: {loglines[i]})")
                r['log_lines_error'] += 1
            if loglines[i].find(b'WARN') != -1:
                print(f"WARNING in {VAR_LOG_FILE}: {loglines[i]})")
                r['log_lines_warns'] += 1
        print("log_lines: {0}".format(r['log_lines']))
        log_from_cron = VAR_LOG / "log.txt"
        if Path(log_from_cron).exists():
            cat_log_cmd = "cat {0}".format(log_from_cron)
            loglines = Popen(cat_log_cmd, shell=True,
                                stdout=PIPE).stdout.readlines()
            r['log_lines_cron'] = len(loglines)
            for i in range (0, len(loglines)):
              if re.search(b'error', loglines[i],  re.IGNORECASE):
                if re.search(b'error\': False', loglines[i],  re.IGNORECASE):
                    continue
                else:
                    print(f"ERROR in log.txt: {loglines[i]})")
                    r['log_lines_error'] += 1
        print("log_lines_cron: {0}".format(r['log_lines_cron']))
        print("log_lines_warns: {0}".format(r['log_lines_warns']))
        print("log_lines_error: {0}".format(r['log_lines_error']))
        return r


    def save_json(self, data, cmd, timenow, topic = "default", extended = None,
            annotation = None):
        p = UPLOAD_PENDING / topic / "json" #active netrics won't touch ..../archive
        a = UPLOAD_ARCHIVE / topic / "json" #but creating here regardless
        Path(p).mkdir(parents=True, exist_ok=True)
        Path(a).mkdir(parents=True, exist_ok=True)
        epoch = timenow.timestamp()
        d = timenow.strftime("nm_data_%Y%m%d_%H%M%S")
        d = "{0}_{1}.json".format(d, cmd)
        if extended is not None:
            extended['Annotation'] = annotation
        else:
            extended = { 'Annotation': annotation }
        final = {
                    'Meta' : {           ## active-netrics doesn't know its own id,
                        'Id' : None,     ## out json should be updated by the collect pkg
                        'Time' : epoch,  ## before it's sent to the server / backend
                        'Extended' : extended,
                        },
                    'Measurements' : data
                }
        output = p / d
        with open(p / d, 'w') as f:
            f.write("{}".format(json.dumps(final)))
            f.close()
            os.sync()
        log.info("pending {0}".format(output))

    #@deprecated
    def save_pkl(self, data, cmd, timenow, topic = "default"):
        p = UPLOAD_PENDING / topic / "pkl"
        a = UPLOAD_ARCHIVE / topic / "pkl"
        Path(p).mkdir(parents=True, exist_ok=True)
        Path(a).mkdir(parents=True, exist_ok=True)
        d = timenow.strftime("nm_data_%Y%m%d_%H%M%S")
        d = "{0}_{1}.pkl".format(d, cmd)
        output = p / d
        with open(output, 'wb') as f:
            f.write(pickle.dumps(data))
            f.close()
            os.sync()
        log.info("pending {0}".format(output))

    def save_zip_dict(self, s, cmd, k, zf, outdict, key):
        for i in outdict.keys():
            if isinstance(outdict[i], dict):
                self.save_zip_dict(s, cmd, k, zf, outdict[i],  ("" if key == "" else key + "-") + i)
            else:
                data = outdict[i]
                if len(data) > 0:
                    zf.writestr("{0}-{1}-{2}-{3}.out".format(s, cmd, k, ("" if key == "" else key + "-") + i), data
                        if isinstance(data, bytes) else "{}".format(data).encode())

    def save_zip(self, data, cmd, timenow, topic = "default"):
        p = UPLOAD_PENDING / topic / "zip"
        a = UPLOAD_ARCHIVE / topic / "zip"
        Path(p).mkdir(parents=True, exist_ok=True)
        Path(a).mkdir(parents=True, exist_ok=True)
        s = timenow.strftime("nm_data_%Y%m%d_%H%M%S")
        d = "{0}_{1}.zip".format(s, cmd)
        output = p / d

        in_memory = BytesIO()
        zf = ZipFile(in_memory, mode="w")

        token = ""
        for k in data.keys():
           if data[k] is not None:
               if isinstance(data[k], dict):
                   self.save_zip_dict(s, cmd, k, zf, data[k], "")
               else:
                   if len(data[k]) > 0:
                     zf.writestr("{0}-{1}-{2}.out".format(s, cmd, k), data[k] 
                        if isinstance(data[k], bytes) else "{}".format(data[k]).encode())

        zf.close()
        in_memory.seek(0)
        data = in_memory.read()
        with open(output,'wb') as out:
           out.write(data)

