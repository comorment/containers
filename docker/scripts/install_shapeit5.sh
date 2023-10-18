#!/bin/sh
set -euo pipefail

# build shapeit5
git clone --depth 1 -b v5.1.1 https://github.com/odelaneau/shapeit5.git --recurse-submodules && \
    cd shapeit5 && \
    cd xcftools && \
    git apply ../../xcftools.diff && \
    cd .. && \
    git apply ../shapeit5.diff && \
    make -j 4 && \
    cp phase_common/bin/phase_common /usr/bin/ && \
    cp phase_rare/bin/phase_rare /usr/bin/ && \
    cp ligate/bin/ligate /usr/bin/ && \
    cp switch/bin/switch /usr/bin/ && \
    cp xcftools/bin/xcftools /usr/bin/

