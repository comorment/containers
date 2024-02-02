#!/bin/sh
set -euo pipefail

wget https://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/liftOver
chmod +x liftOver
mv liftOver /bin
