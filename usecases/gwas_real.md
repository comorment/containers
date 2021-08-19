This use case describes application of [gwas.py](../gwas/gwas.py) to perform GWAS in [MoBa](https://github.com/norment/moba), on height and major depression phenotypes.

Input files:
* [moba.pheno.dict](gwas_real/moba.pheno.dict) - dictionary file. Corresponding ``moba.pheno`` file is not included as it contains individual-level information
* ``moba.hm3.withoutFID.[bed/bim/fam]`` - individual-level genotypes in plink format, constrained to HapMap3 SNPs, with ``N=86890`` individuals and ``M=787125`` markers; this is only used for ``regenie`` analysis
* ``98k-ec-eur-fin-batch-basic-qc-withoutFID.[bed/bim/fam]`` - full genotypes without constraining to HapMap3 SNPs, with exacly the same set of individuals, and ``M=5003746`` markers
* [moba.bed.argsfile](gwas_real/moba.bed.argsfile) and [moba.bgen.argsfile](gwas_real/moba.bgen.argsfile) - file for the ``gwas.py --argsfile`` argument, containing pointers to hard calles (in plink format) and dosages (in ``bgen`` format):    
  ```
  # moba.bed.argsfile
  --pheno-file moba.pheno
  --geno-fit-file moba.hm3.withoutFID
  --geno-file /cluster/projects/p697/genotype/MoBa_98k_post-imputationQC/98k-ec-eur-fin-batch-basic-qc-withoutFID
  --fam moba.hm3.withoutFID.fam
  --singularity-bind "$COMORMENT/containers/reference:/REF:ro,/cluster/projects/p697:/cluster/projects/p697"
  --covar PC1 PC2 PC3 PC4 PC5 PC6 PC7 PC8 PC9 PC10 genotyping_batch YOB Sex
  --variance-standardize
  ```

Now GWAS analysis  can be triggered as follows:
```
mkdir out
export PYTHON="singularity exec --home $PWD:/home $SIF/python3.sif python"

$PYTHON gwas.py gwas --argsfile moba.bed.argsfile --pheno height --analysis plink2 --out out/run1 | bash
$PYTHON gwas.py gwas --argsfile moba.bed.argsfile --pheno height --analysis regenie --out out/run2 | bash
$PYTHON gwas.py gwas --argsfile moba.bed.argsfile --pheno AnyF32 AnyF33 AnyFdep --analysis plink2 --out out/run3 | bash
$PYTHON gwas.py gwas --argsfile moba.bed.argsfile --pheno AnyF32 AnyF33 AnyFdep --analysis regenie --out out/run4 | bash

$PYTHON gwas.py gwas --argsfile moba.bgen.argsfile --pheno height --analysis plink2 --out out/run5 | bash
$PYTHON gwas.py gwas --argsfile moba.bgen.argsfile --pheno height --analysis regenie --out out/run6 | bash
$PYTHON gwas.py gwas --argsfile moba.bgen.argsfile --pheno AnyF32 AnyF33 AnyFdep --analysis plink2 --out out/run7 | bash
$PYTHON gwas.py gwas --argsfile moba.bgen.argsfile --pheno AnyF32 AnyF33 AnyFdep --analysis regenie --out out/run8 | bash
```

Resulting files (summary statistics):
```
run1_height.plink2.gz, 
run2_height.regenie.gz
run3_AnyF32.plink2.gz, run3_AnyF33.plink2.gz, run3_AnyFdep.plink2.gz
run4_AnyF32.regenie.gz, run4_AnyF33.regenie.gz, run4_AnyFdep.regenie.gz
run5_height.plink2.gz, 
run6_height.regenie.gz
run7_AnyF32.plink2.gz, run7_AnyF33.plink2.gz, run7_AnyFdep.plink2.gz
run8_AnyF32.regenie.gz, run8_AnyF33.regenie.gz, run8_AnyFdep.regenie.gz
```

Few notes:
* ``gwas.py gwas`` prints a lot of informational messages to standard error, but when it comes to standard output, it only the ``sbatch`` commands that needs to be executed. Therefore, by piping it's output ``| bash`` we immediately submit the jobs to the cluster
* Custom ``--singularity-bind`` command is needed because some of the input files (namely ``98k-ec-eur-fin-batch-basic-qc-withoutFID.[bed/bim/fam]``) are located outside of the current folder. Also note that even if you create symbolic links to the current folder, it's still important to map folders containing the actual data files into container, otherwise symbolic links won't work
* ``--fam`` argument explicitly pointing to ``moba.hm3.withoutFID.fam`` is optional, but it clarify which individuals are contained in genetic data when for example ``--bgen-test`` is used instead of ``--bed-test``. Note that ``gwas.py`` need to know what individuals are available in the genotype files, to match them with ``--pheno-file`` argument. As ofnow ``gwas.py``can't read ``.sample`` file, and require a ``.fam`` to extract the list of individuals. If neither ``--bed-fit`` nor ``-bed-test`` arguments are provided, the ``gwas.py`` will require ``-fam`` file.

After all jobs are executed the following commands allow to make QQ plots and manhattan plots:
```
ls out/*gz | parallel -j16 $PYTHON gwas.py qq --sumstats {} --out {}.qq.png
ls out/*gz | parallel -j16 $PYTHON gwas.py manh --sumstats {} --out {}.manh.png
```

Also, I've combined QQ plots using (combine_figures.py)[out/combine_figures.py] script.
Some resulting figures:

* Manhattan plot for height GWAS:
  ![run1_height.plink2.gz.manh.png](https://raw.githubusercontent.com/comorment/containers/main/usecases/gwas_real/run1_height.plink2.gz.manh.png) -  
* Combined QQ plot for height GWAS:
  ![height.qq.png](https://raw.githubusercontent.com/comorment/containers/main/usecases/gwas_real/height.qq.png)
* Combined QQ plot for depression GWAS:
  ![dep.qq.png](https://raw.githubusercontent.com/comorment/containers/main/usecases/gwas_real/dep.qq.png)