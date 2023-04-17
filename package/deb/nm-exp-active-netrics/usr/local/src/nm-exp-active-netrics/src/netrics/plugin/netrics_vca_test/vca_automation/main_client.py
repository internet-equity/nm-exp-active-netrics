""" vcqoe command-line interface entry-point """

import toml
import time
import requests 
import os
import re
import logging
import Xlib.display
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
import vcqoe.utility as utility
from subprocess import Popen

trace_filename = None
logger = logging.getLogger(__name__)
vca_list = ["teams", "meet"]
empty_object = {"vca-qoe-metrics": {"run-status-code": 1, "metrics": {}}}


def start_virtual_display(config):
    """
    Starts a virtual display with the given resolutions in config file.

    Args:
        config: dictionary containing config information

    Returns:
        None
    """
    ## create xauthority file and set environment variable
    curwd = os.getcwd()
    os.environ["XAUTHORITY"] = curwd + "/.Xauthority"
    os.system("touch .Xauthority")
    
    ## start the virtual display
    DISPLAY = ':99'
    resolution = config["default"]["resolution"]
    cmd = f"nohup Xvfb {DISPLAY} -screen 0 {resolution} 2> /tmp/nohup.out &"
    Popen(cmd, close_fds=True, shell=True)
    time.sleep(1)
    os.environ['DISPLAY'] = DISPLAY
    import pyautogui
    pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ["DISPLAY"])

def stop_virtual_display():
    """
    Stops virtual display
    """
    _ = Popen('killall Xvfb', shell=True)

#get meet or teams
def get_vca(config):
    """
    Get the vca meeting to run (teams/meet)
    """
    last_test_vca = config['default']['vca']
    idx = (vca_list.index(last_test_vca) + 1) % len(vca_list)
    return vca_list[idx]


def start_test(config_file):
    """
    Start the vca test. Calls the corresponding code for client/server

    Args:
        config_file: dictionary containing config information

    Returns:
        None
    """
    config = toml.load(config_file)
    datapath = config["default"]["datapath"]

    if config["default"]["role"] == "client":
        vca = get_vca(config)
        response = query_vca_url(config, vca) 
        trace_filename = utility.get_trace_filename(datapath, vca)
        set_logger(trace_filename)

        if not response:
            logger.error("could not connect to server")
            return empty_object
        elif response["busy"]:
            logger.error("server is busy")
            return empty_object
        else:
            url = response["url"]
            update_config_file(config_file, vca=vca, url=url)
            
           
        logger.info("Starting test")


    elif config["default"]["role"] == "server":
        trace_filename = utility.get_trace_filename(datapath, config["default"]["vca"])
        set_logger(trace_filename)


    #config["path"] = os.path.dirname(config_file)
    #config["call"]["automation_image_dir"] = f'{config["path"]}/{config["call"]["automation_image_dir"]}'
    
    #start virtual display
    if config['default']['virtual']:
        start_virtual_display(config)
    logger.info("started virtual display")
    


    from vcqoe import cli
    if config["default"]["role"] == "client":
        print(f"<<<<<<<<<<<<< {trace_filename}")
        return cli.execute_client(logger,trace_filename,config_file)

    #if server is running
    elif config["default"]["role"] == "server":
        logger.info("starting server test")
        cli.execute_server(logger,trace_filename,config_file)

    if config['default']['virtual']:
        logger.info("stopping virtual display")
        stop_virtual_display()

def set_logger(trace_filename):
    """
    Creates the logger file to output test log information

    Args:
        config: dictionary containing config information

    Returns:
        None
    """
    global logger
    #trace_filename = utility.get_trace_filename(toml.load(config))
    print("Trace file: ",trace_filename)
    logger = logging.getLogger('vca-netrics')
    handler = logging.FileHandler(f'{trace_filename}.log')
    handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info("Trace file name %s",trace_filename)

def update_config_file(config_file, url = None, vca = None):
    if url:
        escaped_url = url.replace('/', '\/')
        # print("Connecting to: ",escaped_url)
        replace_vca_url_cmd = f"sed -i 's/url=.*/url=\"{escaped_url}\"/' {config_file}"
        os.system(replace_vca_url_cmd)
    if vca:
        replace_vca_cmd = f"sed -i 's/vca=.*/vca=\"{vca}\"/' {config_file}"
        os.system(replace_vca_cmd)
    return 

def query_vca_url(config, vca):
    """
    Tries to connect to host after getting the vca conference to run

    Args:
        config_file: dictionary containing config information
    
    Returns:
        Boolean: True is successfully connected to host. Else, False.
    """
    host, port = config["default"]["host"], config["default"]["port"]
        
    try:
        r = requests.get(f"http://{host}:{port}/run-test?vca={vca}")
        if r.status_code != 200:
            return None
        received = r.json()
        '''
        if received != None:
            if received["busy"]:
                logger.error("server is busy")
                return False
        '''
        return received
    except requests.exceptions.ConnectionError:
        print("Could not connect due to connection error")
        return None

#entry point
if __name__ == "__main__":
    config_file = "config.toml"
    start_test(config_file)
   
