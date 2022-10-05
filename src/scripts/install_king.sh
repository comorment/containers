#!/bin/sh


# metal
apt-get update
apt-get install libquadmath0 libgomp1 -y
wget --no-check-certificate https://www.kingrelatedness.com/Linux-king.tar.gz && \
  tar -xvzf Linux-king.tar.gz && \
  rm -rf Linux-king.tar.gz



   cp king  /bin
