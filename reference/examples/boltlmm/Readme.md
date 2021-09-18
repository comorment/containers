This usecase describe how to obtain required LDscore file and pheno file to run BOLT-LMM. All commands below assume that ``$COMORMENT``, ``$SIF`` and ``$SINGULARITY_BIND`` environmental variables are defined as described in [Getting started](../README.md#getting-started) section of the main README file.



1.  Getting LD file
```
mkdir bolt_out

singularity exec --home $PWD:/home $SIF/ldsc.sif python /tools/ldsc/ldsc.py --bfile /REF/examples/regenie/example_3chr --l2 --ld-wind-cm 1 --yes   --out  bolt_out/myld
```
