#!/bin/sh
set -euo pipefail

apt-get update && apt-get install --no-install-recommends \
    r-mathlib=4.3.3-2build2 \
    libboost-iostreams1.83-dev=1.83.0-2.1ubuntu3.1 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

git clone https://github.com/ofrei/switcherror.git && \
    cd switcherror && \
    git checkout 6e688b1f03972b6bfb965ed8eb341b9309c75207
    git apply ../switchError.diff && \
    make -j 4 && \
    cp bin/switchError /usr/bin/.
