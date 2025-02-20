# Bolt-LMM demo

This usecase describe how to run Bolt-LMM analysis (<https://alkesgroup.broadinstitute.org/BOLT-LMM/BOLT-LMM_manual.html>). All commands below assume that ``$COMORMENT``, ``$SIF`` and ``$APPTAINER_BIND`` environmental variables are defined as described in the [INSTALL](../INSTALL.md) file.

1. Create the required LD and pheno files to run Bolt-LMM from [here](https://github.com/comorment/containers/tree/main/reference/examples/boltlmm)

2. Run the analysis for demo data using gwas.sif container

```
apptainer exec --home $PWD:/home $SIF/gwas.sif bolt --bfile=/REF/examples/regenie/example_3chr --phenoFile=bolt_out/example_3chr.lmm.pheno --phenoCol=PHENO --verboseStats --LDscoresFile=bolt_out/example_3chr.LDSCORE.tab     --covarFile=/REF/examples/regenie/covariates.txt --qCovarCol=V{1:3} --modelSnps=bolt_out/example_3chr.snplist  --statsFile=bolt_out/example_3chr_bolt.stats

```
