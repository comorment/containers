#!/bin/sh

apt-get update && apt-get install -y r-base 

# build R from source
wget https://cran.r-project.org/src/base/R-4/R-4.0.3.tar.gz && tar -xvzf R-4.0.3.tar.gz && cd R-4.0.3
./configure
make -j6
make install

echo "local({
  r <- getOption('repos')
  r['CRAN'] <- 'http://cran.r-project.org'
  options(repos = r)
})" >> ~/.Rprofile
