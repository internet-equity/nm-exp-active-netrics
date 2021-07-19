#!/bin/bash

s3cmd -c .s3cfg sync --skip-existing s3://$1/ sync/
chgrp broadband sync/ -R
