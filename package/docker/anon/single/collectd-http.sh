#!/bin/bash

/etc/init.d/nm-exp-active-netrics start
/etc/init.d/cron start
/usr/local/bin/nm-mgmt-collectd-http
