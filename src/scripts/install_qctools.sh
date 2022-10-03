#!/bin/sh


# qctools

 wget --no-check-certificate https://www.well.ox.ac.uk/~gav/resources/qctool_v2.0.6-Ubuntu16.04-x86_64.tgz && \
    tar -xvzf qctool_v2.0.6-Ubuntu16.04-x86_64.tgz && \
    rm -rf  qctool_v2.0.6-Ubuntu16.04-x86_64.tgz


mv qctool_v2.0.6-Ubuntu16.04-x86_64/* .
cp qctool  /bin

chmod 755 /bin/qctool
