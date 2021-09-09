# About

The goal of this repository is to distribute tools for GWAS and post-GWAS analysis in CoMorMent project (http://comorment.eu/).

Most of these tools are packaged into singularity containers (https://sylabs.io/singularity/) and shared in [singularity](singularity) folder of this repository. You can download individual containers using github's ``Download`` button, or clone the entire repository from command line as described in the [Getting started](#getting-started) section below).

Most of the tools require additional reference data, provided in the [reference](reference) folder of this repository.
Certain reference data can not be made publicly available, in which case we provide access instructions in a separate GitHub repository:
https://github.com/comorment/reference. This repository is private - please approach your contact within CoMorMent project to enable your access.

Description of containers and usage instructions are provided in the [docs](docs) folder.

More extensive use cases of containers, focusing on real data analysis, are provided in the [usecases](usecases) folder.

# Getting started

We recommend to clone this entire repository. 
This is done by running ``git clone --depth 1 https://github.com/comorment/containers.git`` command. 

NB! Please add ``--depth 1`` to your command as shown above. This will limit the amount of data transfered from github to your machine.

However, you need to enable [install GitLFS extension](https://git-lfs.github.com/).
This is done by downloading and unpacking the GitLFS package, adding ``git-lfs`` binary to a folder that is in your ``PATH``, and running
``git lfs install`` command.

```
mkdir ~/bin
export PATH="/home/$USER/bin:$PATH"        # good idea to put this in your ~/.bashrc or ~/.bash_profile
wget https://github.com/git-lfs/git-lfs/releases/download/v2.13.2/git-lfs-linux-amd64-v2.13.2.tar.gz
tar -xzvf git-lfs-linux-amd64-v2.13.2.tar.gz
cp git-lfs /home/$USER/bin
git lfs install
```

Now you're all set to clone this repository:
```
git clone --depth 1 https://github.com/comorment/containers.git
```

For TSD system, a read-only copy of these containers is maintained at these locations
(please read /cluster/projects/pNN/github/README.md file before using these copies):
```
/cluster/projects/p33/github/comorment
/cluster/projects/p697/github/comorment
```

Once you have a clone of this repository on your system, you may proceed with [docs/hello.md](docs/hello.md) example.
Take a look at other README files in the [docs](docs/README.md) folder, as well as detailed use cases in [usecases](usecases/README.md) folder.

To simplify instructions throughout this repository we use certain variables (it's a good idea to include them in your ``.bashrc`` or similar):
* ``$COMORMENT`` refers to a folder with ``comorment`` and ``reference`` subfolders, containing a clone of [containers](https://github.com/comorment/containers) and [reference](https://github.com/comorment/reference) repositories from GitHub. Cloning ``reference`` repository is optional, and it's only needed for internal work within the CoMorMent project - for normal use you may proceed without it.
* ``$SIF`` refers to ``$COMORMENT/containers/singularity`` folder, containing singulairty containers (the ``.sif`` files)
* ``SINGULARITY_BIND="$COMORMENT/containers/reference:/REF:ro,$COMORMENT/containers/matlab:/MATLAB:ro,$COMORMENT/reference:/REF2:ro"`` defines default bindings within container (``/REF``, ``/REF2`` and ``/MATLAB``). If you don't have access to private reference, try out commands without mapping ``$COMORMENT/reference:/REF2:ro`` - most of the exmples don't require private reference data.
* We assume that all containers run with ``--home $PWD:/home``, mounting current folder mounted as ``/home`` within container
* We also recommend using ``--contain`` argument to better isolate container from the environment in your host machine. If you choose not to mount ``--home $PWD:/home``, you may want to add ``--no-home`` argument.
 
# Legacy

Earlier version (prior to April 2021) of all containers and refrence data was distributed on Google Drive. This is no longer the case, the folder on Google drive is no longer maintained. ALl containers and reference data are released through this repository.



