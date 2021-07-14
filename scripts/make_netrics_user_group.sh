#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi


if id "netrics" &>/dev/null; then
    echo 'INFO: user [netrics] found.'
else
    echo 'INFO: user [netrics] not found. Creating...'
    addgroup --system netrics
    adduser --system --home /home/netrics --disabled-password --disabled-login --ingroup netrics netrics
fi
