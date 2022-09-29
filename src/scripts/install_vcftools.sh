#!/bin/sh


# vcfools
 apt-get update
 apt-get install -y automake pkg-config zlib1g-dev
 git clone https://github.com/vcftools/vcftools.git . && \
 ./autogen.sh && \
 ./configure && \
  make -j6 && \
  make install


#cp vcftools  /bin
