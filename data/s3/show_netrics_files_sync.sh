#!/bin/bash

dev=$(for d in `ls -d sync/netrics_mngd/nm-exp-active-netrics/default/*/`;do echo $d;done)
for i in $dev; do
	k=$(basename $i)
	nbrfiles=$(find $i -mtime -1 -ls | wc -l)
	echo "{ \"$k\" : "$nbrfiles" }"
done
