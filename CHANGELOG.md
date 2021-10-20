The development of CoMorMent containers is organized in the following GitHub repositories:
* https://github.com/comorment/containers includes singularity containers (.sif), publicly available reference data, documentation, use cases, and scripts such as gwas.py
* https://github.com/comorment/gwas includes source code used to build containers
* https://github.com/comorment/reference includes reference data with access restricted to CoMorMent collaborator, or instructions how to access such data on secure clusters

All of these repositories have similar version tags on github, e.g. here is ``v1.0.0`` across all repositories:
* https://github.com/comorment/containers/releases/tag/v1.0.0
* https://github.com/comorment/gwas/releases/tag/v1.0.0
* https://github.com/comorment/reference/releases/tag/v1.0.0

To identify the version of each .sif container we recommend running ``md5sum <container>.sif`` command, and find md5sum on the list below.
If md5sum is not listed for a container for a certain release, then it means that the container hasn't been changed in that release.

*Pending changes*

- add CHANGELOG.md (this file)

*Version 1.0.0* - initial release, Wed Oct 20, 2021

```
70502c11d662218181ac79a846a0937a  enigma-cnv.sif
1ddd2831fcab99371a0ff61a8b2b0970  gwas.sif
b02fe60c087ea83aaf1b5f8c14e71bdf  hello.sif
1ab5d82cf9d03ee770b4539bda44a5ba  ipsychcnv.sif
6d024aed591d8612e1cc628f97d889cc  ldsc.sif
2e638d1acb584b42c6bab569676a92f8  matlabruntime.sif
331688fb4fb386aadaee90f443b50f8c  python3.sif
cdbfbddc9e5827ad9ef2ad8d346e6b82  r.sif
b8c1727227dc07e3006c0c8070f4e22e  regenie.sif
97f75a45a39f0a2b3d728f0b8e85a401  regenie3.sif
20e01618bfb4b0825ef8246c5a63aec5  saige.sif
5de579f750fb5633753bfda549822a32  tryggve_query.sif
```

