#!/bin/sh
set -euo pipefail

wget --no-check-certificate https://github.com/chrchang/plink-ng/releases/download/v2.0.0-a.6.28/plink2_linux_x86_64.zip && \
    unzip -j plink2_linux_x86_64.zip && \
    rm -rf plink2_linux_x86_64.zip

cp plink2 /bin
