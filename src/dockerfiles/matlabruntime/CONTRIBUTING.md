
Running your matlab project via Containers

To run your matlab code with this container there are 2 alternatives: 1) Build it the standalone application of your code via Matlab Compiler and  run it with Matlab Runtime 2) Run it with GNU octave (https://www.gnu.org/software/octave/index)

##  With Matlab Runtime

1. Get the standalone application of your code via Matlab Compiler (https://ch.mathworks.com/help/compiler/create-and-install-a-standalone-application-from-matlab-code.html)

2. Mount the directory where your standalone application folder is to container and run the application

```
docker run --rm -ti         -v /the_path_of_the_application/your_application_name/for_redistribution_files_only:/execute         octave-matlab         /execute/your_application <possible commands>

```

For example

```
docker run --rm -ti         -v  /Users/matlab_octave/magicsquare/for_redistribution_files_only:/execute         octave-matlab         /execute/magicsquare 5
```

magigsquare.m is the default example which is given by Mathworks. Hence we have also build and included it inside to container. Hence you can run it as 

```
docker run --rm octave-matlab /magicsquare/for_redistribution_files_only/magicsquare 5
```

and you can observe the same output as it should be


m =

    17    24     1     8    15
    23     5     7    14    16
     4     6    13    20    22
    10    12    19    21     3
    11    18    25     2     9
    
    
##  With GNU Octave
    
    It is also possible to run your code via GNU Octave. For this aim
    
    1. Run the container 
    
 ```
docker run -it octave-matlab
```

2- Type octave and add the path where your code is. For instance, in our case the code (magicsquare.m)  is placed to  /magicsquare/for_redistribution_files_only . Hence all you need to do is adding this directory to octave as

 ```
 addpath('/magicsquare/for_redistribution_files_only')  
 
 ```

Then you can readily run your matlab command to call your function such as:   magicsquare 5

And you can observe the same output as above.
    
    
    
 # Singularity 
 
 ##  With Matlab Runtime

1. Get the standalone application of your code via Matlab Compiler (https://ch.mathworks.com/help/compiler/create-and-install-a-standalone-application-from-matlab-code.html)

2. Mount the directory where your standalone application folder is to container and run the application
 
 ```
singularity exec        -B  /the_path_of_the_application/your_application_name/for_redistribution_files_only:/execute         octave-matlab         /execute/your_application <possible commands>

```

For example

```
singularity exec      -B  /Users/matlab_octave/magicsquare/for_redistribution_files_only:/execute         octave-matlab         /execute/magicsquare 5

```


magigsquare.m is the default example which is given by Mathworks. Hence we have also build and included it inside to container. Hence you can run it as 
 
 
  ```
 singularity exec octave-matlab.sif /magicsquare/for_redistribution_files_only/magicsquare 5
  ``` 
  
     
 ##  With GNU Octave
    
    It is also possible to run your code via GNU Octave. For this aim
    
 1. Run the container in shell mode
    
 ```
   singularity shell  octave-matlab.sif
```

2- Type octave and add the path where your code is. For instance, in our case the code (magicsquare.m)  is placed to  /magicsquare/for_redistribution_files_only . Hence all you need to do is adding this directory to octave as

 ```
 addpath('/magicsquare/for_redistribution_files_only')  
 
 ```

Then you can readily run your matlab command to call your function such as:   magicsquare 5

And you can observe the same output as above.
    

    
    


 
    

