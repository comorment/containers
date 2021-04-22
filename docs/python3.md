## ``python3.sif``

``python3.sif`` container runs ``python 3.8.8`` from Anaconda, and has many useful python modules already installed, 
including pandas, numpy, scipy, matplotlib and few others.

```
>singularity exec python3.sif python
Python 3.8.8 (default, Feb 24 2021, 21:46:12) 
[GCC 7.3.0] :: Anaconda, Inc. on linux
```

You may also use jupyter notebook like this:
```
singularity exec --contain --home $PWD:/home python3.sif jupyter notebook --no-browser --port 8890
```
The port is optional, but you may want to specify it if you'd like to run jupyter on a remote server - in which case you need to enable port forwarding as described [here](https://docs.anaconda.com/anaconda/user-guide/tasks/remote-jupyter-notebook/). This also works if you connect from Windows using Putty as described [here](https://stackoverflow.com/questions/46276612/remote-access-jupyter-notebook-from-windows).

``python3.sif`` container has few additional tools installed:

* ``/tools/ukb/ukb_helper.py`` - https://github.com/precimed/ukb/
* ``/tools/python_convert`` - https://github.com/precimed/python_convert
* ``/tools/mixer`` - https://github.com/precimed/mixer
