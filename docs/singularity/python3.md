# ``python3.sif`` container

## Description

``python3.sif`` container runs [Python](https://python.org) packaged by [Conda-forge](https://conda-forge.org), and has many useful python modules already installed, 
including pandas, numpy, scipy, matplotlib, jupyter and few others (see [here](https://github.com/comorment/gwas/blob/main/containers/python3/Dockerfile) for full details).
Basic usage is very simple:

```
>singularity exec --contain --home $PWD:/home python3.sif python
Python 3.10.6 | packaged by conda-forge | (main, Aug 22 2022, 20:35:26) [GCC 10.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
```

You may also use jupyter notebook like this:
```
singularity exec --contain --home $PWD:/home $SIF/python3.sif jupyter notebook --no-browser --port 8890
```
The port is optional, but you may want to specify it if you'd like to run jupyter on a remote server - in which case you need to enable port forwarding as described [here](https://docs.anaconda.com/anaconda/user-guide/tasks/remote-jupyter-notebook/). This also works if you connect from Windows using Putty as described [here](https://stackoverflow.com/questions/46276612/remote-access-jupyter-notebook-from-windows).

``python3.sif`` container has few additional tools installed:

* ``/tools/ukb/ukb_helper.py`` - https://github.com/precimed/ukb/
* ``/tools/python_convert`` - https://github.com/precimed/python_convert

* ``ldpred`` - https://github.com/bvilhjal/ldpred is installed via pip, simply run 'ldpred --help' to get started


## Software

List of software in the container:

  | OS/tool             | version                                   | license
  | ------------------- | ----------------------------------------- | -------------
  | ubuntu              | 20.04 (LTS)                               | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | LDpred              | 1.0.11                                    | [MIT](https://opensource.org/licenses/MIT)
  | plink               | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | python3             | python 3.10.6 + numpy, pandas, etc.       | [PSF](https://docs.python.org/3.10/license.html)
  | python_convert      | github commit bcde562                     | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  