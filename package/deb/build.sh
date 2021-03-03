#!/bin/bash

#PROC=$(uname -a)
PROC=arm64
mv *.deb backup/
version_pyc=$(cat ../../src/netrics.py | grep "__version__" | grep -Po '(\d)+.(\d)+.(\d)+')
version_deb=$(cat nm-exp-active-netrics/DEBIAN/control| grep "Version:" | grep -Po '(\d)+.(\d)+.(\d)+')
echo "python version:" ${version_pyc}
echo "debian version:" ${version_deb}

cp -R /usr/local/src/nm-exp-active-netrics/src/ nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/
cp -R /usr/local/src/nm-exp-active-netrics/venv/ nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/

mkdir -p nm-exp-active-netrics/etc/nm-exp-active-netrics/
mkdir -p nm-exp-active-netrics/etc/init.d/
mkdir -p nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/databases
mkdir -p nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/
mkdir -p nm-exp-active-netrics/usr/local/bin
mkdir -p nm-exp-active-netrics/usr/bin
cp ../../conf/nm-exp-active-netrics.toml nm-exp-active-netrics/etc/nm-exp-active-netrics/
cp /etc/init.d/nm-exp-active-netrics nm-exp-active-netrics/etc/init.d/
cp /usr/local/src/nm-exp-active-netrics/bin/netrics nm-exp-active-netrics/usr/local/src/nm-exp-active-netrics/bin/
cp /usr/local/src/nm-exp-active-netrics/bin/netrics nm-exp-active-netrics/usr/local/bin/
cp /usr/bin/nm-exp-active-netrics nm-exp-active-netrics/usr/bin/
fakeroot dpkg-deb --build nm-exp-active-netrics
mv nm-exp-active-netrics.deb nm-exp-active-netrics-v${version_pyc}-${PROC}.deb

