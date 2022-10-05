#!/bin/sh
wget --no-check-certificate https://s3.amazonaws.com/plink2-assets/alpha2/plink2_linux_avx2.zip && \
    unzip -j plink2_linux_avx2.zip && \
    rm -rf plink2_linux_avx2.zip
# we install non-avx plink2 so that default plink runs on any  CPU architecture


mv plink2 plink2_avx2
rm -f plink2

cp plink2_avx2 /bin
