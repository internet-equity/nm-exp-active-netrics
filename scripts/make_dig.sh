#!/bin/bash

# if [[ $EUID -ne 0 ]]; then
#   echo "ERROR: This script must be run as root"
#   exit 1
# fi​

PROC=$(uname -p)
VER=9.18.7
# this is essentially the nm-exp-active-netrics base dir
# wherever the source was downloaded/cloned
NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

# $PROC is the processor of the current host machine
# in case one would like to build for some other architecture
mkdir -p commands/src/dig/$PROC/
cd commands/src/dig/$PROC/

apt-get update && apt-get install -y wget build-essential
# link from https://www.linuxfromscratch.org/blfs/view/svn/basicnet/bind-utils.html 
wget https://ftp.isc.org/isc/bind9/$VER/bind-$VER.tar.xz
tar -xvf bind-$VER.tar.xz
cd bind-$VER

mkdir -p $NMAPATH/commands/$PROC/

apt-get install -y pkg-config libuv1-dev libnghttp2-dev libcap-dev libssl-dev libjemalloc-dev

./configure --prefix=$NMAPATH/commands/$PROC/ &&
make -C lib/isc    &&
make -C lib/dns    &&
make -C lib/isc    &&
make -C lib/dns    &&
make -C lib/ns     &&
make -C lib/isccfg &&
make -C lib/bind9  &&
make -C lib/irs    &&
make -C bin/dig    && make -C doc

make -C bin/dig    install


mkdir -p $NMAPATH/commands/$PROC/lib

cp $NMAPATH/commands/src/dig/$PROC/bind-$VER/lib/isc/.libs/libisc-$VER.so $NMAPATH/commands/$PROC/lib
cp $NMAPATH/commands/src/dig/$PROC/bind-$VER/lib/dns/.libs/libdns-$VER.so $NMAPATH/commands/$PROC/lib
cp $NMAPATH/commands/src/dig/$PROC/bind-$VER/lib/isccfg/.libs/libisccfg-$VER.so $NMAPATH/commands/$PROC/lib
cp $NMAPATH/commands/src/dig/$PROC/bind-$VER/lib/irs/.libs/libirs-$VER.so $NMAPATH/commands/$PROC/lib
cp $NMAPATH/commands/src/dig/$PROC/bind-$VER/lib/bind9/.libs/libbind9-$VER.so $NMAPATH/commands/$PROC/lib
cp $NMAPATH/commands/src/dig/$PROC/bind-$VER/lib/ns/.libs/libns-$VER.so $NMAPATH/commands/$PROC/lib

cat <<EOF >$NMAPATH/bin/dig.sh
#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/src/nm-exp-active-netrics/lib
/usr/local/src/nm-exp-active-netrics/bin/dig \$@
EOF

chmod a+rwx $NMAPATH/bin/dig.sh

cp $NMAPATH/bin/dig.sh $NMAPATH/commands/$PROC/bin
