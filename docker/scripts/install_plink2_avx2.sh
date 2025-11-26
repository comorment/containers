#!/bin/sh
set -euo pipefail

wget --no-check-certificate https://github.com/chrchang/plink-ng/releases/download/v2.0.0-a.6.28/plink2_linux_avx2.zip && \
    unzip -j plink2_linux_avx2.zip && \
    rm -rf plink2_linux_avx2.zip
# we install non-avx plink2 so that default plink runs on any  CPU architecture


mv plink2 plink2_avx2
rm -f plink2

cp plink2_avx2 /bin
