# R container
FROM rocker/verse:4.3.3
# based on Ubuntu 22.04.5 LTS (jammy)

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

# Essential tools
WORKDIR /tmp

# deps for R packages; 
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    apt-utils=2.4.13 \
    ca-certificates=20240203~22.04.1 && \
    update-ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl=7.81.0-1ubuntu1.18 \
    libperl-dev=5.34.0-3ubuntu1.3 \
    libgslcblas0=2.7.1+dfsg-3 \
    lmodern=2.004.5-6.1 \
    texlive-latex-extra=2021.20220204-1 && \
    wget=1.21.2-2ubuntu1.1 \
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
RUN R -e "install.packages('devtools', repos='https://packagemanager.posit.co/cran/__linux__/jammy/2024-09-01', dependencies=c('Depends', 'Imports', 'LinkingTo'))"
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
