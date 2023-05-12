# Phenotypes and covariates

For phenotypes and covariates, we expect the data to be organized in a single delimiter-separated file (hereinafter referred to as *phenotype file*),
with rows corresponding to individuals, and columns corresponding to relevant variables of interest or covariates.
By default the delimiter is expected to be a comma, but also can be tab, semicolon, space, or a white-space delimited file.
Phenotype file should be accompanied by a *data dictionary* file, as described below.
We expect a single phenotype file and a single data dictionary file for each cohort:

```
<BASEPATH>/<COHORT>/pheno.csv
<BASEPATH>/<COHORT>/pheno.dict
```

Off note: when we run GWAS analysis on a given cohort, we use subjects that has both genetic and phenotype data available,
thus it's fine to include subjects without genetic data in the phenotype file.
If you have sub-cohorts of the same study, it is OK to re-use one phenotype file containing information for all sub-cohorts,
as long all subjects have a unique IID across cohorts.

The phenotype file must include a subject IID column, containing identifiers that matches the IID in genetic data
(i.e. the ``IID`` column in plink ``.fam`` files).
If ``FID`` column is included in the phenotype file it will be simply ignored.
All subjects should be uniquely identified by their ``IID``.
This is against plink specification for the ``.fam`` file, however other software may not support
subject identification through a pair of (FID, IID). Because of this we require all subject IIDs to be unique across families.

The phenotype file must contain all covariates needed for GWAS analysis, including age, sex, principal genetic components,
and other confounters such as genetic batch or plate, if needed. Column names in the phenotype file must be unique.
It is OK to include other relevant columns in the phenotype file - a GWAS analysis can be customized to use a subset of columns,
as well as a subset of subjects.

Missing values should be encoded by empty string (see example below).
It is allowed to use ``#`` to comment out first lines.
Columns required in phenotype file: ``IID`` and ``SEX`` (note that use of ``IID``, not ``ID``, to match plink nomenclature).

Phenotype file should be accompanied by a *data dictionary* file,
which define whether each variable is a binary (case/control), nominal (a discrete set of values) or continuous.
The data dictionary should be a file with two columns, one row per variable (listed in the first column),
with second column having values *BINARY*, *NOMINAL*, *ORDINAL*, *CONTINUOUS* or *IID*.
Exactly one column must be marked with *IID* type.
The file may have other optional columns, i.e. description of each variable.
The file should have column names, first two columns must have names ``FIELD`` and ``TYPE``.

The purpose of the ``pheno.dict`` file is to allow scripts to choose correct analysis:
for example, if target variable is continous, we can run GWAS with linear regression mode,
while if target variable is binary, we will run logistic regression;
similarly, if a nominal variable is used as covariate, then it will be included as factor.

Binary variables must be encoded as 1 (cases) and 0 (controls).
This is default in [regenie](https://rgcgithub.github.io/regenie/options/#phenotype-file-format).
For [plink](https://www.cog-genomics.org/plink2/formats), such coding can be used with ``--1`` argument.
If you have a binary variable such as SEX and you want to keep the actual labels (e.g. "male" and "female"),
then you should mark it as "NOMINAL" in the dictionary file.

Example ``MoBa/pheno.csv`` file. Subject ``IID=3`` have missing values for ``SEX`` and ``MDD``.

```
# optional comments or description
IID,SEX,MDD,PC1,PC2,PC3
1,M,0,0.1,0.2,0.3
2,F,1,0.4,0.5,0.6
3,,,0.6,0.7,0.8
4,M,0,0.9,0.1,0.2
...
```

Example ``MoBa/pheno.dict`` file:

```
FIELD,TYPE,DESCRIPTION
IID,IID,Identifier
SEX,NOMINAL,Sex (M - male, F - female)
MDD,BINARY,Major depression diagnosis
PC1,CONTINUOUS,First principal component
PC2,CONTINUOUS,2nd principal component
PC3,CONTINUOUS,3rd principal component
...
```
