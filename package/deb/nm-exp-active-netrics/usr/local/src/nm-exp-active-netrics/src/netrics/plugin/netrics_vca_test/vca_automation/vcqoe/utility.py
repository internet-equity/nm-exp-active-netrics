'''
Contains generic utility functions
'''
import  pathlib
import subprocess
import time
import os
import cv2
import numpy as np
from datetime import datetime

def make_dir(new_dir):
    """
    Creates a directory if it does not exists including the
    parent directories
    @param new_dir:
    @return:
    """
    p = pathlib.Path(new_dir)
    if not p.is_dir():
        print(f'making dir [{p}]')
        p.mkdir(parents=True)
    return


def time_diff(st):
    """returns time difference with current time and st"""
    return (datetime.now() - st).total_seconds()


def image_search(image_name, haystack = None, threshold=0.8, grayscale=False):
    """searcges for an image on screen with pyautogui module"""
    import pyautogui
    if haystack:
        sct = cv2.imread(haystack)
    else:
        sct = pyautogui.screenshot()
    img_rgb = np.array(sct)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    img = img_gray if grayscale else img_rgb
    template = cv2.imread(image_name, 0)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print(max_val)
    if max_val < threshold:
        return [-1, -1]
    else:
        return max_loc



def click_image(png_name, grayscale=False, confidence=0.9, max_num_tries=5, wait_interval=1):
    """locates and clicks an image on screen using pyautogui"""
    import pyautogui
    num_tries = 0
    while num_tries < max_num_tries:
        button = locate_on_screen(png_name)
        if not button:
            num_tries += 1
            time.sleep(wait_interval)
            continue
        x = button[0]
        y = button[1]
        if subprocess.call("system_profiler SPDisplaysDataType | grep 'Retina'", shell= True) == 0:
            x = x / scale_factor
            y = y / scale_factor
        pyautogui.moveTo(x,y, 1)
        pyautogui.click()
        return "Clicked {0}".format(png_name)
    basename = os.path.basename(png_name)
    pyautogui.screenshot(f"/tmp/screenshot_{basename}")
    print(f"DEBUG: {basename} not found")
    return None


def get_trace_filename(datapath, vca_name, endpoint="client"):
    """produce trace file name with current time and return the name"""

    #datapath = config["default"]["datapath"]
    #vca_name = config["default"]["vca"]
    data_dir = f'{datapath}/{vca_name}'
    make_dir(data_dir)
    trace_filename = f"{data_dir}/{endpoint}-{vca_name}-{int(time.time())}"
    print("Log file: ",trace_filename)
    
    return trace_filename

def locate_on_screen(png_file):
    """locate a png file image on screen with pyautogui"""
    t = int(time.time())
    import pyautogui
    image = pyautogui.screenshot(f'/tmp/image_{t}.png')
    basename = os.path.basename(png_file)
    #image.save(f'image_debug_{t}_{basename}')
    loc1 = pyautogui.locate(png_file, image, grayscale=True)
    #loc2 = pyautogui.locateOnScreen(png_file)
    #print(loc1, loc2)
    return loc1
