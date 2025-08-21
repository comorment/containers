# gwas container
FROM ubuntu:24.04

ENV TZ=Europe
ENV DEBIAN_FRONTEND=noninteractive

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
WORKDIR /tools/bolt
COPY /scripts/install_bolt.sh /tools/bolt
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

# qctool
WORKDIR /tmp/qctool
COPY /scripts/install_qctools.sh /tmp/qctool/
RUN bash /tmp/qctool/install_qctools.sh && \
    rm -rf /tmp/qctool

# snptest
WORKDIR /tmp/snptest
COPY /scripts/install_snptest.sh /tmp/snptest/
RUN bash /tmp/snptest/install_snptest.sh && \
    rm -rf /tmp/snptest

# king
WORKDIR /tmp/king
COPY /scripts/install_king.sh /tmp/king/
RUN bash /tmp/king/install_king.sh && \
    rm -rf /tmp/king

# ldak
WORKDIR /tmp/ldak
COPY /scripts/install_ldak.sh /tmp/ldak/
RUN bash /tmp/ldak/install_ldak.sh && \
    rm -rf /tmp/ldak

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

# HTSlib (dependency for bcftools & shapeit4++)
WORKDIR /tmp/htslib
COPY /scripts/install_htslib.sh /tmp/htslib/
RUN bash /tmp/htslib/install_htslib.sh && \
    rm -rf /tmp/htslib

# Bcftools
WORKDIR /tmp/bcftools/
COPY /scripts/install_bcftools.sh /tmp/bcftools/
RUN bash /tmp/bcftools/install_bcftools.sh && \
    rm -rf /tmp/bcftools

# flashpca
WORKDIR /tmp/flashpca
COPY /scripts/install_flashpca.sh /tmp/flashpca/
RUN bash /tmp/flashpca/install_flashpca.sh && \
    rm -rf /tmp/flashpca

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

# regenie (install after bgenix)
WORKDIR /tmp/regenie
COPY /scripts/install_regenie.sh /tmp/regenie/
RUN bash /tmp/regenie/install_regenie.sh && \
    rm -rf /tmp/regenie
# https://github.com/potree/PotreeConverter/issues/281
ENV LC_ALL="C"

# shapeit4
WORKDIR /tmp/shapeit4
COPY /scripts/install_shapeit4.sh /tmp/shapeit4/
COPY /scripts/patches/shapeit4.makefile.diff /tmp/shapeit4/
RUN bash /tmp/shapeit4/install_shapeit4.sh && \
    rm -rf /tmp/shapeit4

# shapeit5
WORKDIR /tmp/shapeit5
COPY /scripts/install_shapeit5.sh /tmp/shapeit5/
COPY /scripts/patches/shapeit5.diff /tmp/shapeit5/
COPY /scripts/patches/xcftools.diff /tmp/shapeit5/
RUN bash /tmp/shapeit5/install_shapeit5.sh && \
    rm -rf /tmp/shapeit5

# eagle
WORKDIR /tmp/eagle
COPY /scripts/patches/eagle.diff /tmp/eagle/
COPY /scripts/install_eagle.sh /tmp/eagle/
RUN bash /tmp/eagle/install_eagle.sh && \
    rm -rf /tmp/eagle

# switchError
WORKDIR /tmp/switchError
COPY /scripts/patches/switchError.diff /tmp/switchError//
COPY /scripts/install_switchError.sh /tmp/switchError/
RUN bash /tmp/switchError/install_switchError.sh && \
    rm -rf /tmp/switchError

# beagle
WORKDIR /tmp/beagle
COPY /scripts/install_beagle.sh /tmp/beagle/
COPY /scripts/stub.sh /tmp/beagle/
RUN bash /tmp/beagle/install_beagle.sh && \
    rm -rf /tmp/beagle

# duohmm
WORKDIR /tmp/duohmm
COPY /scripts/install_duohmm.sh /tmp/duohmm/
RUN bash /tmp/duohmm/install_duohmm.sh && \
    rm -rf /tmp/duohmm

# samtools
WORKDIR /tmp/samtools
COPY /scripts/install_samtools.sh /tmp/samtools/
RUN bash /tmp/samtools/install_samtools.sh && \
    rm -rf /tmp/samtools

# bedtools
WORKDIR /tmp/bedtools
COPY /scripts/install_bedtools.sh /tmp/bedtools/
RUN bash /tmp/bedtools/install_bedtools.sh && \
    rm -rf /tmp/bedtools

# liftOver
WORKDIR /tmp/liftover
COPY /scripts/install_liftover.sh /tmp/liftover/
RUN bash /tmp/liftover/install_liftover.sh && \
    rm -rf /tmp/liftover

WORKDIR /tools
