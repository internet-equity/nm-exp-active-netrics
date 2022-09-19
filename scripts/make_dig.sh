#!/bin/bash

# if [[ $EUID -ne 0 ]]; then
#   echo "ERROR: This script must be run as root"
#   exit 1
# fi​

PROC=$(uname -p)

# this is essentially the nm-exp-active-netrics base dir
# wherever the source was downloaded/cloned
NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

​# $PROC is the processor of the current host machine
​# in case one would like to build for some other architecture
mkdir -p commands/src/dig/$PROC/
cd commands/src/dig/$PROC/

# link from https://www.linuxfromscratch.org/blfs/view/svn/basicnet/bind-utils.html 
wget https://ftp.isc.org/isc/bind9/9.18.6/bind-9.18.6.tar.xz
tar -xvf bind-9.18.6.tar.xz
cd bind-9.18.6

mkdir -p $NMAPATH/commands/$PROC/

apt-get install -y pkg-config libuv1-dev libnghttp2-dev libcap-dev

./configure --prefix=$NMAPATH/commands/$PROC/ &&
make -C bin/dig     # && <--   maybe here we can compile only dig ?
#make -C lib/isc    &&
#make -C lib/dns    &&
#make -C lib/ns     &&
#make -C lib/isccfg &&
#make -C lib/bind9  &&
#make -C lib/irs    &&
#make -C doc

make -C bin/dig    install
