#!/bin/bash

if [[ $EUID -eq 0 ]]; then
   echo "ERROR: This script must be run as non-root" 
   exit 1
fi

PROC=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

#mkdir -p commands/src/ndt/$PROC/
#cd commands/src/ndt/$PROC/

if cmd=$(command -v go); then echo $cmd; else echo "ERROR: golang not in the path"; exit 1; fi
go version
USER1=$USER
sudo chown $USER1:$USER1 commands/$PROC -R
export GOPATH=$PWD/commands/$PROC
export GO111MODULE=on
go get -v github.com/m-lab/ndt7-client-go/cmd/ndt7-client
