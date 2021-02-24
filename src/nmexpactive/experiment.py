from genericpath import exists
import os, sys
import logging
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

        env_path = Path('.').absolute() / 'env' / '.env'
        if os.path.exists(env_path):
            load_dotenv(env_path)
            log.info("ENV using {0}".format(env_path))
        elif os.path.exists(ETC_ENV):
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
                self.conf = toml.loads(ETC_CFG)
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
                if deployment is None:
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
                            #add random minutes to iperf and other tools execution
                            print("{0} {1}".format(k, i['times'][k] + random.randrange(-3,3)))

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
                  



        
