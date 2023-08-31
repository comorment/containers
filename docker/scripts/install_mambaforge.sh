curl -sSL https://github.com/conda-forge/miniforge/releases/download/4.14.0-0/Mambaforge-4.14.0-0-$(uname)-$(uname -m).sh -o /tmp/mambaforge.sh \
  && mkdir /root/.conda \
  && bash /tmp/mambaforge.sh -bfp /usr/local \
  && rm -rf /tmp/mambaforge.sh

export PATH=$PATH:/opt/conda/bin
