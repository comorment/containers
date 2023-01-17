#!/bin bash


# PRSice-2
python3 pgs_exec.py \
    --Sumstats_file '/REF/examples/ldpred2/trait1.sumstats.gz' \  # common
    --Pheno_file '/REF/examples/ldpred2/simu.pheno' \
    --Input_dir '/REF/examples/ldpred2' \
    --Data_prefix 'g1000_eur_chr21to22_hm3rnd1' \
    --Output_dir 'PGS_synthetic_prsice2' \
    --runtype 'subprocess' \
    'prsice2' \  # method
    --Cov_file '/REF/examples/prsice2/EUR.cov' \  # method-specific
    --Eigenvec-file 'g1000_eur_chr21to22_hm3rnd1.eigenvec' \
    stat 'BETA' \  # keywords and arguments
    beta ''
