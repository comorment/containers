# ``hello.sif`` container

## Description

You may use ``hello.sif`` container to familirize yourself with Singularity (https://sylabs.io/docs/),
and the way it works on your secure HPC environment (TSD, Bianca, Computerome, or similar).
This singularity container is indented as a demo. 
It only contains Plink 1.9 (http://zzz.bwh.harvard.edu/plink/) software.

## Getting Started

* Download ``hello.sif`` from [here](https://github.com/comorment/containers/tree/main/singularity)
* Download ``chr21.[bed,bim,fam]`` files from [here](https://github.com/comorment/containers/tree/main/reference/hapgen)
* Import these files to your secure HPC environment
* Run ``singularity exec --no-home hello.sif plink --help``, to validate that you can run singularity. This command is expected to produce the standard plink help message, starting like this:
  ```
  PLINK v1.90b6.18 64-bit (16 Jun 2020)          www.cog-genomics.org/plink/1.9/
  (C) 2005-2020 Shaun Purcell, Christopher Chang   GNU General Public License v3
  ```

## Helpful links to singularity documentation

It's good idea to familiraze with basics of the singularity, such as these:

* ["singularity shell" options](https://sylabs.io/guides/3.2/user-guide/cli/singularity_shell.html#options)
* [Bind paths and mounts](https://sylabs.io/guides/3.2/user-guide/bind_paths_and_mounts.html).

## Installing Docker and Singularity on your local machine

While you're getting up to speed with singularity, it might be reasonable to have it install on your local machine (laptop or desktop),
and try out containers locally before importing them to your HPC environment.

To install singularity on Ubuntu follow steps described here: https://sylabs.io/guides/3.7/user-guide/quick_start.html
Note that ``sudo apt-get`` can give only a very old version of singularity, which isn't sufficient.
Therefore it's best to build singularity locally.  Note that singularity depends on GO, so it must be installed first.
If you discovered more speciifc instructions, please submit an issue or pull request to update this documentation.

## Mapping your data to singularity containers

There are several ways to give singularity container access to your data. Here are few examples:

1. ``singularity exec --home $PWD:/home hello.sif plink --bfile chr21 --freq --out chr21`` -
   this command will map your current folder (`$PWD`) into ``/home`` folder within container, and set it as active working directory.
   In this way in your plink command you can refer to the files as if they are in your local folder, i.e. ``chr21`` without specifying the path.
   The command will then use plink to calculate allele frequencies, and save the result in current folder.

2. ``singularity exec --home $PWD:/home hello.sif plink --bfile /home/chr21 --freq --out /home/chr21``
   Same as above command, but more explicitly refer to ``/home/chr21`` files, without relying on it being the active working directory.
   Here you can also choose to use ``--bind`` argument instead of ``--home``, which allow to map multiple folders if needed (comma-separated).
   
3. Now, let's assume that instead of downloading ``chr21.[bim/bed/fam]`` files and ``hello.sif`` container you've cloned the entire github repo
   (``git clone git@github.com:comorment/containers.git``), and have transfered it to your HPC environment.
   Then change your folder to the root of the ``containers`` repository, and run these commands:

   ```
   mkdir out_dir && singularity exec --bind reference/:/ref:ro,out_dir:/out:rw singularity/hello.sif plink --bfile /ref/hapgen/chr21 --freq --out /out/chr21
   ```

   Note that input paths are relative to the current folder. Also, we specified ``ro`` and ``rw`` access, to have reference data as read-only, 
   but explicitly allow the container to write into ``/out`` folder (mapped to ``out_dir`` on the host).

4. Run ``singularity shell --home $PWD:/home -B $(pwd)/data:/data hello.sif`` to use singularity in an interactive mode. 
   In this mode you can interactively run plink commands.
   Note that it will consume resources of the machine where  you currently run the singulairty  comand
   (i.e., most likely, the login node of your HPC cluster).

 ## Running as SLURM job

* Run singularity container within SLURM job scheduler, by creating a ``hello_slurm.sh`` file (by adjusting the example below), and running ``sbatch hello_slurm.sh``:
  ```
  #!/bin/bash
  #SBATCH --job-name=hello
  #SBATCH --account=p697
  #SBATCH --time=00:10:00
  #SBATCH --cpus-per-task=1
  #SBATCH --mem-per-cpu=8000M
  module load singularity/3.7.1
  singularity exec --no-home hello.sif plink --help
  singularity exec --home $PWD:/home hello.sif plink --bfile chr21 --freq --out chr21
  ```

Please [let us know](https://github.com/comorment/containers/issues/new) if you face any problems.

## TSD-specific instructions

The official documentation for singularity on TSD  is available [here](https://www.uio.no/english/services/it/research/sensitive-data/use-tsd/hpc/software/singularity.html). Here are more important notes about singularity on TSD:
* ``module load singularity/2.6.1`` is going to be deprecated soon; instead, there will be a local installation of singularity on each Colossus node
* Singularity might be unavailable on some of the interactive nodes. For example, in ``p33`` project it is recommended to run singularity on ``p33-appn-norment01`` node. You may also find it in ``p33-submit`` nodes. 
* You may want to run ``module purge``, to make sure you use locally installed singularity. It is good idea to run ``which singularity`` to validate this.
* Use ``singularity --version`` to find the version of singularity
* Generally, it is a good idea to add ``--no-home`` argument to your singularity commands, to make sure that that scripts such as ``.bashrc`` do not interfere with singularity container. This also applies if you have custom software installed in your home folder. For other options that control isolation of the containers (i.e. ``--containall`` option) see [here](https://sylabs.io/guides/3.1/user-guide/bind_paths_and_mounts.html#using-no-home-and-containall-flags). 
* If you are a developer, and you would like to generate a singularity container, you may want to do it outside of TSD, and then bring just a ``.sif`` file to TSD. Also, building singularity containers is much easier by building a Docker container first (using ``Dockerfile``), and converting such Docker container to a singularity container.

## Software

List of software included in the container:

  | OS/tool             | version                                   | license
  | ------------------- | ----------------------------------------- | -------------
  | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | plink               | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
