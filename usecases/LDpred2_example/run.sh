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
export DIR_REF_LDPRED=$DIR_BASE/ldpred2_ref

# Tutorial data
# Phenotypic data is part of bed file
export fileInputGeno=$DIR_BASE/usecases/LDpred2_tutorial/tutorial_data/public-data3.bed
export fileInputSumStats=$DIR_BASE/usecases/LDpred2_tutorial/tutorial_data/public-data3-sumstats.txt
export fileOutputSNPR=$DIR_TESTS/data/public-data3.rds
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs
export fileOut=$DIR_TESTS/output/public-data.score

# Create shortcut environment variable for Rscript 
export RSCRIPT="singularity exec -B $DIR_BASE:$DIR_BASE -B $DIR_REFERENCE:/REF $DIR_SIF/r.sif Rscript"

# The different modes to run
LDPRED_MODES="inf auto"

echo "### Running R function unittests"
$RSCRIPT $DIR_TESTS/unittest/fun.R

echo "### Testing RDS/backingfile creation"
source $DIR_TESTS/scripts/backingfile.sh

echo "### Testing imputation"
# Convert a file with missing genotypes
# Copy some plink files
cp $DIR_REFERENCE/examples/prsice2/EUR.bed $DIR_TESTS/data/
cp $DIR_REFERENCE/examples/prsice2/EUR.bim $DIR_TESTS/data/
cp $DIR_REFERENCE/examples/prsice2/EUR.fam $DIR_TESTS/data/
fileImpute=$DIR_TESTS/data/EUR
fileImputed=$DIR_TESTS/data/EUR_imputed
# Convert to bigsnpr
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R /REF/examples/prsice2/EUR.bed $fileImpute.rds )
if [ $? -eq 1 ]; then exit; fi
# Test simple imputation 

# The imputation replaces data on disk. As copying these objects takes
# a lot of time it's probably better to let the user copy the files
# manually if desired to keep the original files unhcanged
cp $fileImpute.bk $fileImputed.bk
cp $fileImpute.rds $fileImputed.rds
$RSCRIPT $DIR_SCRIPTS/imputeGenotypes.R --geno-file-rds $fileImputed.rds \
 --impute-simple mode


echo "### Testing ldpred2.R using externally provided LD"
# Download data if necessary
FILE_LDREF=$DIR_TESTS/data/ld/ldref_with_blocks.zip
FILE_LDMAP=$DIR_TESTS/data/ld/map_hm3_plus.rds
if [ ! -f $FILE_LDREF ]; then 
 echo "Downloading LD reference"
 wget -O $FILE_LDREF "https://figshare.com/ndownloader/files/36363087"; 
 unzip -d $DIR_TESTS/data/ld/ldref_with_blocks.zip $FILE_LDREF
fi;
if [ ! -f $FILE_LDMAP ]; then 
 echo "Downloading LD map"
 wget -O $FILE_LDMAP "https://figshare.com/ndownloader/files/37802721" ;  
fi;

LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --ld-file $DIR_TESTS/data/ld/ldref/LD_with_blocks_chr@.rds \
  --ld-meta-file $DIR_TESTS/data/ld/ldref/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --sumstats $fileInputSumStats --out ${fileOut}_imputed.inf"

$LDP --ldpred-mode inf --geno-file-rds $fileImputed.rds

# Failure due to missing genotypes
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImpute.rds; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; echo "$dump"; exit; fi
# Fix with -geno-impute-zero
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImpute.rds --geno-impute-zero; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Run with preimputed file
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImputed.rds; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

# Note that if files in --dir-genetic-maps do not exist, these will be downloaded. But I think error if the directory doesnt exist
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --ld-file $DIR_TESTS/data/ld/ldref/LD_with_blocks_chr@.rds \
  --ld-meta-file $DIR_TESTS/data/ld/ldref/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a0 --col-A2 a1 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats --out $fileOut.inf"

echo "TEST error: Bad ldpred mode"
dump=$( { $LDP --ldpred-mode infinite; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; exit; fi

echo "TEST error: Bad imputation mode"
dump=$( { $LDP --ldpred-mode inf --geno-impute bad-mode; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; exit; fi

# TEST: Complete runs of --ldpred-mode given by $LDPRED_MODES
for MODE in $LDPRED_MODES; do
 echo "Testing mode $MODE"
 dump=$( { $LDP --ldpred-mode $MODE; } 2>&1 )
 if [ $? -eq 1 ]; then echo "$dump"; exit; fi
done

echo "### Testing LD estimation with calculateLD.R and use in ldpred2.R"
# Basic command to perform LD estimation
LDE="$RSCRIPT $DIR_SCRIPTS/calculateLD.R --geno-file-rds $fileOutputSNPR \
  --dir-genetic-maps $DIR_TESTS/maps/ \
  --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds \
  --file-ld-map $DIR_TESTS/output/ld/map.rds
"

echo "Test restricting on a subset of SNPs (only chromosome 1-9 will run)"
fileSumstats25k=$DIR_TESTS/data/public-data-sumstats25k.txt
head -n 25000 $fileInputSumStats > $fileSumstats25k
dump=$( { $LDE --sumstats $fileSumstats25k rsid ; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Test adding the parameter --thres-r2
dump=$( { $LDE --sumstats $fileSumstats25k rsid --thres-r2 0.2; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test restricting on SNPs provide by a SNP list file: $fileKeepSNPS"
dump=$( { $LDE --extract $fileKeepSNPS; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test sampling individuals (N=400)"
dump=$( { $LDE --sample-individuals 400 --extract $fileKeepSNPS; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test no restrictions on snps (similar to tutorial)"
dump=$( { $LDE; } 2>&1 )
# Use this LD to run LDpred
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R \
  --ld-file $DIR_TESTS/output/ld/ld-chr@.rds \
  --ld-meta-file $DIR_TESTS/output/ld/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats --out $fileOut.inf"
dump=$( { $LDP; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
echo "$dump"

