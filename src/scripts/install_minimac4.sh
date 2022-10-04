#!/bin/sh


apt-get update && \
    apt-get install --no-install-recommends \
    python-pip python-setuptools python-click python-six python-dev -y && \
    rm -rf /var/lib/apt/lists/*

pip install --no-cache-dir cget
git clone https://github.com/statgen/Minimac4.git && \
cd Minimac4 && \
cget install -f ./requirements.txt && \
mkdir build && cd build && \
cmake -DCMAKE_TOOLCHAIN_FILE=../cget/cget/cget.cmake .. && \
make && \
cp minimac4 /bin
#make installi

# remove cget, python-pip etc. used to build minimac4
pip uninstall cget
apt-get purge \
    python-setuptools python-pip python-dev python-click python-six -y && \
    apt-get autoremove --purge -y
