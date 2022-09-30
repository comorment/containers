curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda3.sh \
  && mkdir /root/.conda \
  && bash /tmp/miniconda3.sh -bfp /usr/local \
  && rm -rf /tmp/miniconda3.sh

export PATH=$PATH:/opt/conda/bin

# stop complaints about outdated conda version
# conda update -n base -c defaults conda

# use correct channel ordering for bioconda
conda config --add channels defaults
conda config --add channels bioconda
conda config --add channels conda-forge
conda config --set channel_priority strict
