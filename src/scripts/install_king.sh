#!/bin/sh


# metal
apt-get update
apt-get install libgomp1 -y
wget --no-check-certificate https://www.kingrelatedness.com/executables/Linux-king229.tar.gz && \
  tar -xvzf Linux-king229.tar.gz && \
  rm -rf Linux-king229.tar.gz



   cp king  /bin
