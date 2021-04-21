## gwas.sif

The ``gwas.sif`` container has multiple tools related to imputation and GWAS analysis:
```
    plink               # v1.90b6.18 64-bit (16 Jun 2020)
    plink2              # v2.00a2.3LM 64-bit Intel (24 Jan 2020)
    plink2_avx2         # v2.00a2.3LM AVX2 Intel (24 Jan 2020)
    PRSice_linux        # 2.3.3 (2020-08-05) 
    simu_linux          # Version v0.9.4
    bolt                # v2.3.5 March 20, 2021  
    gcta64              # version 1.93.2 beta Linux
    gctb                # GCTB 2.02
    qctool              #
    king                # KING 2.2.6 - (c)
    metal               # version released on 2011-03-25
    vcftools            # VCFtools (0.1.17)
    bcftools            # Version: 1.12 (using htslib 1.12)
    flashpca_x86-64     # flashpca 2.0
    regenie             # REGENIE v2.0.2.gz
```
Only tools released as binaries (executables) are put in ``gwas`` containers.
Each tool has corresponding folder within ``/tools/``.
Most of the tools are copied to ``/bin``, and can be executed by the name of the binary (as listed above).
Some specific tools (e.g. ``bolt``) add added to the path directly from their tools folder (e.g. ``/tools/bolt``) due to dependencies.
Either way, all tools can be invoked by their name, as listed above. For example:

```
>singularity exec gwas.sif regenie
              |=============================|
              |      REGENIE v2.0.2.gz      |
              |=============================|

Copyright (c) 2020 Joelle Mbatchou and Jonathan Marchini.
Distributed under the MIT License.
Compiled with Boost Iostream library.
Using Intel MKL with Eigen.

ERROR: You must provide an output prefix using '--out'
For more information, use option '--help' or visit the website: https://rgcgithub.github.io/regenie/
```
