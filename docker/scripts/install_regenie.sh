#!/bin/sh
set -euo pipefail

# additional deps
apt-get update && apt-get install --no-install-recommends \
    libboost-iostreams-dev=1.83.0.1ubuntu2 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# required for building regenie (doesn't find bgen otherwise)
SHA="4f70490b4c54be43714900636b514d2b882544df"
git clone https://github.com/dbolser/bgen.git && \
    cd bgen && git checkout $SHA && \
    ./waf configure --prefix=/usr && \
    ./waf && \
    cd ..

# build regenie
git clone --depth 1 --branch v4.1.1 https://github.com/rgcgithub/regenie.git
cd regenie
BGEN_PATH=../bgen HAS_BOOST_IOSTREAM=1 HTSLIB_PATH=/usr/lib/ cmake .
make

cp regenie /bin