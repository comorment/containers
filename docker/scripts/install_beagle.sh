#!/bin/sh
set -euo pipefail

# additional deps
apt-get update && apt-get install --no-install-recommends \
    default-jre=2:1.21-75+exp1 \
    -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

wget http://faculty.washington.edu/browning/beagle/beagle.22Jul22.46e.jar && \
    mv beagle.22Jul22.46e.jar beagle.jar

cat stub.sh beagle.jar > /usr/bin/beagle && chmod +x /usr/bin/beagle
