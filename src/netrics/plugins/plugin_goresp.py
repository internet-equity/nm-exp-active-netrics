from .. utils import popen_exec
import logging
import time
from subprocess import Popen, PIPE
from tinydb import where
from tinydb.operations import increment
from tinydb.operations import set as tdb_set

log = logging.getLogger(__name__)

def test_goresp(key, conf, results, quiet=False):

    #TODO
    pass