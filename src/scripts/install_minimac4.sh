#!/bin/sh


apt-get update
apt-get install cmake -y python-pip python-dev -y
pip install cget
git clone https://github.com/statgen/Minimac4.git && \
cd Minimac4 && \
cget install -f ./requirements.txt && \
mkdir build && cd build && \
cmake -DCMAKE_TOOLCHAIN_FILE=../cget/cget/cget.cmake .. && \
make && \
cp minimac4 /bin
#make installi

