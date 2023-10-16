# The last command of this script replicates the results from the tutorial
echo "Testing LD estimation with calculateLD.R and use in ldpred2.R"
# Basic command to perform LD estimation
LDE="$RSCRIPT $DIR_SCRIPTS/calculateLD.R --geno-file-rds $fileOutputSNPR \
  --dir-genetic-maps $DIR_TESTS/maps/ \
  --file-ld-chr $DIR_TESTS/output/ld/ld-chr@.rds \
  --file-ld-map $DIR_TESTS/output/ld/map.rds "
# Use this LD to run LDpred
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R \
  --ld-file $DIR_TESTS/output/ld/ld-chr@.rds \
  --ld-meta-file $DIR_TESTS/output/ld/map.rds \
  --merge-by-rsid --set-seed 1 \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats"

echo "Test no restrictions on snps (similar to tutorial)"
dump=$( { $LDE; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

for MODE in $LDPRED_MODES; do
 dump=$( { $LDP --ldpred-mode $MODE --out $fileOut.$MODE; } 2>&1 )
 if [ $? -eq 1 ]; then echo "$dump"; exit; fi
done

echo "Running unittests for tutorial results"
$RSCRIPT $DIR_TESTS/unittest/tutorial.R
