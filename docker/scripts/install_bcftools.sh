#!/bin/sh
set -euo pipefail

# deps 
apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-gnutls-dev=7.68.0-1ubuntu2.23 \
    libperl-dev=5.30.0-9ubuntu0.5

apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# bcftools
git clone --recurse-submodules --depth 1 -b 1.19 https://github.com/samtools/bcftools.git && \
cd bcftools && \
autoheader && autoconf && ./configure --enable-libgsl --enable-perl-filters --with-htslib=/usr/ && \
make -j12 && \
make install
