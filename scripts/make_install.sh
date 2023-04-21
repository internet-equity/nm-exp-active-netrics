#!/bin/bash

PROC=$(uname -p)
#PROC='aarch64'

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

# /usr/local/src/nm-exp-active-netrics/
mkdir -p /usr/local/src/nm-exp-active-netrics/
cp -R nm-exp-active-netrics/bin/ /usr/local/src/nm-exp-active-netrics/
cp -R nm-exp-active-netrics/src/ /usr/local/src/nm-exp-active-netrics/
cp -R nm-exp-active-netrics/commands/$PROC/lib /usr/local/src/nm-exp-active-netrics/
cp -R nm-exp-active-netrics/commands/$PROC/bin /usr/local/src/nm-exp-active-netrics/
cp /usr/local/src/nm-exp-active-netrics/bin/netrics /usr/local/bin/

if [ ! -f /usr/bin/nm-exp-active-netrics ];then
  ln -s /usr/local/bin/netrics /usr/bin/nm-exp-active-netrics
fi

# /etc/nm-exp-active-netrics/nm-exp-active-netrics.toml
mkdir -p /etc/nm-exp-active-netrics
cp nm-exp-active-netrics/conf/nm-exp-active-netrics.toml /etc/nm-exp-active-netrics/nm-exp-active-netrics.toml.template
cp nm-exp-active-netrics/conf/nm-exp-active-netrics.toml /etc/nm-exp-active-netrics/

# logrotate.d
mkdir -p /etc/logrotate.d/
cp nm-exp-active-netrics/etc/logrotate.d/netrics /etc/logrotate.d/

# /etc/init.d/nm-exp-active-netrics
cp nm-exp-active-netrics/etc/init.d/nm-exp-active-netrics /etc/init.d/
chmod +x /etc/init.d/nm-exp-active-netrics
update-rc.d nm-exp-active-netrics defaults

# env

cd -

if [ -f env/.env.netrics ];then
  echo "INFO: env detected. copying env/.env.netrics /etc/nm-exp-active-netrics/.env.netrics ..."
  chmod go-rw env/.env.netrics
  cp env/.env.netrics /etc/nm-exp-active-netrics/.env.netrics
else
  echo "INFO: NO env detected."
fi

if [ ! -d "/var/nm" ]; then
  mkdir /var/nm
  chown netrics:netrics /var/nm -R
fi

chown netrics:netrics /etc/nm-exp-active-netrics/.env.netrics
chown netrics:netrics /usr/local/src/nm-exp-active-netrics/ -R
