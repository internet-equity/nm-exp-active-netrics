""" vcqoe command-line interface entry-point """
import os
import argparse
import subprocess
import threading
import time
from . utility import *
import pyautogui
import toml
from subprocess import Popen
from . meet import Meet
from . vca import VCA
from . teams import Teams
from . capture import CaptureTraffic
from . pipe_video import PipeVideo
from cv2 import *
import sys
import os


def execute_client(logger=None,trace_filename=None,config_file=None):
    """ Execute the auto_call CLI command """
    try:
        config = toml.load(config_file)
        config['path'] = os.path.dirname(config_file)
        if len(config['path']) > 0:
            config['call']['automation_image_dir'] = f'{config["path"]}/{config["call"]["automation_image_dir"]}'
        datapath = config["default"]["datapath"]
        vca_name = config["default"]["vca"]
        capture = config["default"]["capture"]

        logger.info("starting capture thread")
        if capture:
            capture_thread = CaptureTraffic(config, trace_filename)
            capture_thread.start()

        rtc_dir = f'{datapath}/{vca_name}/webrtc'
        make_dir(rtc_dir)
        logger.info("webrtc directory: %s",rtc_dir)
        vca = VCA(config, trace_filename)
        vca.logger = logger

        logger.info("starting call")
        vca.start_call()
        time.sleep(config["call"]["duration"])
        logger.info("ending call")
        vca.end_call(False)
        
        if capture:
            capture_thread.is_running = False
        logger.info("ended capture thread")
        return vca.result

    except KeyboardInterrupt:
        logger.error("KEYBOARD INTERRUPT")
        print('\n KEYBOARD INTERRUPT...CLOSED \n')


def execute_server(logger=None,trace_filename=None,config_file=None):
    """ Execute the auto_call CLI command """
    try:
        config = toml.load(config_file)
        datapath = config["default"]["datapath"]
        vca_name = config["default"]["vca"]
        
        capture = config["default"]["capture"]
        if capture:
            capture_thread = CaptureTraffic(config, trace_filename)
            capture_thread.start()

        pipe = config["default"]["pipe-video"]
        if pipe:
            pipe_video = PipeVideo(config)
            pipe_video.start_pipe()

        rtc_dir = f'{datapath}/{vca_name}/webrtc'
        make_dir(rtc_dir)
        logger.info(f"webrtc directory:{rtc_dir}")
        
        vca = VCA(config, trace_filename)
        vca.logger = logger 
        vca.start_call()
        
        admitted = vca.admit_client()
        vca.admitted = admitted
        if admitted:
            logger.info("Client admitted")
            participant_left = vca.wait_until_client_has_left()
            if not participant_left:
                logger.error("Client did not leave gracefully")
        else:
            logger.error("Client not admitted, exiting")        
        logger.info("ending call")
        vca.end_call(True)
        if capture:
            capture_thread.is_running = False
        if pipe:
            pipe_video.end_pipe()
        logger.info("ended pipe")
    except KeyboardInterrupt:
        logger.error("KEYBOARD INTERRUPT")
