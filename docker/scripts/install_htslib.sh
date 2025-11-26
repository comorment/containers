#!/bin/sh
set -euo pipefail

# additional deps
apt-get update && apt-get install --no-install-recommends \
    libbz2-dev=1.0.8-5.1build0.1 \
    liblzma-dev=5.6.1+really5.4.5-1ubuntu0.2 \
    libssl-dev=3.0.13-0ubuntu3.6 \
    -y 
 
apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# build and install HTSlib
git clone --depth 1 -b 1.19.1 https://github.com/samtools/htslib.git --recurse-submodules && \
    cd htslib && \
    autoreconf -i && \
    ./configure --prefix=/usr/ && \
    make -j 4 && \
    make install
