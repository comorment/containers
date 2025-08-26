#!/bin/sh
set -euo pipefail

# build bgen
# fixed build issue in https://enkre.net/cgi-bin/code/bgen/tktview/52cb8e5b67. 
# Use the same git SHA in the install_regenie.sh script
SHA="4f70490b4c54be43714900636b514d2b882544df"
git clone https://github.com/dbolser/bgen.git && \
    cd bgen && git checkout $SHA && \
    ./waf configure --prefix=/usr && \
    ./waf install
