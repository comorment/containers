This is a specification of the input data format for GWAS anslysis, recommended in CoMorMent projects.
Current version: ``v0.9``. Further changes from this version will be documented.

### Genotypes
 
We expect imputed genotype data, which may be split into multiple *cohorts* at each site.
For example, MoBa imputed genotype data is currently split into three cohorts, one per genotype array: GSA, OMNI and HCE.
In this context, a *cohort* is a unit of GWAS analysis, and we do not make distinction between studies (i.e. TOP, DemGENE, HUNT, MoBa),
and sub-cohorts within each study.
If you have multiple studies, each with a set of sub-cohorts,
we suggest to organize it into folders as follows ``<STUDY>_<COHORT>``
(for example, ``MOBA_GSA``, ``MOBA_OMNI``, ``MOBA_HCE``, ``TOP``, ``DemGENE``, ``HUNT``).

We expect the data to be in plink format (.bed/.bim.fam), split per chromosomes, organized for example as follows:
```
<BASEPATH>/<COHORT>/chr@.[bed,bim,fam]        # hard calls in plink format (@ indicates chr label)
<BASEPATH>/<COHORT>/chr@.[vcf.gz,vcf.gz.tbi]  # dosages (either compressed .vcf files, or .bgen format)
<BASEPATH>/<COHORT>/chr@.[bgen,sample]
```

It is recommended (but not required) that all genetic data within cohort is placed into it's own folder.
A strict requirement is that within each cohort the files are only different by chromosome label, so it is possible
to specify them by a single prefix with ``@`` symbol indicating the location of a chromosome label.
If your data is organized differently, we recommend to use 
[symbolic links](https://stackoverflow.com/questions/1951742/how-can-i-symlink-a-file-in-linux),
rather than making a full copy of the data.
We also recommend to set the data as **read-only** using ``chmod 0444 $BASEPATH/$COHORT/chr*`` command.

Many analyses use only plink files.
However, dosage files are required for some analysis, for example SAIGE.
For each analysis you need to provide dosage data in a compatible format
(but we will provide a set of scripts or examples to help converting data between different formats).
For example, SAIG recognize either compressed ``.vcf.gz`` files (with corresponding ``.vcf.gz.tbi`` index),
or ``.bgen / .sample`` formats.
For ``.vcf.gz``, please note that they should be compressed with ``bgzip`` ([see here](https://www.biostars.org/p/59492/))
```
bgzip -c file.vcf > file.vcf.gz
tabix -p vcf file.vcf.gz
```

In the ``.fam`` files, we require ``IID`` column to be globally unique (not just unique within families).
Currently there is no need to provide family annotations, sex information, or phenotype information in ``.fam`` files,
this information is currently not used in the downstream analysis.
In the future we will consider adding a separate file to add pedigree information,
to accomodate more complex family structures than what is feasible with ``.fam`` file.
Currently we do not require ``IID`` values to be unique across cohorts.
  
At of now, we only support the analysis for autosomes (chr 1..22).
Support for other chromosomes will came later.
We expect the same set of individuals across all autosomes (chr 1..22). 
   
### Phenotypes and covariates

For phenotypes and covariates, we expect the data to be organized in a single comma-separated file (hereinafter referred to as *phenotype file*), 
with rows corresponding to individuals, and columns corresponding to relevant variables of interest or covariates.
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
The file must contain all covariates needed for GWAS analysis, including age, sex, principal genetic components, 
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
The file may have other optional columns, i.e. description of each variable.
The file should have column names, first two columns must have names ``COLUMN`` and ``TYPE``.

The purpose of the ``pheno.dict`` file is to allow scripts to choose correct analysis:
for example, if target variable is continous, we can run GWAS with linear regression mode,
while if target variable is binary, we will run logistic regression;
similarly, if a nominal variable is used as covariate, then it will be included as factor.

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
COLUMN,TYPE,DESCRIPTION
IID,IID,Identifier
SEX,NOMINAL,Sex (M - male, F - female)
MDD,BINARY,Major depression diagnosis
PC1,CONTINUOUS,First principal component
PC2,CONTINUOUS,2nd principal component
PC3,CONTINUOUS,3rd principal component
...
```

### Change log

* ``v0.9`` - first version of this document
