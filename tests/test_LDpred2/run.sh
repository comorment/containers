#!/bin/bash
##################################################
### Unit- and end-to-end tests of scripts related 
### to bigsnpr R-package (mainly LDpred2)
##################################################

## Notes
# 	- The script will echo output when an exit code does not equal the expected.
#		This does not include warnings.
# 	- It seems that container errors are not captured
# 	- There is a warning produced for the tutorial data:
# Warning message:
# In merge.data.table(as.data.table(sumstats4), as.data.table(info_snp),  :
#   column names 'pos.ss' are duplicated in the result
# This is likely due to that in the tutorial data, genomic positions are provided
# in the genotype data and this causes a duplication when these positions are merged
# once again during certain tests.

### End-to-end tests
# Tests make use of functions defined in scripts/functions.sh
# Unexpected exception: testSuccess command arg1 arg2 ...
# Exception expected: testException command arg1 arg2 ...

### Unittests
# These files are located in unittests/ and are named after which file they
# test. For example tests/test_LDpred2/unittests/fun.R tests R functions defined in
# scripts/pgs/ldpred2/fun.R while tests/test_LDpred2/unittests/tutorial.R
# tests output from tests/test_LDpred2/scripts/tutorial.sh

##################################################
### Environment/function definitions             
##################################################
timeStart=$(date +%s)

export LC_ALL=C # Silence container locale warning
# To run scripts for ldpred2 and others one needs to define some directories
export DIR_BASE=$( git rev-parse --show-toplevel )
export DIR_SIF=$DIR_BASE/singularity
export DIR_TESTS=$DIR_BASE/tests/test_LDpred2
export DIR_TEMP=$DIR_TESTS/temp
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

# BGEN files
export fileBGEN=$DIR_DATA/example.bgen
export fileBGENasRDS=$DIR_DATA/example.rds
export fileSNPlist=$DIR_DATA/example.snps

# copy .bgen files
cp $DIR_REFERENCE/examples/regenie/example.bgen $fileBGEN
cp $DIR_REFERENCE/examples/regenie/example.bgen.bgi $fileBGEN.bgi

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
export BGENIX="singularity exec -B $DIR_BASE:$DIR_BASE -B $DIR_REF_LDPRED:/ldpred2_ref -B $DIR_REFERENCE:/REF $DIR_SIF/gwas.sif bgenix"
export PYTHON="singularity exec -B $DIR_BASE:$DIR_BASE -B $DIR_REF_LDPRED:/ldpred2_ref -B $DIR_REFERENCE:/REF $DIR_SIF/python3.sif python"

# Some testing functions
source $DIR_TESTS/scripts/functions.sh

# The different modes to run (affects runs of scripts/extended.sh)
LDPRED_MODES="inf auto"

##################################################
### Testing scripts             
##################################################
echo "### Running R function unittests"
$RSCRIPT $DIR_TESTS/unittest/fun.R

echo "### Testing sumstats scripts"
source $DIR_TESTS/scripts/sumstats.sh

echo "### Testing RDS/backingfile creation"
source $DIR_TESTS/scripts/backingfile.sh

echo "### Testing LD calculation"
source $DIR_TESTS/scripts/ld.sh

echo "### Testing tutorial data"
source $DIR_TESTS/scripts/tutorial.sh

echo "### Testing imputation"
source $DIR_TESTS/scripts/imputation.sh

echo "### Testing ldpred2.R (various options, manually downloaded LD, output merge)"
source $DIR_TESTS/scripts/extended.sh

echo "Minutes passed:"
awk "BEGIN {printf \"%.2f\n\", (`date +%s` - $timeStart)/60}"
