#!/bin/sh


# gctb

wget --no-check-certificate https://cnsgenomics.com/software/gctb/download/gctb_2.02_Linux.zip  && \
   unzip   gctb_2.02_Linux.zip && \
   rm -rf gctb_2.02_Linux.zip


mv gctb_2.02_Linux/* .
cp gctb /bin 

chmod 755 /bin/gctb
