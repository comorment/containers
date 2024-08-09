# Installation and set up

In order to set up these resources, some software may be required

- [Singularity/SingularityCE](https://sylabs.io/singularity/) or [Apptainer](https://apptainer.org)
- [Git](https://git-scm.com/)
- [Git LFS](https://git-lfs.com)
- [ORAS CLI](https://oras.land)

## Conda environment (optional)

The above and other miscellaneous dependencies may be installed in a [Conda](https://conda.io) environment using the provided [``environment.yml``](https://github.com/comorment/containers/blob/main/environment.yml) file as (``conda`` may be replaced by ``mamba`` executable):

```bash
conda env create -f environment.yml  # create cosgap environment
conda activate cosgap
# do this and that...
conda deactivate
```

## Clone the repository

To download all files of the last revision of this project, issue:

```bash
cd path/to/repositories
git clone --depth 1 https://github.com/comorment/containers.git
cd containers
git lfs pull  # pull "large" files
```

## Update the Singularity Image Files (containers)

We are presently migrating container builds as distributed here to the [GitHub Container Registry](https://ghcr.io).
Current and future image build artifacts (Singularity and Docker) are listed under [Packages](https://github.com/orgs/comorment/packages?repo_name=containers).

To obtain updated versions of the Singularity Image Format (.sif) container files provided here, issue:

```bash
cd path/to/repositories/containers/singularity
mv <image>.sif <image>.sif.old  # optional, just rename the old(er) file
apptainer pull docker://ghcr.io/comorment/<image>:<tag>  # or
singularity pull docker://ghcr.io/comorment/<image>:<tag> # or 
oras pull ghcr.io/comorment/<image>_sif:<tag>  # note the "_sif" suffix
```

where  `<image>` corresponds to one of `{hello|gwas|python3|r}` and `<tag>` corresponds to a tag listed under `https://github.com/comorment/containers/pkgs/container/<image>`, 
such as `latest`, `main`, or `sha_<GIT_SHA>`. 
The `oras pull` statement pulls the `<image>.sif` file from `https://github.com/comorment/containers/pkgs/container/<image>_sif` using the [ORAS](https://oras.land) registry, without the need to build the container locally.

## Pulling and using Docker image

To pull the corresponding Docker image, issue:

```bash
docker pull ghcr.io/comorment/<image>:<tag>
```

If working on recent Macs, add the `--platform=linux/amd64` flag after `docker pull`. 
This may allow replacing `singularity exec ...` or `apptainer exec ...` statements with appropriate `docker run ...` statements on systems where Singularity or Apptainer is unavailable.
Functionally, the Docker image is equivalent to the Singularity container, but note that syntax for mounting volumes and invoking commands may differ.
Please refer to [docs.docker.com](https://docs.docker.com) for more information.

> [!NOTE]
> Note that the provided Docker image may not support all CPUs, and may not be able to run on all systems via CPU virtualization.
> An option may be to build the Docker image on the host machine directly (e.g., M1/M2/M3 Macs, PCs with older Intel CPUs), as:
>
>```bash
>docker build --platform=linux/amd64 -t ghcr.io/comorment/<image> -f dockerfiles/<image>/Dockerfile .
>```

A minimal usage example may be to invoke the PLINK tool and its help function in the `hello` container:

```bash
export HELLO="ghcr.io/comorment/hello:latest"
export PLINK1="docker run --platform=linux/amd64 --rm -v ${HELLO}/usecases:/home -v ${HELLO}/reference:/REF -w/home --entrypoint=plink1 ${HELLO}"
$PLINK1 --help
```

A more complete example is provided for MiXeR [here](https://github.com/comorment/mixer/blob/main/usecases/mixer_simu.md#docker-details). 

## Systems without internet access

Some secure platforms do not have direct internet access, hence we recommend cloning/pulling all required files on a machine with internet access as explained above and archiving the `containers` directory with all files and moving it using whatever file uploader is available for the platform.

```bash
cd /path/to/containers
SHA=$(git rev-parse --short HEAD)
cd ..
tar --exclude=".git/*" -cvf containers_$SHA.tar containers
```

# Install (old)

We recommend to clone this entire repository using ``git clone --depth 1 https://github.com/comorment/containers.git``.
However, you need to install the [Git LFS extension](https://git-lfs.github.com/).
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

Now you're all set to clone this repository (note that adding ``--depth 1`` to your command as shown below will limit the amount of data transferred from GitHub to your machine):

```
git clone --depth 1 https://github.com/comorment/containers.git
```

At this point you may want to run the following find&grep command to check that all git lfs files were downloaded successfully (i.e. you got an actual content of each file, and not just its git lfs reference). The command searches for and lists all files within $COMORMENT folder which contain a string like ``oid sha``, likely indicating that git lfs file hasn't been downloaded.
If the following commands doesn't find any files that you're good to go. Otherwise you may want to re-run your ``git clone`` commands or investigate why the're failing to download the actual file.

```
find $COMORMENT -type f -not -path '*/.*' -exec sh -c 'head -c 100 "{}" | if grep -H "oid sha"; then echo {}; fi ' \; | grep -v "oid sha256"
```

For TSD system, a read-only copy of $COMORMENT containers is maintained at these locations
(please read github/README.md file before using these copies):

```
# for p33 project
export COMORMENT=/cluster/projects/p33/github/comorment

# for p697 project
export COMORMENT=/ess/p697/data/durable/s3-api/github/comorment
```

Once you have a clone of this repository on your system, you may proceed with [docs/singularity/hello.md](./docs/singularity/hello.md) example.
Take a look at the [README](./docs/singularity/README.md) file in the [docs/singularity](https://github.com/comorment/containers/tree/main/docs/singularity) folder, as well as detailed use cases in [usecases](https://github.com/comorment/containers/tree/main/usecases).

To simplify instructions throughout this repository we use certain variables (it's a good idea to include them in your ``.bashrc`` or similar):

* ``$COMORMENT`` refers to a folder with ``comorment`` and ``reference`` subfolders, containing a clone of the [containers](https://github.com/comorment/containers) and [reference](https://github.com/comorment/reference) repositories from GitHub. Cloning ``reference`` repository is optional, and it's only needed for internal work within the CoMorMent project - for normal use you may proceed without it.
* ``$SIF`` refers to ``$COMORMENT/containers/singularity`` folder, containing singulairty containers (the ``.sif`` files)
* ``SINGULARITY_BIND="$COMORMENT/containers/reference:/REF:ro,$COMORMENT/reference:/REF2:ro"`` defines default bindings within container (``/REF``, ``/REF2``). If you don't have access to private reference, try out commands without mapping ``$COMORMENT/reference:/REF2:ro`` - most (if not all) of the exmples don't require private reference data.
* We assume that all containers run with ``--home $PWD:/home``, mounting current folder mounted as ``/home`` within container
* We also recommend using ``--contain`` argument to better isolate container from the environment in your host machine. If you choose not to mount ``--home $PWD:/home``, you may want to add ``--no-home`` argument.
* You can choose to exclude passing environment variables from the host into the container with the ``--cleanenv`` option. Read more about it [here](https://docs.sylabs.io/guides/3.7/user-guide/environment_and_metadata.html).