#!/bin/sh
apt-get update && apt-get install -y --no-install-recommends apt-utils=2.0.9
apt-get update && apt-get install -y --no-install-recommends ca-certificates=20211016~20.04.1 && \
   update-ca-certificates

# (!) Keep the list below sorted (!)
apt-get update && apt-get install -y --no-install-recommends \
   autoconf=2.69-11.1 \
   automake=1:1.16.1-4ubuntu6 \
   build-essential=12.8ubuntu1 \
   bzip2=1.0.8-2 \
   cmake=3.16.3-1ubuntu1.20.04.1 \
   curl=7.68.0-1ubuntu2.14 \
   dos2unix=7.4.0-2 \
   gfortran=4:9.3.0-1ubuntu2 \
   git=1:2.25.1-1ubuntu3.6 \
   less=551-1ubuntu0.1 \
   libatlas-base-dev=3.10.3-8ubuntu7 \
   libcurl4-openssl-dev=7.68.0-1ubuntu2.14 \
   libgomp1=10.3.0-1ubuntu1~20.04 \
   libgsl-dev=2.5+dfsg-6build1 \
   libnss3=2:3.49.1-1ubuntu1.8 \
   libpcre2-dev=10.34-7ubuntu0.1 \
   libxt-dev=1:1.1.5-1 \
   pandoc=2.5-3build2 \
   pandoc-citeproc=0.15.0.1-1build4 \
   parallel=20161222-1.1 \
   perl=5.30.0-9ubuntu0.3 \
   pkg-config=0.29.1-0ubuntu4 \
   tar=1.30+dfsg-7ubuntu0.20.04.2 \
   tofrodos=1.7.13+ds-4 \
   unzip=6.0-25ubuntu1.1 \
   vim=2:8.1.2269-1ubuntu5.9 \
   wget=1.20.3-1ubuntu2 \
   zlib1g-dev=1:1.2.11.dfsg-2ubuntu1.5 \
   && \
   apt-get clean && \
   rm -rf /var/lib/apt/lists/*
   