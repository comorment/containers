# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Note that CoMorMent containers are organized using several GitHub repositories:
* https://github.com/comorment/containers - .sif files, public reference data, documentation, common scripts
* https://github.com/comorment/gwas - source code (Dockerfile, etc)
* https://github.com/comorment/reference - private reference data with access restricted to CoMorMent collaborator

All of the above repositories are covered by this CHANGELOG. They will have the same version tags on github.
In addition, we have repositories containing specific tools, e.g. https://github.com/comorment/HDL, 
which will be covered by their own CHANGELOG.md file.

To identify the version of a .sif file, run ``md5sum <container>.sif`` command and find the MD5 checksum in the list below.
If MD5 sum is not listed for a certain release then it means that the container hasn't been changed from the previous release.

## [Unreleased]
- add CHANGELOG.md (this file)
  gwas.py: remove ``loci`` step from default ``--analysis`` (#22)
- implement ``gwas.py --analysis saige`` option, allowing to run SAIGE analysis
- add package ``qqman`` to ``r.sif``
- update software versions:
  ```
  ec089544b13d3eb39f13728f8584dcde  saige.sif   (update to SAIGE v0.44.6.5)
  627734a5c74c94bd69453d0366aced5a  r.sif       (new packages)
  ```

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

  Here is the list of tools available in this version:
  
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
  | python3.sif       | python3             | python 3.8 + standard packages (numpy, pandas, etc)
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
