This usecase describe how to obtain required LDscore file and pheno file to run BOLT-LMM. All commands below assume that ``$COMORMENT``, ``$SIF`` and ``$SINGULARITY_BIND`` environmental variables are defined as described in [Getting started](../README.md#getting-started) section of the main README file.



1.  Getting LD file using ldsc and gwas containers
```
mkdir bolt_out

singularity exec --home $PWD:/home $SIF/ldsc.sif python /tools/ldsc/ldsc.py --bfile /REF/examples/regenie/example_3chr --l2 --ld-wind-cm 1 --yes   --out  bolt_out/myld

singularity exec --home $PWD:/home $SIF/gwas.sif plink --bfile /REF/examples/regenie/example_3chr  --freq  --out   bolt_out/example_3chr
```

```
singularity shell --home $PWD:/home $SIF/python3.sif 

python

import pandas as pd

df1=pd.read_csv("bolt_out/myld.l2.ldscore.gz", delimiter="\t")

df2=pd.read_fwf('bolt_out/example_3chr.frq',sep=" ")


dff=pd.merge(df1,df2, on='SNP', how='inner')

mydf=dff[['SNP','CHR_x','BP','MAF','L2']]

mydf=mydf.rename(columns={'CHR_x': 'CHR'}, inplace=False)

mydf.to_csv('bolt_out/example_3chr.LDSCORE.tab', header=True, index=False, sep='\t', mode='a')

```
