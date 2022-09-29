#!/bin/sh


# bcfools
git clone --recurse-submodules --depth 1 --branch 1.12 git://github.com/samtools/htslib.git && \
git clone --recurse-submodules --depth 1 --branch 1.12 git://github.com/samtools/bcftools.git && \
cd bcftools && \
apt-get update && apt-get install -y curl libcurl4-gnutls-dev libbz2-dev liblzma-dev && \
#autoheader && autoconf && ./configure --enable-libgsl --enable-perl-filters && \
make -j12
make install

#cp /bcftools/bcftools  /bin
