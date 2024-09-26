#!/bin/sh
set -euo pipefail

# install some deps for installing cget
apt-get update && \
    apt-get install --no-install-recommends \
    python3-pip=20.0.2-5ubuntu1.10 \
    python3-click=7.0-3 \
    python3-six=1.14.0-2 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install cget 
pip3 install --no-cache-dir cget==0.2.0

# install Minimac4
VERSION="v4.1.6"
git clone --depth 1 -b $VERSION https://github.com/statgen/Minimac4.git && \
cd Minimac4 && \
cget install -f ./requirements.txt && \
mkdir build && cd build && \
cmake -DCMAKE_TOOLCHAIN_FILE=../cget/cget/cget.cmake .. && \
make && \
cp minimac4 /bin

# remove cget, python-pip etc. used to build Minimac4
# pip3 uninstall cget -y
# apt-get purge \
#     python3-pip python3-click python3-six -y && \
#     apt-get autoremove --purge -y
