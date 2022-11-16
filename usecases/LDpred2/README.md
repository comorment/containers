# LDpred2

In order to run imputation and the LDpred2 analysis defined in the file `run_ldpred2.sh`, issue:  
```
# point to input/output files
export fileGeno=/REF/examples/prsice2/EUR.bed
export fileImputedGeno=EUR.imputed.bed
export filePheno=/REF/examples/prsice2/EUR.height
export fileKeepSNPS=/REF/ldsc/w_hm3.justrs
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=test.score

# set environmental variables. Replace "<path/to/containers>" with 
# the full path to the cloned "containers" repository
export SIF=<path/to/containers>/singularity
export REFERENCE=<path/to/containers>/reference
export SINGULARITY_BIND=$REFERENCE:/REF

# run tasks
bash run_ldpred2.sh
```
