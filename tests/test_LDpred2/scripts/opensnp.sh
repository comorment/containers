# Set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT="$(dirname `git rev-parse --show-toplevel`)"
export SIF=$COMORMENT/containers/singularity
export REFERENCE=$COMORMENT/containers/reference
export LDPRED2_REF=$COMORMENT/ldpred2_ref
export OPENSNP=$COMORMENT/opensnp
export LC_ALL=C # Set locale (get warnings otherwise)
export SINGULARITY_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref,${OPENSNP}:/opensnp,${COMORMENT}:/comorment

# Point to LDpred2.R input/output files
export fileGeno=/opensnp/imputed/opensnp_hm3.bed
export fileGenoRDS=opensnp_hm3.rds
export fileSumstats=/opensnp/gwas/UKB_NEALELAB_2018_HEIGHT.GRCh37.hm3.gz
export fileOut=Height
export dirLDpred2=/comorment/containers/scripts/pgs/LDpred2

export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"

# convert genotype to LDpred2 format
$RSCRIPT $dirLDpred2/createBackingFile.R --file-input $fileGeno --file-output $fileGenoRDS

# impute
$RSCRIPT $dirLDpred2/imputeGenotypes.R --impute-simple mean0 --geno-file-rds $fileGenoRDS

# Generate PGS usign LDPRED-inf
$RSCRIPT $dirLDpred2/ldpred2.R \
 --ldpred-mode inf \
 --col-stat BETA \
 --col-stat-se SE \
 --stat-type BETA \
 --geno-file-rds $fileGenoRDS \
 --chr2use 21 22 \
 --sumstats $fileSumstats \
 --out $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT $dirLDpred2/ldpred2.R \
 --ldpred-mode auto \
 --col-stat BETA \
 --col-stat-se SE \
 --stat-type BETA \
 --geno-file-rds $fileGenoRDS \
  --chr2use 21 22 \
 --sumstats $fileSumstats \
 --out $fileOut.auto
 
