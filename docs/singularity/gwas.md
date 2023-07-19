# ``gwas.sif`` container

The ``gwas.sif`` container file has multiple tools related to imputation and GWAS analysis, as summarized in this [table](./../../docker/README.md#software-versions).

Note that some specific tools (e.g. ``bolt``) are added to the path directly from their ``/tools`` folder (e.g. ``/tools/bolt``) due to hard-linked dependencies.
Either way, all tools can be invoked by their name, as listed above. For example:

```
>singularity exec gwas.sif regenie
              |=============================|
              |      REGENIE v2.0.2.gz      |
              |=============================|

Copyright (c) 2020 Joelle Mbatchou and Jonathan Marchini.
Distributed under the MIT License.
Compiled with Boost Iostream library.
Using Intel MKL with Eigen.

ERROR: You must provide an output prefix using '--out'
For more information, use option '--help' or visit the website: https://rgcgithub.github.io/regenie/
```
