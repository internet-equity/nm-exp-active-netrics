#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "ERROR: This script must be run as root" 
   exit 1
fi

addgroup --system netrics
adduser --system --no-create-home  --disabled-password --disabled-login --ingroup netrics netrics
