#!/bin/bash

# Check if OpenSSL is already installed
if ! command -v openssl &> /dev/null
then
    echo "OpenSSL is not installed, installing now..."
    sudo apt-get update
    sudo apt-get install openssl
else
    echo "OpenSSL is already installed"
fi

# Check if httping is already installed
if ! command -v httping &> /dev/null
then
    echo "httping is not installed, installing now..."
    # Download and extract the httping source code
    mkdir /home/ubuntu/nm-exp-active-netrics/commands/src/httping/
    cd /home/ubuntu/nm-exp-active-netrics/commands/src/httping/ 
    wget --no-check-certificate https://www.vanheusden.com/httping/httping-1.5.1.tgz
    tar -xzvf httping-1.5.1.tgz
    cd httping-1.5.1

    # Install httping
    make install

    # Clean up the downloaded files
    cd ..
    rm -rf httping-1.5.1.tgz
else
    echo "httping is already installed"
fi
