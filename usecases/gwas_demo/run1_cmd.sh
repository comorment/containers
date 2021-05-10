for SLURM_ARRAY_TASK_ID in 1 2 3; do $PLINK2  --bfile /REF/examples/regenie/example_3chr --no-pheno  --chr ${SLURM_ARRAY_TASK_ID} --glm hide-covar --pheno run1.pheno --1 --covar run1.covar --out run1_chr${SLURM_ARRAY_TASK_ID}; done
$PYTHON gwas.py merge-plink2  --sumstats run1_chr@.CASE.glm.logistic --out run1_CASE.plink2  --chr2use 1,2,3 
$PYTHON gwas.py merge-plink2  --sumstats run1_chr@.CASE2.glm.logistic --out run1_CASE2.plink2  --chr2use 1,2,3 

$REGENIE  --bt --phenoFile run1.pheno --covarFile run1.covar --step 1 --bsize 1000 --out run1.regenie.step1 --bed /REF/examples/regenie/example_3chr --ref-first --bt --lowmem --lowmem-prefix run1.regenie_tmp_preds
for SLURM_ARRAY_TASK_ID in 1 2 3; do $REGENIE  --bt --phenoFile run1.pheno --covarFile run1.covar --step 2 --bsize 400 --out run1_chr${SLURM_ARRAY_TASK_ID} --bed /REF/examples/regenie/example_3chr --ref-first --bt --firth 0.01 --approx --pred run1.regenie.step1_pred.list --chr ${SLURM_ARRAY_TASK_ID}; done
$PYTHON gwas.py merge-regenie  --sumstats run1_chr@_CASE.regenie --out run1_CASE.regenie  --chr2use 1,2,3 
$PYTHON gwas.py merge-regenie  --sumstats run1_chr@_CASE2.regenie --out run1_CASE2.regenie  --chr2use 1,2,3 

