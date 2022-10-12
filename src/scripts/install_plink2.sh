#!/bin/sh
wget --no-check-certificate https://s3.amazonaws.com/plink2-assets/alpha3/plink2_linux_x86_64_20220814.zip && \
    unzip -j plink2_linux_x86_64_20220814.zip && \
    rm -rf plink2_linux_x86_64_20220814.zip

cp plink2 /bin
