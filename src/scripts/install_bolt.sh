#!/bin/sh

export VERSION="v2.4"
wget --no-check-certificate https://storage.googleapis.com/broad-alkesgroup-public/BOLT-LMM/downloads/BOLT-LMM_$VERSION.tar.gz && \
tar -xvzf BOLT-LMM_$VERSION.tar.gz # && \
rm -rf BOLT-LMM_$VERSION.tar.gz # && \
mv BOLT-LMM_$VERSION/* . # && \

# delete some stuff that should not be containerized:
rm -rf BOLT-LMM_$VERSION
rm license.txt
rm BOLT-LMM_$VERSION_manual.pdf
rm bolt.Makefile.patch
rm -rf src
rm -rf example
rm -rf tables 

# NB! Bolt-LMM must be executed from /tools/bolt/bolt because it links to binaties in /tools/bolt/lib folder.

# mv bolt.Makefile.patch src/
# cd src
# patch Makefile < bolt.Makefile.patch
# make -d


