### Exported variables are used in the unittests

dirOut=$DIR_TESTS/output/ld
if [ ! -d $dirOut ]; then mkdir $dirOut; fi
# Basic command to perform LD estimation
LDE="$RSCRIPT $DIR_SCRIPTS/calculateLD.R --geno-file-rds $fileOutputSNPR \
  --dir-genetic-maps $DIR_TESTS/maps/ "

LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R \
  --ld-file $dirOut/ld-chr@.rds \
  --ld-meta-file $dirOut/map.rds \
  --merge-by-rsid --set-seed 1 \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats"

echo "Running unittests on functions"
testSuccess $RSCRIPT $DIR_TESTS/unittest/funMatrix.R

echo "Test restricting on a subset of SNPs (only chromosome 1-8 will run)"
export fileSumstats25k=$DIR_TESTS/data/public-data-sumstats25k.txt
head -n 25000 $fileInputSumStats > $fileSumstats25k
export fileLD25K=$DIR_TESTS/output/ld/map25K.rds
testSuccess $LDE --sumstats $fileSumstats25k rsid --file-ld-chr $dirOut/ld-chr@.rds --file-ld-map $fileLD25K

# Test adding the parameter --thres-r2
testSuccess $LDE --sumstats $fileSumstats25k rsid --thres-r2 0.2 --chr2use 21 22 --file-ld-chr $dirOut/ld-chr@.rds --file-ld-map $dirOut/map.rds

echo "Test restricting on SNPs provide by a SNP list file: $fileKeepSNPS"
testSuccess $LDE --extract $fileKeepSNPS --file-ld-chr $dirOut/ld-chr@.rds --file-ld-map $dirOut/map.rds

echo "Test sampling individuals (N=400)"
testSuccess $LDE --sample-individuals 400 --extract $fileKeepSNPS --file-ld-chr $dirOut/ld-chr@.rds --file-ld-map $dirOut/map.rds
# Test this LDpred on this LD (restrict to chromosomes 20-22
testSuccess $LDP --ldpred-mode inf --out $fileOut.inf --chr2use 20 21 22

# Filter out SNPs that overlap with genotypes
echo "Test LD estimation with SNP filtering"
cut -f 1 -d , $fileInputSumStats > $DIR_TESTS/data/snps-for-ld.txt
testSuccess $LDE --sumstats $DIR_TESTS/data/snps-for-ld.txt rsid --file-ld-chr $dirOut/ld-chr@.rds
testSuccess $LDP --ldpred-mode auto --out $fileOut.inf --chr2use 20 21 22


echo "Testing analyzeLD.R"
LDA="$RSCRIPT $DIR_SCRIPTS/analyzeLD.R"
testSuccess $LDA --non-zeroes count --file-ld-blocks $dirOut/ld-chr@.rds --chr2use 21 22
export fileOutputZeroes=$DIR_TESTS/output/ld/zeroes.csv
testSuccess $LDA --non-zeroes count --file-ld-blocks $dirOut/ld-chr@.rds --chr2use 21 22 --file-out $fileOutputZeroes
testSuccess $LDA --non-zeroes fraction --file-ld-blocks $dirOut/ld-chr@.rds
testSuccess $LDA --non-zeroes percentage --file-ld-blocks $dirOut/ld-chr@.rds
# Plot all chromosomes
export filePlotFull=$DIR_TESTS/output/ld-fig-chr.png
testSuccess $LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --plot --plot-file-out $filePlotFull
# Plot chromosome 21 and 22 and switch to "basepair scale"
export filePlot2122=$DIR_TESTS/output/ld-fig-chr2122.png
testSuccess $LDA --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
 --plot --plot-scale-x basepair --plot-file-out $filePlot2122 --chr2use 21 22
export fileOutputIntervals=$DIR_TESTS/output/ld/intervals.csv
testSuccess $LDA --intervals --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
  --chr2use 21 22 --file-out $fileOutputIntervals

echo "Testing splitLD.R"
LDS="$RSCRIPT $DIR_SCRIPTS/splitLD.R --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds"
# Fails due to bad parameters
testException $LDS --file-ld-chr $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds \
 --file-output-ld-blocks $dirOut/ld-blocked-chr@.rds --chr2use 21 --max-size-weights 40 33
testSuccess $LDS --file-ld-chr $dirOut/ld-chr22.rds \
 --file-output-ld-blocks $dirOut/ld-blocked-chr@.rds --chr2use 21 --max-size-weights 10 5

echo "Running unittests on output"
testSuccess $RSCRIPT $DIR_TESTS/unittest/ld.R

# Cleanup
rm -f $filePlot2122 $filePlotFull $fileLD25K
