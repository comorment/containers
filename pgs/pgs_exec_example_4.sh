#!/bin/bash

# LDpred-2
python3 pgs_exec.py \
    --Sumstats_file '/MOBA/out/run10_regenie_height_8y_rint.gz' \
    --Pheno_file '/MOBA/master_file.csv' \
    --Phenotype 'height_8y_rint' \
    --Geno_file '/MOBA/MoBaPsychGen_v1-500kSNPs-child' \
    --Output_dir 'results/PGS_MoBa_LDpred2_inf' \
    --runtype 'slurm' \
    'ldpred2-auto' \
    --Cov_file 'results/PGS_MoBa_LDpred2_inf/master_file.cov' \
    --Eigenvec-file 'results/PGS_MoBa_LDpred2_inf/master_file.eigenvec' \
    'fileGenoRDS' 'MoBaPsychGen_v1-500kSNPs-child.rds' \
    'col-pheno' 'height_8y_rint'
    

