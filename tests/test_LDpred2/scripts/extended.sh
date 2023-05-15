LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-bp pos --col-A1 a1 --col-A2 a0 \
  --out ${fileOut}_imputed.inf"

# Create sumstats with characters in chromosome column
echo "Test error: Character in chromosome column"
row=$(tail -n 1  $fileInputSumStats)
row=${row/,22,/,X,}
fileSumstatsWithChar=$DIR_TESTS/data/sumstats_chr_char.txt
head -n -1 $fileInputSumStats > $fileSumstatsWithChar
echo "$row" >> $fileSumstatsWithChar
dump=$( { $LDP --ldpred-mode inf --col-chr chr --geno-file-rds $fileImputed.rds --sumstats $fileSumstatsWithChar; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test error: Missing genotypes"
dump=$( { $LDP --ldpred-mode inf --col-chr chr --geno-file-rds $fileImpute.rds --sumstats $fileInputSumStats; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; echo "$dump"; exit; fi
echo "Test --geno-impute-zero"
dump=$( { $LDP --ldpred-mode inf --col-chr chr --geno-file-rds $fileImpute.rds --geno-impute-zero --sumstats $fileInputSumStats; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
echo "Test preimputed file"
dump=$( { $LDP --ldpred-mode inf --col-chr chr --geno-file-rds $fileImputed.rds --sumstats $fileInputSumStats; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

# Note that if files in --dir-genetic-maps do not exist, these will be downloaded. But I think error if the directory doesnt exist
# --col-chr Chr is to ensure that column names are not case sensitive
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr Chr --col-bp pos --col-A1 a0 --col-A2 a1 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats"

echo "TEST error: Bad ldpred mode"
dump=$( { $LDP --ldpred-mode infinite --out $fileOut.inf; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; exit; fi

echo "TEST error: Bad imputation mode"
dump=$( { $LDP --ldpred-mode inf --geno-impute bad-mode --out $fileOut.inf; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; exit; fi

# TEST: Complete run of --ldpred-mode
dump=$( { $LDP --ldpred-mode inf --out $fileOut.inf; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test appending score to output file"
# These variables are used by the unittests below
export fileExisting=$fileOut.inf
export scoreNameExisting=score # Exists from runs above
export scoreNameNew=newScore # Name for appended score
dump=$( { $LDP --ldpred-mode inf --hyper-p-max 0.4 --name-score $scoreNameNew --out $fileExisting --out-merge; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Runing unittests on output"
$RSCRIPT $DIR_TESTS/unittest/extended.R

