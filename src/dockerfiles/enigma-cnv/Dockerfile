# R container
FROM rocker/verse:3.3.1

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update --yes && \
  apt-get upgrade --yes && \
  apt-get install --yes \
    build-essential \
    libperl-dev

# R packages
RUN R -e "install.packages('rmarkdown')"
RUN R -e "install.packages('ggplot2')"
RUN R -e "install.packages('data.table')"
RUN R -e "install.packages('optparse')"
RUN R -e "install.packages('foreign')"




RUN R -e "setRepositories(ind=1:8); install.packages('devtools'); library(devtools); install_github('mbertalan/iPsychCNV')"


RUN wget https://github.com/WGLab/PennCNV/archive/v1.0.5.tar.gz

RUN tar xvfz v1.0.5.tar.gz

RUN rm v1.0.5.tar.gz

RUN mv /PennCNV-1.0.5 /opt

ENV PATH="/opt/PennCNV-1.0.5:${PATH}"
RUN cd /opt/PennCNV-1.0.5/kext && \
  make
