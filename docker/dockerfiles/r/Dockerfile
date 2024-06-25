# R container
FROM rocker/verse:4.0.5

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

# deps for R packages
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    libperl-dev=5.30.0-9ubuntu0.5 \
    libgslcblas0=2.5+dfsg-6+deb10u1build0.20.04.1 \
    lmodern=2.004.5-6 \
    texlive-latex-extra=2019.202000218-1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# gcta (good to have this in R container because gsmr package uses gcta)
WORKDIR /tmp/gcta
COPY /scripts/install_gcta.sh /tmp/gcta/
RUN bash /tmp/gcta/install_gcta.sh && \
    rm -rf /tmp/gcta

# PRSice-2.
# The container running PRSice.R script with "--prsice PRSice_linux" 
# argument must also contain the PRSice_linux binary)
WORKDIR /tmp/prsice
COPY /scripts/install_prsice.sh /tmp/prsice/
RUN bash /tmp/prsice/install_prsice.sh && \
    rm -rf /tmp/prsice

# R packages.
# CRAN packages
WORKDIR /tmp/
RUN R -e "install.packages('devtools', version='2.4.5', repos='https://packagemanager.posit.co/cran/__linux__/focal/2023-02-16', dependencies=c('Depends', 'Imports', 'LinkingTo'))"
COPY /scripts/R/cran.R .
RUN Rscript cran.R

# Bioconductor distributed packages:
COPY /scripts/R/bioconductor.R .
RUN Rscript bioconductor.R

# GitHub distributed packages:
COPY /scripts/R/github.R .
RUN --mount=type=secret,id=github_pat \
    github_pat=$(cat /run/secrets/github_pat) \
    Rscript github.R

# Misc. packages
COPY /scripts/R/source.R .
RUN Rscript source.R && \
    rm -rf /tmp/*

WORKDIR /tools
