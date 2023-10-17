### These two runs ensure that the backing file is created
### correctly wheter the uses specifies .rds or not
# Passing full name of $fileSNPR
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R --file-input $fileInputGeno --file-output $fileOutputSNPR )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
# Passing basename of $fileSNPR
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R --file-input $fileInputGeno --file-output $(dirname $fileOutputSNPR)/$(basename $fileOutputSNPR) )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R --file-input $fileInputGeno --file-output $fileOutputSNPR )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

# check that .bgen file can be converted
# First, create data/snp_list_id.txt file
dump=$( $BGENIX -g $fileBGEN -incl-range 1:0- -list > $fileSNPlist )
dump=$( $PYTHON -c "import os; import pandas as pd; df = pd.read_csv('$fileSNPlist', delim_whitespace=True, skipfooter=1, skiprows=[0], engine='python'); df = df[['chromosome', 'position', 'first_allele', 'alternative_alleles']]; df.to_csv('$fileSNPlist', index=False, sep='_', header=False)" )
# Then, create backing file
dump=$( $RSCRIPT $DIR_SCRIPTS/createBackingFile.R --file-input $fileBGEN --file-output $fileBGENasRDS --file-snp-list $fileSNPlist )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
