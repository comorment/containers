#!/bin/sh
set -euo pipefail

version=25.3.1-0
curl -sSL https://github.com/conda-forge/miniforge/releases/download/$version/Miniforge3-$version-$(uname)-$(uname -m).sh -o /tmp/mambaforge.sh \
  && mkdir /root/.conda \
  && bash /tmp/mambaforge.sh -bfp /usr/local \
  && rm -rf /tmp/mambaforge.sh

export PATH=$PATH:/opt/conda/bin
