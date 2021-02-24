#!/bin/bash

PROC=$(uname -p)
PROC='aarch64'

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

if [[ "$PROC" != 'aarch64' && "$PROC" != 'armhf' && "$PROC" != 'arm64' ]];then
  echo "ERROR: processor ${PROC} not supported, try a dedicated device (aarch64, armhf, arm64)."
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

if [ ! -d ./venv ];then
   echo "ERROR: please run: make deps venv first"
fi

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"
cd ..
mkdir -p /usr/local/src/
cp -R nm-exp-active-netrics /usr/local/src
cp /usr/local/src/nm-exp-active-netrics/bin/netrics /usr/local/bin/
ln -s /usr/local/bin/netrics /usr/bin/nm-exp-active-netrics