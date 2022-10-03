#!/bin/sh


# metal

wget --no-check-certificate http://csg.sph.umich.edu/abecasis/metal/download/Linux-metal.tar.gz && \
   tar -xvzf Linux-metal.tar.gz && \
   rm -rf  Linux-metal.tar.gz

mv generic-metal/* .
cp metal  /bin
