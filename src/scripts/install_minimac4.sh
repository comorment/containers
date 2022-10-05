#!/bin/sh

# install some deps for installing cget
apt-get update && \
    apt-get install --no-install-recommends \
    python3-pip python3-click python3-six -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# python-setuptools python-click python-six python-dev -y && \

# install cget 
pip3 install --no-cache-dir cget

# install Minimac4
git clone https://github.com/statgen/Minimac4.git && \
cd Minimac4 && \
cget install -f ./requirements.txt && \
mkdir build && cd build && \
cmake -DCMAKE_TOOLCHAIN_FILE=../cget/cget/cget.cmake .. && \
make && \
cp minimac4 /bin
#make installi

# remove cget, python-pip etc. used to build Minimac4
pip3 uninstall cget -y
apt-get purge \
    python3-pip python3-click python3-six -y && \
    apt-get autoremove --purge -y
#     python-setuptools python-pip python-dev python-click python-six -y && \
#     apt-get autoremove --purge -y
