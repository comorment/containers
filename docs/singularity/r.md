# ``r.sif`` container

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
