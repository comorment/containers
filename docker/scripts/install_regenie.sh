#!/bin/sh
set -euo pipefail

# additional deps
apt-get update && apt-get install --no-install-recommends \
    libboost-iostreams-dev=1.71.0.0ubuntu2 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# required for building regenie (doesn't find bgen otherwise)
VERSION="1.1.7"
wget http://code.enkre.net/bgen/tarball/release/v$VERSION.tgz && \
    tar -xvzf v$VERSION.tgz && cd v$VERSION && \
    ./waf configure && \
    ./waf && \
    cd ..

# build regenie
git clone --depth 1 --branch v3.6 https://github.com/rgcgithub/regenie.git
cd regenie
BGEN_PATH=../v$VERSION HAS_BOOST_IOSTREAM=1 HTSLIB_PATH=/usr/lib/ cmake .
make

cp regenie /bin