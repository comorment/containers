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

* ``/tools/ukb/ukb_helper.py`` - <https://github.com/precimed/ukb/>
* ``/tools/python_convert`` - <https://github.com/precimed/python_convert>

* ``ldpred`` - <https://github.com/bvilhjal/ldpred> is installed via pip, simply run 'ldpred --help' to get started

## Software

List of software in the container:

  | OS/tool                     | version                                   | license
  | --------------------------- | ----------------------------------------- | -------------
  | ubuntu                      | 20.04 (LTS)                               | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | LDpred[^ldpred]             | 1.0.11                                    | [MIT](https://opensource.org/licenses/MIT)
  | plink[^plink19]             | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | python3[^python3]           | python 3.10.6 + numpy, pandas, etc.       | [PSF](https://docs.python.org/3.10/license.html)
  | python_convert[^convert]    | git SHA bcde562                           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

[^ldpred]: Bjarni J. Vilhjálmsson, et al. Modeling Linkage Disequilibrium Increases Accuracy of Polygenic Risk Scores, The American Journal of Human Genetics Volume 97, Issue 4, 2015, Pages 576-592, <https://doi.org/10.1016/j.ajhg.2015.09.001>.

[^plink19]: Christopher C Chang, Carson C Chow, Laurent CAM Tellier, Shashaank Vattikuti, Shaun M Purcell, James J Lee, Second-generation PLINK: rising to the challenge of larger and richer datasets, GigaScience, Volume 4, Issue 1, December 2015, s13742–015–0047–8, <https://doi.org/10.1186/s13742-015-0047-8>

[^python3]: Van Rossum, G., & Drake, F. L. (2009). Python 3 Reference Manual. Scotts Valley, CA: CreateSpace.

[^convert]: <https://github.com/precimed/python_convert>
