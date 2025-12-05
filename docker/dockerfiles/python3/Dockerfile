# gwas container
FROM ubuntu:24.04

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

WORKDIR /tmp
COPY /scripts/install_miniforge.sh .
RUN bash install_miniforge.sh && \
    rm install_miniforge.sh

RUN conda install mamba -n base -c conda-forge && \
    conda clean -a -y

# set up python env.
# keep the list of packages sorted alphabetically
# https://www.online-utility.org/text/sort.jsp
RUN mamba install python=3.12.12 \
    configparser=7.2.0 \
    dask=2025.11.0 \
    fastparquet=2024.11.0 \
    graphviz=14.0.5 \
    "h5py=3.15.1=nompi*" \
    jupyterlab=4.5.0 \
    lightgbm=4.6.0 \
    lifelines=0.30.0 \
    imbalanced-learn=0.14.0 \
    intervaltree=3.1.0 \
    matplotlib-venn=1.1.2 \
    matplotlib=3.10.8 \
    miniwdl=1.13.1 \
    miniwdl-slurm=0.4.0 \
    more-itertools=10.8.0 \
    networkx=3.6 \
    numdifftools=0.9.41 \
    numba=0.62.1 \
    numpy=2.3.5 \
    openpyxl=3.1.5 \
    pandas=2.3.3 \
    pandas-plink=2.3.2 \
    paramiko=4.0.0 \
    psutil=7.1.3 \
    pyarrow=22.0.0 \
    pydot=4.0.1 \
    pyreadstat=1.3.2 \
    pytables=3.10.2 \
    python-graphviz=0.21 \
    pyyaml=6.0.3 \
    scikit-learn=1.7.2 \
    scikit-survival=0.25.0 \
    scipy=1.16.3 \
    seaborn=0.13.2 \
    semantic_version=2.10.0 \
    shap=0.48.0 \
    statsmodels=0.14.5 \
    xgboost=3.1.2 \
    xlrd=2.0.2 \
    xmltodict=1.0.2 \
    --yes && \
    mamba clean -a -y

# pip install stuff in env.
RUN pip install --no-cache-dir --no-deps \
    bed-reader==1.0.6 \
    bgen-reader==4.0.9 \
    cbgen==1.0.6 \
    crc32c==2.8 \
    dxpy==0.400.1 \
    fastlmm==0.6.12 \
    hdf5storage==0.2.2 \
    LDpred==1.0.11 \
    Pgenlib==0.93.0 \
    plinkio==0.9.8 \
    plinkliftover==0.5.2 \
    poetry==2.2.1 \
    pooch==1.8.2 \
    pycap==2.7.0 \
    pyliftover==0.4.1 \
    pysnptools==0.5.14 && \
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

