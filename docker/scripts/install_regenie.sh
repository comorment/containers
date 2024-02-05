#!/bin/sh
set -euo pipefail

# required for building regenie (doesn't find bgen otherwise)
VERSION="1.1.7"
wget http://code.enkre.net/bgen/tarball/release/v$VERSION.tgz && \
    tar -xvzf v$VERSION.tgz && cd v$VERSION && \
    ./waf configure && \
    ./waf && \
    cd ..

# build regenie
git clone --depth 1 --branch v3.4.1 https://github.com/rgcgithub/regenie.git
cd regenie
BGEN_PATH=../v$VERSION cmake .
make

cp regenie /bin