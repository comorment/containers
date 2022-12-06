#!/bin/bash
## Note
# The script will echo output when an exit code does not equal the expected.
# But it seems that container errors are not captured
# Output is not echoed for an expected error

export LC_ALL=C # Silence container locale warning
# To run scripts for ldpred2 and others one needs to define some directories
export DIR_BASE=$( git rev-parse --show-toplevel )
export DIR_SIF=$DIR_BASE/singularity
export DIR_TESTS=$DIR_BASE/usecases/LDpred2_example
export DIR_SCRIPTS=$DIR_BASE/usecases/LDpred2
export DIR_REFERENCE=$DIR_BASE/reference

# Tutorial data
# Phenotypic data is part of bed file
export fileInputGeno=$DIR_BASE/usecases/LDpred2_tutorial/tutorial_data/public-data3.bed
export fileInputSumStats=$DIR_BASE/usecases/LDpred2_tutorial/tutorial_data/public-data3-sumstats.txt
export fileOutputSNPR=$DIR_TESTS/data/public-data3.rds

# Create shortcut environment variable for Rscript 
export RSCRIPT="singularity exec -B $DIR_BASE:$DIR_BASE -B $DIR_REFERENCE:/REF $DIR_SIF/r.sif Rscript"

# The different modes to run
LDPRED_MODES="inf"

echo "Testing RDS/backingfile creation"
### These two runs ensure that the backing file is created
### correctly wheter the uses specifies .rds or not
# Passing full name of $fileSNPR
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno $fileOutputSNPR )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Passing basename of $fileSNPR
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno $(dirname $fileOutputSNPR)/$(basename $fileOutputSNPR) )
if [ $? -eq 1 ]; then exit; fi

# Run with a genotype file that contains missing data
export fileInputGeno=/REF/examples/prsice2/EUR
export fileOutputSNPR=$DIR_TESTS/data/EUR.rds
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=$DIR_TESTS/output/height.score

dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno.bed $fileOutputSNPR )
if [ $? -eq 1 ]; then exit; fi

# Perform full runs
# Note that if files in --dir-genetic-maps do not exist, these will be downloaded. But I think error if the directory doesnt exist
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS --col-stat OR --col-stat-se SE --stat-type OR \
  --dir-genetic-maps $DIR_TESTS/maps --genetic-maps-type hapmap "

## TEST: Bad ldpred mode
dump=$( { $LDP --ldpred-mode infinite $fileOutputSNPR $fileSumstats $fileOut.inf; } 2>&1 )
if [ $? -eq 0 ]; then exit; fi

## TEST: Bad imputation mode
dump=$( { $LDP --ldpred-mode inf --geno-impute bad-mode $fileOutputSNPR $fileSumstats $fileOut.inf; } 2>&1 )
if [ $? -eq 0 ]; then exit; fi

## TEST: Sampling for LD estimation (~500 seems to be minimum for this data)
dump=$( { $LDP --ldpred-mode inf --geno-ld-sample 500 $fileOutputSNPR $fileSumstats $fileOut.inf; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

## TEST: Complete runs of --ldpred-mode given by $LDPRED_MODES
for MODE in $LDPRED_MODES; do
 echo "Testing mode $MODE"
 dump=$( { $LDP --ldpred-mode $MODE $fileOutputSNPR $fileSumstats $fileOut.inf; } 2>&1 )
 if [ $? -eq 1 ]; then echo "$dump"; exit; fi
 echo "$dump"
done
