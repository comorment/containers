### These two runs ensure that the backing file is created
### correctly wheter the uses specifies .rds or not
# Passing full name of $fileSNPR
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno $fileOutputSNPR )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Passing basename of $fileSNPR
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno $(dirname $fileOutputSNPR)/$(basename $fileOutputSNPR) )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R $fileInputGeno $fileOutputSNPR )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
