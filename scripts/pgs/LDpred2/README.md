# LDpred2

The files in this directory exemplifies how to run the LDpred2 analysis using the ``bigsnpr`` R library, using [ldpred2.R](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/ldpred2.R) script developed by Andreas Jangmo, Espen Hagen and Oleksandr Frei. The script is based on this [tutorial](https://privefl.github.io/bigsnpr/articles/LDpred2.html).
The LDpred2 method is explained in the publication:

- Florian Privé, Julyan Arbel, Bjarni J Vilhjálmsson, LDpred2: better, faster, stronger, Bioinformatics, Volume 36, Issue 22-23, 1 December 2020, Pages 5424–5431, <https://doi.org/10.1093/bioinformatics/btaa1029>

## Prerequisites

This README assumes the following two repositories are cloned using [git](https://git-scm.com):

- <http://github.com/comorment/containers>
- <https://github.com/comorment/ldpred2_ref>
- <https://github.com/comorment/opensnp>

We also assume the following commands are executed from the current folder
(the one containing [createBackingFile.R](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/createBackingFile.R) and [ldpred2.R](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/ldpred2.R) scripts).

### Note on help functions

The main R scripts contained in this directory (`ldpred2.R`, `createBackingFile.R`, `imputeGenotypes.R`, `complementSum`) are set up using the [argparser](https://www.rdocumentation.org/packages/argparser) package for parsing command line arguments.
The help output from each script can printed to the terminal, issuing:

```
export SIF=$COMORMENT/containers/containers/latest
export RSCRIPT="apptainer exec --home=$PWD:/home $SIF/r.sif Rscript"
# invoke ldpred2.R input options:
$RSCRIPT ldpred2.R --help
```

yielding:

```
usage: ldpred2.R [--] [--help] [--out-merge] [--geno-impute-zero]
       [--merge-by-rsid] [--opts OPTS] [--geno-file-rds GENO-FILE-RDS]
       [--sumstats SUMSTATS] [--out OUT] [--out-merge-ids
       OUT-MERGE-IDS] [--file-keep-snps FILE-KEEP-SNPS] [--ld-file
       LD-FILE] [--ld-meta-file LD-META-FILE] [--chr2use CHR2USE]
       [--col-chr COL-CHR] [--col-snp-id COL-SNP-ID] [--col-A1 COL-A1]
       [--col-A2 COL-A2] [--col-bp COL-BP] [--col-stat COL-STAT]
       [--col-stat-se COL-STAT-SE] [--col-pvalue COL-PVALUE] [--col-n
       COL-N] [--stat-type STAT-TYPE] [--effective-sample-size
       EFFECTIVE-SAMPLE-SIZE] [--n-cases N-CASES] [--n-controls
       N-CONTROLS] [--name-score NAME-SCORE] [--hyper-p-length
       HYPER-P-LENGTH] [--hyper-p-max HYPER-P-MAX] [--ldpred-mode
       LDPRED-MODE] [--cores CORES] [--set-seed SET-SEED]
       [--genomic-build GENOMIC-BUILD] [--tmp-dir TMP-DIR]

Calculate polygenic scores using ldpred2

flags:
  -h, --help                   show this help message and exit
  --out-merge                  Merge output with existing file.
  --geno-impute-zero           Set missing genotypes to zero.
...
```

### Note on filtering of genotype data

The current version of these scripts performs no filtering of genotype data (e.g., minor allele frequency, imputation quality) prior to calculating linkage disequilibrium or polygenic scores.
This should be done for polygenic score analyses intended for publication.

### Note on missing genotypes

If genotypes are missing LDpred2 will stop and return an error (``Error: You can't have missing values in 'X'.``). One can either pass ``--geno-impute-zero`` to replace missing genotypes with zero or impute with any other tool such as plink,
or use [imputeGenotypes.R](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/imputeGenotypes.R) that works for ``bigSNPR`` (.rds/.bk) files. Currently, only "simple" imputation with mode, mean, random or zero is supported by this
script. For documentation on these methods see [snp_fastImputeSimple](https://www.rdocumentation.org/packages/bigsnpr/versions/1.6.1/topics/snp_fastImputeSimple).

First, note that using ``--geno-impute-zero`` is costly in computational time so it's better to impute prior to running ldpred2.R. Second, imputeGenotypes.R does not
create a copy of the genotypes, thus the imputation performed persists. If you wish to keep the original .rds/.bk files you should copy these prior to imputing.

An example use of [imputeGenotypes.R](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/imputeGenotypes.R):

```
# Convert from plink format to bigSNPR .rds/.bk files
$RSCRIPT createBackingFile.R --file-input <fileGeno>.nomiss.bed --file-output <fileGeno>.nomiss.rds

# Copy these files if you wish to leave the original files unchanged
cp <fileGeno>.rds <fileGeno>.nomiss.rds
cp <fileGeno>.bk <fileGeo>.nomiss.bk
$RSCRIPT imputeGenotypes.R --impute-simple mean0 --geno-file-rds <fileGeno>.nomiss.rds
```

Another option is to use PLINK's ``--fill-missing-a2`` option, and re-run ``createBackingFile.R``:

```
export PLINK="apptainer exec --home=$PWD:/home $SIF/gwas.sif plink"
$PLINK --bfile /REF/examples/prsice2/EUR --fill-missing-a2 --make-bed --out EUR.nomiss
$RSCRIPT createBackingFile.R --file-input EUR.nomiss.bed --file-output EUR.nomiss.rds
$RSCRIPT ldpred2.R --geno-file-rds EUR.nomiss.rds ...
```

### Note on genomic builds

By default, the LDpred2 scripts assume that the genotype data and summary statistics use build GRCh37/hg19, 
but there are no explicit checks for consistent builds across input files.
If the genotype data and summary statistics file use another build, the ``--genomic-build <build>`` flag should be used to specify build version,
parsing either `hg18`, `hg19` or `hg38` as an argument.
As of now, setting this argument will affect the loading of LD metadata only, but not the genotype data or summary statistics.
A symptom of using the wrong build is that the script will match only a small fraction of variants between the genotype data, summary statistics file and/or LD reference data.

### Optional: Estimating linkage disequilibrium (LD)

LDpred2 uses the LD structure when calculating polygenic scores. By default, the LDpred2.R script uses LD structure based on European samples provided by the LDpred2 authors.
Instead of calculating LD on your own, the ``calculateLD.R`` script can be used. The output from this script can then be used as input to ``LDpred2.R`` (with the optional ``--ld-file`` flag).

It should be noted that creating these LD matrixes may require several steps that are dependent on what type of genotypic data you have. These are not covered in detail here, but a
first step is to ensure that you filter out related individuals, and use a reasonably sized set of genotyped or well-imputed SNPs. How to restrict individuals and SNPs is covered below.

First, to use ``calculateLD.R`` you need to download genetic maps from [1000 genomes](https://github.com/joepickrell/1000-genomes-genetic-maps) in order to convert each SNPs physical position to genomic position.
If you don't provide these files, LDpred2 will try to download these automatically which will cause an error without an internet connection. To prevent this behavior, these should be downloaded manually and
the folder where they are stored should be passed to the LDpred2-script using the flag ``--dir-genetic-maps your-genetic/maps-directory``.

Two parameters that can be passed to ``calculateLD.R`` and affect the LD estimation are ``--window-size`` (region around index SNP in base pairs) and ``--thres-r2`` (threshold for including
a SNP correlation in the LD). The default for ``--thres-r2`` is 0 in ``bigsnpr::snp_cor``, but ``calculateLD.R`` has a default of 0.01.

The example script below will output one file per chromosome (``output/ld-chr-1.rds``, ``output/ld-chr-2.rds``, ...) and a "map" indicating the SNPs used in LD estimation (``output/map.rds``).
The flag ``--sumstats`` can be used to filter SNPs to use where the first argument is the file and the second the column name or position of the RSID of the SNP (ie it does not need to be a proper
sumstats file). The ``--extract`` argument does similar but expects a file that is just a list of RSIDs. These arguments can be combined and the SNPs used will then be limited to those
that overlap in both files.

By a similar principle, ``--extract-individuals`` can be used together with ``--sample-individuals`` to limit the set of individuals (e.g., unrelated only), and then to draw a sample
from this set.

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
export SIF=$COMORMENT/containers/containers/latest
export REFERENCE=$COMORMENT/containers/reference
export LDPRED2_REF=$COMORMENT/ldpred2_ref
export APPTAINER_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref

export RSCRIPT="apptainer exec --home=$PWD:/home $SIF/r.sif Rscript"

# convert genotype to LDpred2 format
$RSCRIPT createBackingFile.R --file-input $fileGeno --file-output $fileGenoRDS

# create genetics maps directory, download and process
mkdir -p 100genomes/maps
$RSCRIPT calculateLD.R --geno-file-rds $fileGenoRDS \
 --dir-genetic-maps 100genomes/maps \
 --chr2use 21 22  --sumstats $fileSumstats SNP \
 --file-ld-blocks $fileOutLD --file-ld-map $fileOutLDMap
```

Note that "bad" LD matrixes may result in optimization failures as these when running the LDpred2 scoring:
```
Running LDPRED2 auto model
Erorr in { : task 1 failed - "L-BFGS-B needs finite values of 'fn'"
Calls: snp_ldpred2_auto -> %dorng% -> do.call -> <Anonymous> -> <Anonymous>
```

The LDpred2 creators recommend creating independent LD blocks in these matrixes. the ``splitLD.R`` script can be used for this purpose. The setup is the same as the
example above, but we add a modified ``$RSCRIPT [...]`` statement using the outputted matrixes from ``calculateLD.R`` as input to ``splitLD.R``. There are several parameters
to this script that will affect the "shape" of these blocks (thus subsequent performance in LDpred2). Consult ``splitLD.R`` and ``bigsnpr::snp_ldsplit`` for details.
```
$RSCRIPT splitLD.R --file-ld-blocks $fileOutLD \
 --file-ld-map $fileOutLDMap \
 --file-output-ld-blocks ld-blocked-chr@.rds
```

The script ``analyzeLD.R`` can be used to visualize these matrixes and provide summary statistics. We don't cover its use in detail here, but
if you experience issues with LD matrixes one way may be to compare plots and statistics between your matrixes and those provided by by the LDpred2
creators. ``Rscript analyzeLD.R --help`` provides an overview of usage.

## Running LDpred2 analysis

### Effective sample-size

LDpred2 requires information on effective sample size. There are three ways to provide this to LDpred2:

- As a column in the summary statistics, defaulting to column `N`. If it is a different column, provide with argument `--col-n`.
- Manually calculated by providing this number with `--effective-sample-size`.
- Manually specified by providing the number of cases and controls with arguments `--n-cases` and `--n-controls`.

Specifying the effective sample size manually will override any sample size column in the sumstats.
Providing both `--effective-sample-size` and `--n-cases/--n-controls` will throw an error.

### Summary statistics

LDpred2 requires chromosome number, effective allele (eg A1), reference allele (eg A2, A0), and either SNP ID (RSID) or genomic position. If the summary statistics lack any of this
information, the software will not run. Commonly, output from meta-analysis software such as metal do not contain this information. The [complementSumstats.R](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/complementSumstats.R)
script can be used to add these columns. In the example below, this script is used to append this information in a set of gzipped files inside a directory, and output these as gzipped
files:

```
# set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT=<path/to/comorment>
export SIF=$COMORMENT/containers/containers
export REFERENCE=$COMORMENT/containers/reference
export APPTAINER_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref

export RSCRIPT="apptainer exec --home=$PWD:/home $SIF/r.sif Rscript"

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

When working within the container, the `--reference argument` can be omitted, but can be replaced with anything else along with `--col-reference-snp-id`
to set the SNP ID column in the reference file. The argument `--columns-append` controls which columns to append and default to the `#CHROM` and `POS` which are the
columns of chromosome and position in the `HRC` reference data (default of `--reference` argument). This script will fail if there are duplicate SNPs in any of these
files that are matched. In the example below, output is piped to gzip. To write directly to a file the arguments `--file-output <output file>` and `--file-output-col-sep`
controls the location of the output file and the column separator used (defaults to tab, "\t").

**_NOTE:_** In case the summary statistics file (or any other file used by the scripts) is outside the working directory, make sure to append its directory to the `APPTAINER_BIND` environment variable as above, and refer to the file accordingly - otherwise the running container won't see the file.

### Synthetic example (chr21 and chr22)

The following set of commands gives an example of how to apply LDpred2 on a synthetic example generated [here](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/ldpred2_simulations.ipynb). This only uses chr21 and chr22, so it runs much faster than the previous example.
This example requires only  ``map_hm3_plus.rds``, ``ldref_hm3_plus/LD_with_blocks_chr21.rds``, and ``ldref_hm3_plus/LD_with_blocks_chr22.rds`` files from the [ldpred2_ref](https://github.com/comorment/ldpred2_ref) repository, so you may download them separately rather than clone the entire repo.

```
# point to input/output files
export fileGeno=/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1.bed
export fileGenoRDS=g1000_eur_chr21to22_hm3rnd1.rds
export fileSumstats=/REF/examples/ldpred2/trait1.sumstats.gz
export fileOut=simu

# set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT=<path/to/comorment>
export SIF=$COMORMENT/containers/containers/latest
export REFERENCE=$COMORMENT/containers/reference
export LDPRED2_REF=$COMORMENT/ldpred2_ref
export APPTAINER_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref

export RSCRIPT="apptainer exec --home=$PWD:/home $SIF/r.sif Rscript"

# convert genotype to LDpred2 format
$RSCRIPT createBackingFile.R --file-input $fileGeno --file-output $fileGenoRDS

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

The following set of commands gives an example of how to apply LDpred2 on genetic data from the [OpenSNP](https://opensnp.org/) project, and a height GWAS sumstats file.
This example requires the ``opensnp_hm3.*`` and ``UKB_NEALELAB_2018_HEIGHT.GRCh37.hm3.gz`` files from the [opensnp](https://github.com/comorment/opensnp) repository, so you may download them separately rather than clone the entire repo, 
and place them according to the paths in the script below.

```
# Set environmental variables. Replace "<path/to/comorment>" with 
# the full path to the folder containing cloned "containers" and "ldpred2_ref" repositories
export COMORMENT=<path/to/comorment>
export SIF=$COMORMENT/containers/containers/latest
export REFERENCE=$COMORMENT/containers/reference
export LDPRED2_REF=$COMORMENT/ldpred2_ref
export OPENSNP=$COMORMENT/opensnp
export APPTAINER_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref,${OPENSNP}:/opensnp

# Point to LDpred2.R input/output files
export fileGeno=/opensnp/imputed/opensnp_hm3.bed
export fileGenoRDS=opensnp_hm3.rds
export fileSumstats=/opensnp/gwas/UKB_NEALELAB_2018_HEIGHT.GRCh37.hm3.gz
export fileOut=Height

export RSCRIPT="apptainer exec --home=$PWD:/home $SIF/r.sif Rscript"

# convert genotype to LDpred2 format
$RSCRIPT createBackingFile.R --file-input $fileGeno --file-output $fileGenoRDS

# impute
$RSCRIPT imputeGenotypes.R --impute-simple mean0 --geno-file-rds $fileGenoRDS

# Generate PGS usign LDPRED-inf
$RSCRIPT ldpred2.R \
 --ldpred-mode inf \
 --col-stat BETA \
 --col-stat-se SE \
 --stat-type BETA \
 --geno-file-rds $fileGenoRDS \
 --sumstats $fileSumstats \
 --out $fileOut.inf

# Generate PGS using LDPRED2-auto
$RSCRIPT ldpred2.R \
 --ldpred-mode auto \
 --col-stat BETA \
 --col-stat-se SE \
 --stat-type BETA \
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

On an HPC resource, the same analysis can be run by first writing a job script [run_ldpred2_slurm.job](https://github.com/comorment/containers/blob/main/scripts/pgs/LDpred2/run_ldpred2_slurm.job).
In order to run the job, first make sure that the ``SBATCH_ACCOUNT`` environment variable is defined:

```
export SBATCH_ACCOUNT=project_ID
```

where ``project_ID`` is the granted project that computing time is allocated.
As above, ``<path/to/containers`` should point to the cloned ``containers`` repository.
Entries like ``--partition=normal`` may also be adapted for different HPC resources.
Then, the job can be submitted to the queue by issuing ``sbatch run_ldpred2_slurm.job``.
The status of running jobs can usually be enquired by issuing ``squeue -u $USER``.


### Redirect temporary file output

By default, the LDpred2.R script will put large file(s) in the system temporary directory (using `base::tempdir()`).
For use on HPC resources, use of the designated `$SCRATCH`, `$LOCALTMP`, or `$TMPDIR` directories is recommended to avoid
filling up the system temporary directory.

One can redirect the temporary file output by setting the `TMPDIR` environment variable to a mounted directory on the HPC resource, 
by incorporating the following lines into the job script:

```
export APPTAINER_BIND=$REFERENCE:/REF,${LDPRED2_REF}:/ldpred2_ref,$SCRATCH:/scratch
export APPTAINERENV_TMPDIR=/scratch
```

Otherwise, the location of temporary files can be specified by the `--tmp-dir` argument to the `ldpred2.R` script.
