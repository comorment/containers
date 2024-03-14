# gwas container
FROM 'ubuntu:20.04'

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

WORKDIR /tmp
COPY /scripts/install_mambaforge.sh .
RUN bash install_mambaforge.sh && \
    rm install_mambaforge.sh

WORKDIR /tools/GenoPred
RUN git clone  --depth 1 --branch v2.2.0 https://github.com/opain/GenoPred.git .

RUN conda env update -f /tools/GenoPred/pipeline/envs/pipeline.yaml

# set env variables
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate genopred" >> ~/.bashrc

RUN /bin/bash -c ". activate genopred && cd /tools/GenoPred/pipeline && snakemake --restart-times 3 -j 1 --use-conda --conda-frontend mamba get_dependencies"

# cleanup for smaller image size
RUN mamba clean -a -y
RUN pip cache purge 

WORKDIR /tools
 
