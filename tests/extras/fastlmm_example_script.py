# https://nbviewer.org/github/fastlmm/FaST-LMM/blob/master/doc/ipynb/FaST-LMM.ipynb
import numpy as np
from fastlmm.association import single_snp
from fastlmm.util import example_file # Download and return local file name
bed_fn = example_file('tests/datasets/synth/all.*','*.bed')
pheno_fn = example_file("tests/datasets/synth/pheno_10_causals.txt")
cov_fn = example_file("tests/datasets/synth/cov.txt")

results_df = single_snp(bed_fn, pheno_fn, covar=cov_fn, count_A1=False)
assert results_df.shape == (5000, 11)
