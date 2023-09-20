#!/usr/bin/env bash

set -eou pipefail

# This script documents how to build the singularity container
# from the Dockerfile

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "Must run script with sudo or as root"
    exit
fi

# exit on errors
trap 'exit' ERR

# build docker image
source ~/.bash_profile  # need env variable GITHUB_PAT set in /root/.bash_profile of host
docker build --build-arg GITHUB_PAT=$GITHUB_PAT -t $1 -f dockerfiles/$1/Dockerfile .