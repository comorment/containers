#!/bin/sh
set -euo pipefail

# python appears to be a build time dependency
apt-get update && apt-get install -y  --no-install-recommends python3=3.8.2-0ubuntu2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# /usr/bin/python must exist
update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# qctools
wget --no-check-certificate https://code.enkre.net/qctool/zip/e5723df2c0c85959/qctool.zip
unzip qctool.zip
cd qctool
./waf configure
./waf

# copy binaries to /bin
cp build/release/apps/inthinnerator_v2.2.2 /bin/inthinnerator
cp build/release/apps/hptest_v2.2.2 /bin/hptest
cp build/release/apps/ldbird_v2.2.2 /bin/ldbird
cp build/release/apps/qctool_v2.2.2 /bin/qctool
cp build/release/apps/selfmap_v2.2.2 /bin/selfmap

# remove python
apt-get purge \
    python3 -y && \
    apt-get autoremove --purge -y
