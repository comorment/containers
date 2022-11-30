# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note that CoMorMent containers are organized using several GitHub repositories:

* <https://github.com/comorment/containers> - .sif files, public reference data, documentation, common scripts
* <https://github.com/comorment/gwas> - source code (Dockerfile, etc)
* <https://github.com/comorment/reference> - private reference data with access restricted to CoMorMent collaborator

All of the above repositories are covered by this CHANGELOG. They will have the same version tags on github.
In addition, we have repositories containing specific tools, e.g. <https://github.com/comorment/HDL>,
which will be covered by their own CHANGELOG.md file.

To identify the version of a .sif file, run ``md5sum <container>.sif`` command and find the MD5 checksum in the list below.
If MD5 sum is not listed for a certain release then it means that the container hasn't been changed from the previous release.

## [Unreleased]

### Added

- additions goes here

### Updated

- Updates goes here

### Fixed

- Fixes goes here

### Removed

- MAGMA, LAVA and ldblock software is moved to https://github.com/comorment/magma.
  MAGMA reference files are also moved to this repository.
- enigma-cnv.sif and enigma-cnv.sif is moved to https://github.com/comorment/iPsychCNV
  enigma-cnv.sif is also available here: in https://github.com/ENIGMA-git/ENIGMA-CNV/tree/main/CNVCalling/containers
- tryggve_query.sif  is moved to https://github.com/comorment/Tryggve_psych
- ``matlabruntime.sif`` container is moved to https://github.com/comorment/matlabruntime. 
  pleioFDR reference files are also moved to this repository.

## [1.1] - 2022-11-29

