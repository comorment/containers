# Snippets of sumstats and HRC SNP data
fileSumstats=$DIR_TESTS/unittest/data/sumstats.txt
fileReference=$DIR_TESTS/unittest/data/hrc37.txt
# The tests are not run using the full HRC data to speed things up
COM="$RSCRIPT $DIR_SCRIPTS/complementSumstats.R --reference $fileReference"
# Output to stdout
#dump=$( { $COM --sumstats $fileSumstats; } 2>&1 )
#if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Add up som more columns than the defaults
dump=$( { $COM --columns-append "#CHROM" POS --sumstats $fileSumstats ; } 2>&1 )
#$COM --columns-append "#CHROM" POS AF --column-names-output CHR POS AF --sumstats $fileSumstats
#exit
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
