# gwas container
FROM ubuntu:20.04

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

WORKDIR /tmp
COPY /scripts/install_mambaforge.sh .
RUN bash install_mambaforge.sh && \
    rm install_mambaforge.sh

# set up python env.
# keep the list of packages sorted alphabetically
# https://www.online-utility.org/text/sort.jsp
RUN mamba install python=3.10.6 \
    configparser=7.0.0 \
    dask=2023.3.0 \
    fastparquet=2024.11.0 \
    graphviz=12.2.1 \
    "h5py=3.7.0=nompi*" \
    jupyterlab=3.4.8 \
    lightgbm=4.5.0 \
    lifelines=0.27.0 \
    imbalanced-learn=0.12.3 \
    intervaltree=3.1.0 \
    matplotlib-venn=0.11.5 \
    matplotlib=3.6.0 \
    miniwdl=1.12.1 \
    miniwdl-slurm=0.2.0 \
    more-itertools=9.0.0 \
    numdifftools=0.9.39 \
    numba=0.60.0 \
    numpy=1.23.3 \
    openpyxl=3.1.5 \
    pandas=2.2.3 \
    pandas-plink=2.2.9 \
    paramiko \
    psutil=5.9.3 \
    pyarrow=19.0.1 \
    pydot=3.0.4 \
    pyreadstat=1.2.7 \
    pytables=3.7.0 \
    python-graphviz=0.20.3 \
    pyyaml=6.0 \
    scikit-learn=1.5.2 \
    scikit-survival=0.23.0 \
    scipy=1.9.1 \
    seaborn=0.13.2 \
    semantic_version=2.10.0 \
    shap=0.46.0 \
    statsmodels=0.13.2 \
    xgboost=2.1.4 \
    xlrd=2.0.1 \
    xmltodict=0.13.0 \
    --yes && \
    mamba clean -a -y

# pip install stuff in env.
RUN pip install --no-cache-dir cbgen==1.0.2 && \
    pip install --no-cache-dir bgen-reader==4.0.8 && \
    pip install --no-cache-dir bed-reader==0.2.24 && \
    pip install --no-cache-dir dxpy==0.383.1 && \
    pip install --no-cache-dir pysnptools==0.5.7 && \
    pip install --no-cache-dir fastlmm==0.6.3 && \
    pip install --no-cache-dir plinkio==0.9.8 && \
    pip install --no-cache-dir LDpred==1.0.11 && \
    pip install --no-cache-dir pycap==2.1.0 && \
    pip install --no-cache-dir pyliftover==0.4.1 && \
    pip cache purge 

# Plink (as python_convert depends on plink)
WORKDIR /tmp/plink
COPY /scripts/install_plink.sh /tmp/plink/
RUN bash /tmp/plink/install_plink.sh && \
    rm -rf /tmp/plink

# Plink2
WORKDIR /tmp/plink2
COPY /scripts/install_plink2.sh /tmp/plink2/
RUN bash /tmp/plink2/install_plink2.sh && \
    rm -rf /tmp/plink2

# python_convert script(s)
WORKDIR /tools/python_convert
RUN git clone https://github.com/precimed/python_convert.git . && \
    git reset --hard bcde562f0286f3ff271dbb54d486d4ca1d40ae36

# ukb script(s)
WORKDIR /tools/ukb
RUN git clone https://github.com/precimed/ukb.git . && \
    git reset --hard dc57e0d8380cd9b2eca479dc6f181d76ca5a429a

# PRSice_linux binary (useful)
WORKDIR /tmp/prsice
COPY /scripts/install_prsice.sh /tmp/prsice/
RUN bash /tmp/prsice/install_prsice.sh && \
    rm -rf /tmp/prsice

WORKDIR /tools

# https://github.com/comorment/containers/issues/267:
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
 
