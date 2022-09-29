curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda3.sh \
  && mkdir /root/.conda \
  && bash /tmp/miniconda3.sh -bfp /usr/local \
  && rm -rf /tmp/miniconda3.sh

export PATH=$PATH:/opt/conda/bin
