# ``r.sif`` container

## Description

The ``r.sif`` container has multiple genetics tools based or relying on R, with a full R environment and Rstudio-server, based on the [Rocker Project](https://rocker-project.org/images/) `rocker/verse` image.
Please refer to the [Software](#software) table below for details.
In addition, several standard R packages are also included (e.g. data.table, ggplot2, rmarkdown, etc.)

Please report an [issue](https://github.com/comorment/containers/issues) if you encounter errors that have not been reported.

For GSMR, the example data (``http://cnsgenomics.com/software/gsmr/static/test_data.zip``) is available in ``$COMORMENT/containers/reference/example/gsmr`` folder.
You may start the container like this:

```
cd $COMORMENT/containers/reference/examples/gsmr
apptainer shell --home $PWD:/home $SIF/r.sif 
```

and then follow the official tutorial <https://cnsgenomics.com/software/gsmr/> .
Note that ``gcta64`` tool is also included in ``r.sif`` container, as the tutorial depends on it.

## Invoking Rstudio-server

The `r.sif` container includes Rstudio-server, which can be accessed in a browser running on the host machine by

1. Start Rstudio-server on the local or remote machine as:

  ```
  cd <working/dir>
  mkdir -p run var-lib-rstudio-server
  printf 'provider=sqlite\ndirectory=/var/lib/rstudio-server\n' > database.conf
  apptainer exec --bind run:/run,var-lib-rstudio-server:/var/lib/rstudio-server,database.conf:/etc/rstudio/database.conf --home=$PWD <path/to>/r.sif /usr/lib/rstudio-server/bin/rserver --www-address=127.0.0.1 --www-port=8787 --server-user $USER
  ```
  
  where `<working/dir>` is the directory where you want to start Rstudio-server, and `<path/to/r.sif>` is the path to the `r.sif` container.

  If you want to mount additional directories, you can append the ``--bind`` argument to the apptainer call (attaching ``/ess`` and ``/cluster`` as examples):
  ```
  --bind run:/run,var-lib-rstudio-server:/var/lib/rstudio-server,database.conf:/etc/rstudio/database.conf,/ess:/ess,/cluster:/cluster
  ```

  If you get messages like “address already in use”, try and replace the port number 8787 with another port number (e.g., 8888, etc.) everywhere in the steps above and below.

2. (Optional) Create SSH tunnel using port 8787 from the local host to the remote machine

  ```
  ssh -N -f -L "localhost:8787:localhost:8787" <remote/machine/address>  # replace <remote/machine/address> as necessary
  ```

3. Then, open address [0.0.0.0:8787](https://0.0.0.0:8787) or [127.0.0.1:8787](https://127.0.0.1:8787) in a web browser like Firefox on the host.

Please refer to the Rocker Project [documentation](https://rocker-project.org/use/singularity.html) for more details.

## Software

### Genetic analysis software

List of main software in the container:

  | OS/tool                   | version                                   | license
  | ------------------------- | ----------------------------------------- | -------------
  | ubuntu                    | 24.04LTS                                   | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | R[^r]                     | 4.5.1 (2025-06-13) + data.table, ggplot, etc. | [misc](https://www.r-project.org/Licenses/)
  | gcta64[^gcta]             | 1.94.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | GenomicSEM[^genomicsem]   | [GenomicSEM/GenomicSEM@8e0ef5](https://github.com/GenomicSEM/GenomicSEM/commit/8e0ef594e95885b1f734f1dfcfe668b16ada2880)  | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
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

### R packages

In addition to the `rocker/verse` image and the above genomics tools listed above there are a host of additional R packages and dependencies installed in the container.
See the installer scripts for [CRAN](https://github.com/comorment/containers/blob/main/docker/scripts/R/cran.R), 
[Bioconductor](https://github.com/comorment/containers/blob/main/docker/scripts/R/bioconductor.R), 
[GitHub](https://github.com/comorment/containers/blob/main/docker/scripts/R/github.R), 
and [source](https://github.com/comorment/containers/blob/main/docker/scripts/R/source.R) packages for details.
