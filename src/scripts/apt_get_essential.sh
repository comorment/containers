#!/bin/sh
apt-get update && apt-get install -y ca-certificates && update-ca-certificates

# (!) Keep the list below sorted (!)
apt-get update && apt-get install -y  --no-install-recommends apt-utils \
   autoconf \
   build-essential \
   bzip2 \
   cmake \
   curl \
   dos2unix \
   gfortran \
   git \
   less \
   libatlas-base-dev \
   libcurl4 \
   libcurl4-openssl-dev \
   libgomp1 \
   libgsl0-dev \
   libnss3 \
   libpcre2-dev \
   libquadmath0 \
   libxt-dev \
   make \
   pandoc \
   pandoc-citeproc \
   parallel \
   perl \
   tar \
   tofrodos \
   unzip \
   vim \
   wget \
   zlib1g-dev \
   && \
   rm -rf /var/lib/apt/lists/*
   