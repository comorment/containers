#!/bin/sh
set -euo pipefail

# gcta
curl -O -J -L https://github.com/jianyangqt/gcta/releases/download/v1.93.3beta2/gcta_1.93.3beta2.zip && \
    unzip -j  gcta_1.93.3beta2.zip && \
    rm -rf gcta_1.93.3beta2.zip

cp gcta64  /bin
