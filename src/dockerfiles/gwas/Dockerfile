# gwas container
FROM 'ubuntu:20.04'

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN bash apt_get_essential.sh && \
    rm apt_get_essential.sh

# Plink
WORKDIR /tmp/plink
COPY /scripts/install_plink.sh /tmp/plink/
RUN bash /tmp/plink/install_plink.sh && \
    rm -rf /tmp/plink

# prsice
WORKDIR /tmp/prsice
COPY /scripts/install_prsice.sh /tmp/prsice/
RUN bash /tmp/prsice/install_prsice.sh && \
    rm -rf /tmp/prsice

# simu
WORKDIR /tmp/simu
COPY /scripts/install_simu.sh /tmp/simu/
RUN bash /tmp/simu/install_simu.sh && \
    rm -rf /tmp/simu

# Plink2
WORKDIR /tmp/plink2
COPY /scripts/install_plink2.sh /tmp/plink2/
RUN bash /tmp/plink2/install_plink2.sh && \
    rm -rf /tmp/plink2

# plink2-avx2
WORKDIR /tmp/plink2_avx2
COPY /scripts/install_plink2_avx2.sh /tmp/plink2_avx2/
RUN bash /tmp/plink2_avx2/install_plink2_avx2.sh && \
    rm -rf /tmp/plink2_avx2

# Bolt LMM
# RUN apt-get update && apt-get install -y  --no-install-recommends \
#     libboost-dev=1.71.0.0ubuntu2 \
#     libboost-iostreams-dev=1.71.0.0ubuntu2 \
#     libboost-program-options-dev=1.71.0.0ubuntu2 \
#     libmkl-dev=2020.0.166-1 \
#     libnlopt-cxx-dev=2.6.1-8ubuntu2 \
#     && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

WORKDIR /tools/bolt
COPY /scripts/install_bolt.sh /tools/bolt
COPY /scripts/bolt.Makefile.patch /tools/bolt/
RUN bash /tools/bolt/install_bolt.sh && \
    rm /tools/bolt/install_bolt.sh
ENV PATH="/tools/bolt:${PATH}"

# gcta
WORKDIR /tmp/gcta
COPY /scripts/install_gcta.sh /tmp/gcta/
RUN bash /tmp/gcta/install_gcta.sh && \
    rm -rf /tmp/gcta

# gctb
WORKDIR /tmp/gctb
COPY /scripts/install_gctb.sh /tmp/gctb/
RUN bash /tmp/gctb/install_gctb.sh && \
    rm -rf /tmp/gctb

# qctools
WORKDIR /tmp/qctools
COPY /scripts/install_qctools.sh /tmp/qctools/
RUN bash /tmp/qctools/install_qctools.sh && \
    rm -rf /tmp/qctools

# king
WORKDIR /tmp/king
COPY /scripts/install_king.sh /tmp/king/
RUN bash /tmp/king/install_king.sh && \
    rm -rf /tmp/king

# metal
WORKDIR /tmp/metal
COPY /scripts/install_metal.sh /tmp/metal/
RUN bash /tmp/metal/install_metal.sh && \
    rm -rf /tmp/metal

# vcftools
WORKDIR /tmp/vcftools
COPY /scripts/install_vcftools.sh /tmp/vcftools/
RUN bash /tmp/vcftools/install_vcftools.sh && \
    rm -rf /tmp/vcftools

# Bcftools (installs /tools/bcftools and /tools/htslib)
WORKDIR /tmp/bcftools/
COPY /scripts/install_bcftools.sh /tmp/bcftools/
RUN bash /tmp/bcftools/install_bcftools.sh && \
    rm -rf /tmp/bcftools

# flashpca
WORKDIR /tmp/flashpca
COPY /scripts/install_flashpca.sh /tmp/flashpca/
RUN bash /tmp/flashpca/install_flashpca.sh && \
    rm -rf /tmp/flashpca

# regenie
WORKDIR /tmp/regenie
COPY /scripts/install_regenie.sh /tmp/regenie/
RUN bash /tmp/regenie/install_regenie.sh && \
    rm -rf /tmp/regenie
# https://github.com/potree/PotreeConverter/issues/281
ENV LC_ALL="C"

# gwama
WORKDIR /tmp/gwama
COPY /scripts/install_gwama.sh /tmp/gwama/
RUN bash /tmp/gwama/install_gwama.sh && \
    rm -rf /tmp/gwama

# minimac4
WORKDIR /tmp/minimac4
COPY /scripts/install_minimac4.sh /tmp/minimac4/
RUN bash /tmp/minimac4/install_minimac4.sh && \
    rm -rf /tmp/minimac4

# bgenix, cat-bgen, edit-bgen
WORKDIR /tmp/bgenix
COPY /scripts/install_bgenix.sh /tmp/bgenix/
RUN bash /tmp/bgenix/install_bgenix.sh && \
    rm -rf /tmp/bgenix

# HTSlib + shapeit4
WORKDIR /tmp/shapeit4
COPY /scripts/install_shapeit4.sh /tmp/shapeit4/
RUN bash /tmp/shapeit4/install_shapeit4.sh && \
    rm -rf /tmp/shapeit4

WORKDIR /tools
