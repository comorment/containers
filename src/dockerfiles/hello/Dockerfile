# demo container
FROM 'ubuntu:18.04'

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential Tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN chmod +x apt_get_essential.sh
RUN bash apt_get_essential.sh

# Plink
WORKDIR /tools/plink
COPY /scripts/install_plink.sh /tmp
RUN chmod +x /tmp/install_plink.sh
RUN bash /tmp/install_plink.sh

WORKDIR /tools
