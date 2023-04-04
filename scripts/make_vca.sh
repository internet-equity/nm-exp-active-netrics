#!/bin/bash

## install software
sudo apt install snapd
sudo snap install chromium

## create xauthority file needed for the virtual display
touch ~/.Xauthority

## download the vca code
git submodule update --init --recursive
git submodule update --remote

## copy the config file
VCA_PATH="src/netrics/plugin/netrics_vca_test"
VCA_AUTO_PATH="$VCA_PATH/vca_automation"
cp "$VCA_AUTO_PATH/configs/config_client.toml_bkp" "$VCA_AUTO_PATH/config.toml"

## install python requirements 
### activate the virtual environment
if [ ! "$VIRTUAL_ENV" == "/usr/local/src/nm-exp-active-netrics/venv" ];
then
	. ./venv/bin/activate
fi
requirements="$VCA_PATH/requirements.txt"
python3 -m pip install -r $requirements

