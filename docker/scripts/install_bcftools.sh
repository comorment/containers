#!/bin/sh
set -euo pipefail

# deps 
apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-gnutls-dev=8.5.0-2ubuntu10.6 \
    libperl-dev=5.38.2-3.2ubuntu0.2

apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# bcftools
git clone --recurse-submodules --depth 1 -b 1.19 https://github.com/samtools/bcftools.git && \
cd bcftools && \
autoheader && autoconf && ./configure --enable-libgsl --enable-perl-filters --with-htslib=/usr/ && \
make -j12 && \
make install
