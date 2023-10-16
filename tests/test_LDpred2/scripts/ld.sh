dirOut=$DIR_TESTS/output/ld
if [ ! -d $dirOut ]; then mkdir $dirOut; fi
# Basic command to perform LD estimation
LDE="$RSCRIPT $DIR_SCRIPTS/calculateLD.R --geno-file-rds $fileOutputSNPR \
  --dir-genetic-maps $DIR_TESTS/maps/ \
  --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds \
  --file-ld-map $DIR_TESTS/output/ld/map.rds "

LDA="$RSCRIPT $DIR_SCRIPTS/analyzeLD.R"
 
#$LDA --non-zeroes count --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds
#$LDA --non-zeroes fraction --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds
#$LDA --non-zeroes percentage --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --file-out $DIR_TESTS/output/ld-summary.tsv
#$LDA --non-zeroes percentage --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --plot --plot-file-out $DIR_TESTS/output/ld-fig-ch@.png
#$LDA --non-zeroes percentage --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds \
# --plot --plot-file-out $DIR_TESTS/output/ld-fig-chr.png --chr2use 21 22
#$LDA --non-zeroes percentage --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair.png --chr2use 21 22
#$LDA --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair2122.png --chr2use 21 22

#$LDA --intervals --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
#  --chr2use 21 22 --file-out $DIR_TESTS/output/intervals.csv

#$RSCRIPT $DIR_SCRIPTS/splitLD.R --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --file-output-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --chr2use 22
#$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-own-basepair22-block.png --chr2use 22
#$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
# --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair22-block.png --chr2use 22

$RSCRIPT $DIR_SCRIPTS/splitLD.R --file-ld-blocks $DIR_REF_LDPRED/ldref_hm3_plus/LD_with_blocks_chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
 --file-output-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --chr2use 22
$RSCRIPT $DIR_TESTS/unittest/funMatrix.R
exit
$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
 --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-own-basepair22-block.png --chr2use 22
$LDA --file-ld-blocks $DIR_TESTS/output/ld/ld-blocked-chr@.rds --file-ld-map $DIR_REF_LDPRED/map_hm3_plus.rds \
 --plot --plot-threshold 0.2 --plot-scale-x basepair --plot-file-out $DIR_TESTS/output/ld-fig-chr-basepair22-block.png --chr2use 22


$RSCRIPT $DIR_TESTS/unittest/funMatrix.R
