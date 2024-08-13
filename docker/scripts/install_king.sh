#!/bin/sh
set -euo pipefail

# king
VERSION="232"
wget --no-check-certificate --referer=http://example.com/referer-page/ https://www.kingrelatedness.com/executables/Linux-king$VERSION.tar.gz && \
    tar -xvzf Linux-king$VERSION.tar.gz && \
    rm -rf Linux-king$VERSION.tar.gz

cp king  /bin

rm -rf *