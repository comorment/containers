#!/bin/sh
set -euo pipefail

# deps
apt-get update && apt-get install --no-install-recommends \
    libgomp1=10.3.0-1ubuntu1~20.04 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# king
wget --no-check-certificate https://www.kingrelatedness.com/executables/Linux-king229.tar.gz && \
    tar -xvzf Linux-king229.tar.gz && \
    rm -rf Linux-king229.tar.gz

cp king  /bin

rm -rf *