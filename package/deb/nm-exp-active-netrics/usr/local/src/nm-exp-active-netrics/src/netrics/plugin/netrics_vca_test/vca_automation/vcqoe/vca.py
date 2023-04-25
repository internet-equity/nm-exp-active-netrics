"""VCA Class to start test and capture metrics"""
import threading
import time
from . meet import Meet
from . teams import Teams
from . utility import *
from subprocess import Popen
import pyautogui
from sys import platform
import os, sys
import Xlib.display
from . webrtc import *
import logging
import json

class VCA():

    vca_client = None

    def __init__(self, config, filename):
        """Initiates a vca object"""
        self.config = config

        self.vca_name = config["default"]["vca"]
        if self.vca_name == "meet":
            self.vca_client = Meet(self.config)
           
        elif self.vca_name == "teams":
            self.vca_client = Teams(self.config)
        
        filename = filename.replace("//", "/")
        self.json_fname = f'{filename}.json'
        
        print("WebRTC file: ", self.json_fname)

        if len(config['default']['platform']) > 0:
            self.platform = config['default']['platform']
        else:
            self.platform = 'raspi' if platform == "linux" and os.uname()[1] == "raspberrypi" else platform


        self.automation_img_dir = f'{config["call"]["automation_image_dir"]}/{self.platform}'
        
        self.DISPLAY = ':0'
        self.admitted = False
        self.logger = None;
        self.result = ""
        
    
    def launch_browser(self):
        """Launches browser for running the video conference call"""
        # kill browser
        os.system("pkill -KILL .*chrom*")
        
        st = datetime.now()

        flags = ""
        flags = "--disable-gpu "
        flags += "--start-maximized"
        proc = Popen(f'{self.config["platform"]["browserpath"]} {flags} &', shell=True)

        #pyautogui.screenshot("screenshot_browser.png")

        time.sleep(5)
        
        ## close any open restore page popup
        pyautogui.hotkey("esc")
        pyautogui.hotkey("esc")

        time.sleep(1)

        pyautogui.hotkey(self.config["platform"]["ctl_key"], "l")
        # Opening WebRTC internals
        pyautogui.typewrite('chrome://webrtc-internals')
        pyautogui.hotkey('enter')
        pyautogui.hotkey(self.config["platform"]["ctl_key"], 't')
        self.logger.info("Opened webrtc internals")

        self.logger.info("DEBUG: Opened a new tab")
        #pyautogui.screenshot("screenshot_newtab.png")
        

        '''
        # if restore pages, close it 
        if locate_on_screen(f'{self.automation_img_dir}/restore_close.png'):
            self.logger.info("DEBUG: found restore pages and closing it")
            click_image(f'{self.automation_img_dir}/restore_close.png')
        else:
            self.logger.info("No restore image in browser")
        '''

    def dump_webrtc(self):
        """Downloads webrtc file and copies the file to webrtc dump file in the vca-test module"""
        ## Download and close webrtc tab
        # Remove any prior webrtc files in the download directory
        download_dir = self.config["platform"]["download_dir"] if len(self.config["platform"]["download_dir"]) > 0 else "~/Downloads"
        
        if os.path.exists(f"{download_dir}/webrtc-internals*"):
             os.system(f"rm {download_dir}/webrtc-internals*")
       
        pyautogui.hotkey(self.config["platform"]["ctl_key"], '1')
        time.sleep(1)
        pyautogui.hotkey("tab")
        time.sleep(0.5)
        pyautogui.hotkey("enter")
        time.sleep(0.5)
        pyautogui.hotkey("tab")
        time.sleep(0.5)
        pyautogui.hotkey("enter")
        time.sleep(5)
        '''
        ## code for downloading the webrtc using images
        click_image(f'{self.automation_img_dir}/dump_webrtc.png')
        time.sleep(2)
        click_image(f'{self.automation_img_dir}/webrtc_download.png')
        time.sleep(2)
        '''

        pyautogui.hotkey(self.config["platform"]["ctl_key"], 'w')


    def start_call(self):
        """Starts a video call after opening browser"""
        #if self.config["default"]["virtual"]:
        #    self.start_virtual_display()
        self.logger.info("Launching browser")
        self.logger.info("Automation images %s",f'{self.automation_img_dir}')
        self.vca_client.logger = self.logger

        self.launch_browser()
        self.vca_client.join_call()

        
    def end_call(self,isServer):
        """Ends call once test is done"""
        # download webrtc stats from browser
        # if admitted:
        self.dump_webrtc()

        # end the call and close the browser
        self.vca_client.exit_call()

        # copy webrtc stats to data directory
        self.copy_webrtc_stats(self.admitted)
        self.logger.info("successfully parsed webrtc and ending call")
        # stop virtual display
        #if self.config["default"]["virtual"]:
        #    self.stop_virtual_display()

    def copy_webrtc_stats(self,isadmitted):
        time.sleep(5)
        """copies webrtc stats file to a dump file in project file system and parses the webrtc to sumamrised metrics"""
        status = 0
        
        ## copying the webrtc stats
        download_dir = self.config["platform"]["download_dir"] if len(self.config["platform"]["download_dir"]) > 0 else "~/Downloads"
        _ = Popen(f'cp {download_dir}/webrtc_internals_dump.txt {self.json_fname}', shell=True)
        _ = Popen(f'rm {download_dir}/webrtc_internals_dump.txt', shell=True)
        
        json_vals = dict()
        json_vals["vca-qoe-metrics"] = dict()
        json_vals["vca-qoe-metrics"]["vca-name"] = self.vca_name
        json_vals["vca-qoe-metrics"]["run-status-code"] = 0 if isadmitted else 1

        if self.config["default"]["role"] == "client":
            self.logger.info("calling parsing")
            json_vals = self.parse_webrtc(json_vals)
            
        netrics_filename = self.json_fname.replace(".json","-netrics.json")
        self.logger.info("netrics file name: %s",netrics_filename)
        
        self.result = json_vals
            
    def parse_webrtc(self, json_vals):
        """parses webrtc to summarised metrics"""
        self.logger.info("Entered webrtc parsing")
        values = get_webrtc(self.json_fname,self.logger,self.vca_name)
        
        if not values[1]:
            json_vals["vca-qoe-metrics"]["run-status-code"] = 1
        
        values = values[0]
        
        json_vals['vca-qoe-metrics']['metrics'] = {}
        json_vals['vca-qoe-metrics']['extra-files'] = [self.json_fname, self.json_fname[:-4]+"pcap", self.json_fname[:-4]+"log"]
        self.logger.info("Webrtc content: %s",values)
        for metric in values:
            json_vals["vca-qoe-metrics"]["metrics"][metric] = values[metric]
        self.logger.info("done parsing")
        return json_vals

    def admit_client(self):
        """Admits the client by clicking on admit client button"""
        return self.vca_client.admit_client()

    def wait_until_client_has_left(self):
        """waits until client has left to end the test"""
        return self.vca_client.wait_until_client_has_left()
