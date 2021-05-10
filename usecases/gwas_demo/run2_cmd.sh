for SLURM_ARRAY_TASK_ID in 1 2 3; do $PLINK2  --bfile /REF/examples/regenie/example_3chr --no-pheno  --chr ${SLURM_ARRAY_TASK_ID} --glm hide-covar --pheno run2.pheno --covar run2.covar --out run2_chr${SLURM_ARRAY_TASK_ID}; done
$PYTHON gwas.py merge-plink2  --sumstats run2_chr@.PHENO.glm.linear --out run2_PHENO.plink2  --chr2use 1,2,3 
$PYTHON gwas.py merge-plink2  --sumstats run2_chr@.PHENO2.glm.linear --out run2_PHENO2.plink2  --chr2use 1,2,3 

$REGENIE  --phenoFile run2.pheno --covarFile run2.covar --step 1 --bsize 1000 --out run2.regenie.step1 --bed /REF/examples/regenie/example_3chr --ref-first --lowmem --lowmem-prefix run2.regenie_tmp_preds
for SLURM_ARRAY_TASK_ID in 1 2 3; do $REGENIE  --phenoFile run2.pheno --covarFile run2.covar --step 2 --bsize 400 --out run2_chr${SLURM_ARRAY_TASK_ID} --bed /REF/examples/regenie/example_3chr --ref-first --pred run2.regenie.step1_pred.list --chr ${SLURM_ARRAY_TASK_ID}; done
$PYTHON gwas.py merge-regenie  --sumstats run2_chr@_PHENO.regenie --out run2_PHENO.regenie  --chr2use 1,2,3 
$PYTHON gwas.py merge-regenie  --sumstats run2_chr@_PHENO2.regenie --out run2_PHENO2.regenie  --chr2use 1,2,3 

