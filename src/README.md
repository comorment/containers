## Singularity containers for GWAS and post-GWAS analysis
This repository is used to develop and document singularity containers with various software and analytical tools for GWAS and post-GWAS analysis.

## Getting started
For new users we recommend to go over introductory instructions in [docs/hello.md](docs/hello.md), which explain the basic usage of singularity containers, using a minimalistic example (singularity container with ``plink`` binary).

If you would like to contribute to developing these containers, please see  [docs/contributing.md](docs/contributing.md).

For a tutorial on GWAS with synthetic data, see [docs/gwas.md](docs/gwas.md).

## Prerequisites (to running tutorials):
* download containers shared on the [Google Drive](https://drive.google.com/drive/folders/1mfxZJ-7A-4lDlCkarUCxEf2hBIxQGO69?usp=sharing).
* download ``comorment_ref.tar.gz`` file from the above Google Drive folder, extract it with ``tar -xzvf comorment_ref.tar.gz`` command,
  and create an environmental variable ``COMORMENT_REF`` pointing to the folder containing extracted ``comorment_ref.tar.gz`` data.
  If you want to see the content of ``comorment_ref.tar.gz`` without downloading and extracting, 
  you may take a quick look [here](https://github.com/norment/comorment_data). This is a private repository, and you need to get access.
  Please contact Oleksandr and Bayram by e-mail and send us your github user name. If you don't have it, create one [here](http://github.com/join).
* create an empty folder called ``data``, for storing the results and intermediate files produced by running containers.
  (most instructinos mount this folder like this: ``-B data:/data``).

## Description of available containers:
* ``hello`` - a hello-world introductory container
* ``gwas`` - basic tools for gwas (``plink``, ``plink2``, ``prsice``, ``BoltLMM``)
* ``python3`` - python3 packages distributed via miniconda. This package also contains jupyter notebook.
* ``ldsc`` - LD score regression
* ``matlab`` - container allowing to run pre-compiled MATLAB software. This container also has OCTAVE installed.
* ``R`` - contaienr for R analysis (installed by native R package manager)

All containers have a shared layer of common utilities (``wget``, ``gzip``, etc). 

## Feedback

If you face any issues, or if you need additional software, please let us know by creating an [issue](https://github.com/comorment/gwas/issues/new). 

## Note about NREC machine

We use NREC machine to develop and build containers.
NREC machine has small local disk (~20 TB) and a larger external volume attached (~400 TB)
If you use NREC machine, it's important to not store large data or install large software to your home folder which is located on a small disk,
using ``/nrec/projects space`` instead:

```
Filesystem                         Size  Used Avail Use% Mounted on
/dev/sda1                               20G  9.6G  9.7G  50% /
/dev/mapper/nrec_extvol-comorment      393G  346G   28G  93% /nrec/projects
/dev/mapper/nrec_extvol_2-comorment_2  935G  609G  279G  69% /nrec/space


```

Both docker and singularity were configured to avoid placing cached files into local file system.
For docker this involves changing ``/etc/docker/daemon.json`` file by adding this:
```
{ 
    "data-root": "/nrec/projects/docker_root"
}
```
(as described https://tienbm90.medium.com/how-to-change-docker-root-data-directory-89a39be1a70b ; you may use ``docker info`` command to check the data-root)

For singularity, the configuration is described here https://sylabs.io/guides/3.6/user-guide/build_env.html
and it was done for the root user by adding  the following line into /etc/environment
```
export SINGULARITY_CACHEDIR="/nrec/projects/singularity_cache"
```

Common software, such as git-lfs, is installed to /nrec/projects/bin. 
Therefore it's reasonable for all users of the NREC comorment instance
to add this folder to the path by changing ``~/.bashrc`` and ``~/.bash_profile``.
```
export PATH="/nrec/projects/bin:$PATH"
```

A cloned version of comorment repositories is available here:
```
/nrec/projects/github/comorment/containers
/nrec/projects/github/comorment/reference
```
Feel free to change these folders and use git pull / git push. TBD: currently the folder is cloned as 'ofrei' user - I'm not sure if it will actually work to pull & push. But let's figure this out.


