#!/bin/sh

set -e

# deps 
apt-get update && apt-get install -y --no-install-recommends \
    curl libcurl4-gnutls-dev libbz2-dev liblzma-dev \
    libperl-dev && \
    rm -rf /var/lib/apt/lists/*


# bcfools
git clone --recurse-submodules --depth 1 -b 1.12 https://github.com/samtools/htslib.git && \
git clone --recurse-submodules --depth 1 -b 1.12 https://github.com/samtools/bcftools.git && \
cd bcftools && \
autoheader && autoconf && ./configure --enable-libgsl --enable-perl-filters && \
make -j12 && \
make install

#cp /bcftools/bcftools  /bin
