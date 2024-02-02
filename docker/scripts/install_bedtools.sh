#!/bin/bash
set -euo pipefail

VERSION="2.31.1"
wget https://github.com/arq5x/bedtools2/releases/download/v$VERSION/bedtools-$VERSION.tar.gz
tar -zxvf bedtools-$VERSION.tar.gz
cd bedtools2
make -j4
cp bin/* /bin

