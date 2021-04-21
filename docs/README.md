Here is a brief overview of available containers (more info in the links below):

* [hello.sif](hello.md) - a simple container for demo purpose, allowing to experiment with singularity features
* [gwas.sif](gwas.md) - multiple tools (released as binaries/executables) for imputation and GWAS analysis
* [matlabruntime.sif](matlabruntime.md) - container allowing to run several tools implemented in MATLAB
* [python3.sif] - python3 environment with pre-installed modules and tools
* [r.sif] - R environment
* [ldsc.sif] - LD score regression

To simplify instructions throughout this repository, we assume that certain folders are mounted to your container:
* ``--bind containers/reference:/REF:ro`` - public reference data (read-only)
* ``--bind containers/matlab:/MATLAB:ro`` - matlab binaries (read-only)
* ``--bind reference:/REF2:ro`` - private reference data (read-only)
* ``--bind out:/OUT:rw`` - any output folder of your choice (read-write)
You may either add this flags to your singularity command:
```
singularity shell --bind containers/reference:/REF:ro,containers/matlab:/MATLAB:ro,reference:/REF2:ro,out:/OUT:rw <container>.sif
```
or create environmental variable like this, then use ``singularity shell <container.sif>``.
```
export SINGULARITY_BIND="containers/reference:/REF:ro,containers/matlab:/MATLAB:ro,reference:/REF2:ro,out:/OUT:rw"
```
We also recommend using ``--container`` or ``--no-home`` arguments to better isolate container from the environment in your host machine.

All containers have a common set of linux tools like ``gzip``, ``tar``, ``parallel``, etc.
Please open an issue if you'd like to add more of such basic tools.
Please [let us know](https://github.com/comorment/containers/issues/new) if you face any problems.

