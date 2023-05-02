#!/bin/sh

set -e

# deps 
apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-gnutls-dev=7.68.0-1ubuntu2.14 \
    libperl-dev=5.30.0-9ubuntu0.3 \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# bcfools
git clone --recurse-submodules --depth 1 -b 1.12 https://github.com/samtools/bcftools.git && \
cd bcftools && \
autoheader && autoconf && ./configure --enable-libgsl --enable-perl-filters --with-htslib=/usr/ && \
make -j12 && \
make install
