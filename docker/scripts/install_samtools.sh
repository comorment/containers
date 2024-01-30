#!/bin/sh
set -euo pipefail

# bcfools
git clone --depth 1 -b 1.12 https://github.com/samtools/samtools.git && \
cd bcftools && \
    autoheader && \
    autoconf -Wno-syntax && \
    ./configure --with-htslib=/usr/ && \
    make -j12 && \
    make install
