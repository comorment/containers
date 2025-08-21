#!/bin/sh
set -euo pipefail

wget --no-check-certificate https://s3.amazonaws.com/plink2-assets/plink2_linux_x86_64_20250819.zip && \
    unzip -j plink2_linux_x86_64_20250819.zip && \
    rm -rf plink2_linux_x86_64_20250819.zip

cp plink2 /bin
