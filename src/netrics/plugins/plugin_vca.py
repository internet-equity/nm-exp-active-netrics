from .. utils import popen_exec
import logging
import re
import toml
from subprocess import Popen, PIPE
from .. plugins.netrics_vca_test.vca_automation import main_client

log = logging.getLogger(__name__)

def test_vca(key, conf, results, quiet=False):
    config_file = conf["vca"]["basic"]["config_file"]
    config = toml.load(config_file)
    for k in conf["vca"]:
        if k in config:
            val = config[k]
            val.update(conf["vca"][k])
        else:
            val = conf["vca"]
        config[k] = val
    result = main_client.start_test(config)
    results[key] = result["vca-qoe-metrics"]
    return results

