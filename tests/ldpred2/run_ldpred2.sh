#!/bin/bash
fileGeno=../../reference/examples/prsice2/EUR.bed
fileImputedGeno=EUR.imputed.bed
filePheno=../../reference/examples/prsice2/EUR.height
fileKeepSNPS=../../reference/ldsc/w_hm3.justrs
fileSumstats=Height.gwas.txt
fileOut=test.score

# Impute missing genotypes in $fileGeno
# impute.R is only for testing purposes and using the simplest imputation method in bigsnpr
if [ -f $fileImputedGeno ]; then rm $(basename $fileImputedGeno .bed).*; fi
singularity exec ldpred2.sif Rscript impute.R $fileGeno $fileImputedGeno

# Generate PGS usign LDPRED-inf
singularity exec ldpred2.sif Rscript ldpred2.R \
 --ldpred-mode inf \
 --file-keep-snps $fileKeepSNPS \
 --file-pheno $filePheno \
 --col-stat OR --col-stat-se SE \
 --stat-type OR \
 $fileImputedGeno $fileSumstats $fileOut.inf

# Generate PGS using LDPRED2-auto
singularity exec ldpred2.sif Rscript ldpred2.R \
 --ldpred-mode auto \
 --file-keep-snps $fileKeepSNPS \
 --file-pheno $filePheno \
 --col-stat OR --col-stat-se SE \
 --stat-type OR \
 $fileImputedGeno $fileSumstats $fileOut.auto