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
RUN mamba install python=3.10 \
    numpy \
    scipy \
    pandas \
    statsmodels \
    matplotlib \
    seaborn \
    pyyaml \
    jupyterlab \
    matplotlib-venn \
    numdifftools \
    lifelines \
    pyreadstat \
    xlrd \
    "h5py=3.7.0=nompi*" \
    semantic_version \
    --yes
# RUN conda install -c conda-forge bgenix  # don't include accd. to @ofrei
# RUN conda install -c bioconda htslib  # don't include accd. to @ofrei

# Plink (as python_convert depends on plink)
WORKDIR /tools/plink
COPY /scripts/install_plink.sh /tmp
RUN chmod +x /tmp/install_plink.sh
RUN bash /tmp/install_plink.sh

# python_convert script(s)
WORKDIR /tools/python_convert
RUN git clone https://github.com/precimed/python_convert.git . && git reset --hard bcde562f0286f3ff271dbb54d486d4ca1d40ae36

# ukb script(s)
WORKDIR /tools/ukb
RUN git clone https://github.com/precimed/ukb.git

RUN yes | pip install plinkio  
RUN yes | pip install ldpred
RUN yes | pip install pycap

# cleanup for smaller image size
RUN mamba clean -a -y
RUN pip cache purge 


WORKDIR /tools
 
