# ``r.sif`` container

## Description

The ``r.sif`` container has multiple genomics tools related based on R.
Please confer this [table](./../../docker/README.md#software-versions) for the more complete list.

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

  | OS/tool             | version                                   | license
  | ------------------- | ----------------------------------------- | -------------
  | r.sif             | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | r.sif             | R                   | 4.0.5 (2021-03-31) + data.table, ggplot, etc. | [misc](https://www.r-project.org/Licenses/)
  | r.sif             | gcta64              | 1.94.1                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | r.sif             | GenomicSEM          | [GenomicSEM/GenomicSEM@bcbbaff](https://github.com/GenomicSEM/GenomicSEM/commit/bcbbaffff5767acfc5c020409a4dc54fbf07876b)  | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | r.sif             | GSMR                | v1.0.9                                    | [GPL>=v2](https://www.gnu.org/licenses/gpl-2.0.html)
  | r.sif             | rareGWAMA           | [dajiangliu/rareGWAMA@72e962d](https://github.com/dajiangliu/rareGWAMA/commit/72e962dae19dc07251244f6c33275ada189c2126)  | -
  | r.sif             | seqminer            | [zhanxw/seqminer@142204d](https://github.com/zhanxw/seqminer/commit/142204d1005553ea87e1740ff97f0286291e41f9)  | [GPL](https://github.com/zhanxw/seqminer/blob/master/LICENSE)
  | r.sif             | PRSice_linux        | 2.3.5                                     | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | r.sif             | TwoSampleMR         | [MRCIEU/TwoSampleMR@c174107](https://github.com/MRCIEU/TwoSampleMR/commit/c174107cfd9ba47cf2f780849a263f37ac472a0e)  | [unknown/MIT](https://github.com/MRCIEU/TwoSampleMR#:~:text=Unknown%2C%20MIT%20licenses-,found,-Citation)
  | r.sif             | snpStats            | v1.40.0                                   | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
