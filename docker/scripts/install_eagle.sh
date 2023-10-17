#!/bin/sh
set -euo pipefail

apt-get update && apt-get install --no-install-recommends \
    libopenblas-dev=0.3.8+ds-1ubuntu0.20.04.1 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

git clone --depth 1 -b v2.4.1 https://github.com/poruloh/Eagle.git && \
    cd Eagle && \
    git apply ../eagle.diff && \
    cd src && \
    make -j 4 && \
    cp eagle /usr/bin/


