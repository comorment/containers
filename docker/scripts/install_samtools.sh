#!/bin/sh
set -euo pipefail

apt-get update && apt-get install -y --no-install-recommends \
    libncurses-dev=6.4+20240113-1ubuntu2 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# samtools
git clone --depth 1 -b 1.19.2 https://github.com/samtools/samtools.git && \
cd samtools && \
    autoheader && \
    autoconf -Wno-syntax && \
    ./configure --with-htslib=/usr/ && \
    make -j12 && \
    make install
