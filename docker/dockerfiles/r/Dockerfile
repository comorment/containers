# R container
FROM ghcr.io/rocker-org/verse:4.5.1
# based on Ubuntu 24.04 LTS (noble)

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

# Essential tools
WORKDIR /tmp

# deps for R packages; 
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    apt-utils=2.8.3 \
    ca-certificates=20240203 && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl=8.5.0-2ubuntu10.6 \
    libperl-dev=5.38.2-3.2ubuntu0.2 \
    libgslcblas0=2.7.1+dfsg-6ubuntu2 \
    lmodern=2.005-1 \
    texlive-latex-extra=2023.20240207-1 && \
    wget=1.21.4-1ubuntu4.1 \
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
RUN R -e "install.packages('devtools', repos='https://packagemanager.posit.co/cran/__linux__/noble/2025-08-01', dependencies=c('Depends', 'Imports', 'LinkingTo'))"
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

# Misc. binaries
# PRSice-2.
# The container running PRSice.R script with "--prsice PRSice_linux" 
# argument must also contain the PRSice_linux binary)
WORKDIR /tmp/prsice
COPY /scripts/install_prsice.sh /tmp/prsice/
RUN bash /tmp/prsice/install_prsice.sh && \
    rm -rf /tmp/prsice


WORKDIR /tools
