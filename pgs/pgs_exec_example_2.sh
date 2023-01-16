#!/bin/bash

# LDpred2-inf
python3 pgs_exec.py \
    --Sumstats_file '/REF/examples/ldpred2/trait1.sumstats.gz' \
    --Pheno_file '/REF/examples/ldpred2/simu.pheno' \
    --Input_dir '' \
    --Data_prefix 'g1000_eur_chr21to22_hm3rnd1' \
    --Output_dir 'PGS_synthetic_LDpred2_inf' \
    --runtype 'sh' \
    'ldpred2-inf' \
    'fileGeno' '/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1.bed' \
    'fileGenoRDS' 'g1000_eur_chr21to22_hm3rnd1.rds' \
    'col_stat' 'BETA' \
    'col_stat_se' 'SE' \
    'stat_type' 'BETA' \
    'col-pheno' 'trait1' 'chr2use' '21,22' \
    'cores' '2'