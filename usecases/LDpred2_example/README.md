# LDpred2 example

Example running LDpred2
(Privé et al., Bioinformatics, Volume 36, Issue 22-23, 1 December 2020, Pages 5424–5431, <https://doi.org/10.1093/bioinformatics/btaa1029>)
for deriving polygenic scores based on summary statistics and a matrix of correlation between genetic variants.

To run the example, issue in a terminal

```
bash run.sh
```

For indepth explanations of the example codes, cf. the [LDpred2 tutorial](https://privefl.github.io/bigsnpr/articles/LDpred2.html).

The main purpose of the `run.sh` shell script is for testing the functionality of the [`LDpred2.R` script](https://github.com/comorment/containers/blob/main/usecases/LDpred2/ldpred2.R),
but may be set up for other datasets.

Changing the line `LDPRED_MODES="inf"` to `LDPRED_MODES="auto"` allows running the LDpred2 analysis in "automatic" mode.
