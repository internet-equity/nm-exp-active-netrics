"""

    Class for initiating the teams calls in client of browser
"""
import os
from subprocess import Popen, PIPE

import cv2
import time
import netrc
import sys
import pyautogui
from sys import platform
import random
import string
from . utility import *
import logging
log = logging.getLogger(__name__)




class Teams:

    def __init__(self, config):
        """Initiates a teams call object"""
        self.id = config["teams"]["url"]
        self.config = config

        if len(config['default']['platform']) > 0:
            self.platform = config['default']['platform']
        else:
            self.platform = 'raspi' if platform == "linux" and os.uname()[1] == "raspberrypi" else platform

        self.logger = None 
        self.automation_img_dir = f'{config["call"]["automation_image_dir"]}/{self.platform}'
        self.sleep_interval = 1

    def join_call_mac(self):
        """Join teams call on mac"""

        ## closing the pop up asking to open teams native client
        t = click_image(f'{self.automation_img_dir}/teams_close_popup.png')
        if not t:
            self.logger.error("close popup window not found!")
            print("close popup window not found!")

        time.sleep(1)
        
        t = click_image(f'{self.automation_img_dir}/teams_continue_browser.png')
        if not t:
            self.logger.error("error: continue on browser not found")
        
        time.sleep(5)
        
        t = click_image(f'{self.automation_img_dir}/teams_camera_on.png', max_num_tries=10)
        if not t:
            self.logger.error("error: camera button not found")
        
        time.sleep(2)

        t = click_image(f'{self.automation_img_dir}/teams_join_now.png')
        if not t:
            self.logger.error("error: join now tab not found")
        
        time.sleep(3)
    
    def paste(self):
        p = Popen(['xclip', '-out', '-selection', 'clipboard'], stdout=PIPE)
        return p.communicate()[0]

    def join_call_raspi(self):
        """Join teams call on raspi"""

        # time.sleep(10)
        """ 
        if self.platform == "netrics-raspi":
            t = click_image(f"{self.automation_img_dir}/teams_cancel.png")
            time.sleep(1)
            t = click_image(f"{self.automation_img_dir}/teams_continue_browser.png")
        """
        ## additional wait as raspi redirection takes time
        time.sleep(50)
        """
        # joining as guest
        num_tries = 0
        max_tries = 8

        while num_tries < max_tries:
            screenshot = pyautogui.screenshot()
            screenshot.save(f'screenshot_{num_tries}.png')
            
            bbox = pyautogui.locate(f'{self.automation_img_dir}/teams_meeting_now.png', screenshot, confidence= 0.5, grayscale=True, region=(0, 0, 1500, 500))
            if not bbox:
                sleep_time = 5
                time.sleep(sleep_time)
                print("sleeping for {} seconds".format(sleep_time))
                num_tries += 1
            else:
                break
        
        if num_tries == max_tries:
            print("could not find enter name")
            return
        
        print("pressing tab key")
        pyautogui.hotkey("tab")
        time.sleep(1)
        
        print("pressing shift tab key")
        pyautogui.hotkey("shift", "tab")
        time.sleep(1)

        print("pressing shift tab key")
        pyautogui.hotkey("shift", "tab")
        """
        print('Typing name...')
        res = 'R' + ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=10))
        pyautogui.hotkey('alt', 'd')
        pyautogui.hotkey('ctrl', 'c')
        url = self.paste().decode('utf-8')
        
        if 'pre-join-calling' in url:
            for _ in range(3):
                pyautogui.hotkey('tab')
            pyautogui.typewrite(res)
            pyautogui.hotkey('enter')
        else:
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.typewrite(res)
            pyautogui.typewrite('enter')
        #pyautogui.typewrite("guest")
        print("Waiting for the server to admit", time.time())
        ## Waiting time before server admits
        time.sleep(8)
        print("Sleeping now")

    def join_call_linux(self):
        """Join teams call on linux"""

        self.join_call_mac()

    def join_call(self):
        """Join a teams call after checking the os"""

        # Open Teams VCA
        pyautogui.hotkey(self.config["platform"]["ctl_key"], 'l')
        pyautogui.typewrite(self.id)
        pyautogui.hotkey('enter')
        time.sleep(2)
        
        self.logger.info("Joining teams call on %s",self.platform)
        if self.platform == "darwin":
            self.join_call_mac()
        elif self.platform == "raspi" or self.platform == "netrics-raspi":
            self.join_call_raspi()
        elif self.platform == "linux":
            self.join_call_linux()

    def exit_call(self):
        """exit a teams call by clicking end call button on the screen"""

        ## Hang up call
        time.sleep(1)
        #pyautogui.move(0, 100)
        #time.sleep(2)
        #s = pyautogui.screenshot()
        #s.save('screenshot.png')
        #t = click_image(f'{self.automation_img_dir}/teams_leave.png', grayscale=True)
        #if not t:
        #    print("leave image not found, exiting using the shortcut")
            ## exit using the shortcut
        pyautogui.hotkey(self.config["platform"]["ctl_key"], "shift", "h")
        #    self.logger.error("error: leave call button not found")
        time.sleep(2)

        ## Close the browser window
        pyautogui.hotkey(self.config["platform"]["ctl_key"], 'w')
        self.logger.info("closed browser")

    def admit_client(self):
        """Admit client on a teams call by clicking admit button on screen"""
        max_wait_time = 30#self.config["call"]["duration"]
        wait_time = 0
        admitted_participant = False
        client_present_img = f'{self.automation_img_dir}/teams_client_present.png'
        while wait_time < max_wait_time:
            self.logger.info(f'Waiting for client: {wait_time}')
            if locate_on_screen(client_present_img):
                admitted_participant = True
                break
            else:
                #pyautogui.screenshot(f"screenshot_teams_admit_{wait_time}.png")
                time.sleep(self.sleep_interval)
                wait_time += self.sleep_interval
        self.logger.info("Admitted participant: %s",admitted_participant)
        return admitted_participant

    def wait_until_client_has_left(self):
        """sleep until there is no client in the call"""

        wait_time = 0
        participant_left = False
        time.sleep(self.config["call"]["duration"] + 20)
        if not locate_on_screen(f'{self.automation_img_dir}/teams_participant_exists.png'):
            participant_left = True
        return participant_left
