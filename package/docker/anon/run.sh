#!/bin/bash


if [ -d 'volume' ]; then
  echo "INFO: volume detected. "
else
echo "INFO: creating volume folder at $PWD/volume"
  mkdir -p volume/etc/nm-exp-active-netrics
  mkdir -p volume/var/nm
  wget https://github.com/chicago-cdac/nm-exp-active-netrics/releases/download/v1.0.0-2022/nm-exp-active-netrics.toml -O volume/etc/nm-exp-active-netrics/nm-exp-active-netrics.toml
fi
 
if [ -f 'netrics_id' ];then
  netrics_id=$(cat netrics_id)
else
  netrics_id=$(echo  "nm-anon-$(date +'%Y%m%d')-$(uuidgen | awk -F- '{print $1}')")
  echo $netrics_id > netrics_id 
fi

docker run --restart=unless-stopped -d -e NETRICS_ID=$netrics_id \
	-v $PWD/volume/etc/nm-exp-active-netrics:/etc/nm-exp-active-netrics \
	-v $PWD/volume/var/nm:/var/nm \
	--name netrics-anon-v0  ggmartins/netrics-anon:v0
echo "INFO: your NETRICS_ID is:"
cat netrics_id
