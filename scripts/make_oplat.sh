#!/bin/bash

if [[ $EUID -eq 0 ]]; then
      echo "ERROR: this script must run as NON-root, (from a user with sudo priv)"
   exit 1
fi

PROC=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

echo $PWD
sudo mkdir -p commands/src/oplat/$PROC/
sudo chown $USER:$USER commands/src/oplat/$PROC/
cd commands/src/oplat/$PROC

git clone https://github.com/kyle-macmillan/OpLat.git
go env -w GO111MODULE=off
export GOPATH=$PWD #/commands/$PROC

if cmd=$(command -v go); then echo $cmd; else echo "ERROR: golang not in the path"; exit 1; fi

go get -u github.com/go-ping/ping

cd OpLat
go build oplat.go
cp oplat $NMAPATH/commands/$PROC/bin/
