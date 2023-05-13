#!/bin/bash
## Note
# 	- The script will echo output when an exit code does not equal the expected.
# 	- But it seems that container errors are not captured
# 	- Output is not echoed for an expected error
# 	- There is a warning produced for the tutorial data:
# Warning message:
# In merge.data.table(as.data.table(sumstats4), as.data.table(info_snp),  :
#   column names 'pos.ss' are duplicated in the result
# This is likely due to that in the tutorial data, genomic positions are provided
# in the genotype data and this causes a duplication when these positions are merged
# once again during certain tests.

export LC_ALL=C # Silence container locale warning
# To run scripts for ldpred2 and others one needs to define some directories
export DIR_BASE=$( git rev-parse --show-toplevel )
export DIR_SIF=$DIR_BASE/singularity
export DIR_TESTS=$DIR_BASE/tests/test_LDpred2
export DIR_DATA=$DIR_TESTS/data
export DIR_SCRIPTS=$DIR_BASE/scripts/pgs/LDpred2
export DIR_REFERENCE=$DIR_BASE/reference
# The location of the comorment/ldpred2_ref repository that containts LD matrixes
export DIR_REF_LDPRED=$DIR_BASE/../ldpred2_ref

# Tutorial data
# Phenotypic data is part of public-data3.fam file
export fileInputGeno=$DIR_DATA/tutorial_data/public-data3.bed
export fileInputSumStats=$DIR_DATA/tutorial_data/public-data3-sumstats.txt
export fileOutputSNPR=$DIR_DATA/public-data3.rds
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs
export fileOut=$DIR_TESTS/output/public-data.score

### For imputation testing
# Copy some plink files
cp $DIR_REFERENCE/examples/prsice2/EUR.bed $DIR_DATA/
cp $DIR_REFERENCE/examples/prsice2/EUR.bim $DIR_DATA/
cp $DIR_REFERENCE/examples/prsice2/EUR.fam $DIR_DATA/
# File to impute
fileImpute=$DIR_DATA/EUR
# Imputed file
fileImputed=$DIR_DATA/EUR_imputed


# Create shortcut environment variable for Rscript 
export RSCRIPT="singularity exec -B $DIR_BASE:$DIR_BASE -B $DIR_REF_LDPRED:/ldpred2_ref -B $DIR_REFERENCE:/REF $DIR_SIF/r.sif Rscript"

# The different modes to run (affects runs of scripts/extended.sh)
LDPRED_MODES="inf auto"

echo "### Running R function unittests"
$RSCRIPT $DIR_TESTS/unittest/fun.R

echo "### Testing sumstats scripts"
source $DIR_TESTS/scripts/sumstats.sh

echo "### Testing RDS/backingfile creation"
source $DIR_TESTS/scripts/backingfile.sh

echo "### Testing tutorial data"
source $DIR_TESTS/scripts/tutorial.sh

echo "### Testing imputation"
source $DIR_TESTS/scripts/imputation.sh

echo "### Testing ldpred2.R (various options, manually downloaded LD, output merge)"
source $DIR_TESTS/scripts/extended.sh
