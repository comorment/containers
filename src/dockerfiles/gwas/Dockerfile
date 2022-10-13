# gwas container
FROM 'ubuntu:20.04'

ENV TZ=Europe
ENV DEBIAN_FRONTEND noninteractive

# Essential tools
WORKDIR /tmp
COPY /scripts/apt_get_essential.sh .
RUN chmod +x apt_get_essential.sh
RUN bash apt_get_essential.sh

# Plink
WORKDIR /tools/plink
COPY /scripts/install_plink.sh /tmp
RUN chmod +x /tmp/install_plink.sh
RUN bash /tmp/install_plink.sh

# prsice
WORKDIR /tools/prsice
COPY /scripts/install_prsice.sh /tmp
RUN chmod +x /tmp/install_prsice.sh
RUN bash /tmp/install_prsice.sh

# simu
WORKDIR /tools/simu
COPY /scripts/install_simu.sh /tmp
RUN chmod +x /tmp/install_simu.sh
RUN bash /tmp/install_simu.sh

# Plink2
WORKDIR /tools/plink2
COPY /scripts/install_plink2.sh /tmp
RUN chmod +x /tmp/install_plink2.sh
RUN bash /tmp/install_plink2.sh

# plink2-avx2
WORKDIR /tools/plink2_avx2
COPY /scripts/install_plink2_avx2.sh /tmp
RUN chmod +x /tmp/install_plink2_avx2.sh
RUN bash /tmp/install_plink2_avx2.sh

# Bolt LMM
WORKDIR /tools/bolt
COPY /scripts/install_bolt.sh /tmp
RUN chmod +x /tmp/install_bolt.sh
RUN bash /tmp/install_bolt.sh
ENV PATH="/tools/bolt:${PATH}"

# gcta
WORKDIR /tools/gcta
COPY /scripts/install_gcta.sh /tmp
RUN chmod +x /tmp/install_gcta.sh
RUN bash /tmp/install_gcta.sh

# gctb
WORKDIR /tools/gctb
COPY /scripts/install_gctb.sh /tmp
RUN chmod +x /tmp/install_gctb.sh
RUN bash /tmp/install_gctb.sh

# qctools
WORKDIR /tools/qctools
COPY /scripts/install_qctools.sh /tmp
RUN chmod +x /tmp/install_qctools.sh
RUN bash /tmp/install_qctools.sh

# king
WORKDIR /tools/king
COPY /scripts/install_king.sh /tmp
RUN chmod +x /tmp/install_king.sh
RUN bash /tmp/install_king.sh

# metal
WORKDIR /tools/metal
COPY /scripts/install_metal.sh /tmp
RUN chmod +x /tmp/install_metal.sh
RUN bash /tmp/install_metal.sh

# vcftools
WORKDIR /tools/vcftools
COPY /scripts/install_vcftools.sh /tmp
RUN chmod +x /tmp/install_vcftools.sh
RUN bash /tmp/install_vcftools.sh

# Bcftools (installes /tools/bcftools and /tools/htslib)
WORKDIR /tools
COPY /scripts/install_bcftools.sh /tmp
RUN chmod +x /tmp/install_bcftools.sh
RUN bash /tmp/install_bcftools.sh

# flashpca
WORKDIR /tools/flashpca
COPY /scripts/install_flashpca.sh /tmp
RUN chmod +x /tmp/install_flashpca.sh
RUN bash /tmp/install_flashpca.sh

# regenie
WORKDIR /tools/regenie
COPY /scripts/install_regenie.sh /tmp
RUN chmod +x /tmp/install_regenie.sh
RUN bash /tmp/install_regenie.sh
# https://github.com/potree/PotreeConverter/issues/281
ENV LC_ALL="C"

# gwama
WORKDIR /tools/gwama
COPY /scripts/install_gwama.sh /tmp
RUN chmod +x /tmp/install_gwama.sh
RUN bash /tmp/install_gwama.sh

# minimac4
WORKDIR /tools/
COPY /scripts/install_minimac4.sh /tmp
RUN chmod +x /tmp/install_minimac4.sh
RUN bash /tmp/install_minimac4.sh

# bgenix, cat-bgen, edit-bgen
WORKDIR /tools/
COPY /scripts/install_bgenix.sh /tmp
RUN chmod +x /tmp/install_bgenix.sh
RUN bash /tmp/install_bgenix.sh

# HTSlib + shapeit4
WORKDIR /tmp/shapeit4
COPY /scripts/install_shapeit4.sh .
RUN chmod +x install_shapeit4.sh
RUN ./install_shapeit4.sh

WORKDIR /tools
