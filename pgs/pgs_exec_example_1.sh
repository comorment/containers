#!/bin bash
python3 pgs_exec.py \
    --Sumstats_file '/REF/examples/ldpred2/trait1.sumstats.gz' \
    --Pheno_file '/REF/examples/ldpred2/simu.pheno' \
    --Input_dir '/REF/examples/ldpred2' \
    --Data_prefix 'g1000_eur_chr21to22_hm3rnd1' \
    --Output_dir 'PGS_synthetic_prsice2' \
    --method prsice2 \
    --runtype 'subprocess' \
    --Cov_file '/REF/examples/prsice2/EUR.cov' \
    --Eigenvec-file 'g1000_eur_chr21to22_hm3rnd1.eigenvec' \
    stat 'BETA' \
    beta ''