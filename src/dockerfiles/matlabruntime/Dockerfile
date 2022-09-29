# matlab/octave container

FROM ubuntu:xenial
#FROM 'ubuntu:18.04'

# runtime
RUN apt-get -qq update && apt-get -qq install -y \
    unzip \
    xorg \
    wget \
    curl && \
    mkdir /mcr-install && \
    mkdir /opt/mcr && \
    cd /mcr-install && \
    wget http://ssd.mathworks.com/supportfiles/downloads/R2018b/deployment_files/R2018b/installers/glnxa64/MCR_R2018b_glnxa64_installer.zip && \
    cd /mcr-install && \
    unzip -q MCR_R2018b_glnxa64_installer.zip && \
    ./install -destinationFolder /opt/mcr -agreeToLicense yes -mode silent && \
    cd / && \
    rm -rf mcr-install

    # octave

    RUN apt-get update && apt-get install -y \
    octave \
    octave-control octave-image octave-io octave-optim octave-signal octave-statistics





# Configure environment variables for MCR
ENV LD_LIBRARY_PATH /opt/mcr/v95/runtime/glnxa64:/opt/mcr/v95/bin/glnxa64:/opt/mcr/v95/sys/os/glnxa64:/opt/mcr/v95/extern/bin/glnxa64
ENV XAPPLRESDIR /opt/mcr/v95/X11/app-defaults


ENV MCR_CACHE_ROOT /tmp




#required tools
RUN apt-get update && apt-get install -y  --no-install-recommends apt-utils\
    python3 \
    tar \
    wget \
    unzip \
    git  \
  libgsl0-dev \
   perl \
    less \
    parallel \
    liboctave-dev \
    && \
    rm -rf /var/lib/apt/lists/*

    RUN  apt-get install -y liboctave-dev


ADD /magicsquare /magicsquare
