#!/bin/sh
# plink
wget --no-check-certificate https://s3.amazonaws.com/plink1-assets/plink_linux_x86_64_20200616.zip && \
    unzip -j plink_linux_x86_64_20200616.zip && \
    rm -rf plink_linux_x86_64_20200616.zip
cp plink /bin
