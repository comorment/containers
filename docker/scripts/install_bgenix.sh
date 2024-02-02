#!/bin/sh
set -euo pipefail

# build bgen
VERSION="1.1.7"
wget http://code.enkre.net/bgen/tarball/release/v$VERSION.tgz && \
    tar -xvzf v$VERSION.tgz && mv v$VERSION/* . && \
    ./waf configure --prefix=/usr && \
    ./waf install
