# CoMorMent-containers

The goal of the [CoMorMent](https://www.comorment.uio.no) containers repository at <https://github.com/comorment/containers> is to distribute tools for GWAS and post-GWAS analysis in CoMorMent project (<http://comorment.eu/>).

Most of these tools are packaged into singularity containers (<https://sylabs.io/singularity/>) and shared in [singularity](https://github.com/comorment/containers/tree/main/singularity) folder of this repository. You can download individual containers using github's ``Download`` button, or clone the entire repository from command line as described in the [Getting started](#getting-started) section below).

Most of the tools require additional reference data, provided in the [reference](https://github.com/comorment/containers/tree/main/reference) folder of this repository.
Certain reference data can not be made publicly available, in which case we provide access instructions in a separate GitHub repository:
<https://github.com/comorment/reference>. This repository is private - please approach your contact within CoMorMent project to enable your access.

Description of containers and usage instructions are provided in the [docs](https://github.com/comorment/containers/tree/main/docs) folder.

More extensive use cases of containers, focusing on real data analysis, are provided in the [usecases](https://github.com/comorment/containers/tree/main/usecases) folder.

The history of changes is available in the [CHANGELOG.md](https://github.com/comorment/containers/blob/main/CHANGELOG.md) file.

Additional tools are available in separate repositories:

* <https://github.com/comorment/HDL> - High-Definition Likelihood

## <a name="getting-started"></a>Getting started

We recommend to clone this entire repository using ``git clone.``
However, you need to enable [install Git LFS extension](https://git-lfs.github.com/).
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

NB! Please add ``--depth 1`` to your command as shown above. This will limit the amount of data transfered from github to your machine.

For TSD system, a read-only copy of these containers is maintained at these locations
(please read /cluster/projects/pNN/github/README.md file before using these copies):

```
/cluster/projects/p33/github/comorment
/cluster/projects/p697/github/comorment
```

Once you have a clone of this repository on your system, you may proceed with [docs/hello.md](https://github.com/comorment/containers/blob/main/docs/hello.md) example.
Take a look at other README files in the [docs](https://github.com/comorment/containers/tree/main/docs/) folder, as well as detailed use cases in [usecases](https://github.com/comorment/containers/tree/main/usecases/) folder.

To simplify instructions throughout this repository we use certain variables (it's a good idea to include them in your ``.bashrc`` or similar):

* ``$COMORMENT`` refers to a folder with ``comorment`` and ``reference`` subfolders, containing a clone of [containers](https://github.com/comorment/containers) and [reference](https://github.com/comorment/reference) repositories from GitHub. Cloning ``reference`` repository is optional, and it's only needed for internal work within the CoMorMent project - for normal use you may proceed without it.
* ``$SIF`` refers to ``$COMORMENT/containers/singularity`` folder, containing singulairty containers (the ``.sif`` files)
* ``SINGULARITY_BIND="$COMORMENT/containers/reference:/REF:ro,$COMORMENT/containers/matlab:/MATLAB:ro,$COMORMENT/reference:/REF2:ro"`` defines default bindings within container (``/REF``, ``/REF2`` and ``/MATLAB``). If you don't have access to private reference, try out commands without mapping ``$COMORMENT/reference:/REF2:ro`` - most of the exmples don't require private reference data.
* We assume that all containers run with ``--home $PWD:/home``, mounting current folder mounted as ``/home`` within container
* We also recommend using ``--contain`` argument to better isolate container from the environment in your host machine. If you choose not to mount ``--home $PWD:/home``, you may want to add ``--no-home`` argument.

## Legacy

Earlier version (prior to April 2021) of all containers and refrence data was distributed on Google Drive. This is no longer the case, the folder on Google drive is no longer maintained. ALl containers and reference data are released through this repository.

## Source files

The source files for configuring and building the container files provided here are found in the [src](https://github.com/comorment/containers/tree/main/src) directory.
See the corresponding README file therein for detailes.

## Online documentation

The online documentation hosted at [comorment-containers.rtfd.io](https://comorment-containers.readthedocs.io) can be built locally using [Sphinx](https://www.sphinx-doc.org/en/master/) in a conda environment as

```
cd sphinx-docs/source  # documentation source/config directory
conda env create -f environment.yml  # creates environment "sphinx"
conda activate sphinx
make html  # make html-documentation in $PWD/_build/html/
```

The resulting file(s) ``$PWD/_build/html/index.html`` can be viewed in any web browser.

In order to make a pdf with the documentation, issue

```
make pdflatex
```

and open ``$PWD/_build/latex/comorment-containers.pdf`` in a pdf viewer.
