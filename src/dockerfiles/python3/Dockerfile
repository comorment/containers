# gwas container
FROM 'ubuntu:18.04'

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN chmod +x apt_get_essential.sh
RUN bash apt_get_essential.sh

WORKDIR /tmp
COPY /scripts/install_miniforge3.sh .
RUN chmod +x install_miniforge3.sh
RUN bash install_miniforge3.sh

# set up python env.
RUN conda install python=3.10 \
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
    lifelines --yes
#RUN conda install -c conda-forge jupyterlab matplotlib-venn numdifftools lifelines --yes
# RUN conda install -c conda-forge bgenix  # don't include accd. to Alex
# RUN conda install -c bioconda htslib  # don't include accd. to Alex

# Plink (as python_convert depends on plink)
WORKDIR /tools/plink
COPY /scripts/install_plink.sh /tmp
RUN chmod +x /tmp/install_plink.sh
RUN bash /tmp/install_plink.sh

# python_convert script(s)
WORKDIR /tools/python_convert
RUN git clone https://github.com/precimed/python_convert.git . && git reset --hard bcde562f0286f3ff271dbb54d486d4ca1d40ae36

WORKDIR /tools/ukb
RUN git clone https://github.com/precimed/ukb.git

RUN yes | pip install pyreadstat
RUN yes | pip install xlrd
RUN yes | pip install plinkio
RUN yes | pip install ldpred
RUN yes | pip install h5py
RUN yes | pip install pycap

WORKDIR /tools
 
