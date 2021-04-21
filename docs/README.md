Here is a brief overview of available containers (more info in the links below):

* [hello.sif](hello.md) - a simple container for demo purpose, allowing to experiment with singularity features
* [gwas.sif](gwas.md) - multiple tools (released as binaries/executables) for imputation and GWAS analysis
* [matlabruntime.sif](../matlab/README.md) - container allowing to run several tools implemented in MATLAB
* [python3.sif] - python3 environment with pandas and many other libraries, and several pre-downloaded tools (e.g. ``/tools/python_convert``)
* [r.sif] - R environment
* [ldsc.sif] - LD score regression

All containers have a common set of linux tools like ``gzip``, ``tar``, ``parallel``, etc.
Please open an issue if you'd like to add more of such basic tools.
Please [let us know](https://github.com/comorment/containers/issues/new) if you face any problems.