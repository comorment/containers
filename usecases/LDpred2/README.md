# LDpred2

The files in this directory exemplifies how to run the LDpred2 analysis using the ``bigsnpr`` R library. 
Please confer this [tutorial](https://privefl.github.io/bigsnpr/articles/LDpred2.html) for additional explainations of the actual codes.
The method is explained in the publication:

- Florian Privé, Julyan Arbel, Bjarni J Vilhjálmsson, LDpred2: better, faster, stronger, Bioinformatics, Volume 36, Issue 22-23, 1 December 2020, Pages 5424–5431, https://doi.org/10.1093/bioinformatics/btaa1029


## Running LDpred2 analysis

In order to run the LDpred2 analysis defined in the file `run_ldpred2.sh`, issue:  
```
# point to input/output files
export fileGeno=/REF/examples/prsice2/EUR.bed
export fileGenoRDS=EUR.rds
export filePheno=/REF/examples/prsice2/EUR.height
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=test.score

# set environmental variables. Replace "<path/to/containers>" with 
# the full path to the cloned "containers" repository
export SIF=<path/to/containers>/singularity
export REFERENCE=<path/to/containers>/reference
export SINGULARITY_BIND=$REFERENCE:/REF

# run tasks
bash run_ldpred2.sh
```

## Output

The main LDpred2 output files are ``test.score.auto`` and ``test.score.inf`` put in this directory. 
The files are text files with tables formatted as 
```
FID IID Height score
HG00096 HG00096 169.132168767547 -1.49668824138468e+100
HG00097 HG00097 171.256258630279 -3.37195056659838e+99
HG00099 HG00099 171.534379938588 -5.02262306623802e+100
HG00100 HG00100 NA -1.8332542097235e+100
...
```

The ``run_ldpred2.sh`` script will also output ``.bk`` and ``.rds`` binary files with prefix ``EUR`` in this directory.


## Slurm job

On an HPC resource the same analysis can be run by first writing a job script ``run_ldpred2_slurm.job`` like:
```
#!/bin/bash
#SBATCH --job-name=LDpred2  # job name
#SBATCH --output=LDpred2.txt  # output
#SBATCH --error=LDpred2.txt  # errors
#SBATCH --account=$SBATCH_ACCOUNT  # project ID
#SBATCH --time=00:15:00  # walltime
#SBATCH --cpus-per-task=1  # number of CPUS for task
#SBATCH --mem-per-cpu=2000  # memory (MB)
#SBATCH --partition=normal

# check if singularity is available, if not load it (adapt as necessary)
if ! command -v singularity &> /dev/null
then
    module load singularity
fi

# point to input/output files
export fileGeno=/REF/examples/prsice2/EUR.bed
export fileGenoRDS=EUR.rds
export filePheno=/REF/examples/prsice2/EUR.height
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export fileOut=test.score

# set environmental variables. Replace "<path/to/containers>" with 
# the full path to the cloned "containers" repository
export SIF=<path/to/containers>/singularity
export REFERENCE=<path/to/containers>/reference
export SINGULARITY_BIND=$REFERENCE:/REF

# run tasks
bash run_ldpred2.sh
```

In order to run the job, first make sure that the ``SBATCH_ACCOUNT`` environment variable is defined:
```
export SBATCH_ACCOUNT=project_ID
```
where ``project_ID`` is the granted project that compute time is allocated. 
As above, ``<path/to/containers`` should point to the cloned ``containers`` repository. 
Entries like ``--partition=normal`` may also be adapted for different HPC resources.
Then, the job can be submitted to the queue by issuing ``sbatch run_ldpred2_slurm.job``. 
The status of running jobs can usually be enquired by issuing ``squeue -u $USER``. 
