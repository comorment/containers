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

### Note on missing genotypes

If genotypes are missing LDpred2 will stop and return an error (``Error: You can't have missing values in 'X'.``). One can either pass ``--geno-impute-zero`` to replace missing genotypes with zero or impute with any other tool such as plink,
or use [imputeGenotypes.R](imputeGenotypes.R) that works for ``bigSNPR`` (.rds/.bk) files. Currently only "simple" imputation with mode, mean, random or zero is supported by this
script. For a documentation on these methods see [snp_fastImputeSimple](https://www.rdocumentation.org/packages/bigsnpr/versions/1.6.1/topics/snp_fastImputeSimple).

First, note that using ``--geno-impute-zero`` is costly in computational time so it's better to impute prior to running ldpred2.R. Second, imputeGenotypes.R does not
create a copy of the genotypes, thus the imputation performed persists. If you wish to keep the original .rds/.bk files you should copy these prior to imputing.

An example use of [imputeGenotypes.R](imputeGenotypes.R):

```
# Conver from plink format to bigSNPR .rds/.bk files
$RSCRIPT createBackingFile.R <fileGeno>.nomiss.bed <fileGeno>.nomiss.rds

# Copy these files if you wish to leave the original files unchanged
cp <fileGeno>.rds <fileGeno>.nomiss.rds
cp <fileGeno>.bk <fileGeo>.nomiss.bk
$RSCRIPT imputeGenotypes.R --impute-simple mean0 --geno-file-rds <fileGeno>.nomiss.rds
```

Another option is to use plink's ``--fill-missing-a2`` option, and re-run ``createBackingFile.R``:

```
export PLINK="singularity exec --home=$PWD:/home $SIF/gwas.sif plink"
$PLINK --bfile /REF/examples/prsice2/EUR --fill-missing-a2 --make-bed --out EUR.nomiss
$RSCRIPT createBackingFile.R EUR.nomiss.bed EUR.nomiss.rds
$RSCRIPT ldpred2.R --geno-file-rds EUR.nomiss.rds ...
```

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

## Running LDpred2 analysis

### Effective sample-size

LDpred2 requires information on effective sample-size. There are three ways to provide this to LDpred2:
- As a column in the summary statistics, defaulting to column `N`. If it is a different column, provide with argument `--col-n`.
- Manually calculated by providing this number with `--effective-sample-size`.
- Manually specified by providing number of cases and controls with arguments `--n-cases` and `--n-controls`.

Specifying the effective sample size manually will override any sample size column in the sumstats.
Providing both `--effective-sample-size` and `--n-cases/--n-controls` will throw an error.

### Summary statistics

LDpred2 requires chromosome number, effective allele (eg A1), reference allele (eg A2, A0), and either SNP ID (RSID) or genomic position. If the summary statistics lack any of this
information, the software will not run. Commonly, output from meta-analysis software such as metal do not contain this information. The [complementSumstats.R](complementSumstats.R)
script can be used to add these columns. In the example below, this script is used to append this information in a set of gzipped files inside a directory, and output these as gzipped
files:

```
# set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT=<path/to/comorment>
export SIF=$COMORMENT/containers/singularity
export REFERENCE=$COMORMENT/containers/reference
export SINGULARITY_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref

export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"

# Directory with possibly gzipped sumstat files
dirSumstats=directory/sumstats
# Directory to direct output
dirOutput=directory/sumstats/processed
if [ ! -d $dirOutput ]; then mkdir $dirOutput; fi;

for fileSumstats in `ls $dirSumstats`; do
 echo "Processing file $fileSumstats"
 $RSCRIPT $COMORMENT/containers/LDpred2/complementSumstats.R --col-sumstats-snp-id MarkerName --sumstats $dirSumstats/$fileSumstats --file-output $dirOutput/$fileSumstats
 gzip $dirOutput/$fileSumstats
done
```

When working within the container, the `--reference argument` can be omitted, but can of course be replaced with anything else along with `--col-reference-snp-id`
to set the SNP ID column in the reference file. The argument `--columns-append` controls which columns to append and default to the `#CHROM` and `POS` which are the
columns of chromosome and position in the `HRC` reference data (default of `--reference` argument). This script will fail if there are duplicate SNPs in any of these
files that are matched. In the example below, output is piped to gzip. To write directly to a file the arguments `--file-output <output file>` and `--file-output-col-sep`
controls the location of the output file and the column separator used (defaults to tab, "\t").

### Synthetic example (chr21 and chr22)

The following set of commands gives an example of how to apply LDpred2 on a synthetic example generated [here](ldpred2_simulations.ipynb). This only uses chr21 and chr22, so it runs much faster than previous example.
This example require only  ``map_hm3_plus.rds``, ``ldref_hm3_plus/LD_with_blocks_chr21.rds``, and ``ldref_hm3_plus/LD_with_blocks_chr22.rds`` files [ldpred2_ref](https://github.com/comorment/ldpred2_ref) repository, so you may download them separately rather then clone the entire repo.

```
# point to input/output files
export fileGeno=/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1.bed
export fileGenoRDS=g1000_eur_chr21to22_hm3rnd1.rds
export fileSumstats=/REF/examples/ldpred2/trait1.sumstats.gz
export fileOut=simu

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
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.inf
 
# run LDpred2 automatic mode
$RSCRIPT ldpred2.R --ldpred-mode auto \
 --chr2use 21 22 \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.auto
```

### Optional: Append score to existing file

It is possible to merge the calculated score to an existing file. For example, you might have a file looking like this:

```
FID IID SEX PC1 ...
1 1 M 1.1 ...
2 2 F 0.3 ...
```

By replacing the ``$fileOut.inf`` and ``$fileOut.auto`` argument above with `<myfile>` and using the options
``--name-score myScoreInf`` for the ``--ldpred-mode inf`` statement and ``--name-score myScoreAuto`` for the other,
and add the flag ``--out-merge`` you end up with these scores in the existing file.

```
FID IID SEX PC1 ... myScoreInf myScoreAuto
1 1 M 1.1 ... 0.3  0.4
2 2 F 0.3 ... -0.2  0.1
```

Note that by default, merging is based on the columns ``IID`` and ``FID`` in the output file. If these columns are
named differently the option ``--out-merge-ids <FID column> <IID column`` should be used to specify their names.

### Height example

The following set of commands gives an example of how to apply LDpred2 on a demo height data:

```
# point to input/output files
export fileGeno=/REF/examples/prsice2/EUR.bed
export fileGenoRDS=EUR.rds
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=Height

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

# impute
$RSCRIPT imputeGenotypes.R --impute-simple mean0 --geno-file-rds $fileGenoRDS

# Generate PGS usign LDPRED-inf
$RSCRIPT ldpred2.R \
 --ldpred-mode inf \
 --col-stat OR \
 --col-stat-se SE \
 --stat-type OR \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT ldpred2.R \
 --ldpred-mode auto \
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
FID IID score
HG00096 HG00096 -0.733896062346436
HG00097 HG00097 0.688693127521599
HG00099 HG00099 0.203279440703434
HG00100 HG00100 0.0890499485064315
...
```

The script will also output ``.bk`` and ``.rds`` binary files with prefix ``EUR`` in this directory.

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
