#!/bin/bash

if [[ $EUID -eq 0 ]]; then
	echo "ERROR: This script must run as NON-root, (from an user with sudo priv)" 
   exit 1
fi

PROC=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

echo $PWD
sudo mkdir -p commands/src/ndt/$PROC/
sudo chown $USER:$USER commands/src/ndt/$PROC/
cd commands/src/ndt/$PROC/

if cmd=$(command -v go); then echo $cmd; else echo "ERROR: golang not in the path"; exit 1; fi
go version
export GOPATH=$PWD/commands/$PROC
export GO111MODULE=on
echo $PWD
#go get -v github.com/m-lab/ndt7-client-go/cmd/ndt7-client

mkdir gocache
export GOCACHE=$PWD/gocache
export GOPATH=$PWD

git clone https://github.com/m-lab/ndt7-client-go.git
cd ndt7-client-go/cmd/ndt7-client
go build -o ndt7-client main.go
cp ndt7-client $NMAPATH/commands/$PROC/bin/
