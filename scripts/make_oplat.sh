#!/bin/bash

if [[ $EUID -eq 0 ]]; then
      echo "ERROR: this script must run as NON-root, (from a user with sudo priv)"
   exit 1
fi

proc=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

echo $PWD
sudo mkdir -p commands/src/oplat/$PROC/
sudo chown $USER:$USER commands/src/oplat/$PROC/
cd commands/src/oplat/$PROC

wget https://golang.org/dl/go1.17.linux-arm64.tar.gz
tar -xzf go1.17.linux-arm64.tar.gz
export PATH=$PATH:~/go/bin

if cmd=$(command -v go); then echo $cmd; else echo "ERROR: golang not in the path"; exit 1; fi

go get -u github.com/go-ping/ping
git clone https://github.com/kyle-macmillan/OpLat.git
cd OpLat
go build oplat.go
cp oplat $NMAPATH/commands/$PROC/bin
