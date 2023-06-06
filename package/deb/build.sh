#!/bin/bash


if [[ $EUID -eq 0 ]]; then
   echo "ERROR: This script must be run as NON-root" 
   exit 1
fi

PROC_U=$(uname -p)
PROC=arm64
mv *.deb backup/
version_pyc=$(cat ../../src/netrics.py | grep "__version__" | grep -Po '(\d)+.(\d)+.(\d)+')
version_deb=$(cat nm-exp-active-netrics/DEBIAN/control| grep "Version:" | grep -Po '(\d)+.(\d)+.(\d)+')
echo "python version:" ${version_pyc}
echo "debian version:" ${version_deb}

if [ "${version_pyc}" != "${version_deb}" ];then
	echo "ERROR: python and debian version do not match."
	exit 1
fi

#clean venv
if [ -d nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/venv ];then
	rm -Rf nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/venv
fi

cp -R /usr/local/src/nm-exp-active-netrics/src/ nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/
cp -R /usr/local/src/nm-exp-active-netrics/venv/ nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/

mkdir -p nm-exp-active-netrics/etc/nm-exp-active-netrics/
mkdir -p nm-exp-active-netrics/etc/logrotate.d/
mkdir -p nm-exp-active-netrics/etc/init.d/
mkdir -p nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/databases
mkdir -p nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/
mkdir -p nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/lib/
mkdir -p nm-exp-active-netrics/usr/local/bin
mkdir -p nm-exp-active-netrics/usr/bin

#netrics
cp ../../conf/nm-exp-active-netrics.toml nm-exp-active-netrics/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml.template
cp /etc/init.d/nm-exp-active-netrics nm-exp-active-netrics/etc/init.d/
cp /etc/logrotate.d/netrics nm-exp-active-netrics/etc/logrotate.d/
cp /usr/local/src/nm-exp-active-netrics/bin/netrics nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/
cp /usr/local/src/nm-exp-active-netrics/bin/netrics nm-exp-active-netrics/usr/local/bin/
cp /usr/bin/nm-exp-active-netrics nm-exp-active-netrics/usr/bin/

#iperf3 / ndt / speedtest (moved to venv/...)
cp ../../commands/$PROC_U/bin/* nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/
cp ../../commands/$PROC_U/lib/* nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/lib/
cp /usr/local/src/nm-exp-active-netrics/bin/iperf3.sh nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/
cp /usr/local/src/nm-exp-active-netrics/bin/makecronandtoml.py nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/

fakeroot dpkg-deb --build nm-exp-active-netrics
mv nm-exp-active-netrics.deb nm-exp-active-netrics-v${version_pyc}-${PROC}.deb
