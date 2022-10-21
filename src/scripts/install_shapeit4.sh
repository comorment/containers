#!/bin/sh

# additional deps
apt-get update && apt-get install --no-install-recommends \
    libssl-dev=1.1.1f-1ubuntu2.16 \
    libboost-iostreams-dev=1.71.0.0ubuntu2 \
    libboost-program-options-dev=1.71.0.0ubuntu2 \
    libbz2-dev=1.0.8-2 \
    liblzma-dev=5.2.4-1ubuntu1.1 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# build and install HTSlib
git clone --depth 1 -b 1.11 https://github.com/samtools/htslib.git --recurse-submodules && \
    cd htslib && \
    autoreconf -i && \
    ./configure --prefix=/usr/ && \
    make -j 4 && \
    make install && \
    cd ..

# Build and install shapeit4
## workaround for shapeit4 makefile looking for $(USER)/Tools/htslib-1.11/libhts.a
mkdir /root/Tools && mkdir /root/Tools/htslib-1.11 && ln -s /usr/lib/libhts.a /root/Tools/htslib-1.11/libhts.a
# build shapeit4
git clone --depth 1 -b v4.2.2 https://github.com/odelaneau/shapeit4.git && \
    cd shapeit4 && \
    make -j 4 && \
    cp bin/* /usr/bin/.