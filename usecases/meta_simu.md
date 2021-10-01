This file describe use cases related to meta-analysis.

# GWAMA

To run the example provided with GWAMA software, use this following:

```
cd $COMORMENT/containers/reference/examples/gwama
singularity exec --home $PWD:/home $SIF/gwas.sif GWAMA -qt
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
CUSTOMVARIABLE NCASE
CUSTOMVARIABLE NCONTROL

# Best to meta-analyze raw summary statistics. It case of a major problems with lambdaGC this needs to be looked into manually.
# GENOMICCONTROL ON

# Define how columns are named
MARKER   SNP
ALLELE   A1 A2
EFFECT   log(OR)
STDERR   SE
PVAL     PVAL

# Process a summary statistics file using the above configuration
PROCESS <path>/PGC_MDD_2018_no23andMe.sumstats.gz

# change configuration before processing the next file. This is optional if all files have the same column names
# in this example only BETA has changed, so it would be fine to omit MARKER, ALLELE, STDERR and PVAL lines.
MARKER   SNP
ALLELE   A1 A2
EFFECT   BETA
STDERR   SE
PVAL     PVAL

# Process the next summary stats file. Keep adding PROCESS command for each sumstat file that needs to be meta-analysed.
PROCESS <path>/23andMe_MDD_2016.sumstats.gz

# define output file name
OUTFILE <path>/PGC_MDD_2018_with23andMe_ .csv

ANALYZE\
```
