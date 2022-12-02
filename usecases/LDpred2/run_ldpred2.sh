#!/bin/bash

# Create shortcut environment variable for Rscript 
export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"

# Convert plink files to bigSNPR backingfile(s) (.rds/.bk)
$RSCRIPT $CONTAINERS/usecases/LDpred2/createBackingFile.R $fileGeno $fileGenoRDS

# Generate PGS usign LDPRED-inf
$RSCRIPT ldpred2.R \
 --ldpred-mode inf \
 --file-keep-snps $fileKeepSNPS \
 --file-pheno $filePheno \
 --col-stat OR --col-stat-se SE \
 --stat-type OR \
 $fileGenoRDS $fileSumstats $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT ldpred2.R \
 --ldpred-mode auto \
 --file-keep-snps $fileKeepSNPS \
 --file-pheno $filePheno \
 --col-stat OR --col-stat-se SE \
 --stat-type OR \
 $fileGenoRDS $fileSumstats $fileOut.auto
