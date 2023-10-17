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

# need env variable GITHUB_PAT set in /root/.bash_profile of host for r.sif to build.
# this is a personal access token from github with read:packages scope and will have
# to be updated every 30 days.
if [ $1 == "r" ]; then
    source ~/.bash_profile
    if [ -z "$GITHUB_PAT" ]; then
        echo "GITHUB_PAT not set"
        exit 1
    fi
fi
# build docker image
docker build --build-arg GITHUB_PAT=$GITHUB_PAT -t $1 -f dockerfiles/$1/Dockerfile .