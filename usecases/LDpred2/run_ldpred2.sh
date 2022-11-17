#!/bin/bash

# Create shortcut environment variable for Rscript 
export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"

# Impute missing genotypes in $fileGeno
# impute.R is only for testing purposes and using the simplest imputation method in bigsnpr
if [ -f $fileImputedGeno ]; then rm $(basename $fileImputedGeno .bed).*; fi
$RSCRIPT impute.R $fileGeno $fileImputedGeno

# Generate PGS usign LDPRED-inf
$RSCRIPT ldpred2.R \
 --ldpred-mode inf \
 --file-keep-snps $fileKeepSNPS \
 --file-pheno $filePheno \
 --col-stat OR --col-stat-se SE \
 --stat-type OR \
 $fileImputedGeno $fileSumstats $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT ldpred2.R \
 --ldpred-mode auto \
 --file-keep-snps $fileKeepSNPS \
 --file-pheno $filePheno \
 --col-stat OR --col-stat-se SE \
 --stat-type OR \
 $fileImputedGeno $fileSumstats $fileOut.auto