#!/bin/sh
set -euo pipefail

wget --no-check-certificate https://github.com/precimed/simu/releases/download/v0.9.4/simu_linux
chmod +x simu_linux
cp simu_linux  /bin/
