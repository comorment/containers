# COSGAP: COntainerized Statistical Genetics Analysis Pipelines

## Documentation

The main documentation for COSGAP is hosted at [cosgap.rtfd.io](https://cosgap.readthedocs.io)

## Project status

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7385621.svg)](https://doi.org/10.5281/zenodo.7385621)
[![Documentation Status](https://readthedocs.org/projects/cosgap/badge/?version=latest)](https://cosgap.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Hadolint](https://github.com/comorment/containers/actions/workflows/docker.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/docker.yml)
[![Flake8](https://github.com/comorment/containers/actions/workflows/python.yml/badge.svg)](https://github.com/comorment/containers/actions/workflows/python.yml)

## Information

The goal of this github repository (<https://github.com/comorment/containers>) is to distribute software tools for statistical genetics analysis, alongside with their respective reference data and  scripts ("analysis pipelines") to facilitate application of these tools. The scope of this project is currently limited to genome-wide association studies (GWAS) and post-GWAS statistical-genetics analyses, including polygenic scoring (PGS). This project builds on earlier work by [Tryggve consortium](https://neic.no/tryggve/),
with most recent major development done as part of the CoMorMent EU H2020 project ([comorment.eu](https://comorment.eu)). For more information see our [preprint](https://arxiv.org/abs/2212.14103) manuscript, [this presentation](https://www.youtube.com/watch?v=msegdR2vJZs) on PGC WWL meeting (Feb 9, 2024), or our online documentation [here](https://cosgap.readthedocs.io/en/latest/).

For an overview of available software, see [here](docs/README.md).

Most of these tools are packaged into singularity containers (<https://sylabs.io/singularity/>) and shared in the [singularity](https://github.com/comorment/containers/tree/main/singularity) folder of this repository. You can download individual containers using github's ``Download`` button, or clone the entire repository from command line as described in the [INSTALL.md](./INSTALL.md) file.

Many of the tools require additional reference data provided in the [reference](https://github.com/comorment/containers/tree/main/reference) folder of this repository.
Certain reference data can not be made publicly available, in which case we provide access instructions in a separate GitHub repository:
<https://github.com/comorment/reference>. This repository is private - please approach your contact within CoMorMent project to enable your access.

Description of containers and usage instructions are provided in the [docs](https://github.com/comorment/containers/tree/main/docs) folder.

More extensive use cases of containers, focusing on real data analysis, are provided in the [usecases](https://github.com/comorment/containers/tree/main/usecases) folder.

The history of changes is available in the [CHANGELOG.md](./CHANGELOG.md) file.

If you would like to contribute to developing these containers, please see the [CONTRIBUTING](CONTRIBUTING.md) file.

Additional tools are available in separate repositories:

* <https://github.com/comorment/ldsc> - LD score regression
* <https://github.com/comorment/mixer> - cross-trait MiXeR analysis
* <https://github.com/comorment/popcorn> - cross-ancestry genetic correlations
* <https://github.com/comorment/magma> - MAGMA, LAVA, lava-partitioning tools
* <https://github.com/comorment/HDL> - High-Definition Likelihood
* <https://github.com/comorment/ldpred2_ref> - reference files for LDpred2. The tool itself is included in ``r.sif`` ([more info](https://github.com/comorment/containers/tree/main/scripts/pgs)).

## Cite

If you use the software provided here, please get the citation info via the the "Cite this repository" button on the right side of this page, and cite our preprint:

```
Akdeniz, B.C., Frei, O., Hagen, E., Filiz, T.T., Karthikeyan, S., Pasman, J.A., Jangmo, A., Bergsted, J., Shorter, J.R., Zetterberg, R., Meijsen, J.J., Sønderby, I.E., Buil, A., Tesli, M., Lu, Y., Sullivan, P., Andreassen, O.A., & Hovig, E. (2022). COGEDAP: A COmprehensive GEnomic Data Analysis Platform. arXiv:2212.14103 [q-bio.GN]. DOI: [10.48550/arXiv.2212.14103](https://doi.org/)
```

Bibtex format:
```
@misc{akdeniz2022cogedap,
      title={COGEDAP: A COmprehensive GEnomic Data Analysis Platform}, 
      author={Bayram Cevdet Akdeniz and Oleksandr Frei and Espen Hagen and Tahir Tekin Filiz and Sandeep Karthikeyan and Joelle Pasman and Andreas Jangmo and Jacob Bergsted and John R. Shorter and Richard Zetterberg and Joeri Meijsen and Ida Elken Sonderby and Alfonso Buil and Martin Tesli and Yi Lu and Patrick Sullivan and Ole Andreassen and Eivind Hovig},
      year={2022},
      eprint={2212.14103},
      archivePrefix={arXiv},
      primaryClass={q-bio.GN}
}
```

Note that this project will soon be renamed "COSGAP", and that the citation info will be updated accordingly.

## Installation

See the [INSTALL.md](./INSTALL.md) file for installation instructions.

## Legacy

Earlier version (prior to April 2021) of all containers and refrence data was distributed on Google Drive. This is no longer the case, the folder on Google drive is no longer maintained. ALl containers and reference data are released through this repository.

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
