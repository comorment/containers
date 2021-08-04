This file describe use cases related to meta-analysis.

# GWAMA

To run the example provided with GWAMA software, use this following:

```
cd $COMORMENT/containers/reference/examples/gwama
singularity exec --home $PWD:/home $SIF/gwas.sif GWAMA -qt
```

For more informatino about GWAMA, see here: https://genomics.ut.ee/en/tools/gwama

# METAL

METAL tool for meta-analysis ( https://genome.sph.umich.edu/wiki/METAL_Documentation ) is available in gwas.sif container and can be executed as follows:

```
singularity exec --home $PWD:/home $SIF/gwas.sif metal
```
