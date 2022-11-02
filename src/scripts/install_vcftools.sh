#!/bin/sh


# vcfools
git clone --depth 1 https://github.com/vcftools/vcftools.git && \
    cd vcftools && \
    git reset --hard 581c231991cb4db017b92eabc573e17128541ab5 && \
    ./autogen.sh && \
    ./configure && \
make -j6 && \
make install


#cp vcftools  /bin
