dirOut=$DIR_TESTS/output/ld
if [ ! -d $dirOut ]; then mkdir $dirOut; fi
# Basic command to perform LD estimation
LDE="$RSCRIPT $DIR_SCRIPTS/calculateLD.R --geno-file-rds $fileOutputSNPR \
  --dir-genetic-maps $DIR_TESTS/maps/ \
  --file-ld-chr $DIR_TESTS/output/ld/ld-chr@.rds \
  --file-ld-map $DIR_TESTS/output/ld/map.rds "

LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R \
  --ld-file $DIR_TESTS/output/ld/ld-chr@.rds \
  --ld-meta-file $DIR_TESTS/output/ld/map.rds \
  --merge-by-rsid --set-seed 1 \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats"

LDA="$RSCRIPT $DIR_SCRIPTS/analyzeLD.R"

echo "Running unittests on functions"
$RSCRIPT $DIR_TESTS/unittest/funMatrix.R

echo "Test restricting on a subset of SNPs (only chromosome 1-8 will run)"
fileSumstats25k=$DIR_TESTS/data/public-data-sumstats25k.txt
head -n 25000 $fileInputSumStats > $fileSumstats25k
#testSuccess "$LDE --sumstats $fileSumstats25k rsid"

# Test adding the parameter --thres-r2
#testSuccess "$LDE --sumstats $fileSumstats25k rsid --thres-r2 0.2"

echo "Test restricting on SNPs provide by a SNP list file: $fileKeepSNPS"
#testSuccess "$LDE --extract $fileKeepSNPS"

echo "Test sampling individuals (N=400)"
#testSuccess "$LDE --sample-individuals 400 --extract $fileKeepSNPS"
# Test this LDpred on this LD (restrict to chromosomes 20-22
#testSuccess "$LDP --ldpred-mode inf --out $fileOut.inf --chr2use 20 21 22"

# Filter out SNPs that overlap with genotypes
echo "Test LD estimation with SNP filtering"
cut -f 1 -d , $fileInputSumStats > $DIR_TESTS/data/snps-for-ld.txt
#testSuccess "$LDE --sumstats $DIR_TESTS/data/snps-for-ld.txt rsid"
#testSuccess "$LDP --ldpred-mode auto --out $fileOut.inf --chr2use 20 21 22"


echo "Testing analyzeLD.R"
#testSuccess "$LDA --non-zeroes count --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds"
#testSuccess "$LDA --non-zeroes fraction --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds"
#testSuccess "$LDA --non-zeroes percentage --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --file-out $DIR_TESTS/output/ld-summary.tsv"
#testSuccess "$LDA --non-zeroes percentage --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --plot --plot-file-out $DIR_TESTS/output/ld-fig-ch@.png"
#testSuccess "$LDA --non-zeroes percentage --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds \
# --plot --plot-file-out $DIR_TESTS/output/ld-fig-chr.png --chr2use 21 22"
#testSuccess "$LDA --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair2122.png --chr2use 21 22"
testSuccess "$LDA --intervals --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
  --chr2use 21 22 --file-out $DIR_TESTS/output/intervals.csv"

echo "Testing splitLD.R"
#$RSCRIPT $DIR_SCRIPTS/splitLD.R --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --file-output-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --chr2use 21 --max-size-weights 40 33
#$RSCRIPT $DIR_SCRIPTS/splitLD.R --file-ld-blocks $dirOut/ld-chr22.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --file-output-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --chr2use 21 --max-size-weights 10 5
#$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-own-basepair22-block.png --chr2use 22
#$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair22-block.png --chr2use 22

#$RSCRIPT $DIR_SCRIPTS/splitLD.R --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --file-output-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --chr2use 22
#exit
#$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-own-basepair22-block.png --chr2use 22
#$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair22-block.png --chr2use 22

