# GWAS appplication using OPENSNP data

This usecase describe how to run GWAS analysis with [plink2](https://www.cog-genomics.org/plink/2.0/) and [regenie](https://rgcgithub.github.io/regenie/) on binary and quantitative traits for [opensnp](https://github.com/comorment/opensnp) data.

This will use genotype and phenotype data formatted according to [CoMorMent specifications](./../specifications/README.md),
and the helper [gwas.py](https://github.com/comorment/containers/blob/main/scripts/gwas/gwas.py) script that reads the phenotype data,
extracts user-defined subset of phenotypes and covariates,
and prepares the scripts or SLURM jobs for ``plink2`` and ``regenie`` analysis.
In this demo, we're using example data from [comorment/opensnp](https://github.com/comorment/opensnp) folder.
Take a moment to look at the [phenotype file](https://github.com/comorment/opensnp/blob/main/pheno/pheno.csv) and it's [dictionary file](https://github.com/comorment/opensnp/blob/main/pheno/pheno.dict) which will be used throughout this application.
For genetic data, we're using imputed hard genotype calls in plink format, with ``n=6500`` individuals ([opensnp_hm3.fam](https://github.com/comorment/opensnp/tree/main/imputed/opensnp_hm3.fam)) and ``m=500`` SNPs across three chromosomes ([opensnp_hm3.bim](https://github.com/comorment/opensnp/tree/main/imputed/opensnp_hm3.bim)). Note: if you click on the above links and see ``Stored with Git LFS`` message on the github pages, you'll only need to click the ``View raw`` link and it should show the content of the file you're trying to see.

Now, to run this use case, just copy the [gwas.py](https://github.com/comorment/containers/blob/main/scripts/gwas/gwas.py) script and [config.yaml](https://github.com/comorment/containers/blob/main/scripts/gwas/config.yaml) file from ``$COMORMENT/containers/scripts/gwas.py`` into your current folder, and run the following commands (where ``run1`` gives example of case/control GWAS with plink2, while ``run2`` is an example for quantitative traits with regenie; these choices are independent - you could run case/control GWAS with regenie, and quantitative trait with plink2 by choosing --analysis argument accordingly; the meaning of the ``/REF`` and ``$SIF`` is explained in the [INSTALL](../INSTALL.md) section of the main README file, as well as the way you are expected to setup the ``SINGULARITY_BIND`` variable; 

```
singularity exec --home $PWD:/home $COMORMENT/containers/singularity/python3.sif python /home/gwas.py gwas \
--geno-file /REF3/imputed/opensnp_hm3.bed \
--geno-fit-file /REF3/imputed/opensnp_hm3.bed \
--pheno-file /REF3/pheno/pheno.csv --dict-file /REF3/pheno/pheno.dict  --pheno height_cm \
--covar sex batch PC1 PC2 \
--analysis plink2 figures --out /home/opensnp_hm3_plink \
--chr2use 1-22 \
--variance-standardize \
--maf 0.1 --geno 0.5 --hwe 0.01 \
--config /home/config.yaml 

singularity exec --home $PWD:/home $COMORMENT/containers/singularity/python3.sif python /home/gwas.py gwas \
--geno-file /REF3/imputed/opensnp_hm3.bed \
--geno-fit-file /REF3/imputed/opensnp_hm3.bed \
--pheno-file /REF3/pheno/pheno.csv --dict-file /REF3/pheno/pheno.dict  --pheno height_cm \
--covar sex batch PC1 PC2 \
--analysis regenie figures --out /home/opensnp_hm3_regenie \
--chr2use 1-22 \
--variance-standardize \
--maf 0.1 --geno 0.5 --hwe 0.01 \
--config /home/config.yaml 

```

Off note, if you configured a local python3 environment (i.e. if you can use python without containers), and you have basic packages such as numpy, scipy and pandas, you may use ``gwas.py`` script directly - i.e. drop ``singularity exec --home $PWD:/home $SIF/python3.sif`` part of the above comand. Otherwise, we recommend to export ``$PYTHON`` variable as follows: ``export PYTHON="singularity exec --home $PWD:/home $SIF/python3.sif python"``, and then it e.g. like this: ``$PYTHON gwas.py ...``.

Note that we are using some flags to call files and options such as: what phenotype file to use (``--pheno-file``), which chromosome labels to use (``--chr2use``), which genotype file to use in fitting the regenie model (``--geno-fit-file``) as well as genotype file to use when testing for associations (``--geno-file``); the ``--variance-standardize`` will apply linear transformation to all continuous phenotypes so that they became zero mean and unit variance, similar [--variance-standardize](https://www.cog-genomics.org/plink/2.0/data#variance_standardize) argument in plink2. The ``--info-file`` points to a file with two columns, ``SNP`` and ``INFO``, listing imputation info score for the  variants. This is optional and only needed for the ``--info`` threshold to work. Other available QC filters include ``--maf``, ``--geno`` and ``--hwe``.


In the above example ``--geno-fit-file`` points to the same file as ``--geno-file``, which is NOT how things should be done in a real application. ``--geno-fit-file`` should point to a single genetic file (merged across chromosomes),
constrained to approximately less than a million SNPs, for example constrain to genotyped SNPs, or constrain to  the set of HapMap3 SNPs. For a real example, see [gwas_real.md](./gwas_real.md).

Adding ``figures`` to the ``--analysis`` argument trigger post-GWAS scripts to generate manhattan / qq plots.

Take a look at the resulting [opensnp_hm3_plink.log](https://github.com/comorment/containers/blob/gwas_opensnp/usecases/gwas_opensnp/opensnp_hm3_plink.log) and [opensnp_hm3_regenie.log](https://github.com/comorment/containers/blob/gwas_opensnp/usecases/gwas_opensnp/opensnp_hm3_regenie.log), to see if gwas.py was executed as intended.
For this small-scale demo example, you could execute the actual GWAS locally on your machine as follows:

```
export REGENIE="singularity exec --home $PWD:/home $SIF/gwas.sif regenie"
export PLINK2="singularity exec --home $PWD:/home $SIF/gwas.sif plink2"
export PYTHON="singularity exec --home $PWD:/home $SIF/python3.sif python"
export SAIGE="singularity exec --home $PWD:/home $SIF/saige.sif "
export RSCRIPT="singularity exec --home $PWD:/home $SIF/r.sif Rscript"

cat opensnp_hm3_plink_cmd.sh | bash
cat opensnp_hm3_regenie_cmd.sh | bash
```

Otherwise you need to submit the SLURM jobs, generated by gwas.py script.  These jobs must be executed in order, i.e. ``.2.job`` need to wait for ``.1.job``, and ``.3.job`` need to wait for ``.2.job``. You still can submit all jobs at once, but use SLURM's dependency management as described [here](https://stackoverflow.com/questions/19960332/use-slurm-job-id):

```
RES=$(sbatch /home/opensnp_hm3_plink.1.job)
RES=$(sbatch --dependency=afterok:${RES##* } /home/opensnp_hm3_plink.2.job)
RES=$(sbatch --dependency=afterok:${RES##* } /home/opensnp_hm3_plink.3.job)
```

To customize parameters in the header of the slurm jobs, use ``--slurm-job-name``, ``--slurm-account``, ``--slurm-time``, ``--slurm-cpus-per-task``, ``--slurm-mem-per-cpu`` arguments of the ``gwas.py`` script (and let us know if there is anything else you need to customize!).
Further, you may need to customize ``--module-load`` argument, which by default loads ``singularity/3.7.1`` module.
Feel free to replace this with other version of singularity, or list multiple modules if you need to load something else in addition to singularity.
(a handy trick: if you want to explicily avoid loading the singularity module, because it's pre-installed, but don't need any other modules, you may add another irrelevant module just to overwrite the default ``--module-load`` argument).
Finally, you need to customize ``--comorment-folder`` folder containing a ``containers`` subfolder with a full copy of <https://github.com/comorment/containers>.

For more results, see [gwas_demo](https://github.com/comorment/containers/blob/main/usecases/gwas_demo) folder. Main results are the following GWAS summary statistics:

```
opensnp_hm3_plink_height_cm.gz
opensnp_hm3_plink_regenie_cm.gz
```

Each file is merged across all chromosomes, and has a minimal set of columns (``SNP, CHR, BP, A1, A2, N, Z, BETA, SE, PVAL``), as described in the [specification](./../specifications/sumstats_specification.md). And corresponding qq and manhattan plots are created





