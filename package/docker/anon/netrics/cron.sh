#!/bin/bash
echo "NETRICS INFO: Netrics restart..."
dpkg -i ./nm-exp-active-netrics-v1.0.0-arm64.deb
#/etc/init.d/nm-exp-active-netrics restart
chown netrics:netrics /var/nm/nm-exp-active-netrics/ -R
cron -f -L 15
