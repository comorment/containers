# SAIGE demo

This usecase describe how to run Saige analysis (<https://github.com/weizhouUMICH/SAIGE>). All commands below assume that ``$COMORMENT``, ``$SIF`` and ``$SINGULARITY_BIND`` environmental variables are defined as described in the [INSTALL](../INSTALL.md) section of the main README file.

1. create folder for output

```
mkdir saige_out
```

2. prepare input files (merge phenofile and cov file, generate --sampleFile argument required for SAIGE step2)

```
singularity exec --home $PWD:/home $SIF/python3.sif sh -c "cut /REF/examples/regenie/example_3chr.fam -f 1 > /home/saige_out/samples.txt"

singularity exec --home $PWD:/home $SIF/python3.sif python3

import pandas as pd
df1=pd.read_csv('/REF/examples/regenie/example_3chr.pheno', delimiter=",")
df2=pd.read_csv('/REF/examples/regenie/covariates.txt', delimiter=" ")
dff=pd.merge(df1,df2, on='IID', how='inner')
dff.to_csv('saige_out/pheno_cov.txt', header=True, index=False, sep='\t', mode='a')
```

3. Run SAIGE step 1

```
singularity exec --home $PWD:/home $SIF/saige.sif step1_fitNULLGLMM.R \
    --plinkFile=/REF/examples/regenie/example_3chr \
    --phenoFile=/home/saige_out/pheno_cov.txt \
    --phenoCol=PHENO \
    --covarColList=PC1,PC2,V1,V2,V3 \
    --sampleIDColinphenoFile=IID \
    --traitType=quantitative \
    --invNormalize=TRUE \
    --outputPrefix=/home/saige_out/out2 \
    --nThreads=4 \
    --LOCO=FALSE \
    --minMAF=0.01 \
    --tauInit=1,0
```

4. Run SAIGE step 2

```
singularity exec --home $PWD:/home $SIF/saige.sif step2_SPAtests.R \
        --bgenFile=/REF/examples/regenie/example_3chr.bgen \
        --bgenFileIndex=/REF/examples/regenie/example_3chr.bgen.bgi \
        --minMAF=0.0001 \
        --minMAC=1 \
        --sampleFile=/home/saige_out/samples.txt \
        --GMMATmodelFile=/home/saige_out/out2.rda \
        --varianceRatioFile=/home/saige_out/out2.varianceRatio.txt \
        --SAIGEOutputFile=/home/saige_out/example_3chr_saige_out \
        --numLinesOutput=2 \
        --IsOutputAFinCaseCtrl=TRUE \
        --LOCO=FALSE
```
