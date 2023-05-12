# Genotypes

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
