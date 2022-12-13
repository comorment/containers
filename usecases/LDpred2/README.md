# LDpred2

The files in this directory exemplifies how to run the LDpred2 analysis using the ``bigsnpr`` R library, using [ldpred2.R](ldpred2.R) script developed by Andreas Jangmo, Espen Hagen and Oleksandr Frei. The script is based on this [tutorial](https://privefl.github.io/bigsnpr/articles/LDpred2.html).
The LDpred2 method is explained in the publication:

- Florian Privé, Julyan Arbel, Bjarni J Vilhjálmsson, LDpred2: better, faster, stronger, Bioinformatics, Volume 36, Issue 22-23, 1 December 2020, Pages 5424–5431, https://doi.org/10.1093/bioinformatics/btaa1029

## Prerequisites

This README assumes the following two repositories are git cloned.

* http://github.com/comorment/containers
* https://github.com/comorment/ldpred2_ref

We also assume the following commands are executed from the current folder
(the one containing [createBackingFile.R](createBackingFile.R) and [ldpred2.R](ldpred2.R) scripts).

<!--

LDpred2 uses genetic maps from [1000 genomes](https://github.com/joepickrell/1000-genomes-genetic-maps) to convert each SNPs physical position to genomic position.
LDpred2 will try to download these which will cause an error without an internet connection. To prevent this behavior, these should be downloaded manually and
the folder where they are stored should be passed to the LDpred2-script using the flag ``--dir-genetic-maps your-genetic/maps-directory``.
 -->

## Running LDpred2 analysis - synthetic example (chr21 and chr22)

The following set of commands gives an example of how to apply LDpred2 on a synthetic example generated [here](ldpred2_simulations.ipynb). This only uses chr21 and chr22, so it runs much faster than previous example.
This example require only  ``map_hm3_plus.rds``, ``ldref_hm3_plus/LD_with_blocks_chr21.rds``, and ``ldref_hm3_plus/LD_with_blocks_chr22.rds`` files [ldpred2_ref](https://github.com/comorment/ldpred2_ref) repository, so you may download them separately rather then clone the entire repo.

```
# point to input/output files
export fileGeno=/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1.bed
export fileGenoRDS=g1000_eur_chr21to22_hm3rnd1.rds
export filePheno=/REF/examples/ldpred2/simu.pheno
export fileSumstats=/REF/examples/ldpred2/trait1.sumstats.gz
export fileOut=simu
export colPheno=trait1

# set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT=<path/to/comorment>
export SIF=$COMORMENT/containers/singularity
export REFERENCE=$COMORMENT/containers/reference
export LDPRED2_REF=$COMORMENT/ldpred2_ref
export SINGULARITY_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref

export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"

# convert genotype to LDpred2 format
$RSCRIPT createBackingFile.R $fileGeno $fileGenoRDS

$RSCRIPT ldpred2.R --ldpred-mode inf \
 --chr2use 21 22 --file-pheno $filePheno --col-pheno $colPheno \
 --geno-file $fileGenoRDS --sumstats $fileSumstats --out $fileOut.inf

$RSCRIPT ldpred2.R --ldpred-mode auto \
 --chr2use 21 22 --file-pheno $filePheno --col-pheno $colPheno  \
 --geno-file $fileGenoRDS --sumstats $fileSumstats --out $fileOut.auto
```

## Running LDpred2 analysis - height example

The following set of commands gives an example of how to apply LDpred2 on a demo height data:
```
# point to input/output files
export fileGeno=/REF/examples/prsice2/EUR.bed
export fileGenoRDS=EUR.rds
export filePheno=/REF/examples/prsice2/EUR.height
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=Height
export colPheno=Height

# set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT=<path/to/comorment>
export SIF=$COMORMENT/containers/singularity
export REFERENCE=$COMORMENT/containers/reference
export LDPRED2_REF=$COMORMENT/ldpred2_ref
export SINGULARITY_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref

export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"

# convert genotype to LDpred2 format
$RSCRIPT createBackingFile.R $fileGeno $fileGenoRDS

# Generate PGS usign LDPRED-inf
$RSCRIPT ldpred2.R \
 --ldpred-mode inf \
 --file-pheno $filePheno --col-pheno $colPheno \
 --col-stat OR --col-stat-se SE --stat-type OR \
 --geno-file $fileGenoRDS --sumstats $fileSumstats --out $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT ldpred2.R \
 --ldpred-mode auto \
 --file-pheno $filePheno --col-pheno $colPheno \
 --col-stat OR --col-stat-se SE --stat-type OR \
 --geno-file $fileGenoRDS --sumstats $fileSumstats --out $fileOut.auto
```

## Output

The main LDpred2 output files are ``Height.score.inf`` and ``Height.score.auto`` put in this directory. 
The files are text files with tables formatted as 
```
FID IID Height score
HG00096 HG00096 169.132168767547 -1.49668824138468e+100
HG00097 HG00097 171.256258630279 -3.37195056659838e+99
HG00099 HG00099 171.534379938588 -5.02262306623802e+100
HG00100 HG00100 NA -1.8332542097235e+100
...
```

The script will also output ``.bk`` and ``.rds`` binary files with prefix ``EUR`` in this directory.

## Handling missing genotypes

By default LDpred2.R script will impute missing genotypes bigsnpr's ``mean0`` method from [snp_fastImputeSimple](https://www.rdocumentation.org/packages/bigsnpr/versions/1.6.1/topics/snp_fastImputeSimple).
This is done because otherwise bigsnpr returns an error (``Error: You can't have missing values in 'X'.``).
Imputing missing values, however, can be very slow, and eventually we want to include this in ``createBackingFile.R`` step, so this is done once, rather then as part of every ``LDpred2.R`` invocation.

For now, as a workaround, you may fall back to plink's ``fill-missing-a2`` option, then
re-run ``createBackingFile.R``, and include ``--geno-impute skip`` in your ``LDpred2.R`` command:

```
plink --bfile EUR --fill-missing-a2 --make-bed --out EUR.nomiss
$RSCRIPT createBackingFile.R EUR.nomiss.bed EUR.nomiss.rds
$RSCRIPT ldpred2.R --geno-file EUR.nomiss.rds --geno-impute skip ...
```



## Slurm job

On an HPC resource the same analysis can be run by first writing a job script [run_ldpred2_slurm.job](run_ldpred2_slurm.job).
In order to run the job, first make sure that the ``SBATCH_ACCOUNT`` environment variable is defined:
```
export SBATCH_ACCOUNT=project_ID
```
where ``project_ID`` is the granted project that compute time is allocated. 
As above, ``<path/to/containers`` should point to the cloned ``containers`` repository. 
Entries like ``--partition=normal`` may also be adapted for different HPC resources.
Then, the job can be submitted to the queue by issuing ``sbatch run_ldpred2_slurm.job``. 
The status of running jobs can usually be enquired by issuing ``squeue -u $USER``. 
