#!/bin/bash

if [ ! -f /etc/cron.d/cron-nm-exp-active-netrics ];then
  if [ -f /etc/nm-exp-active-netrics/cron-nm-exp-active-netrics ];then
	cp /etc/nm-exp-active-netrics/cron-nm-exp-active-netrics /etc/cron.d/
	chmod 0644 /etc/cron.d/cron-nm-exp-active-netrics
  fi
fi
