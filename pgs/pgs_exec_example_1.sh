#!/bin bash

# PRSice-2
python3 pgs_exec.py \
    --Sumstats_file /REF/examples/ldpred2/trait1.sumstats.gz \
    --Pheno_file /REF/examples/ldpred2/simu.pheno \
    --Phenotype trait1 \
    --Phenotype_class CONTINUOUS \
    --Geno_file /REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1 \
    --Output_dir output/PGS_synthetic_prsice2 \
    --runtype subprocess \
    prsice2 \
    --Cov_file /REF/examples/prsice2/EUR.cov \
    --Eigenvec-file g1000_eur_chr21to22_hm3rnd1.eigenvec
