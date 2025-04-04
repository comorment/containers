# Documentation

## Singularity/Apptainer

The list of all tools is provided in the pages describing each container listed below.
For a comprehensive understanding of the installation of tools within each container, please confer the build files in the [<containers>/docker](https://github.com/comorment/containers/tree/main/docker) directory.

This software is organized into the following containers:
* [hello.sif](/docs/containers/hello.md) - a simple container for demo purpose, allowing to experiment with Apptainer features
* [gwas.sif](/docs/containers/gwas.md) - multiple tools (released as binaries/executables) for imputation and GWAS analysis
* [python3.sif](/docs/containers/python3.md) - python3 environment with pre-installed modules and tools
* [r.sif](/docs/containers/r.md) - R/Rstudio-server environment with rareGWAMA, GenomicSEM, TwoSampleMR and GSMR packages installed (plus some standard R packages)

All containers have a common set of linux tools like ``gzip``, ``tar``, ``parallel``, etc.
Please [open an issue](https://github.com/comorment/containers/issues/new) if you'd like to add more of such basic tools, or if you would like to update some software to a newer version.

## Data Format Specifications

To improve interoperability between different tools we developed the following data format specification:

* [Genotypes data](/specifications/geno_specification.md)
* [Phenotypes data](/specifications/pheno_specification.md)
* [GWAS Summary Statistics](/specifications/sumstats_specification.md)

These format specifications are applicable to various scripts, released in this repository, including

* [gwas.py](/scripts/gwas/README.md) - pipeline for GWAS analysis
* [LDpred2](/scripts/pgs/LDpred2/README.md) - command-line wrapper around LDpred2
