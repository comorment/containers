#!/bin/sh
set -euo pipefail

apt-get update && apt-get install -y --no-install-recommends apt-utils=2.8.3
apt-get update && apt-get install -y --no-install-recommends ca-certificates=20240203 && \
   update-ca-certificates

# (!) Keep the list below sorted (!)
apt-get update && apt-get install -y --no-install-recommends \
   autoconf=2.71-3 \
   automake=1:1.16.5-1.3ubuntu1 \
   build-essential=12.10ubuntu1 \
   bzip2=1.0.8-5.1build0.1 \
   cmake=3.28.3-1build7 \
   curl=8.5.0-2ubuntu10.6 \
   dos2unix=7.5.1-1 \
   gdb=15.0.50.20240403-0ubuntu1 \
   gfortran=4:13.2.0-7ubuntu1 \
   git=1:2.43.0-1ubuntu7.3 \
   less=590-2ubuntu2.1 \
   libatlas-base-dev=3.10.3-13ubuntu1 \
   libcurl4-openssl-dev=8.5.0-2ubuntu10.6 \
   libgomp1=14.2.0-4ubuntu2~24.04 \
   libgsl-dev=2.7.1+dfsg-6ubuntu2 \
   libnss3=2:3.98-1build1 \
   libpcre2-dev=10.42-4ubuntu2.1 \
   libxt-dev=1:1.2.1-1.2build1 \
   pandoc=3.1.3+ds-2 \
   parallel=20231122+ds-1 \
   perl=5.38.2-3.2ubuntu0.2 \
   pkg-config=1.8.1-2build1 \
   python3-dev=3.12.3-0ubuntu2.1 \
   python3-pytest=7.4.4-1 \
   tar=1.35+dfsg-3build1 \
   tofrodos=1.7.13+ds-6 \
   unzip=6.0-28ubuntu4.1 \
   vim=2:9.1.0016-1ubuntu7.9 \
   wget=1.21.4-1ubuntu4.1 \
   zlib1g-dev=1:1.3.dfsg-3.1ubuntu2.1
   
apt-get clean && rm -rf /var/lib/apt/lists/*
   
# /usr/bin/python must exist for bgenix, qctool
update-alternatives --install /usr/bin/python python /usr/bin/python3 10
update-alternatives --install /usr/bin/py.test py.test /usr/bin/py.test-3 10
