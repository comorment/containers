#!/bin/bash

# LDpred2-inf
python3 pgs_exec.py \
    --sumstats-file /REF/examples/ldpred2/trait1.sumstats.gz \
    --pheno-file /REF/examples/ldpred2/simu.pheno \
    --phenotype trait1 \
    --phenotype-class CONTINUOUS \
    --geno-file-prefix /REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1 \
    --output-dir output/PGS_synthetic_LDpred2_inf \
    --runtype sh \
    ldpred2-inf \
    --covariate-file /REF/examples/prsice2/EUR.cov \
    --eigenvec-file output/PGS_synthetic_LDpred2_inf/g1000_eur_chr21to22_hm3rnd1.eigenvec \
    --file-geno-rds output/PGS_synthetic_LDpred2_inf/g1000_eur_chr21to22_hm3rnd1.rds \
    file-keep-snps /REF/hapmap3/w_hm3.justrs \
    chr2use 21,22
    