Maintenance/feature release with the following main changes since release version [1.0.0](https://github.com/comorment/containers/releases/tag/v1.0.0): 

### Added

- add autobuilt online documentation from repository sources at https://comorment-containers.readthedocs.io/en/latest/
- add R libraries for LDpred2 analysis to `r.sif` + corresponding example.
- add tests for ``metal`` and ``qctool`` in ``gwas.sif`` build
- add basic GitHub actions from https://github.com/precimed/container_template.git
- add ``FaST-LMM`` (version 0.6.3) to future ``python3.sif``, and corresponding test
- add ``shapeit4.2`` binary (shapeit4 v.4.2.2) and HTSlib (1.11) to future ``gwas.sif`` builds, and corresponding test
- added additional tests for software in ``gwas.sif``, ``python3.sif`` builds
- add versions identifiers for all explicitly installed software across ``hello.sif``, ``gwas.sif``, ``python3.sif``, ``r.sif``, listed in [src/README.md](https://github.com/comorment/containers/src/README.md)
- replaced Ubuntu 18.04 with 20.04 (LTS) as base image for ``hello.sif``, ``gwas.sif``, ``python3.sif``
- replaced ``src/scripts/install_miniconda3.sh`` by ``scr/scripts/install_mambaforge.sh`` which is now used in future  ``python3.sif`` builds 
- add tests for bgenix and Minimac4 software in ``gwas.sif``, removing build-time dependencies for these from container
- add basic test that KING software runs in ``gwas.sif``
- add Dockerfiles and install scripts for `gwas.sif`, `hello.sif`, `python3.sif`, `r.sif`, `saige.sif` from [gwas](https://github.com/comorment/gwas). 
- add CHANGELOG.md (this file)
- add ``gwas.py --analysis saige`` option, allowing to run SAIGE analysis
- add ``gwas.py --analysis figures`` option, using R qqman for QQ and manhattan plots
- add ``gwas.py --pheno-sep`` and ``--dict-sep`` options to specify delimiter for the phenotype file and phenotype dictionary file
- add package ``qqman`` to ``r.sif``
- add package ``yaml`` to ``python3.sif``
- add ``gctb_2.0_tutorial.zip`` reference files under ``reference/examples/gctb_2.0_tutorial``
- add ``config.yaml`` file with configuration options, which can be specified via ``gwas.py --config`` option
- add ``--chunk-size-bp`` and ``--bim`` option, allowing to run SAIGE analysis in smaller chunks
- add ``--keep`` and ``--remove`` options to ``gwas.py``, allowing to keep and remove subsets of individuals from analysis; the functions work similarly to plink2 as described [here](https://www.cog-genomics.org/plink/2.0/filter#sample).

### Updated

* rebuilt the following containers following version pinning in Dockerfiles, install scripts, etc. (see above additions):
  ```
  bb7a8e0b977e29e03067d75d19803913  singularity/gwas.sif
  11ac9e8fe69df07d650bd5e1e7cdeee5  singularity/hello.sif
  c78d57397471ee802d37837ca5f8b797  singularity/python3.sif
  c87c69d2fbab4a317f9d6bb725c76150  singularity/r.sif
  a3f1d8411e1e3cf8670551b7f334a58d  singularity/saige.sif
  ```

* update the following containers:

  ```
  ec089544b13d3eb39f13728f8584dcde  saige.sif   (update to SAIGE v0.44.6.5)
  627734a5c74c94bd69453d0366aced5a  r.sif       (add qqman package)
  ec2824fc1ad8673739b219864c1b4097  python3.sif (add yaml package)
  5c830470a2ee3562974d1e2890d52315  python3.sif (remove mixer package)
  ```

### Fixed

* use ``afterok`` spec instead of ``afterany`` in SLURM dependencies so that next steps of the pipeline don't run if a previous step has failed (fix #26)
* use SLURM's ``cpus_per_task=1`` for SAIGE step2, because it doesn't support --nThreads (see <https://github.com/saigegit/SAIGE/issues/9>)

### Removed

- removed misc. source/data files in /tools/* from container builds
- removed unused ``libquadmath0`` library from builds (affecting future ``gwas.sif``, ``hello.sif``, and ``python3.sif`` builds)
- the following command-line options are removed; instead, they can be specified via ``config.yaml`` file:
  ``--slurm-job-name``, ``--slurm-account``, ``--slurm-time``, ``--slurm-cpus-per-task``, ``--slurm-mem-per-cpu``, ``--module-load``, ``--comorment-folder``, ``--singularity-bind``.
  Note that ``config.yaml`` file is now required.
* ``gwas.py --analysis loci manh qq`` options as removed (fix #22)
* ``--bed-fit``, ``--bed-test``, ``--bgen-fit``, ``--bgen-test`` options of ``gwas.py`` are removed; use new options ``--geno-fit-file`` and ``--geno-file`` instead
* remove ``regenie.sif`` and ``regenie3.sif``, because regenie software is also included in ``gwas.sif``
* remove MiXeR package from ``python3.sif`` container, because MiXeR is now available as a separate container (<https://github.com/comorment/mixer>). This is also where you will find MiXeR's use-cases.

## [1.0.0] - 2020-10-20

### Added

- initial release of the following containers:

  ```
  70502c11d662218181ac79a846a0937a  enigma-cnv.sif
  1ddd2831fcab99371a0ff61a8b2b0970  gwas.sif
  b02fe60c087ea83aaf1b5f8c14e71bdf  hello.sif
  1ab5d82cf9d03ee770b4539bda44a5ba  ipsychcnv.sif
  6d024aed591d8612e1cc628f97d889cc  ldsc.sif
  2e638d1acb584b42c6bab569676a92f8  matlabruntime.sif
  331688fb4fb386aadaee90f443b50f8c  python3.sif
  cdbfbddc9e5827ad9ef2ad8d346e6b82  r.sif
  b8c1727227dc07e3006c0c8070f4e22e  regenie.sif
  97f75a45a39f0a2b3d728f0b8e85a401  regenie3.sif
  20e01618bfb4b0825ef8246c5a63aec5  saige.sif
  5de579f750fb5633753bfda549822a32  tryggve_query.sif
  ```

  Here is the list of tools available in prebuilt containers:
  
  | container         | tool                | version
  | ----------------- | ------------------- | ----------------------------------------
  | hello.sif         | demo example        |
  | gwas.sif          | plink               | v1.90b6.18 64-bit (16 Jun 2020)
  | gwas.sif          | plink2              | v2.00a2.3LM 64-bit Intel (24 Jan 2020)
  | gwas.sif          | plink2_avx2         | v2.00a2.3LM AVX2 Intel (24 Jan 2020)
  | gwas.sif          | PRSice_linux        | 2.3.3 (2020-08-05)
  | gwas.sif          | simu_linux          | Version v0.9.4
  | gwas.sif          | bolt                | v2.3.5 March 20, 2021  
  | gwas.sif          | gcta64              | version 1.93.2 beta Linux
  | gwas.sif          | gctb                | GCTB 2.02
  | gwas.sif          | qctool              | version: 2.0.6, revision 18b8f17
  | gwas.sif          | king                | KING 2.2.6 - (c)
  | gwas.sif          | metal               | version released on 2011-03-25
  | gwas.sif          | vcftools            | VCFtools (0.1.17)
  | gwas.sif          | bcftools            | Version: 1.12 (using htslib 1.12)
  | gwas.sif          | flashpca_x86-64     | flashpca 2.0
  | gwas.sif          | regenie             | REGENIE v2.0.2.gz
  | gwas.sif          | GWAMA               | GWAMA_v2.2.2.zip
  | gwas.sif          | magma               | magma_v1.09a_static.zip
  | gwas.sif          | shapeit2            | Version : v2.r904
  | gwas.sif          | impute4             | impute4.1.2_r300.3
  | gwas.sif          | minimac4            | Version: 1.0.2; Built: Fri Sep  3 13:25:51
  | gwas.sif          | bgenix              | version: 1.1.7, revision
  | gwas.sif          | cat-bgen            | same version as bgenix  
  | gwas.sif          | edit-bgen           | same version as bgenix  
  | python3.sif       | python3             | python 3.10 + standard packages (numpy, pandas, etc)
  | python3.sif       | ldpred              | ?
  | python3.sif       | mixer               | mixer v1.3
  | python3.sif       | python_convert      | github commit bcde562f0286f3ff271dbb54d486d4ca1d40ae36
  | r.sif             | R                   | version 4.0.3 + standard packages (data.table, ggplot, etc)
  | r.sif             | seqminer            | ?
  | r.sif             | rareGWAMA           | ?
  | r.sif             | GenomicSEM          | ?
  | r.sif             | TwoSampleMR         | ?
  | r.sif             | GSMR                | v1.0.9
  | r.sif             | LAVA                | ?
  | r.sif             | LAVA partitioning   | ?
  | saige.sif         | SAIGE               | version 0.43
  | enigma-cnv.sif    | PennCNV             | version 1.0.5
  | ldsc.sif          | LDSC                | version 1.0.1
  | ipsychcnv.sif     | ????                | missing Dockerfile
  | matlabruntime.sif | ????                | work in progress
  | regenie.sif       | ????                | ?
  | regenie3.sif      | ????                | ?  
