#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/src/nm-exp-active-netrics/lib
/usr/local/src/nm-exp-active-netrics/bin/dig $@
