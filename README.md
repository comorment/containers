# About

The goal of this repository is to distribute tools for GWAS and post-GWAS analysis in CoMorMent project (http://comorment.eu/).

Most of these tools are packaged into singularity containers (https://sylabs.io/singularity/) and shared in [singularity](singularity) folder of this repository. You can download individual containers using github's ``Download`` button, or clone the entire repository from command line (in which case make sure to [install GitLFS extension](https://git-lfs.github.com/)).

Most of the tools require additional reference data, provided in the [reference](reference) folder of this repository.
Certain reference data can not be made publicly available, in which case we provide access instructions in a separate GitHub repository:
https://github.com/comorment/reference. This repository is private - please approach your contact within CoMorMent project to enable your access.

Description of containers and usage instructions are provided in the [docs](docs) folder.

More extensive use cases of containers, focusing on real data analysis, are provided in the [usecases](usecases) folder.

For TSD system, a read-only copy of these containers is maintained at these locations
(please read /cluster/projects/pNN/github/README.md file before using these copies):
```
/cluster/projects/p33/github/comorment
/cluster/projects/p697/github/comorment
```

# Legacy

Earlier version (prior to April 2021) of all containers and refrence data was distributed on Google Drive. This is no longer the case, the folder on Google drive is no longer maintained. ALl containers and reference data are released through this repository.



