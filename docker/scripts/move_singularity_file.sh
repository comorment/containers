#!/usr/bin/env bash
# helper script to change ownership to $USER of built container,
# and moving file to the appropriate directory in repository
set -e

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "Must run script with sudo or as root"
    exit
fi

# exit on errors
trap 'exit' ERR

# change ownership to $USER, move built container to appropriate directory
chown $(logname) $1.sif && \
chgrp $(logname) $1.sif && \
chmod 664 $1.sif && \
mv $1.sif ../singularity/.