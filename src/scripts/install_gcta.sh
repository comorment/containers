#!/bin/sh

# gcta
curl -O -J -L https://cnsgenomics.com/software/gcta/bin/gcta_1.93.2beta.zip && \
    unzip -j  gcta_1.93.2beta.zip && \
    rm -rf gcta_1.93.2beta.zip

cp gcta64  /bin
