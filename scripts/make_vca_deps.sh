#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi


## install software
apt -y install snapd python3-dev python3-opencv xvfb python3-tk python3-dev scrot xclip xdg-utils chromium-browser


## install python requirements 
### activate the virtual environment
if [ ! "$VIRTUAL_ENV" == "/usr/local/src/nm-exp-active-netrics/venv" ];
then
	echo "activating virtual environment" >> "test.txt"
	. ./venv/bin/activate
fi

VCA_PATH="src/netrics/plugins/netrics_vca_test"
requirements="$VCA_PATH/requirements.txt"
pip3 install -r $requirements

## enable packet capture
sudo chmod +x /usr/bin/dumpcap
