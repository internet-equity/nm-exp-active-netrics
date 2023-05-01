#!/bin/bash
export PATH=$PATH:/usr/bin/go/bin
current_dir=$(pwd)

# Check if go is installed
if cmd=$(command -v go); then echo $cmd; else echo "ERROR: golang not in the path"; exit 1; fi
go version

PROC=$(uname -p)

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

cd $NMAPATH
echo "INFO: working dir ("$(pwd)")"

mkdir -p commands/src/goresp/$PROC/
cd commands/src/goresp/$PROC/


echo "Cloning the git repository to $current_dir/commands/src/goresp..."
sudo git clone https://github.com/network-quality/goresponsiveness.git goresp
sudo chmod 777 goresp

echo "Building the networkQuality.go executable..."
cd goresp
echo "INFO: working dir ("$(pwd)")"


export GO111MODULE="on"

go mod download
go build networkQuality.go

mkdir -p $NMAPATH/commands/$PROC/bin/
cp networkQuality $NMAPATH/commands/$PROC/bin/
