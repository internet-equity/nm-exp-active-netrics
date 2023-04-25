"""
    Class for launching Google Meet Calls.
"""
from . utility import *
from subprocess import Popen

import time
import subprocess
import sys
import netrc
import pyautogui
import os
import signal
import cv2
import random
import string

from sys import platform
class Meet:

    def __init__(self, config):
        """Initiates a meet call object"""
        self.id = config["meet"]["url"]
        self.config = config
        
        if len(config['default']['platform']) > 0:
            self.platform = config['default']['platform']
        else:
            self.platform = 'raspi' if platform == "linux" and os.uname()[1] == "raspberrypi" else platform


        self.logger = None
        self.automation_img_dir = f'{config["call"]["automation_image_dir"]}/{self.platform}'
        self.sleep_interval = 1

    def join_call_mac(self):
        """join the meet call by clicking join image"""
        click_image(f'{self.automation_img_dir}/meet_join_now.png')

    def join_call_raspi(self):
        """Join meet call on raspi"""
        time.sleep(20)
        pyautogui.hotkey('esc')
        res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=10))
        pyautogui.typewrite(res)
        time.sleep(1)
        pyautogui.hotkey("tab")
        pyautogui.hotkey("enter")
        ## adding 10 more seconds of sleep to account for the overhead in joining the call
        time.sleep(10)

    def join_call_linux(self):
        """Join meet call on linux"""
        self.join_call_mac()

    def join_call(self):
        """Join a meet call after checking the os"""
        self.logger.info("Joining meet call on %s",self.platform)
        pyautogui.typewrite(self.id)
        pyautogui.hotkey('enter')
        time.sleep(5)
        
        if self.platform == "darwin":
            self.join_call_mac()
        elif self.platform == "raspi" or self.platform == "netrics-raspi":
            self.join_call_raspi()
        elif self.platform == "linux":
            self.join_call_linux()

    def admit_client(self):
        """Admit client on a meet call by clicking admit button on screen"""
        max_wait_time = 30#self.config["call"]["duration"]
        wait_time = 0
        admitted_participant = False
        while wait_time < max_wait_time:
            if locate_on_screen(f'{self.automation_img_dir}/meet_admit.png'):
                pyautogui.hotkey('tab')
                time.sleep(1)
                pyautogui.hotkey('enter')
                #click_image(f'{self.automation_img_dir}/meet_admit.png')
                admitted_participant = True
                break
            else:
                time.sleep(self.sleep_interval)
                wait_time += self.sleep_interval
        self.logger.info("Admitted participant?: %s",admitted_participant)
        return admitted_participant

    def wait_until_client_has_left(self):
        """sleep until there is no client in the call"""
        wait_time = 0
        max_wait_time = self.config["call"]["duration"]+20
        participant_left = False
        while wait_time < max_wait_time:
            if not locate_on_screen(f'{self.automation_img_dir}/meet_participant_not_exist.png'):
                time.sleep(self.sleep_interval)
                wait_time += self.sleep_interval
            else:
                participant_left = True
                break
        return participant_left

    def exit_call(self):
        """exit a meet call by clicking end call button on the screen"""
        ## End Meet call
        click_image(f'{self.automation_img_dir}/meet_end_call.png')
        time.sleep(2)
        
        pyautogui.hotkey(self.config["platform"]["ctl_key"], 'w')
        self.logger.info("Exited meet call")
        return
