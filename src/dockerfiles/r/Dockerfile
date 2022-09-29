# R container
FROM rocker/verse:4.0.3

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN chmod +x apt_get_essential.sh
RUN bash apt_get_essential.sh

RUN apt-get update -y && apt-get install -y libperl-dev

# R packages
RUN R -e "install.packages('rmarkdown')"
RUN R -e "install.packages('ggplot2')"
RUN R -e "install.packages('data.table')"
RUN R -e "install.packages('optparse')"
RUN R -e "install.packages('foreign')"
RUN R -e "install.packages('mvtnorm')"

RUN R -e "setRepositories(ind=1:8); install.packages('devtools')"

RUN R -e "library(devtools); install_github('zhanxw/seqminer')"
RUN R -e "library(devtools); install_github('dajiangliu/rareGWAMA')"
RUN R -e "library(devtools); install_github('GenomicSEM/GenomicSEM')"

RUN R -e "install.packages('remotes')"
RUN R -e "remotes::install_github('MRCIEU/TwoSampleMR')"

RUN R -e "install.packages('survey')"
RUN R -e "install.packages('http://cnsgenomics.com/software/gsmr/static/gsmr_1.0.9.tar.gz',repos=NULL,type='source')"

# gcta (good to have this in R container because gsmr package uses gcta)
WORKDIR /tools/gcta
COPY /scripts/install_gcta.sh /tmp
RUN chmod +x /tmp/install_gcta.sh
RUN bash /tmp/install_gcta.sh

RUN R -e "install.packages('BiocManager')"
RUN R -e "BiocManager::install('snpStats')"
RUN R -e "devtools::install_git('https://github.com/josefin-werme/LAVA.git')"

WORKDIR /tools/
COPY /scripts/install_lava_partitioning.sh /tmp
RUN chmod +x /tmp/install_lava_partitioning.sh
RUN bash /tmp/install_lava_partitioning.sh

RUN R -e "install.packages('qqman')"

WORKDIR /tools

