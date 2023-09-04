#!/bin bash

# PRSice-2
python3 pgs_exec.py \
    --sumstats-file /REF/examples/ldpred2/trait1.sumstats.gz \
    --pheno-file /REF/examples/ldpred2/simu.pheno \
    --phenotype trait1 \
    --phenotype-class CONTINUOUS \
    --geno-file-prefix /REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1 \
    --output-dir output/PGS_synthetic_prsice2 \
    --runtype subprocess \
    prsice2 \
    --covariate-file /REF/examples/prsice2/EUR.cov \
    --eigenvec-file output/PGS_synthetic_prsice2/g1000_eur_chr21to22_hm3rnd1.eigenvec
