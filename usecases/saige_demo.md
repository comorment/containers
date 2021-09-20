This usecase describe how to run Saige analysis (https://github.com/weizhouUMICH/SAIGE). All commands below assume that ``$COMORMENT``, ``$SIF`` and ``$SINGULARITY_BIND`` environmental variables are defined as described in [Getting started](../README.md#getting-started) section of the main README file.

!!! This analysis is specifically valid for wzhou88/saige:0.36.3.3 


1.   create folder for output
```
mkdir saige_out
```


2.  Merge phenofile and cov file

```
singularity shell --home $PWD:/home $SIF/python3.sif 

python3
import pandas as pd

df1=pd.read_csv('/REF/examples/regenie/example_3chr.pheno', delimiter=",")

df2=pd.read_csv('/REF/examples/regenie/covariates.txt', delimiter=" ")

dff=pd.merge(df1,df2, on='IID', how='inner')

dff.to_csv('saige_out/pheno_cov.txt', header=True, index=False, sep='\t', mode='a')
```

3.  Run step 1

```
singularity shell --home $PWD:/home $SIF/saig2.sif

# saige step1

Rscript /SAIGE/extdata/step1_fitNULLGLMM.R      --plinkFile=/REF/examples/regenie/example_3chr   --phenoFile=/home/saige_out/pheno_cov.txt    --phenoCol=PHENO --covarColList=PC1,PC2,V1,V2,V3 --sampleIDColinphenoFile=IID    --traitType=quantitative    --invNormalize=TRUE  --outputPrefix=/home/saige_out/out2   --nThreads=4 --LOCO=FALSE --minMAF=0.01 --tauInit=1,0


```

4.  step 2 requires requires creating sample files 

```
singularity shell --home $PWD:/home $SIF/gwas.sif

# convert to vcf

plink --bfile /REF/examples/regenie/example_3chr  --recode vcf-iid --out /home/saige_out/out_vcf
bcftools query -l /home/saige_out/out_vcf.vcf > /home/saige_out/samples.txt 


```

5.  Run step 2

```
singularity shell --home $PWD:/home $SIF/saig2.sif

Rscript /SAIGE/extdata/step2_SPAtests.R \
        --bgenFile=/REF/examples/regenie/example_3chr.bgen \
        --bgenFileIndex=/REF/examples/regenie/example_3chr.bgen.bgi \
        --minMAF=0.0001 \
        --minMAC=1 \
        --sampleFile=/home/saige_out/samples.txt \
        --GMMATmodelFile=/home/saige_out/out2.rda \
        --varianceRatioFile=/home/saige_out/out2.varianceRatio.txt \
        --SAIGEOutputFile=/home/saige_out/example_3chr_saige_out \
        --numLinesOutput=2 \
        --IsOutputAFinCaseCtrl=TRUE


```



