# Installation

We recommend to clone this entire repository using ``git clone.``
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

Now you're all set to clone this repository (note that adding ``--depth 1`` to your command as shown below will limit the amount of data transfered from github to your machine):

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