The results of GWAS are represented as summary statistics, with the following columns:

* ``SNP`` - marker name, for example rs#.
* ``CHR`` - chromosome label
* ``BP`` - base-pair position
* ``A1`` - effect allele for ``Z`` and ``BETA`` columns
* ``A2`` - other allele
* ``N`` - sample size
* ``A1_FREQ`` - frequency of A1 allele
* ``Z`` - z-score (or t-score) of association
* ``BETA`` - effect size; for logistic regression, this contains ``log(OR)``
* ``SE`` - standard error of the ``BETA`` column
* ``L95``, ``U95`` - lower and upper 95% confidence interval of the``BETA``.
* ``PVAL`` -- p-value

For ``SNP``, ``CHR``, ``BP``, ``A1`` and ``A2`` columns the [gwas.py](gwas.py) script will simply copy over the information from the genetic file, i.e. from ``.bgen`` or ``.bim`` files. This means that ``SNP`` is likely to be dbSNP rs#, or some other form of identifyied such as ``CHR:BP:A1:A2``. 
For ``CHR`` and ``BP``, there we don't enforce a specific genomic build - it all depends on what build was used by the genotype data.
Finally, ``A1`` and ``A2`` are not guarantied to be minor or major alleles, but ``A1`` will be used as an effect allele for signed summary statistics (i.e. ``Z`` and ``BETA`` columns).

The sample size ``N`` is as reported by the software (``plink2`` or ``regenie``). For case-control traits, this appears to be a sum of cases and controls (not the effective sample size which would take into account imbalance between cases and controls).

The ``L95`` and ``U95`` is only provided for ``plink2`` results.
