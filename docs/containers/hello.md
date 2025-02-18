# ``hello.sif`` container

## Description

You may use ``hello.sif`` container to familiarize yourself with Apptainer (https://apptainer.org) or Singularity (https://sylabs.io/singularity/),
and the way it works on your secure HPC environment (TSD, Bianca, Computerome, or similar).
This container is indented as a demo.
It only contains Plink 1.9 (http://zzz.bwh.harvard.edu/plink/) software.
Commands below will assume Apptainer (`apptainer` command), which is largely compatible with Singularity (`singularity` command), but with some additional features.

## Getting Started

* Download ``hello.sif`` as described in the [INSTALL](./../../INSTALL) instructions
* Download ``chr21.[bed,bim,fam]`` files from [here](https://github.com/comorment/containers/tree/main/reference/hapgen)
* Import these files to your secure HPC environment
* Run ``apptainer exec --no-home hello.sif plink --help``, to validate that you can run Apptainer. This command is expected to produce the standard plink help message, starting like this:
  ```
  PLINK v1.90b6.18 64-bit (16 Jun 2020)          www.cog-genomics.org/plink/1.9/
  (C) 2005-2020 Shaun Purcell, Christopher Chang   GNU General Public License v3
  ```

## Helpful links to Singularity documentation

It's good idea to familiraze with basics of the Singularity/Apptainer, such as these:

* ["apptainer shell" options](https://apptainer.org/docs/user/main/cli/apptainer_shell.html)
* [Bind paths and mounts](https://apptainer.org/docs/user/latest/bind_paths_and_mounts.html).

## Installing Docker and Apptainer on your local machine

While you're getting up to speed with Apptainer, it might be reasonable to have it install on your local machine (laptop or desktop),
and try out containers locally before importing them to your HPC environment.

To install Apptainer on Ubuntu follow steps described [here](https://apptainer.org/docs/user/latest/quick_start.html#installation).

## Mapping your data to containers

There are several ways to give the container access to your data. Here are few examples:

1. ``apptainer exec --home $PWD:/home hello.sif plink --bfile chr21 --freq --out chr21`` -
   this command will map your current folder (`$PWD`) into ``/home`` folder within container, and set it as active working directory.
   In this way in your plink command you can refer to the files as if they are in your local folder, i.e. ``chr21`` without specifying the path.
   The command will then use plink to calculate allele frequencies, and save the result in current folder.

2. ``apptainer exec --home $PWD:/home hello.sif plink --bfile /home/chr21 --freq --out /home/chr21``
   Same as above command, but more explicitly refer to ``/home/chr21`` files, without relying on it being the active working directory.
   Here you can also choose to use ``--bind`` argument instead of ``--home``, which allow to map multiple folders if needed (comma-separated).
   
3. Now, let's assume that instead of downloading ``chr21.[bim/bed/fam]`` files and ``hello.sif`` container you've cloned the entire github repo
   (``git clone git@github.com:comorment/containers.git``), and have transfered it to your HPC environment.
   Then change your folder to the root of the ``containers`` repository, and run these commands:

   ```
   mkdir out_dir && apptainer exec --bind reference/:/ref:ro,out_dir:/out:rw containers/latest/hello.sif plink --bfile /ref/hapgen/chr21 --freq --out /out/chr21
   ```

   Note that input paths are relative to the current folder. Also, we specified ``ro`` and ``rw`` access, to have reference data as read-only, 
   but explicitly allow the container to write into ``/out`` folder (mapped to ``out_dir`` on the host).

4. Run ``apptainer shell --home $PWD:/home -B $(pwd)/data:/data hello.sif`` to use the container in an interactive mode. 
   In this mode you can interactively run plink commands.
   Note that it will consume resources of the machine where  you currently run the singulairty  comand
   (i.e., most likely, the login node of your HPC cluster).

 ## Running as SLURM job

* Run container within SLURM job scheduler, by creating a ``hello_slurm.sh`` file (by adjusting the example below), and running ``sbatch hello_slurm.sh``:
  ```
  #!/bin/bash
  #SBATCH --job-name=hello
  #SBATCH --account=p697
  #SBATCH --time=00:10:00
  #SBATCH --cpus-per-task=1
  #SBATCH --mem-per-cpu=8000M

  # module load apptainer # adapt according to your HPC environment

  apptainer exec --no-home hello.sif plink --help
  apptainer exec --home $PWD:/home hello.sif plink --bfile chr21 --freq --out chr21
  ```

Please [let us know](https://github.com/comorment/containers/issues/new) if you face any problems.

## TSD-specific instructions

The official documentation for Apptainer on TSD  is available [here](https://www.uio.no/english/services/it/research/sensitive-data/help/hpc/software/singularity.html). Here are more important notes about singularity on TSD:
* Generally, it is a good idea to add ``--no-home`` argument to your apptainer commands, to make sure that that scripts such as ``~/.bashrc`` do not interfere with the container. This also applies if you have custom software installed in your home folder. For other options that control isolation of the containers (i.e. ``--containall`` option) see [here](https://apptainer.org/docs/user/latest/bind_paths_and_mounts.html#using-no-home-and-containall-flags). 
* If you are a developer, and you would like to generate a container, you may want to do it outside of TSD, and then bring just a ``.sif`` file to TSD. Also, building  containers is much easier by building a Docker container first (using ``Dockerfile``), and converting to a Singularity image file.

## Software

List of software included in the container:

  | OS/tool             | version                                   | license
  | ------------------- |------------------------------------------ | -------------
  | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | plink[^1]          | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

### References

[^1]: Christopher C Chang, Carson C Chow, Laurent CAM Tellier, Shashaank Vattikuti, Shaun M Purcell, James J Lee, Second-generation PLINK: rising to the challenge of larger and richer datasets, GigaScience, Volume 4, Issue 1, December 2015, s13742–015–0047–8, https://doi.org/10.1186/s13742-015-0047-8