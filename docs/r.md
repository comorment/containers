The ``r.sif`` container has multiple tools related based on R:
```
    seqminer               # https://github.com/zhanxw/seqminer
    rareGWAMA              # https://github.com/dajiangliu/rareGWAMA
    GenomicSEM             # https://github.com/GenomicSEM/GenomicSEM
    TwoSampleMR            # https://github.com/MRCIEU/TwoSampleMR
    GSMR                   # https://cnsgenomics.com/software/gsmr
```

In addition several standard R packages are also included (e.g. data.table, ggplot2, rmarkdown, etc.

I haven't tested the packages except that ``library('<package>')`` works well. Please report if you see any errors.

For GSMR, the example data (``http://cnsgenomics.com/software/gsmr/static/test_data.zip``) is availabel in $COMORMENT/containers/reference/example/gsmr folder.
You may start the container like this:
```
cd $COMORMENT/containers/reference/examples/gsmr
singularity shell --home $PWD:/home $SIF/r.sif 
```
and then follow the official tutorial https://cnsgenomics.com/software/gsmr/ . 
Note that ``gcta64`` tool is also include in ``r.sif`` container, as the tutorial depends on it.

