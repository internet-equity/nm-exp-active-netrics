#!/usr/bin/env python3

import os, sys, traceback, json
from datetime import datetime
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb import InfluxDBClient
from dotenv import load_dotenv
from subprocess import Popen, PIPE

load_dotenv()

os.environ["PYTHONUNBUFFERED"] = "1"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

"""(ssx) salt-stack execution plugin template"""
PLUGIN_PRIORITY = 0
name = "show_netrics_files"
config = None
db = None
#log = logging.getLogger(__name__)

def init(conf = None):
  global db
  config = None
  print(f'PLUGIN: init {name}')
  print(f'ENV enable: {os.environ["SSX_ENV"]}')

  db = InfluxDBClient(host=os.getenv("INFLUXDB_HOST"), port=os.getenv("INFLUXDB_PORT"),
          username=os.getenv("INFLUXDB_USER"), password=os.getenv("INFLUXDB_PASS"),
          database=os.getenv("INFLUXDB_DB"), ssl=True, verify_ssl=True)

  return PLUGIN_PRIORITY, "ok"

def process(data):
  global db
  #log.info("hello plugin preprocess")
  print(f'PLUGIN: processing {name}')
  for line in data.splitlines():
    try:
      j = json.loads(line)
      for k in j.keys():
          insert = { 'files_sync_last24h': 0 }
          try:
            #l=j[k].encode('utf-8').decode('unicode_escape')
            files_sync_last24h=int(j[k])
          except:
            files_sync_last24h = 0
            pass
          insert['files_sync_last24h'] = files_sync_last24h
          devid = k
          ret = db.write_points([{"measurement": "ops",
                         "tags"        : {"d": devid},
                         "fields"      : insert,
                         "time"        : datetime.utcnow()}])
          if not ret:
              print("influxdb write_points return: false")
    except json.decoder.JSONDecodeError:
        pass
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("ERROR: ({0}) {1} {2} {3}".format(str(e), exc_type, fname, exc_tb.tb_lineno))
        traceback.print_exc()
        print(f'INFO: skipping {line}, reason: {type(e)}')
        pass
  return data


init()

pipe = Popen('./show_netrics_files_sync.sh', shell=True, stdout=PIPE, stderr=PIPE)

output = ""
for line in pipe.stdout:
    l = line.decode('utf-8')
    output=output+l
    print(bcolors.OKGREEN + l.strip() + bcolors.ENDC)

if len(output) > 0:
    process(output)

err = ""
for line in pipe.stderr:
    l = line.decode('utf-8')
    err=err+l
    print(bcolors.FAIL+ l.strip() + bcolors.ENDC)
