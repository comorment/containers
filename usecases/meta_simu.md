This file describe use cases related to meta-analysis.

# GWAMA

To run the example provided with GWAMA software, use this following:

```
cd $COMORMENT/containers/reference/examples/gwama
singularity exec --home $PWD:/home $SIF/gwas.sif GWAMA -qt
```
Each GWA study file has mandatory column headers:
MARKERNAME --snp name
EA -- effect allele
NEA -- non effect allele
OR -- odds ratio
OR_95L -- lower confidence interval of OR
OR_95U -- upper confidence interval of OR
   study files might also contain columns:
N -- number of samples
EAF -- effect allele frequency
STRAND -- marker strand (if the column is missing then the program expects all markers being on positive strand)
IMPUTED -- if marker is imputed of not (if the column is missing then all markers are counted as directly genotyped ones)

A GWAMA pointer file is needed, which simply is a .txt file that contains the path of the summary statistics files for the meta analysis. The above columns are needed for GWAMA analysis.

```
GWAMA \
-i /GWAMA_pointer_file.txt \
--name_marker ID \
--name_n OBS_CT \
--name_ea ea \
--name_nea nea \
--name_or OR \
--name_or_95l L95 \
--name_or95u U95 \
-o /output_path
```

For more informatino about GWAMA, see here: https://genomics.ut.ee/en/tools/gwama

# METAL

METAL tool for meta-analysis ( https://genome.sph.umich.edu/wiki/METAL_Documentation ) is available in gwas.sif container and can be executed as follows:

```
singularity exec --home $PWD:/home $SIF/gwas.sif metal
```

Here is an example script for METAL analysis. If this file is named ``metal_script.txt`` and it's stored in your local folder, 
you may then trigger the analysis using ``singularity exec --home $PWD:/home $SIF/gwas.sif metal metal_script.txt`` command.
See comments below, and refer to the METAL documentation for more information.

```
# choose STDERR scheme (variance-based meta-analysis)
SCHEME   STDERR

# define variables that need to be accumulated across GWASes for each SNP.
# such CUSTOMVARIABLE columns are optional, but it's a good practice to accumulate per-SNP sample size across studies.
# it's also reasonale to compute per-study effective sample size, i.e. 4/(1/nca + 1/nco), and accumulate this value across studies.
CUSTOMVARIABLE NCASE
CUSTOMVARIABLE NCONTROL

# Best to meta-analyze raw summary statistics. It case of a major problems 
with lambdaGC this needs to be looked into manually.
# GENOMICCONTROL ON

# Define how columns are named
MARKER   SNP
ALLELE   A1 A2
EFFECT   log(OR)
STDERR   SE
PVAL     PVAL

# Process a summary statistics file using the above configuration
PROCESS <path>/PGC_MDD_2018_no23andMe.sumstats.gz

# change configuration before processing the next file. This is optional if 
# all files have the same column names in this example only BETA has changed, 
# so it would be fine to omit MARKER, ALLELE, STDERR and PVAL lines.
MARKER   SNP
ALLELE   A1 A2
EFFECT   BETA
STDERR   SE
PVAL     PVAL

# Process the next summary stats file. Keep adding PROCESS command for each 
# sumstat file that needs to be meta-analysed.
PROCESS <path>/23andMe_MDD_2016.sumstats.gz

# define output file name
OUTFILE <path>/PGC_MDD_2018_with23andMe_ .csv

ANALYZE
```
