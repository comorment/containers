#!/bin/sh
set -euo pipefail

apt-get update && apt-get install --no-install-recommends \
    r-mathlib=3.6.3-2 \
    libboost-iostreams1.71-dev=1.71.0-6ubuntu6 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

git clone https://github.com/ofrei/switcherror.git && \
    cd switcherror && \
    git checkout 6e688b1f03972b6bfb965ed8eb341b9309c75207
    git apply ../switchError.diff && \
    make -j 4 && \
    cp bin/switchError /usr/bin/.
