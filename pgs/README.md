# PGS toolset

More on PGS: https://choishingwan.github.io/PRS-Tutorial/

## Codes

- ``README.md``: this file
- ``pgrs.py``: Python class definitions setup to create bash commands for different PGS tools (``plink``, ``PRSice2``, ``LDpred2``, etc.)
- ``run_pgrs.py``: Python run script setup to run PGS tools on datas provided in this repository, mainly for testing purposes.
- ``pgrs_exec.py``: ``gwas.py`` like command line tool that can be used to run, create bash and slurm job scripts for different PGS tools. See ``python pgrs_exec.py --help`` for options. 
- ``*.R``: misc. ``R`` scripts defining or being used by the PGS tools or optional QC steps. 
- ``vis_pgs.ipynb``: Jupyter notebook plotting/comparing the PGS scores.
- ``start_jupyter_server.py``: start a Jupyter server using the ``python3.sif`` container (allows running ``vis_pgs.ipynb`` within VSCode with the Jupyter extension for instance)
- ``config.yaml``: YAML file defining some parameters for Slurm jobscripts and PGS methods

## Running the codes

(subject to change)

```
$ python run_pgrs.py
```

> **_NOTE:_**  The script may require other packages than Python builtins, such as ``pandas`` and ``pyyaml``.  
