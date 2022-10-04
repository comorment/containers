curl -sSL https://github.com/conda-forge/miniforge/releases/download/4.14.0-0/Miniforge3-4.14.0-0-$(uname)-$(uname -m).sh -o /tmp/miniforge3.sh \
  && mkdir /root/.conda \
  && bash /tmp/miniforge3.sh -bfp /usr/local \
  && rm -rf /tmp/miniforge3.sh

export PATH=$PATH:/opt/conda/bin
