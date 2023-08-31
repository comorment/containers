curl -sSL https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -o /tmp/miniconda2.sh \
  && mkdir /root/.conda \
  && bash /tmp/miniconda2.sh -bfp /usr/local \
  && rm -rf /tmp/miniconda2.sh

export PATH=$PATH:/opt/conda/bin
