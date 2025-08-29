#!/bin/sh
set -euo pipefail

export VERSION="v2.4.1"
                           
wget --no-check-certificate https://storage.googleapis.com/broad-alkesgroup-public/BOLT-LMM/downloads/old/BOLT-LMM_${VERSION}.tar.gz
tar -xvzf BOLT-LMM_$VERSION.tar.gz
rm -rf BOLT-LMM_$VERSION.tar.gz
mv BOLT-LMM_$VERSION/* .

# delete some stuff that should not be containerized:
rm -rf BOLT-LMM_$VERSION
rm license.txt
rm BOLT-LMM_*_manual.pdf
rm -rf src
rm -rf example
rm -rf tables 

# NB! Bolt-LMM must be executed from /tools/bolt/bolt because it links to binaries in /tools/bolt/lib folder.


