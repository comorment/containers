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
#export fileInputGeno=/REF/examples/prsice2/EUR
#export fileOutputSNPR=$DIR_TESTS/data/EUR.rds
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs
#export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=$DIR_TESTS/output/public-data.score

dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno $fileOutputSNPR )
if [ $? -eq 1 ]; then exit; fi

### LD
# LD estimation
LDE="$RSCRIPT $DIR_SCRIPTS/calculateLD.R --geno-file $fileOutputSNPR \
  --file-keep-snps $fileKeepSNPS \
  --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds \
  --file-ld-map $DIR_TESTS/output/ld/map.rds
"
$LDE

LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --ld-file $DIR_TESTS/output/ld/ld-chr@.rds \
  --ld-meta-file $DIR_TESTS/output/ld/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a0 --col-A2 a1 \
  --geno-file $fileOutputSNPR --sumstats $fileInputSumStats --out $fileOut.inf"
$LDP
exit

# Perform full runs using externally provided LD
# LDREF with blocks
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

# Note that if files in --dir-genetic-maps do not exist, these will be downloaded. But I think error if the directory doesnt exist
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --ld-file $DIR_TESTS/data/ld/ldref/LD_with_blocks_chr@.rds \
  --ld-meta-file $DIR_TESTS/data/ld/ldref/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a0 --col-A2 a1 \
  --geno-file $fileOutputSNPR --sumstats $fileInputSumStats --out $fileOut.inf"

## TEST: Bad ldpred mode
dump=$( { $LDP --ldpred-mode infinite; } 2>&1 )
if [ $? -eq 0 ]; then exit; fi

## TEST: Bad imputation mode
dump=$( { $LDP --ldpred-mode inf --geno-impute bad-mode; } 2>&1 )
if [ $? -eq 0 ]; then exit; fi

## TEST: Complete runs of --ldpred-mode given by $LDPRED_MODES
for MODE in $LDPRED_MODES; do
 echo "Testing mode $MODE"
 dump=$( { $LDP --ldpred-mode $MODE; } 2>&1 )
 if [ $? -eq 1 ]; then echo "$dump"; exit; fi
 echo "$dump"
done
