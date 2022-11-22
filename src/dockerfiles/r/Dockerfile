# R container
FROM rocker/verse:4.0.5

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

# deps for R packages
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    libperl-dev=5.30.0-9ubuntu0.3 \
    libgslcblas0=2.5+dfsg-6build1 \
    lmodern=2.004.5-6 \
    texlive-latex-extra=2019.202000218-1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# gcta (good to have this in R container because gsmr package uses gcta)
WORKDIR /tmp/gcta
COPY /scripts/install_gcta.sh /tmp/gcta/
RUN bash /tmp/gcta/install_gcta.sh && \
    rm -rf /tmp/gcta

# R packages.
# CRAN packages
WORKDIR /tmp/
RUN R -e "install.packages('devtools', version='2.4.5', repos='https://cloud.r-project.org', dependencies=TRUE)"
COPY /scripts/R/cran.R .
RUN Rscript cran.R

# GitHub distributed packages:
COPY /scripts/R/github.R .
RUN Rscript github.R

# Misc. packages
COPY /scripts/R/misc.R .
RUN Rscript misc.R

# PRSice-2.
# The container running PRSice.R script with "--prsice PRSice_linux" 
# argument must also contain the PRSice_linux binary)
WORKDIR /tmp/prsice
COPY /scripts/install_prsice.sh /tmp/prsice/
RUN bash /tmp/prsice/install_prsice.sh && \
    rm -rf /tmp/prsice

WORKDIR /tools
