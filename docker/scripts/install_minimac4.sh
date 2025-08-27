#!/bin/sh
set -euo pipefail

# install some deps for installing cget
apt-get update && \
    apt-get install --no-install-recommends \
    python3-pip=24.0+dfsg-1ubuntu1.2 \
    python3-click=8.1.6-2 \
    python3-six=1.16.0-4 \
    -y && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# install cget
# The "--break-system-packages" flag was needed to not break build
pip3 install --no-cache-dir --break-system-packages cget==0.2.0

# install Minimac4
VERSION="v4.1.6"
git clone --depth 1 -b $VERSION https://github.com/statgen/Minimac4.git
cd Minimac4
cget ignore xz
cget install -f ./requirements.txt
mkdir build
cd build
cmake -DCMAKE_TOOLCHAIN_FILE=../cget/cget/cget.cmake ..
make
cp minimac4 /bin

# remove cget, python-pip etc. used to build Minimac4
pip3 uninstall --break-system-packages cget -y
apt-get purge \
    python3-pip python3-click python3-six -y && \
    apt-get autoremove --purge -y
