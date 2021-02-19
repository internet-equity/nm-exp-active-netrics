import os, sys
import logging
import traceback
import toml
import pathlib
from dotenv import load_dotenv
from pathlib import Path

project = "netrics"

EXP = "nm-exp-active-{0}".format(project)
ETC = "/etc/" + EXP
ETC_ENV = ETC + "/.env"
TMP = "/tmp/nm/" + EXP + "/"
TMP_LOG = TMP + "log/"
TMP_LOG_FILE = TMP_LOG + EXP + ".log"

CFG = EXP + ".toml"
ETC_CFG = ETC + "/" + CFG

class NetMicroscopeControl:
    def __init__(self, args):

        self.conf = {}

        pathlib.Path(TMP_LOG).mkdir(parents=True, exist_ok=True)

        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', 
          datefmt='%Y-%m-%dT%H:%M:%S',
          filename=TMP_LOG_FILE,
          #filemode='w', 
          level=logging.INFO)

        log = logging.getLogger(__name__)

        env_path = Path('.').absolute() / 'env' / ' .env'
        if os.path.exists(env_path):
            load_dotenv(env_path)
            log.info("ENV using {0}".format(env_path))
        elif os.path.exists(ETC_ENV):
            load_dotenv(ETC_ENV)
            log.info("ENV using {0}".format(ETC_ENV))
        else:
            log.warn("ENV not set.")
        
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
        log.info(self.conf['databases'])

        
