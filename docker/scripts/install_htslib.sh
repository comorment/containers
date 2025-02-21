#!/bin/sh
set -euo pipefail

# additional deps
apt-get update && apt-get install --no-install-recommends \
    libbz2-dev=1.0.8-2 \
    liblzma-dev=5.2.4-1ubuntu1.1 \
    libssl-dev=1.1.1f-1ubuntu2.24 \
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
