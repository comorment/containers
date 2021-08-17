The results of GWAS are represented as summary statistics, with the following columns:

* ``SNP`` - marker name, for example rs#.
* ``CHR`` - chromosome label
* ``BP`` - base-pair position
* ``A1`` - effect allele for ``Z`` and ``BETA`` columns
* ``A2`` - other allele
* ``N`` - sample size
* ``CaseN``, ``ControlN`` - sample size for cases and controls (logistic regression only)
* ``FRQ`` - frequency of A1 allele
* ``Z`` - z-score (or t-score) of association
* ``BETA`` - effect size; for logistic regression, this contains ``log(OR)``
* ``SE`` - standard error of the ``BETA`` column
* ``L95``, ``U95`` - lower and upper 95% confidence interval of the ``BETA``.
* ``P`` -- p-value

For ``SNP``, ``CHR``, ``BP``, ``A1`` and ``A2`` columns the [gwas.py](gwas.py) script will simply copy over the information from the genetic file, i.e. from ``.bgen`` or ``.bim`` files. This means that ``SNP`` is likely to be dbSNP rs#, or some other form of identifyied such as ``CHR:BP:A1:A2``. 
For ``CHR`` and ``BP``, there we don't enforce a specific genomic build - it all depends on what build was used by the genotype data.
Finally, ``A1`` and ``A2`` are not guarantied to be minor or major alleles, but ``A1`` will be used as an effect allele for signed summary statistics (i.e. ``Z`` and ``BETA`` columns).

The sample size ``N`` is as reported by the software (``plink2`` or ``regenie``). For case-control traits, this appears to be a sum of cases and controls (not the effective sample size which would take into account imbalance between cases and controls).

``L95`` and ``U95`` columns are only provided for ``plink2`` results.
``CaseN`` and ``ControlN`` columns are only provided for ``plink2`` results for logistic regression.
If you need these columns for ``regenie`` analysis consider also running ``plink2`` analysis, and copy over the columns into your ``regenie`` output.

## Comparison of columns names

* CoMorMent: this file
* LDSC: https://github.com/precimed/ldsc/blob/master/munge_sumstats.py
* BioPsyk: https://github.com/BioPsyk/cleansumstats/blob/dev/assets/schemas/cleaned-sumstats.yaml
* NORMENT: https://github.com/precimed/python_convert/blob/master/sumstats_utils.py


| CoMorMent     | daner         | LDSC          | BioPsyk       | NORMENT       | Description |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| missing       | ?             | missing       | 0             | missing       | good idea to provide this column and referencing a line in .bim file     |
| CHR           | CHR           | CHR           | CHR           | CHR           | OK     |
| BP            | BP            | BP            | POS           | BP            | keep BP which is more informative ( "POS" could also stand for genomic position )    |
| SNP           | SNP           | SNP           | RSID          | SNP           | keep SNP which makes more sense as we copy over marker name from  genetic file      |
| A1            | A1            | A2            | EffectAllele  | A1            | keep A1 for consistency with LDSC even thought EffectAllele is more informative  |
| A2            | A2            | A2            | OtherAllele   | A2            | keep A2 for consistency with LDSC even though OtherAllele is more informative |
| P             | P             | P             | P             | PVAL          | OK    |
| SE            | SE            | SE            | SE            | SE            | OK     |
| L95           | ?             | missing       | ORL95         | missing       | keep "L95" as confidence interval may also be for the BETA or LOG(OR) |
| U95           | ?             | missing       | ORU95         | missing       | keep "U95"    |
| N             | ?             | N             | N             | N             | OK     |
| CaseN         | Nca           | N_CAS         | CaseN         | NCASE         | OK     |
| ControlN      | Nco           | N_CON         | ControlN      | NCONTROL      | OK     |
| INFO          | INFO          | INFO          | INFO          | INFO          | OK     |
| Direction     | Direction     | missing       | Direction     | DIRECTION     | OK     |
| BETA          | BETA or OR    | BETA          | B             | BETA or OR    | keep "BETA" for consistency with LDSC (and also BETA is more informative)     |
| Z             | ?             | Z             | Z             | Z             | OK     |
| FRQ           | FRQ_A_NNN     | FRQ           | EAF           | FRQ           | keep "FRQ" which makes more sense for non-EUR populations     |
| missing       | ?             | missing       | EAF_1KG       | missing       | not needed     |

