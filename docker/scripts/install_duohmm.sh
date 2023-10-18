#!/bin/sh
set -euo pipefail

git clone https://github.com/jaredo/duohmm.git && \
    cd duohmm && \
    git checkout 95bd3958792aeaa43e9f301ead139e5691d7c165 && \
    make -j 4 && \
    cp bin/duohmm /usr/bin/


