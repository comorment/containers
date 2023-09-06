#!/bin/bash

# LDpred-2
python3 pgs_exec.py \
    --config config_p697.yaml \
    --sumstats-file /MOBA/out/run10_regenie_height_8y_rint.gz \
    --pheno-file /MOBA/master_file.csv \
    --phenotype height_8y_rint \
    --phenotype-class CONTINUOUS \
    --geno-file-prefix /MOBA/MoBaPsychGen_v1-500kSNPs-child \
    --output-dir output/PGS_MoBa_LDpred2_auto \
    --runtype slurm \
    ldpred2-auto \
    --covariate-file output/PGS_MoBa_LDpred2_auto/master_file.cov \
    --eigenvec-file output/PGS_MoBa_LDpred2_auto/master_file.eigenvec \
    fileGenoRDS MoBaPsychGen_v1-500kSNPs-child.rds
    

