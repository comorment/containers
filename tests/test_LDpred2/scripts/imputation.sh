
# Convert to bigsnpr
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R --file-input /REF/examples/prsice2/EUR.bed --file-output $fileImpute.rds )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Test simple imputation 

# The imputation replaces data on disk. As copying these objects takes
# a lot of time it's probably better to let the user copy the files
# manually if desired to keep the original files unhcanged
cp $fileImpute.bk $fileImputed.bk
cp $fileImpute.rds $fileImputed.rds
dump=$( { $RSCRIPT $DIR_SCRIPTS/imputeGenotypes.R --geno-file-rds $fileImputed.rds \
 --impute-simple mode; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
