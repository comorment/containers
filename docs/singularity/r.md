# ``r.sif`` container

## Description

The ``r.sif`` container has multiple genomics tools related based on R.
Please confer the [Software](#software) table below for the more complete list.

In addition several standard R packages are also included (e.g. data.table, ggplot2, rmarkdown, etc.)

Please report an [issue](https://github.com/comorment/containers/issues) if you encounter errors that have not been reported.

For GSMR, the example data (``http://cnsgenomics.com/software/gsmr/static/test_data.zip``) is available in ``$COMORMENT/containers/reference/example/gsmr`` folder.
You may start the container like this:

```
cd $COMORMENT/containers/reference/examples/gsmr
singularity shell --home $PWD:/home $SIF/r.sif 
```

and then follow the official tutorial <https://cnsgenomics.com/software/gsmr/> .
Note that ``gcta64`` tool is also include in ``r.sif`` container, as the tutorial depends on it.

## Software

List of software in the container:

  | OS/tool                   | version                                   | license
  | ------------------------- | ----------------------------------------- | -------------
  | ubuntu                    | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | R[^r]                     | 4.0.5 (2021-03-31) + data.table, ggplot, etc. | [misc](https://www.r-project.org/Licenses/)
  | gcta64[^gcta]             | 1.94.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | GenomicSEM[^genomicsem]   | [GenomicSEM/GenomicSEM@bcbbaff](https://github.com/GenomicSEM/GenomicSEM/commit/bcbbaffff5767acfc5c020409a4dc54fbf07876b)  | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | GSMR[^gsmr]               | v1.0.9                                    | [GPL>=v2](https://www.gnu.org/licenses/gpl-2.0.html)
  | rareGWAMA[^raregwama]     | [dajiangliu/rareGWAMA@72e962d](https://github.com/dajiangliu/rareGWAMA/commit/72e962dae19dc07251244f6c33275ada189c2126)  | -
  | seqminer[^seqminer]       | [zhanxw/seqminer@142204d](https://github.com/zhanxw/seqminer/commit/142204d1005553ea87e1740ff97f0286291e41f9)  | [GPL](https://github.com/zhanxw/seqminer/blob/master/LICENSE)
  | PRSice_linux[^prsice]     | 2.3.5                                     | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | TwoSampleMR[^twosamplemr] | [MRCIEU/TwoSampleMR@c174107](https://github.com/MRCIEU/TwoSampleMR/commit/c174107cfd9ba47cf2f780849a263f37ac472a0e)  | [unknown/MIT](https://github.com/MRCIEU/TwoSampleMR#:~:text=Unknown%2C%20MIT%20licenses-,found,-Citation)
  | snpStats[^twosamplemr]    | v1.40.0                                   | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

[^r]: <https://www.r-project.org>

[^gcta]: Yang J, Lee SH, Goddard ME, Visscher PM. GCTA: a tool for genome-wide complex trait analysis. Am J Hum Genet. 2011 Jan 7;88(1):76-82. doi: 10.1016/j.ajhg.2010.11.011. Epub 2010 Dec 17.

[^genomicsem]: Grotzinger, A.D., Rhemtulla, M., de Vlaming, R. et al. Genomic structural equation modelling provides insights into the multivariate genetic architecture of complex traits. Nat Hum Behav 3, 513–525 (2019). <https://doi.org/10.1038/s41562-019-0566-x>

[^gsmr]: Zhu, Z., Zheng, Z., Zhang, F. et al. Causal associations between risk factors and common diseases inferred from GWAS summary data. Nat Commun 9, 224 (2018). <https://doi.org/10.1038/s41467-017-02317-2>

[^raregwama]: Liu, D., Peloso, G., Zhan, X. et al. Meta-analysis of gene-level tests for rare variant association. Nat Genet 46, 200–204 (2014). <https://doi.org/10.1038/ng.2852>

[^seqminer]: Lina Yang, Shuang Jiang, Bibo Jiang, Dajiang J Liu, Xiaowei Zhan, Seqminer2: an efficient tool to query and retrieve genotypes for statistical genetics analyses from biobank scale sequence dataset, Bioinformatics, Volume 36, Issue 19, October 2020, Pages 4951–4954, <https://doi.org/10.1093/bioinformatics/btaa628>

[^prsice]: Shing Wan Choi, Paul F O'Reilly, PRSice-2: Polygenic Risk Score software for biobank-scale data, GigaScience, Volume 8, Issue 7, July 2019, giz082, <https://doi.org/10.1093/gigascience/giz082>

[^twosamplemr]: Hemani, G., Haycock, P., Zheng, J., Gaunt, T., Elsworth, B., & Palmer, T. (2024). TwoSampleMR R package (v0.5.10). Zenodo. <https://doi.org/10.5281/zenodo.10684540>
