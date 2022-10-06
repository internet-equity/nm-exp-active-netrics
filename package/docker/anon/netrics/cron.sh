#!/bin/bash
/etc/init.d/nm-exp-active-netrics restart
chown netrics:netrics /var/nm/nm-exp-active-netrics/ -R
cron -f
