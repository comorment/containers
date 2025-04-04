# GWAS demo

This usecase describe how to run a demo GWAS analysis with [plink2](https://www.cog-genomics.org/plink/2.0/) and [regenie](https://rgcgithub.github.io/regenie/).
Further down in this README file you also have an example of how to run [PRSice2](https://www.prsice.info/) software to compute polygenic risk scores.

This will use genotype and phenotype data formatted according to [CoMorMent specifications](./../specifications/README.md),
and the helper [gwas.py](https://github.com/comorment/containers/blob/main/scripts/gwas/gwas.py) script that reads the phenotype data,
extracts user-defined subset of phenotypes and covariates,
and prepares the scripts or SLURM jobs for ``plink2`` and ``regenie`` analysis.
In this demo we're using example data from [reference/examples/regenie](https://github.com/comorment/containers/blob/main/reference/examples/regenie) folder.
Take a moment to look at the [phenotype file](https://github.com/comorment/containers/blob/main/reference/examples/regenie/example_3chr.pheno) and it's [dictionary file](https://github.com/comorment/containers/blob/main/reference/examples/regenie/example_3chr.pheno.dict) which will be used throughout this example.
For genetic data, we're using hard genotype calles in plink format, with ``n=500`` individuals ([example_3chr.fam](https://github.com/comorment/containers/blob/main/reference/examples/regenie/example_3chr.fam)) and ``m=500`` SNPs across three chromosomes ([example_3chr.bim](https://github.com/comorment/containers/blob/main/reference/examples/regenie/example_3chr.bim)). Note: if you click on the above links and see ``Stored with Git LFS`` message on the github pages, you'll only need to click the ``View raw`` link and it should show the content of the file you're trying to see.

Now, to run this use case, just copy the [gwas.py](https://github.com/comorment/containers/blob/main/scripts/gwas/gwas.py) script and [config.yaml](https://github.com/comorment/containers/blob/main/scripts/gwas/config.yaml) file from ``$COMORMENT/containers/scripts/gwas.py`` into your current folder, and run the following commands (where ``run1`` gives example of case/control GWAS with plink2, while ``run2`` is an example for quantitative traits with regenie; these choices are independent - you could run case/control GWAS with regenie, and quantitative trait with plink2 by choosing --analysis argument accordingly; the meaning of the ``/REF`` and ``$SIF`` is explained in the [INSTALL](../INSTALL.md) section of the main README file, as well as the way you are expected to setup the ``APPTAINER_BIND`` variable; if you are confused by ``--argsfile``, read further down below on this page where it's explained in detail):

```
apptainer exec --home $PWD:/home $SIF/python3.sif python gwas.py gwas \
--argsfile /REF/examples/regenie/example_3chr.argsfile \
--pheno CASE CASE2 --covar PC1 PC2 BATCH --analysis plink2 figures --out run1_plink2 

apptainer exec --home $PWD:/home $SIF/python3.sif python gwas.py gwas \
--argsfile /REF/examples/regenie/example_3chr.argsfile \
--pheno PHENO PHENO2 --covar PC1 PC2 BATCH --analysis regenie figures --out run2_regenie
```

Off note, if you configured a local python3 environment (i.e. if you can use python without containers), and you have basic packages such as numpy, scipy and pandas, you may use ``gwas.py`` script directly - i.e. drop ``apptainer exec --home $PWD:/home $SIF/python3.sif`` part of the above comand. Otherwise, we recommend to export ``$PYTHON`` variable as follows: ``export PYTHON="apptainer exec --home $PWD:/home $SIF/python3.sif python"``, and then it e.g. like this: ``$PYTHON gwas.py ...``.

We're going to use ``--argsfile`` argument pointing to [example_3chr.argsfile](https://github.com/comorment/containers/blob/main/reference/examples/regenie/example_3chr.argsfile) to specify some lengthy flags used across all invocations of the ``gwas.py`` scripts in this tutorial. It defines what phenotype file to use (``--pheno-file``), which chromosome labels to use (``--chr2use``), which genotype file to use in fitting the regenie model (``--geno-fit-file``) as well as genotype file to use when testing for associations (``--geno-file``); the ``--variance-standardize`` will apply linear transformation to all continuous phenotypes so that they became zero mean and unit variance, similar [--variance-standardize](https://www.cog-genomics.org/plink/2.0/data#variance_standardize) argument in plink2. The ``--info-file`` points to a file with two columns, ``SNP`` and ``INFO``, listing imputation info score for the  variants. This is optional and only needed for the ``--info`` threshold to work. Other available QC filters include ``--maf``, ``--geno`` and ``--hwe``.

```
# example_3chr.args file defines the following arguments:
--pheno-file /REF/examples/regenie/example_3chr.pheno 
--geno-fit-file /REF/examples/regenie/example_3chr.bed
--geno-file /REF/examples/regenie/example_3chr.bed
--info-file /REF/examples/regenie/example_3chr.info --info 0.8
--chr2use 1-3
--variance-standardize
--maf 0.1        # normally 0.01 or lower
--geno 0.5       # normally 0.98 or higher
--hwe 0.01       # normaly 1e-10 or lower
```

In the above example ``--geno-fit-file`` points to the same file as ``--geno-file``, which is NOT how things should be done in a real application. ``--geno-fit-file`` should point to a single genetic file (merged across chromosomes),
constrained to approximately less than a million SNPs, for example constrain to genotyped SNPs, or constrain to  the set of HapMap3 SNPs. For a real example, see [gwas_real.md](./gwas_real.md).

Adding ``figures`` to the ``--analysis`` argument trigger post-GWAS scripts to generate manhattan / qq plots.

Take a look at the resulting [run1.log](https://github.com/comorment/containers/blob/main/usecases/gwas_demo/run1.log) and [run2.log](https://github.com/comorment/containers/blob/main/usecases/gwas_demo/run2.log), to see if gwas.py was executed as intended.
For this small-scale demo example, you could execute the actual GWAS locally on your machine as follows:

```
export REGENIE="apptainer exec --home $PWD:/home $SIF/gwas.sif regenie"
export PLINK2="apptainer exec --home $PWD:/home $SIF/gwas.sif plink2"
export PYTHON="apptainer exec --home $PWD:/home $SIF/python3.sif python"
export RSCRIPT="apptainer exec --home $PWD:/home $SIF/r.sif Rscript"

cat run1_plink2_cmd.sh | bash
cat run2_regenie_cmd.sh | bash
```

Otherwise you need to submit the SLURM jobs, generated by gwas.py script. There are two jobs for ``plink2`` analysis: ``run1_plink2.1.job`` and ``run1_plink2.2.job``, and three jobs for ``regenie`` analysis: ``run1_regenie.1.job``, ``run1_regenie.2.job``, ``run1_regenie.3.job`` (and similarly for ``run2``). These jobs must be executed in order, i.e. ``.2.job`` need to wait for ``.1.job``, and ``.3.job`` need to wait for ``.2.job``. You still can submit all jobs at once, but use SLURM's dependency management as described [here](https://stackoverflow.com/questions/19960332/use-slurm-job-id):

```
RES=$(sbatch run1_plink2.1.job)
RES=$(sbatch --dependency=afterany:${RES##* } run1_plink2.2.job)
RES=$(sbatch run2_regenie.1.job)
RES=$(sbatch --dependency=afterany:${RES##* } run2_regenie.2.job)
RES=$(sbatch --dependency=afterany:${RES##* } run2_regenie.3.job)
```

To customize parameters in the header of the slurm jobs, use ``--slurm-job-name``, ``--slurm-account``, ``--slurm-time``, ``--slurm-cpus-per-task``, ``--slurm-mem-per-cpu`` arguments of the ``gwas.py`` script (and let us know if there is anything else you need to customize!).
Further, you may need to customize ``--module-load`` argument, which by default loads ``singularity/3.7.1`` module.
Feel free to replace this with other version of Singularity/Apptainer, or list multiple modules if you need to load something else in addition to Singularity.
(a handy trick: if you want to explicily avoid loading the Singularity module, because it's pre-installed, but don't need any other modules, you may add another irrelevant module just to overwrite the default ``--module-load`` argument).
Finally, you need to customize ``--comorment-folder`` folder containing a ``containers`` subfolder with a full copy of <https://github.com/comorment/containers>.

For more results, see [gwas_demo](https://github.com/comorment/containers/blob/main/usecases/gwas_demo) folder. Main results are the following GWAS summary statistics:

```
run1_plink2_CASE.gz
run1_plink2_CASE2.gz
run2_regenie_PHENO.gz
run2_regenie_PHENO2.gz
```

Each file is merged across all chromosomes, and has a minimal set of columns (``SNP, CHR, BP, A1, A2, N, Z, BETA, SE, PVAL``), as described in the [specification](./../specifications/sumstats_specification.md).

It is also supported to run GWAS on dosages stored in BGEN format, instead of using hard call phenotypes from plink's bed/bim/fam format.
If you have genotypes formatted this way, the only change you need is to change ``--geno-file`` file, pointing it to ``.bgen``  (or a ``.vcf``) file
as in this example: [example_3chr_bgen.argsfile](https://github.com/comorment/containers/blob/main/reference/examples/regenie/example_3chr_bgen.argsfile).
It is expected that ``.bgen`` has corresponding ``.sample`` and ``.bgen.bgi`` files.
Similarly, for a ``.vcf`` (or ``.vcf.gz``) formats you need to generate ``.tbi`` and/or ``.csi`` index files (see <https://www.biostars.org/p/59492/>).

To see more info about ``gwas.py`` arguments, try this:

```
>apptainer exec --home $PWD:/home $SIF/python3.sif python gwas.py gwas --help
```

Key arguments are also described below,
but the actual ``--help`` output will describe more arguments - we don't copy this information here since gwas.py tool is being actively developed.

```
usage: gwas.py gwas [-h] [--out OUT] 
                    [--geno-file GENO_FILE] [--geno-fit-file GENO_FIT_FILE] [--fam FAM]
                    [--chr2use CHR2USE]                    
                    [--pheno-file PHENO_FILE] [--dict-file DICT_FILE]
                    [--covar COVAR [COVAR ...]]
                    [--variance-standardize [VARIANCE_STANDARDIZE [VARIANCE_STANDARDIZE ...]]]
                    [--pheno PHENO [PHENO ...]] [--pheno-na-rep PHENO_NA_REP]
                    [--analysis {plink2,regenie,figures} [{plink2,regenie,figures} ...]]

  --analysis {plink2,regenie,figures} [{plink2,regenie,figures} ...]

  --out OUT             prefix for the output files (<out>.covar, <out>.pheno, etc)
  --geno-file GENO      required argument pointing to a genetic file: (1)
                        plink's .bed file, or (2) .bgen file, or (3) .pgen
                        file, or (4) .vcf file. Note that a full name of .bed
                        (or .bgen, .pgen, .vcf) file is expected here.
                        Corresponding files should have standard names, e.g.
                        for plink's format it is expected that .fam and .bim
                        file can be obtained by replacing .bed extension
                        accordingly. supports '@' as a place holder for
                        chromosome labels
  --geno-fit-file GENO_FIT_FILE
                        genetic file to use in a first stage of mixed effect
                        model. Expected to have the same set of individuals as
                        --geno-file (this is NOT validated by the gwas.py script,
                        and it is your responsibility to follow this
                        assumption). Optional for standard association
                        analysis (e.g. if for plink's glm). The argument
                        supports the same file types as the --geno-file argument.
                        Noes not support '@' (because mixed effect tools
                        typically expect a single file at the first stage.
  --fam FAM             an argument pointing to a plink's .fam file, use by
                        gwas.py script to pre-filter phenotype information
                        (--pheno) with the set of individuals available in the
                        genetic file (--geno-file / --geno-fit-file). Optional when
                        either --geno-file or --geno-fit-file is in plink's format,
                        otherwise required - but IID in this file must be
                        consistent with identifiers of the genetic file.
  --chr2use CHR2USE     Chromosome ids to use (e.g. 1,2,3 or 1-4,12,16-20).
                        Used when '@' is present in --geno-file, and allows to
                        specify for which chromosomes to run the association
                        testing.
  --pheno-file PHENO_FILE
                        phenotype file, according to CoMorMent spec
  --dict-file DICT_FILE
                        phenotype dictionary file, defaults to <pheno>.dict
  --covar COVAR [COVAR ...]
                        covariates to control for (must be columns of the
                        --pheno-file); individuals with missing values for any
                        covariates will be excluded not just from <out>.covar,
                        but also from <out>.pheno file
  --variance-standardize [VARIANCE_STANDARDIZE [VARIANCE_STANDARDIZE ...]]
                        the list of continuous phenotypes to standardize
                        variance; accept the list of columns from the --pheno
                        file (if empty, applied to all); doesn't apply to
                        dummy variables derived from NOMINAL or BINARY
                        covariates.
  --pheno PHENO [PHENO ...]
                        target phenotypes to run GWAS (must be columns of the
                        --pheno-file

Filtering options:
  --info-file INFO_FILE
                        File with SNP and INFO columns. Values in SNP column must be unique.
  --info INFO           threshold for filtering on imputation INFO score
  --maf MAF             threshold for filtering on minor allele frequency
  --hwe HWE             threshold for filtering on hardy weinberg equilibrium p-value
  --geno GENO           threshold for filtering on per-variant missingness rate)
```

## How to run PRSice2 software

Computing polygenic risk scores require (and testing how they work on a known phenotype data)  
require a similar set input to what you use for running a GWAS analysis,
with an addition of an ``--sumstats`` argument that points to summary statistics.

You can run an example as follows:

```
apptainer exec --home $PWD:/home $SIF/python3.sif python gwas.py pgrs \
  --sumstats run1_plink2_CASE.gz \
  --geno-file /REF/examples/regenie/example_3chr.bed \
  --geno-ld-file /REF/examples/regenie/example_3chr.bed \
  --pheno-file /REF/examples/regenie/example_3chr.pheno --pheno CASE CASE2 --covar PC1 PC2 BATCH \
  --chr2use 1-3 --variance-standardize \
  --analysis prsice2 --out run3_prsice2 \
  --keep-ambig  # only for a purpose of this demo; exclude for real analysis (unlee you know why it's there)

export PRSICE2="apptainer exec --home $PWD:/home $SIF/gwas.sif PRSice_linux"

cat run3_prsice2_cmd.sh | bash
```

The resulting ``run3_prsice2.summary`` file looks as follows,
which is reasonable: PGRS computed based on CASE phenotypes explains CASE phenotype better (P=1.88e-09) than CASE2 phenotype.

```
Phenotype Set Threshold PRS.R2 Full.R2 Null.R2 Prevalence Coefficient Standard.Error P Num_SNP
CASE Base 0.9 0.064886 0.818532 0.753646 - 92.0264 15.3183 1.88278e-09 50
CASE2 Base 0.9 5.09224e-05 0.0334905 0.0334396 - 0.93301 7.02908 0.894402 50
```

For more information, see this:

```
apptainer exec --home $PWD:/home $SIF/python3.sif python gwas.py pgrs --help
```
