# demo container
FROM ubuntu:20.04

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

# Essential Tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

# Plink
WORKDIR /tmp/plink
COPY /scripts/install_plink.sh /tmp/plink/
RUN bash /tmp/plink/install_plink.sh && \
    rm -rf /tmp/plink

WORKDIR /tools
