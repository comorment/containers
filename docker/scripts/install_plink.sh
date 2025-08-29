#!/bin/sh
set -euo pipefail

# plink
wget --no-check-certificate https://github.com/chrchang/plink-ng/releases/download/v1.9.0-b.7.11/plink_linux_x86_64.zip && \
    unzip -j plink_linux_x86_64.zip && \
    rm -rf plink_linux_x86_64.zip
cp plink /bin
