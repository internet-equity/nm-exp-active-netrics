#!/bin/bash

## switch to a new user
## download the vca code
git submodule update --init --recursive
git submodule update --remote --recursive



## copy the config file
VCA_PATH="src/netrics/plugin/netrics_vca_test"
VCA_AUTO_PATH="$VCA_PATH/vca_automation"
cp "$VCA_AUTO_PATH/configs/config_client.toml_bkp" "$VCA_AUTO_PATH/config.toml"

