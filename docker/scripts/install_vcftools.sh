#!/bin/sh
set -euo pipefail

# vcfools
git clone https://github.com/vcftools/vcftools.git && \
    cd vcftools && \
    git reset --hard d511f469e87c2ac9779bcdc3670b2b51667935fe && \
    ./autogen.sh && \
    ./configure && \
make -j6 && \
make install


#cp vcftools  /bin
