#!/bin/sh
wget --no-check-certificate https://github.com/rgcgithub/regenie/releases/download/v2.0.2/regenie_v2.0.2.gz_x86_64_Linux_mkl.zip && \
    unzip -j regenie_v2.0.2.gz_x86_64_Linux_mkl.zip && \
    rm -rf regenie_v2.0.2.gz_x86_64_Linux_mkl.zip && \
    mv regenie_v2.0.2.gz_x86_64_Linux_mkl regenie
cp regenie /bin
