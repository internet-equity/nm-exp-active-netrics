#!/bin/bash

NMAPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/../

if [ ! -d "venv" ]; then
  python3 -m venv venv
  python3 -m pip install -r requirements
else
  echo "WARN: existing venv, already built?"
fi
echo -e "please run:\n. ./venv/bin/activate"
