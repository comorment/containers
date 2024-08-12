# ``gwas.sif`` container

## Description

The ``gwas.sif`` container file has multiple tools related to imputation and GWAS analysis, as summarized in the [Sofware](#software) table below.

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

  | OS/tool                         | version                                   | license
  | ------------------------------- | ----------------------------------------- | -------------
  | ubuntu                          | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | bcftools[^bcftools]             | 1.19                                      | [MIT/Expat/GPLv3](https://github.com/samtools/bcftools/blob/develop/LICENSE)
  | bedtools[^bedtools]             | 2.31.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | beagle[^beagle1] [^beagle2]     | 22Jul22.46e                               | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | bgenix[^bgenix]                 | 1.1.7                                     | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | bolt[^bolt]                     | v2.4.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | cat-bgen[^cat-bgen]             | same version as bgenix                    | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | duohmm[^duohmm]                 | 95bd395                                   | [MIT](https://opensource.org/licenses/MIT)
  | eagle[^eagle]                   | v2.4.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | edit-bgen[^edit-bgen]           | same version as bgenix                    | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | flashpca_x86-64[^flashpca]      | 2.0                                       | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gcta64[^gcta]                   | 1.94.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gctb[^gctb]                     | 2.04.3                                    | [MIT](https://opensource.org/licenses/MIT)
  | GWAMA[^gwama]                   | 2.2.2                                     | [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause)
  | HTSlib[^htslib]                 | 1.19.1                                    | [MIT/Expat/Modified-BSD](https://github.com/samtools/htslib/blob/develop/LICENSE)
  | king[^king]                     | 2.3.2                                     | [permissive](https://www.kingrelatedness.com/Download.shtml)
  | ldak[^ldak]                     | 6                                         | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | liftOver[^liftover]             | latest                                    | [permissive](https://genome-store.ucsc.edu)
  | metal[^metal]                   | 2020-05-05                                | -
  | minimac4[^minimac4]             | v4.1.6                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | plink[^plink19]                 | v1.90b7.2 64-bit (11 Dec 2023)            | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | plink2[^plink2]                 | v2.00a5.10LM 64-bit Intel (5 Jan 2024)    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | plink2_avx2[^plink2]            | v2.00a5.10LM AVX2 Intel (5 Jan 2024)      | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | PRSice_linux[^prsice]           | 2.3.5                                     | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | qctool[^qctool]                 | 2.2.2, revision e5723df2c0c85959          | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | regenie[^regenie]               | v3.4                                      | [MIT/Boost](https://github.com/rgcgithub/regenie/blob/master/LICENSE)
  | samtools[^bcftools]             | v1.19.2                                   | [MIT/ExpatD](https://github.com/samtools/samtools/blob/develop/LICENSE)
  | shapeit4.2[^shapeit4]           | v4.2.2                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5[^shapeit5] phase_rare  | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5[^shapeit5] phase_common | v5.1.1                                  | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5[^shapeit5] ligate      | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5[^shapeit5] switch      | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | shapeit5[^shapeit5] xcftools    | v5.1.1                                    | [MIT](https://opensource.org/licenses/MIT)
  | simu_linux[^simu]               | v0.9.4                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | snptest[^snptest]               | v2.5.6                                    | [permissive](https://www.chg.ox.ac.uk/~gav/snptest/#download)
  | switchError[^switcherror]       | 6e688b1                                   | [MIT](https://opensource.org/licenses/MIT)
  | vcftools[^vcftools]             | 0.1.17 (git SHA: d511f469e)               | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

[^bcftools]: Petr Danecek, James K Bonfield, Jennifer Liddle, John Marshall, Valeriu Ohan, Martin O Pollard, Andrew Whitwham, Thomas Keane, Shane A McCarthy, Robert M Davies, Heng Li, Twelve years of SAMtools and BCFtools, GigaScience, Volume 10, Issue 2, February 2021, giab008, <https://doi.org/10.1093/gigascience/giab008>

[^bedtools]: Aaron R. Quinlan, Ira M. Hall, BEDTools: a flexible suite of utilities for comparing genomic features, Bioinformatics, Volume 26, Issue 6, March 2010, Pages 841–842, <https://doi.org/10.1093/bioinformatics/btq033>

[^beagle1]: B L Browning, X Tian, Y Zhou, and S R Browning (2021) Fast two-stage phasing of large-scale sequence data. Am J Hum Genet 108(10):1880-1890. doi:10.1016/j.ajhg.2021.08.005

[^beagle2]: B L Browning, Y Zhou, and S R Browning (2018). A one-penny imputed genome from next generation reference panels. Am J Hum Genet 103(3):338-348. doi:10.1016/j.ajhg.2018.07.015

[^bgenix]: [https://enkre.net/cgi-bin/code/bgen/wiki?name=bgenix](https://enkre.net/cgi-bin/code/bgen/wiki?name=bgenix)

[^bolt]: Loh, P.-R. et al. Efficient Bayesian mixed model analysis increases association power in large cohorts. Nature Genetics 47, 284–290 (2015).

[^cat-bgen]: [https://enkre.net/cgi-bin/code/bgen/wiki?name=cat-bgen](https://enkre.net/cgi-bin/code/bgen/wiki?name=cat-bgen)

[^duohmm]: O'Connell J, Gurdasani D, Delaneau O, Pirastu N, Ulivi S, et al. (2014) A General Approach for Haplotype Phasing across the Full Spectrum of Relatedness. PLOS Genetics 10(4): e1004234. <https://doi.org/10.1371/journal.pgen.1004234>

[^eagle]: Loh, P.-R. et al. Reference-based phasing using the Haplotype Reference Consortium panel. Nature Genetics 48, 1443–1448 (2016)

[^edit-bgen]: [https://enkre.net/cgi-bin/code/bgen/wiki?name=edit-bgen](https://enkre.net/cgi-bin/code/bgen/wiki?name=edit-bgen)

[^flashpca]: Gad Abraham, Yixuan Qiu, Michael Inouye, FlashPCA2: principal component analysis of Biobank-scale genotype datasets, Bioinformatics, Volume 33, Issue 17, September 2017, Pages 2776–2778, <https://doi.org/10.1093/bioinformatics/btx299>

[^gcta]: Yang J, Lee SH, Goddard ME, Visscher PM. GCTA: a tool for genome-wide complex trait analysis. Am J Hum Genet. 2011 Jan 7;88(1):76-82. doi: 10.1016/j.ajhg.2010.11.011. Epub 2010 Dec 17.

[^gctb]: Zeng, J., de Vlaming, R., Wu, Y. et al. Signatures of negative selection in the genetic architecture of human complex traits. Nat Genet 50, 746–753 (2018). <https://doi.org/10.1038/s41588-018-0101-4>

[^gwama]: Mägi, R., Morris, A.P. GWAMA: software for genome-wide association meta-analysis. BMC Bioinformatics 11, 288 (2010). <https://doi.org/10.1186/1471-2105-11-288>

[^htslib]: James K Bonfield, John Marshall, Petr Danecek, Heng Li, Valeriu Ohan, Andrew Whitwham, Thomas Keane, Robert M Davies, HTSlib: C library for reading/writing high-throughput sequencing data, GigaScience, Volume 10, Issue 2, February 2021, giab007, <https://doi.org/10.1093/gigascience/giab007>

[^king]: Ani Manichaikul, Josyf C. Mychaleckyj, Stephen S. Rich, Kathy Daly, Michèle Sale, Wei-Min Chen, Robust relationship inference in genome-wide association studies, Bioinformatics, Volume 26, Issue 22, November 2010, Pages 2867–2873, <https://doi.org/10.1093/bioinformatics/btq559>

[^ldak]: Speed, D., Cai, N., the UCLEB Consortium. et al. Reevaluation of SNP heritability in complex human traits. Nat Genet 49, 986–992 (2017). <https://doi.org/10.1038/ng.3865>

[^liftover]: Phuc-Loi Luu, Phuc-Thinh Ong, Thanh-Phuoc Dinh, Susan J Clark, Benchmark study comparing liftover tools for genome conversion of epigenome sequencing data, NAR Genomics and Bioinformatics, Volume 2, Issue 3, September 2020, lqaa054, <https://doi.org/10.1093/nargab/lqaa054>

[^metal]: Cristen J. Willer, Yun Li, Gonçalo R. Abecasis, METAL: fast and efficient meta-analysis of genomewide association scans, Bioinformatics, Volume 26, Issue 17, September 2010, Pages 2190–2191, <https://doi.org/10.1093/bioinformatics/btq340>

[^minimac4]: [https://genome.sph.umich.edu/wiki/Minimac4](https://genome.sph.umich.edu/wiki/Minimac4)

[^plink19]: Christopher C Chang, Carson C Chow, Laurent CAM Tellier, Shashaank Vattikuti, Shaun M Purcell, James J Lee, Second-generation PLINK: rising to the challenge of larger and richer datasets, GigaScience, Volume 4, Issue 1, December 2015, s13742–015–0047–8, <https://doi.org/10.1186/s13742-015-0047-8>

[^plink2]: [https://www.cog-genomics.org/plink/2.0/](https://www.cog-genomics.org/plink/2.0/)

[^prsice]: Shing Wan Choi, Paul F O'Reilly, PRSice-2: Polygenic Risk Score software for biobank-scale data, GigaScience, Volume 8, Issue 7, July 2019, giz082, <https://doi.org/10.1093/gigascience/giz082>

[^qctool]: [https://code.enkre.net/qctool](https://code.enkre.net/qctool)

[^regenie]: Mbatchou, J., Barnard, L., Backman, J. et al. Computationally efficient whole-genome regression for quantitative and binary traits. Nat Genet 53, 1097–1103 (2021). <https://doi.org/10.1038/s41588-021-00870-7>

[^shapeit4]: Delaneau, O., Zagury, JF., Robinson, M.R. et al. Accurate, scalable and integrative haplotype estimation. Nat Commun 10, 5436 (2019). <https://doi.org/10.1038/s41467-019-13225-y>

[^shapeit5]: Hofmeister, R.J., Ribeiro, D.M., Rubinacci, S. et al. Accurate rare variant phasing of whole-genome and whole-exome sequencing data in the UK Biobank. Nat Genet 55, 1243–1249 (2023). <https://doi.org/10.1038/s41588-023-01415-w>

[^simu]: [https://github.com/precimed/simu](https://github.com/precimed/simu)

[^snptest]: [https://www.chg.ox.ac.uk/~gav/snptest/#download](https://www.chg.ox.ac.uk/~gav/snptest/#download)

[^switcherror]: O'Connell J, Gurdasani D, Delaneau O, Pirastu N, Ulivi S, et al. (2014) A General Approach for Haplotype Phasing across the Full Spectrum of Relatedness. PLOS Genetics 10(4): e1004234. <https://doi.org/10.1371/journal.pgen.1004234>

[^vcftools]: Danecek P, Auton A, Abecasis G, Albers CA, Banks E, DePristo MA, Handsaker RE, Lunter G, Marth GT, Sherry ST, McVean G, Durbin R;
