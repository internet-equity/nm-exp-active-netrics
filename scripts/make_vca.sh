#!/bin/bash

## switch to a new user
## download the vca code
git submodule update --init --recursive
git submodule update --remote --recursive



## copy the config file
vca_path="src/netrics/plugins/netrics_vca_test/vca_automation"
cp "$vca_path/configs/config_client.toml_bkp" "$vca_path/config.toml"
config_file="$vca_path/config.toml"
download_dir="/home/netrics/snap/chromium/current/Downloads"
sed -i "s@download_dir=.*@download_dir='$download_dir'@" $config_file

