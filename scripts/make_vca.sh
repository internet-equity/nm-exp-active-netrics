#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi


## install software
apt -y install snapd python3-dev python3-opencv xvfb python3-tk python3-dev scrot xclip xdg-utils
snap install chromium

## create xauthority file needed for the virtual display
## FIX
touch ~/.Xauthority

## copy the config file
VCA_PATH="src/netrics/plugin/netrics_vca_test"
VCA_AUTO_PATH="$VCA_PATH/vca_automation"
cp "$VCA_AUTO_PATH/configs/config_client.toml_bkp" "$VCA_AUTO_PATH/config.toml"

## install python requirements 
### activate the virtual environment
if [ ! "$VIRTUAL_ENV" == "/usr/local/src/nm-exp-active-netrics/venv" ];
then
	echo "activating virtual environment" >> "test.txt"
	. ./venv/bin/activate
fi
requirements="$VCA_PATH/requirements.txt"
pip3 install -r $requirements

## switch to a new user
## download the vca code
git submodule update --init --recursive
git submodule update --remote


