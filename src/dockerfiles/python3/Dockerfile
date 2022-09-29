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
COPY /scripts/install_miniconda3.sh .
RUN chmod +x install_miniconda3.sh
RUN bash install_miniconda3.sh

RUN conda install python=3.8 --yes
RUN conda install -c conda-forge jupyterlab --yes
RUN conda install numpy scipy pandas statsmodels matplotlib seaborn --yes
RUN conda install -c conda-forge matplotlib-venn numdifftools lifelines --yes
RUN conda install -c conda-forge bgenix
RUN conda install -c bioconda htslib

# Plink (as python_convert depends on plink)
WORKDIR /tools/plink
COPY /scripts/install_plink.sh /tmp
RUN chmod +x /tmp/install_plink.sh
RUN bash /tmp/install_plink.sh

WORKDIR /tools
COPY /scripts/install_mixer.sh /tmp
RUN chmod +x /tmp/install_mixer.sh
RUN bash /tmp/install_mixer.sh
ENV BGMG_SHARED_LIBRARY="/tools/mixer/src/build/lib/libbgmg.so"

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

RUN conda install -c conda-forge pyyaml --yes

WORKDIR /tools
 
