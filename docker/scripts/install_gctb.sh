#!/bin/sh
set -euo pipefail

# gctb
VERSION="2.04.3"
wget --no-check-certificate https://cnsgenomics.com/software/gctb/download/gctb_${VERSION}_Linux.zip  && \
   unzip   gctb_${VERSION}_Linux.zip && \
   rm -rf gctb_${VERSION}_Linux.zip

mv gctb_${VERSION}_Linux/* .
cp gctb /bin 

chmod 755 /bin/gctb
