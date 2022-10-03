curl -sSL https://github.com/conda-forge/miniforge/releases/download/4.14.0-0/Miniforge3-4.14.0-0-Linux-x86_64.sh -o /tmp/miniforge3.sh \
  && mkdir /root/.conda \
  && bash /tmp/miniforge3.sh -bfp /usr/local \
  && rm -rf /tmp/miniforge3.sh

export PATH=$PATH:/opt/conda/bin

# stop complaints about outdated conda version
# conda update -n base -c defaults conda

# use correct channel ordering for bioconda
# conda config --add channels defaults
# conda config --add channels bioconda
# conda config --add channels conda-forge
# conda config --set channel_priority strict
