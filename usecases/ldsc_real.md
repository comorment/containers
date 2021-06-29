This usecase describe how to run LDSC analysis (https://github.com/bulik/ldsc) on Morningness and Intelligence summary statistics data. All commands below assume that ``$SIF`` and ``$SINGULARITY_BIND`` environmental variables are defined as described in [Getting started](../README.md#getting-started) section of the main README file.



1.  Export the path of the summary statistics, name this path as 'sumstats_ld'
```
export sumstats_ld=$COMORMENT/containers/reference/sumstats
```

2. Uncompress sumstat data if required and copy these uncompressed sumstats to your working directory
```
gunzip $sumstats_ld/Morningness_sumstats_Jansenetal.txt.gz
unzip $sumstats_ld/SavageJansen_IntMeta_sumstats.zip

cp $sumstats_ld/Morningness_sumstats_Jansenetal.txt .

```

3. Arranging sumstats file for LDSC analysis via  munge_sumstats.py

```
singularity exec --home $PWD:/home $SIF/ldsc.sif python /tools/ldsc/munge_sumstats.py \
--sumstats sumstats/SavageJansen_2018_intelligence_metaanalysis.txt \
--N  2000 \
--out int_munge \
--merge-alleles /REF/ldsc/w_hm3.snplist

singularity exec --home $PWD:/home $SIF/ldsc.sif python /tools/ldsc/munge_sumstats.py \
--sumstats Morningness_sumstats_Jansenetal.txt \
--out mor_munge \
--merge-alleles /REF/ldsc/w_hm3.snplist \
--signed-sumstats OR,0

```

4. remove .gz extension for munged sumstats

```
mv mor_munge.sumstats.gz mor_munge.sumstats
mv int_munge.sumstats.gz int_munge.sumstats
```



5. Ready to run LDSC analysis

```
singularity exec --home $PWD:/home $SIF/ldsc.sif python /tools/ldsc/ldsc.py  \
--rg int_munge.sumstats,mor_munge.sumstats \
--ref-ld-chr /REF/ldsc/eur_w_ld_chr/ \
--w-ld-chr /REF/ldsc/eur_w_ld_chr/ \
--out int_mor

```
The succesfull munge_sumstats.py and ldsc.py results shoud look like this:

Munge Intelligence:
![munge1.png](https://raw.githubusercontent.com/comorment/containers/main/usecases/ldsc_demo/munge1.png)

Munge Morningness:
![munge2.png](https://raw.githubusercontent.com/comorment/containers/main/usecases/ldsc_demo/munge2.png)

LDSC:
![ldsc.png](https://raw.githubusercontent.com/comorment/containers/main/usecases/ldsc_demo/ldsc.png)


