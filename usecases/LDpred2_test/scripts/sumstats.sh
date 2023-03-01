# Snippets of sumstats and HRC SNP data
fileSumstats=$DIR_TESTS/unittest/data/sumstats.txt
fileReference=$DIR_TESTS/unittest/data/hrc37.txt
# The tests are not run using the full HRC data to speed things up
COM="$RSCRIPT $DIR_SCRIPTS/complementSumstats.R --sumstats $fileSumstats --reference $fileReference"
# Output to stdout
dump=$( { $COM; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Add up som more columns than the defaults
dump=$( { $COM --columns-append "#CHROM" POS AF; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
echo "$dump"
