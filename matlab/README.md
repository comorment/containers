This folder contains pre-compiled binaries of certain MATLAB-based tools.
These binaries can be executed using ``singularity/matlabruntime.sif`` container as described below.

## magicsquare

A demo which prints NxN magic square (just for you to test our ``matlabruntime.sif``).

Here is a command that generates 5x5 magic square. To execute, set curent working directory to the root of this github repository.
```
singularity exec --no-home  --bind matlab:/matlab singularity/matlabruntime.sif /matlab/magicsquare 5
```

pleiofdr
========

Pre-compiled MATLAB binary allowing to run https://github.com/precimed/pleiofdr analysis.

Here is a command that executes ``/pleiofdr/demo_data`` example:
```
singularity exec -B matlab:/matlab -B reference/pleiofdr:/pleiofdr --pwd /pleiofdr/demo_data singularity/matlabruntime.sif /matlab/pleiofdr
```                                                                                                               
