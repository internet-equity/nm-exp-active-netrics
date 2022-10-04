#!/bin/bash

docker run -d -e NETRICS_ID=nm-anon-20220920-00000001 \
	-v $PWD/volume/etc/nm-exp-active-netrics:/etc/nm-exp-active-netrics \
	-v $PWD/volume/var/nm:/var/nm \
	--name netrics-anon-v0  netrics-anon:v0
