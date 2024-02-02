#!/bin/sh
set -euo pipefail

# install some deps for installing cget
apt-get update && \
    apt-get install --no-install-recommends \
    fossil=1:2.10-1 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# qctools
fossil clone https://code.enkre.net/qctool qctool.fossil -A root
fossil open qctool.fossil
fossil checkout e5723df2c0c85959  # 2.2.2

./waf configure --prefix=/usr/
./waf install
ln -s /usr/bin/qctool_v2.2.2 /usr/bin/qctool

# remove fossil used to build qctools
apt-get purge \
    fossil -y && \
    apt-get autoremove --purge -y
