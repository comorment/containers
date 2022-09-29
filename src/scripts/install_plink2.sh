#!/bin/sh
wget --no-check-certificate https://s3.amazonaws.com/plink2-assets/alpha2/plink2_linux_x86_64.zip && \
    unzip -j plink2_linux_x86_64.zip && \
    rm -rf plink2_linux_x86_64.zip

cp plink2 /bin
