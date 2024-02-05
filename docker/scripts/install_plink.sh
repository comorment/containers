#!/bin/sh
set -euo pipefail

# plink
wget --no-check-certificate https://s3.amazonaws.com/plink1-assets/plink_linux_x86_64_20231211.zip && \
    unzip -j plink_linux_x86_64_20231211.zip && \
    rm -rf plink_linux_x86_64_20231211.zip
cp plink /bin
