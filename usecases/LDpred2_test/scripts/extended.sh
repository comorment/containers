# Download data if necessary
FILE_LDREF=$DIR_TESTS/data/ld/ldref_with_blocks.zip
FILE_LDMAP=$DIR_TESTS/data/ld/map.rds
FILE_LDMAP_PLUS=$DIR_TESTS/data/ld/map_hm3_plus.rds
if [ ! -f $FILE_LDREF ]; then 
 echo "Downloading LD reference"
 wget -O $FILE_LDREF "https://figshare.com/ndownloader/files/36363087"; 
 unzip -d $DIR_TESTS/data/ld/ $FILE_LDREF
fi;
if [ ! -f $FILE_LDMAP ]; then 
 echo "Downloading LD map"
 wget -O $FILE_LDMAP "https://figshare.com/ndownloader/files/36360900" ;  
fi;
if [ ! -f $FILE_LDMAP_PLUS ]; then 
 echo "Downloading LD map (map_hm3_plus.rds)"
 wget -O $FILE_LDMAP "https://figshare.com/ndownloader/files/37802721" ;  
fi;

LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --ld-file $DIR_TESTS/data/ld/ldref/LD_with_blocks_chr@.rds \
  --ld-meta-file $DIR_TESTS/data/ld/ldref/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a1 --col-A2 a0 \
  --out ${fileOut}_imputed.inf"

# Create sumstats with characters in chromosome column
echo "Test error: Character in chromosome column"
row=$(tail -n 1  $fileInputSumStats)
row=${row/,22,/,X,}
fileSumstatsWithChar=$DIR_TESTS/data/sumstats_chr_char.txt
head -n -1 $fileInputSumStats > $fileSumstatsWithChar
echo "$row" >> $fileSumstatsWithChar
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImputed.rds --sumstats $fileSumstatsWithChar; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

echo "Test error: Missing genotypes"
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImpute.rds --sumstats $fileInputSumStats; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; echo "$dump"; exit; fi
echo "Test --geno-impute-zero"
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImpute.rds --geno-impute-zero --sumstats $fileInputSumStats; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
echo "Test preimputed file"
dump=$( { $LDP --ldpred-mode inf --geno-file-rds $fileImputed.rds --sumstats $fileInputSumStats; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi

# Note that if files in --dir-genetic-maps do not exist, these will be downloaded. But I think error if the directory doesnt exist
LDP="$RSCRIPT $DIR_SCRIPTS/ldpred2.R --file-keep-snps $fileKeepSNPS \
  --ld-file $DIR_TESTS/data/ld/ldref/LD_with_blocks_chr@.rds \
  --ld-meta-file $DIR_TESTS/data/ld/ldref/map.rds \
  --merge-by-rsid \
  --col-stat beta --col-stat-se beta_se \
  --col-snp-id rsid --col-chr chr --col-bp pos --col-A1 a0 --col-A2 a1 \
  --geno-file-rds $fileOutputSNPR --sumstats $fileInputSumStats"

echo "TEST error: Bad ldpred mode"
dump=$( { $LDP --ldpred-mode infinite --out $fileOut.inf; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; exit; fi

echo "TEST error: Bad imputation mode"
dump=$( { $LDP --ldpred-mode inf --geno-impute bad-mode --out $fileOut.inf; } 2>&1 )
if [ $? -eq 0 ]; then echo "No error received"; exit; fi

# TEST: Complete runs of --ldpred-mode given by $LDPRED_MODES
for MODE in $LDPRED_MODES; do
 echo "Testing mode $MODE"
 dump=$( { $LDP --ldpred-mode $MODE --out $fileOut.$MODE; } 2>&1 )
 if [ $? -eq 1 ]; then echo "$dump"; exit; fi
done
echo "Test appending score to output file"
export fileExisting=$fileOut.inf
export scoreNameExisting=score # Exists from runs above
export scoreNameNew=newScore # Name for appended score
dump=$( { $LDP --ldpred-mode inf --name-score $scoreNameNew --out $fileExisting --out-merge; } 2>&1 )
if [ $? -eq 1 ]; then echo "$dump"; exit; fi
echo "Runing unittests on output"
$RSCRIPT $DIR_TESTS/unittest/extended.R

