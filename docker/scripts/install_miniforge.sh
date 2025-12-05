#!/bin/sh
set -euo pipefail

version=25.11.0-1
curl -sSL https://github.com/conda-forge/miniforge/releases/download/$version/Miniforge3-$version-$(uname)-$(uname -m).sh -o /tmp/miniforge.sh
mkdir /root/.conda
bash /tmp/miniforge.sh -bfp /usr/local
rm -rf /tmp/miniforge.sh

export PATH=$PATH:/opt/conda/bin
