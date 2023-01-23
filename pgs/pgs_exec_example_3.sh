#!/bin/bash

# LDpred2-inf
python3 pgs_exec.py \
    --Sumstats_file '/REF/examples/ldpred2/trait1.sumstats.gz' \
    --Pheno_file '/REF/examples/ldpred2/simu.pheno' \
    --Geno_file '/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1' \
    --Output_dir 'PGS_synthetic_LDpred2_auto' \
    --runtype 'slurm' \
    'ldpred2-auto' \
    --file_keep_snps '/REF/hapmap3/w_hm3.justrs' \
    'fileGenoRDS' 'g1000_eur_chr21to22_hm3rnd1.rds' \
    'col_stat' 'BETA' \
    'col_stat_se' 'SE' \
    'stat_type' 'BETA' \
    'col-pheno' 'trait1' 'chr2use' '21,22' \
    'cores' '2'