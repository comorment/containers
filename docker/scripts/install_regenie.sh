#!/bin/sh
set -euo pipefail

wget --no-check-certificate https://github.com/rgcgithub/regenie/releases/download/v3.2.8/regenie_v3.2.8.gz_x86_64_Linux_mkl.zip && \
    unzip -j regenie_v3.2.8.gz_x86_64_Linux_mkl.zip && \
    rm -rf regenie_v3.2.8.gz_x86_64_Linux_mkl.zip && \
    mv regenie_v3.2.8.gz_x86_64_Linux_mkl regenie
cp regenie /bin
