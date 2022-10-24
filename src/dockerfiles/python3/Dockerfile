# gwas container
FROM 'ubuntu:20.04'

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN chmod +x apt_get_essential.sh
RUN bash apt_get_essential.sh

WORKDIR /tmp
COPY /scripts/install_mambaforge.sh .
RUN chmod +x install_mambaforge.sh
RUN bash install_mambaforge.sh

# set up python env.
RUN mamba install python=3.10.6 \
    numpy=1.23.3 \
    scipy=1.9.1 \
    pandas=1.5.0 \
    statsmodels=0.13.2 \
    matplotlib=3.6.0 \
    seaborn=0.12.0 \
    pyyaml=6.0 \
    jupyterlab=3.4.8 \
    matplotlib-venn=0.11.5 \
    numdifftools=0.9.39 \
    lifelines=0.27.0 \
    pyreadstat=1.1.9 \
    xlrd=2.0.1 \
    "h5py=3.7.0=nompi*" \
    semantic_version=2.10.0 \
    --yes
# RUN conda install -c conda-forge bgenix  # don't include accd. to @ofrei
# RUN conda install -c bioconda htslib  # don't include accd. to @ofrei

# pip install stuff in env.
RUN pip install --no-cache-dir plinkio==0.9.8 \
    pip install --no-cache-dir LDpred==1.0.11 \
    pip install --no-cache-dir pycap==2.1.0

# Plink (as python_convert depends on plink)
WORKDIR /tools/plink
COPY /scripts/install_plink.sh /tmp
RUN chmod +x /tmp/install_plink.sh
RUN bash /tmp/install_plink.sh

# python_convert script(s)
WORKDIR /tools/python_convert
RUN git clone https://github.com/precimed/python_convert.git . && \
    git reset --hard bcde562f0286f3ff271dbb54d486d4ca1d40ae36

# ukb script(s)
WORKDIR /tools/ukb
RUN git clone https://github.com/precimed/ukb.git . && \
    git reset --hard dc57e0d8380cd9b2eca479dc6f181d76ca5a429a

# cleanup for smaller image size
RUN mamba clean -a -y
RUN pip cache purge 

WORKDIR /tools
 
