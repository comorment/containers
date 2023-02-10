# LDpred2

The files in this directory exemplifies how to run the LDpred2 analysis using the ``bigsnpr`` R library, using [ldpred2.R](ldpred2.R) script developed by Andreas Jangmo, Espen Hagen and Oleksandr Frei. The script is based on this [tutorial](https://privefl.github.io/bigsnpr/articles/LDpred2.html).
The LDpred2 method is explained in the publication:

- Florian Privé, Julyan Arbel, Bjarni J Vilhjálmsson, LDpred2: better, faster, stronger, Bioinformatics, Volume 36, Issue 22-23, 1 December 2020, Pages 5424–5431, <https://doi.org/10.1093/bioinformatics/btaa1029>

## Prerequisites

This README assumes the following two repositories are cloned using [git](https://git-scm.com):

- <http://github.com/comorment/containers>
- <https://github.com/comorment/ldpred2_ref>

We also assume the following commands are executed from the current folder
(the one containing [createBackingFile.R](createBackingFile.R) and [ldpred2.R](ldpred2.R) scripts).

### Note on filtering of genotype data

The current version of these scripts conduct no filtering of genotype data (e.g., minor allele frequency, imputation quality) prior to calculating linkage disequillibrium or polygenic scores.
This should be done for polygenic score analyses intended for publication.

### Optional: Estimating linkage disequillibrium (LD)

LDpred2 uses the LD structure when calculating polygenic scores. By default, the LDpred2.R script uses LD structure based on European samples provided by the LDpred2 authors.
To instead calculate LD on your own, the ``calculateLD.R`` script can be used. The output from this script can then be used as input to ``LDpred2.R`` (with the optional ``--ld-file`` flag).

To use ``calculateLD.R`` you need to download genetic maps from [1000 genomes](https://github.com/joepickrell/1000-genomes-genetic-maps) in order to convert each SNPs physical position to genomic position.
If you don't provide these files, LDpred2 will try to download these automatically which will cause an error without an internet connection. To prevent this behavior, these should be downloaded manually and
the folder where they are stored should be passed to the LDpred2-script using the flag ``--dir-genetic-maps your-genetic/maps-directory``.

Two parameters that can be passed to ``calculateLD.R`` and affect the LD estimation are ``--window-size`` (region around index SNP in basepairs) and ``--thres-r2`` (threshold for including
a SNP correlation in the LD). The default for ``--thres-r2`` is 0 in ``bigsnpr::snp_cor``, but ``calculateLD.R`` has a default of 0.01. 

The example script below will output one file per chromosome (``output/ld-chr-1.rds``, ``output/ld-chr-2.rds``, ...) and a "map" indicating the SNPs used in LD estimation (``output/map.rds``).
The flag ``--sumstats`` can be used to filter SNPs to use where the first argument is the file and the second the column name or position of the RSID of the SNP (ie it does not neeed to be a proper
sumstats file).

```
# point to input/output files
export fileGeno=/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1.bed
export fileGenoRDS=g1000_eur_chr21to22_hm3rnd1.rds
export filePheno=/REF/examples/ldpred2/simu.pheno
export fileSumstats=/REF/examples/ldpred2/trait1.sumstats.gz
export fileOutLD=ld-chr-@.rds
export fileOutLDMap=ld-map.rds

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

# create genetics maps directory, download and process
mkdir -p 100genomes/maps
$RSCRIPT calculateLD.R --geno-file-rds $fileGenoRDS \
 --dir-genetic-maps 100genomes/maps \
 --chr2use 21 22  --sumstats $fileSumstats SNP \
 --file-ld-blocks $fileOutLD --file-ld-map $fileOutLDMap
```

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

# run LDpred2 infinitesimal mode
$RSCRIPT ldpred2.R --ldpred-mode inf \
 --chr2use 21 22 \
 --file-pheno $filePheno \
 --col-pheno $colPheno \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.inf
 
# run LDpred2 automatic mode
$RSCRIPT ldpred2.R --ldpred-mode auto \
 --chr2use 21 22 \
 --file-pheno $filePheno \
 --col-pheno $colPheno  \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.auto
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
 --file-pheno $filePheno \
 --col-pheno $colPheno \
 --col-stat OR \
 --col-stat-se SE \
 --stat-type OR \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT ldpred2.R \
 --ldpred-mode auto \
 --file-pheno $filePheno \
 --col-pheno $colPheno \
 --col-stat OR \
 --col-stat-se SE \
 --stat-type OR \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.auto
```

## Output

The main LDpred2 output files are ``Height.score.inf`` and ``Height.score.auto`` put in this directory.
The files are text files with tables formatted as

```
FID IID Height score
HG00096 HG00096 169.132168767547 -0.733896062346436
HG00097 HG00097 171.256258630279 0.688693127521599
HG00099 HG00099 171.534379938588 0.203279440703434
HG00100 HG00100 NA 0.0890499485064315
...
```

The script will also output ``.bk`` and ``.rds`` binary files with prefix ``EUR`` in this directory.

## Handling missing genotypes

By default the LDpred2.R script will impute missing genotypes bigsnpr's ``mean0`` method from [snp_fastImputeSimple](https://www.rdocumentation.org/packages/bigsnpr/versions/1.6.1/topics/snp_fastImputeSimple).
This is done because otherwise bigsnpr returns an error (``Error: You can't have missing values in 'X'.``).
Imputing missing values, however, can be very slow, and eventually we [want](https://github.com/comorment/containers/pull/117#issuecomment-1409985505) to include this in ``createBackingFile.R`` step, so this is done once, rather then as part of every ``LDpred2.R`` invocation.

For now, as a workaround, you may fall back to plink's ``fill-missing-a2`` option, then
re-run ``createBackingFile.R``, and include ``--geno-impute skip`` in your ``LDpred2.R`` command:

```
export PLINK="singularity exec --home=$PWD:/home $SIF/gwas.sif plink"
$PLINK --bfile /REF/examples/prsice2/EUR --fill-missing-a2 --make-bed --out EUR.nomiss
$RSCRIPT createBackingFile.R EUR.nomiss.bed EUR.nomiss.rds
$RSCRIPT ldpred2.R --geno-file-rds EUR.nomiss.rds --geno-impute skip ...
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
