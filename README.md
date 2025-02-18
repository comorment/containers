# COSGAP: COntainerized Statistical Genetics Analysis Pipelines

## Documentation

The main documentation for COSGAP is hosted at [cosgap.rtfd.io](https://cosgap.readthedocs.io)

## Project status

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7385621.svg)](https://doi.org/10.5281/zenodo.7385621)
[![Documentation Status](https://readthedocs.org/projects/cosgap/badge/?version=latest)](https://cosgap.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Hadolint](https://github.com/comorment/containers/actions/workflows/docker.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/docker.yml)
[![Flake8](https://github.com/comorment/containers/actions/workflows/python.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/python.yml)
[![Docker build "hello"](https://github.com/comorment/containers/actions/workflows/docker_build_hello.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/docker_build_hello.yml)
[![Docker build "python3"](https://github.com/comorment/containers/actions/workflows/docker_build_python3.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/docker_build_python3.yml)
[![Docker build "gwas"](https://github.com/comorment/containers/actions/workflows/docker_build_gwas.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/docker_build_gwas.yml)
[![Docker build "r"](https://github.com/comorment/containers/actions/workflows/docker_build_r.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/docker_build_r.yml)

## Information

The goal of this GitHub repository (<https://github.com/comorment/containers>) is to distribute software tools for statistical genetics analysis, alongside their respective reference data and scripts ("analysis pipelines") to facilitate the application of these tools. The scope of this project is currently limited to genome-wide association studies (GWAS) and post-GWAS statistical-genetics analyses, including polygenic scoring (PGS). This project builds on earlier work by [Tryggve consortium](https://neic.no/tryggve/),
with the most recent major development done as part of the CoMorMent EU H2020 project ([comorment.eu](https://comorment.eu)). For more information see our [paper](https://doi.org/10.1093/bioadv/vbae067), [this presentation](https://www.youtube.com/watch?v=msegdR2vJZs) on PGC WWL meeting (Feb 9, 2024), or our online documentation [here](https://cosgap.readthedocs.io/en/latest/).

For an overview of available software, see [here](docs/README.md).

Most of these tools are packaged into Docker images (<https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/>) and Singularity Image Format files (<https://github.com/apptainer/sif>), compatible with both Singularity (<https://sylabs.io/singularity/>) and Apptainer (<https://apptainer.org>) and shared as [packages](https://github.com/orgs/comorment/packages?repo_name=containers) on GitHub.
You can download individual container files as described in the [INSTALL](./INSTALL.md) file.

Many of the tools require additional reference data provided in the [reference](https://github.com/comorment/containers/tree/main/reference).
Certain reference data can not be made publicly available, in which case we provide access instructions in a separate GitHub repository:
<https://github.com/comorment/reference>. This repository is private - please approach your contact within the CoMorMent project to enable your access.

Description of containers and usage instructions are provided in the [docs](https://github.com/comorment/containers/tree/main/docs) folder.

More extensive use cases of containers, focusing on real data analysis, are provided in the [usecases](https://github.com/comorment/containers/tree/main/usecases) folder.

The history of changes is available in the [CHANGELOG](./CHANGELOG.md) file.

If you would like to contribute to developing these containers, please see the [CONTRIBUTING](CONTRIBUTING.md) file.

Additional tools are available in separate repositories:

* <https://github.com/comorment/ldsc> - LD score regression
* <https://github.com/comorment/mixer> - cross-trait MiXeR analysis
* <https://github.com/comorment/popcorn> - cross-ancestry genetic correlations
* <https://github.com/comorment/magma> - MAGMA, LAVA, lava-partitioning tools
* <https://github.com/comorment/HDL> - High-Definition Likelihood
* <https://github.com/comorment/mtag_container> - Multi-Trait Analysis of GWAS using MTAG
* <https://github.com/comorment/ldpred2_ref> - reference files for LDpred2. The tool itself is included in ``r.sif`` ([more info](https://github.com/comorment/containers/tree/main/scripts/pgs)).

## Cite

If you use the software provided here, please cite our [Zenodo.org](https://zenodo.org) code deposit (change version accordingly):
```
Oleksandr Frei, Andreas Jangmo, Espen Hagen, bayramakdeniz, ttfiliz, Richard Zetterberg, & John Shorter. (2024). comorment/containers: Comorment-Containers-v1.8.1 (v1.8.1). Zenodo. https://doi.org/10.5281/zenodo.10782180
```

Bibtex format:
```
@software{oleksandr_frei_2024_10782180,
  author       = {Oleksandr Frei and
                  Andreas Jangmo and
                  Espen Hagen and
                  bayramakdeniz and
                  ttfiliz and
                  Richard Zetterberg and
                  John Shorter},
  title        = {comorment/containers: Comorment-Containers-v1.8.1},
  month        = mar,
  year         = 2024,
  publisher    = {Zenodo},
  version      = {v1.8.1},
  doi          = {10.5281/zenodo.10782180},
  url          = {https://doi.org/10.5281/zenodo.10782180}
}
```

Please also cite our paper:

```
Bayram Cevdet Akdeniz, Oleksandr Frei, Espen Hagen, Tahir Tekin Filiz, Sandeep Karthikeyan, Joëlle Pasman, Andreas Jangmo, Jacob Bergstedt, John R Shorter, Richard Zetterberg, Joeri Meijsen, Ida Elken Sønderby, Alfonso Buil, Martin Tesli, Yi Lu, Patrick Sullivan, Ole A Andreassen, Eivind Hovig, COSGAP: COntainerized Statistical Genetics Analysis Pipelines, Bioinformatics Advances, Volume 4, Issue 1, 2024, vbae067, <https://doi.org/10.1093/bioadv/vbae067>
```

Bibtex format:
```
@article{10.1093/bioadv/vbae067,
    author = {Akdeniz, Bayram Cevdet and Frei, Oleksandr and Hagen, Espen and Filiz, Tahir Tekin and Karthikeyan, Sandeep and Pasman, Joëlle and Jangmo, Andreas and Bergstedt, Jacob and Shorter, John R and Zetterberg, Richard and Meijsen, Joeri and Sønderby, Ida Elken and Buil, Alfonso and Tesli, Martin and Lu, Yi and Sullivan, Patrick and Andreassen, Ole A and Hovig, Eivind},
    title = {COSGAP: COntainerized Statistical Genetics Analysis Pipelines},
    journal = {Bioinformatics Advances},
    volume = {4},
    number = {1},
    pages = {vbae067},
    year = {2024},
    month = {05},
    abstract = {The collection and analysis of sensitive data in large-scale consortia for statistical genetics is hampered by multiple challenges, due to their non-shareable nature. Time-consuming issues in installing software frequently arise due to different operating systems, software dependencies, and limited internet access. For federated analysis across sites, it can be challenging to resolve different problems, including format requirements, data wrangling, setting up analysis on high-performance computing (HPC) facilities, etc. Easier, more standardized, automated protocols and pipelines can be solutions to overcome these issues. We have developed one such solution for statistical genetic data analysis using software container technologies. This solution, named COSGAP: “COntainerized Statistical Genetics Analysis Pipelines,” consists of already established software tools placed into Singularity containers, alongside corresponding code and instructions on how to perform statistical genetic analyses, such as genome-wide association studies, polygenic scoring, LD score regression, Gaussian Mixture Models, and gene-set analysis. Using provided helper scripts written in Python, users can obtain auto-generated scripts to conduct the desired analysis either on HPC facilities or on a personal computer. COSGAP is actively being applied by users from different countries and projects to conduct genetic data analyses without spending much effort on software installation, converting data formats, and other technical requirements.COSGAP is freely available on GitHub (https://github.com/comorment/containers) under the GPLv3 license.},
    issn = {2635-0041},
    doi = {10.1093/bioadv/vbae067},
    url = {https://doi.org/10.1093/bioadv/vbae067},
    eprint = {https://academic.oup.com/bioinformaticsadvances/article-pdf/4/1/vbae067/57955150/vbae067.pdf},
}
```

Note that this project is now renamed "COSGAP", and that the citation info has been updated accordingly.

## Installation

Please confer the [INSTALL.md](./INSTALL.md) file for installation instructions.

## Legacy

Earlier versions (prior to April 2021) of all containers and reference data were distributed via Google Drive. This is no longer the case, the folder on Google Drive is no longer maintained. All containers and reference data are released through this repository.

## Source files

The source files for configuring and building the container files provided here are found in the [docker](https://github.com/comorment/containers/tree/main/docker) directory.
See the corresponding [README](./docker/README.md) file therein for details.

## Documentation build instructions

The online documentation hosted at [cosgap.rtfd.io](https://cosgap.readthedocs.io) can be built locally using [Sphinx](https://www.sphinx-doc.org/en/master/) in a conda environment as

```
cd sphinx-docs/source  # documentation source/config directory
conda env create -f environment.yml  # creates environment "sphinx"
conda activate sphinx
make html  # make html-documentation in $PWD/_build/html/
```

The resulting file(s) ``$PWD/_build/html/index.html`` can be viewed in any web browser.
In order to make a pdf with the documentation, issue

```
make pdflatex
```

and open ``$PWD/_build/latex/cosgap.pdf`` in a pdf viewer.
