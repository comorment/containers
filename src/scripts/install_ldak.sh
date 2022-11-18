#!/bin/sh

# ldak
export VERSION='5.2'
wget --no-check-certificate https://dougspeed.com/wp-content/uploads/ldak$VERSION.linux_.zip && \
    unzip -j ldak$VERSION.linux_.zip && \
    rm -rf ldak$VERSION.linux_.zip
cp ldak$VERSION.linux /bin
ln -s /bin/ldak$VERSION.linux /bin/ldak