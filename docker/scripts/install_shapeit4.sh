#!/bin/sh
set -euo pipefail

# additional deps
apt-get update && apt-get install --no-install-recommends \
    libboost-program-options-dev=1.71.0.0ubuntu2 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# build shapeit4
git clone --depth 1 -b v4.2.2 https://github.com/odelaneau/shapeit4.git && \
    cd shapeit4 && \
    patch makefile < ../shapeit4.makefile.diff
    make -j 4 && \
    cp bin/* /usr/bin/.