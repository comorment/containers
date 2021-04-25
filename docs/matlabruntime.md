## ``matlabruntime.sif``
This is a special container allowing to execute pre-built MATLAB binaries.
The binaries are NOT included included in the container and need to be mounted separately from [matlab](../matlab) folder.
If you get ``access denied`` errors, make sure to make those binaries executable (i.e. run ``chmod a+x $COMORMENT/matlab/pleiofdr``).

## magicsquare

A demo which prints NxN magic square (just for you to test our ``matlabruntime.sif``).

Here is a command that generates 5x5 magic square. To execute, set curent working directory to the root of this github repository.
```
singularity exec --no-home $SIF/matlabruntime.sif /MATLAB/magicsquare 5
```

## pleiofdr

Pre-compiled MATLAB binary allowing to run https://github.com/precimed/pleiofdr analysis.

Here is a command that executes the example in ``/reference/pleiofdr/demo_data`` folder:
```
singularity exec --home $PWD:/home $SIF/matlabruntime.sif /MATLAB/pleiofdr
```                                                                                                               
