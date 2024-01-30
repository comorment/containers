#!/bin/sh
set -euo pipefail

# metal
wget --no-check-certificate https://github.com/statgen/METAL/archive/refs/tags/2020-05-05.tar.gz
tar -xvzf 2020-05-05.tar.gz

mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ../METAL-2020-05-05/.
make -j4
make install
cp bin/metal /bin
