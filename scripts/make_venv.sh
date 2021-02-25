#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

requirements=$NMAPATH/requirements.txt

ls -lh $requirements

mkdir -p /usr/local/src/nm-exp-active-netrics

cd /usr/local/src/nm-exp-active-netrics

if [ ! -d "venv" ]; then
  python3 -m venv venv
  . ./venv/bin/activate
  python3 -m pip install -r $requirements
else
  echo "WARN: existing venv, already built?"
fi
