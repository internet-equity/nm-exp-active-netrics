#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

PROC=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

mkdir -p commands/src/iperf/$PROC/
cd commands/src/iperf/$PROC/
wget https://downloads.es.net/pub/iperf/iperf-3.9.tar.gz
tar -xvf iperf-3.9.tar.gz
cd iperf-3.9
mkdir -p $NMAPATH/commands/$PROC/
./configure --prefix $NMAPATH/commands/$PROC/
make; make install; make clean
./configure #no prefix, install on /
make; make install; make clean
