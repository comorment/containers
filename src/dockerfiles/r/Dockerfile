# R container
FROM rocker/verse:4.0.3

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    libperl-dev=5.30.0-9ubuntu0.3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# gcta (good to have this in R container because gsmr package uses gcta)
WORKDIR /tmp/gcta
COPY /scripts/install_gcta.sh /tmp/gcta/
RUN bash /tmp/gcta/install_gcta.sh && \
    rm -rf /tmp/gcta

# R packages.
# CRAN packages
RUN R -e "install.packages('devtools', version='2.4.4', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('rmarkdown', version='2.17', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('ggplot2', version='3.3.5', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('data.table', version='1.14.2', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('optparse', version='1.7.3', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('foreign', version='0.8-83', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('mvtnorm', version='1.1-3', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('remotes', version='2.4.2', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('survey', version='4.1-1', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('BiocManager', version='1.30.18', repos='http://cran.us.r-project.org')"
RUN R -e "require(devtools); install_version('qqman', version='0.1.8', repos='http://cran.us.r-project.org')"

# GitHub distributed packages:
RUN R -e "library(devtools); install_github('zhanxw/seqminer', ref='142204d1005553ea87e1740ff97f0286291e41f9')"
RUN R -e "library(devtools); install_github('dajiangliu/rareGWAMA', ref='72e962dae19dc07251244f6c33275ada189c2126')"
RUN R -e "library(devtools); install_github('GenomicSEM/GenomicSEM', ref='bcbbaffff5767acfc5c020409a4dc54fbf07876b')"
RUN R -e "library(devtools); install_github('MRCIEU/TwoSampleMR', ref='c174107cfd9ba47cf2f780849a263f37ac472a0e')"

# Misc. packages
RUN R -e "install.packages('http://cnsgenomics.com/software/gsmr/static/gsmr_1.0.9.tar.gz', repos=NULL, type='source')"
RUN R -e "BiocManager::install('snpStats', version='3.12')"  # installs snpStats_1.40.0. Version 3.12 refs to the Bioconductor package version.

WORKDIR /tools

