"""
    Functions for capturing network traffic
"""
import threading
import time
import subprocess
import psutil
from . utility import *
import os

class CaptureTraffic(threading.Thread):
    is_running = False
    capture_filter = ""
    config = None

    def __init__(self, config, filename):
        """Initiates a CaptureTraffic object"""
        self.filename = f"{filename}.pcap"
        self.capture_filter = config["capture"]["filter"]
        threading.Thread.__init__(self)

    def run(self):
        """calls function to run capture thread"""
        self.capture_traffic()

    def stop_capture(self, proc):
        """Stops capture thread"""
        print("stopping capture")
        bash_proc = psutil.Process(proc.pid)
        for child_process in bash_proc.children(recursive=True):
            subprocess.Popen(f'kill -KILL {child_process.pid}', shell=True)
            #child_process.send_signal(15)
        proc.send_signal(15)

    def capture_traffic(self):
        """ Capture network traffic using input filter """
        self.is_running = True
        dirname = os.path.dirname(self.filename)
        os.system("chmod -R 777 " + dirname)
        cmd = f'tshark {self.capture_filter} -w {self.filename}'
        proc = subprocess.Popen(cmd, shell=True)

        while self.is_running:
            time.sleep(1)

        self.stop_capture(proc)
