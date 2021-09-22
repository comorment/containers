Lava turorial is available here:
https://github.com/josefin-werme/LAVA

You may a demo analysis by changing to this folder, and executing the following commands:

```
singularity shell --home $PWD:/home $COMORMENT/containers/singularity/r.sif 

Rscript lava_script.R "vignettes/data/g1000_test" "vignettes/data/test.loci" "vignettes/data/input.info.txt" "vignettes/data/sample.overlap.txt" "depression;bmi" "depression.bmi"
```

The following files are generated as an output:
```
depression.bmi.univ.lava
depression.bmi.bivar.lava
```
