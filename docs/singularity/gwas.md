# ``gwas.sif`` container

The ``gwas.sif`` container file has multiple tools related to imputation and GWAS analysis, as summarized in this [table](./../../docker/README.md#software-versions).

Note that some specific tools (e.g. ``bolt``) are added to the path directly from their ``/tools`` folder (e.g. ``/tools/bolt``) due to hard-linked dependencies.
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


## Software

List of software included in the container:

  | OS/tool             | version                                   | license
  | ------------------- | ----------------------------------------- | -------------
  | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | bcftools            | 1.19                                      | [MIT/Expat/GPLv3](https://github.com/samtools/bcftools/blob/develop/LICENSE)
  | bedtools            | 2.31.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | beagle              | 22Jul22.46e                               | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | bgenix              | 1.1.7                                     | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | bolt                | v2.4.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | cat-bgen            | same version as bgenix                    | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | duohmm              | 95bd395                                   | [MIT](https://opensource.org/licenses/MIT)
  | eagle               | v2.4.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | edit-bgen           | same version as bgenix                    | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | flashpca_x86-64     | 2.0                                       | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gcta64              | 1.94.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gctb                | 2.04.3                                    | [MIT](https://opensource.org/licenses/MIT)
  | qctool              | 2.2.2, revision e5723df2c0c85959          | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | GWAMA               | 2.2.2                                     | [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause)
  | HTSlib              | 1.19.1                                    | [MIT/Expat/Modified-BSD](https://github.com/samtools/htslib/blob/develop/LICENSE)
  | king                | 2.3.2                                     | [permissive](https://www.kingrelatedness.com/Download.shtml)
  | liftOver            | latest                                    | [permissive](https://genome-store.ucsc.edu)
  | ldak                | 5.2                                       | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | metal               | 2020-05-05                                | -
  | minimac4            | v4.1.6                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | plink               | v1.90b7.2 64-bit (11 Dec 2023)            | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | plink2              | v2.00a5.10LM 64-bit Intel (5 Jan 2024)    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | plink2_avx2         | v2.00a5.10LM AVX2 Intel (5 Jan 2024)      | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | PRSice_linux        | 2.3.5                                     | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | regenie             | v3.4                                      | [MIT/Boost](https://github.com/rgcgithub/regenie/blob/master/LICENSE)
  | samtools            | v1.19.2                                   | [MIT/ExpatD](https://github.com/samtools/samtools/blob/develop/LICENSE)
  | shapeit4.2          | v4.2.2                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5 phase_rare | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5 phase_common | v5.1.1                                  | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5 ligate     | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5 switch     | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5 xcftools   | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | simu_linux          | v0.9.4                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | snptest             | v2.5.6                                    | [permissive](https://www.chg.ox.ac.uk/~gav/snptest/#download)
  | switchError         | 6e688b1                                   | [MIT](https://opensource.org/licenses/MIT)
  | vcftools            | 0.1.17 (git SHA: d511f469e)               | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
