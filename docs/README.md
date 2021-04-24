Here is a brief overview of available containers (more info in the links below):

* [hello.sif](hello.md) - a simple container for demo purpose, allowing to experiment with singularity features
* [gwas.sif](gwas.md) - multiple tools (released as binaries/executables) for imputation and GWAS analysis
* [matlabruntime.sif](matlabruntime.md) - container allowing to run several tools implemented in MATLAB
* [python3.sif](python3.md) - python3 environment with pre-installed modules and tools
* [r.sif] - R environment
* [ldsc.sif] - LD score regression

To simplify instructions throughout this repository we use certain variables (it's a good idea to include them in your ``.bashrc`` or similar):
* ``$COMORMENT`` refers to a folder with ``comorment`` and ``reference`` subfolders, containing a clone of [containers](https://github.com/comorment/containers) and [reference](https://github.com/comorment/reference) repositories from GitHub
* ``$SIF`` refers to ``$COMORMENT/containers/singularity`` folder, containing several ``.sif`` files
* ``SINGULARITY_BIND="$COMORMENT/containers/reference:/REF:ro,$COMORMENT/containers/matlab:/MATLAB:ro,$COMORMENT/reference:/REF2:ro"`` defines default bindings within container (``/REF``, ``/REF2`` and ``/MATLAB``). If you don't have access to private reference, try out commands without mapping ``$COMORMENT/reference:/REF2:ro`` - most of the exmples don't require private reference data.
* We assume that all containers run with ``--home $PWD:/home``, mounting current folder mounted as ``/home`` within container
* We also recommend using ``--contain`` argument to better isolate container from the environment in your host machine. If you choose not to mount ``--home $PWD:/home``, you may want to add ``--no-home`` argument.

All containers have a common set of linux tools like ``gzip``, ``tar``, ``parallel``, etc.
Please open an issue if you'd like to add more of such basic tools.
Please [let us know](https://github.com/comorment/containers/issues/new) if you face any problems.

