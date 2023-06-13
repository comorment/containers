# The last command of this script replicates the results from the tutorial
echo "Testing LD estimation with calculateLD.R and use in ldpred2.R"
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

# Use this LD to run LDpred
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R \
  --ld-file $DIR_TESTS/output/ld/ld-chr@.rds \
  --ld-meta-file $DIR_TESTS/output/ld/map.rds \
  --merge-by-rsid --set-seed 1 \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats"

echo "Test sampling individuals (N=400)"
dump=$( { $LDE --sample-individuals 400 --extract $fileKeepSNPS; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

dump=$( { $LDP --ldpred-mode inf --out $fileOut.inf; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
 
# Filter out SNPs that overlap with genotypes
echo "Test LD estimation with SNP filtering"
cut -f 1 -d , $fileInputSumStats > $DIR_TESTS/data/snps-for-ld.txt
dump=$( { $LDE --sumstats $DIR_TESTS/data/snps-for-ld.txt rsid; } 2<&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test no restrictions on snps (similar to tutorial)"
dump=$( { $LDE; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

for MODE in $LDPRED_MODES; do
 dump=$( { $LDP --ldpred-mode $MODE --out $fileOut.$MODE; } 2>&1 )
 if [ $? -eq 1 ]; then echo "$dump"; exit; fi
done

echo "Running unittests for tutorial results"
$RSCRIPT $DIR_TESTS/unittest/tutorial.R
