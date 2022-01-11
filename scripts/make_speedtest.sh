#!/bin/bash

# from https://www.speedtest.net/apps/cli

PROC=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

if [ -f "/usr/bin/speedtest" ];then
  cp -f /usr/bin/speedtest ./bin/
  cp -f /usr/bin/speedtest ./commands/${PROC}/bin/
else
  sudo apt-get install -y gnupg1 apt-transport-https dirmngr

  # https://www.speedtest.net/apps/cli
  curl -s https://install.speedtest.net/app/cli/install.deb.sh | sudo bash

  # Other non-official binaries will conflict with Speedtest CLI
  # Example how to remove using apt-get
  # sudo apt-get remove speedtest-cli
  sudo apt-get install -y speedtest
fi
