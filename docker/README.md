# Docker

Build recipes for containers using [Docker](https://www.docker.com) and [Singularity](https://sylabs.io/singularity/).

## Software versions

Please confer and update accordingly the software version tables in the respective [singularity](./../singularity/README.md) files for each container.

## Feedback

If you face any issues, or if you need additional software, please let us know by creating an [issue](https://github.com/comorment/containers/issues/new).

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

(as described <https://tienbm90.medium.com/how-to-change-docker-root-data-directory-89a39be1a70b> ; you may use ``docker info`` command to check the data-root)

For singularity, the configuration is described here <https://sylabs.io/guides/3.6/user-guide/build_env.html>
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

## Testing container builds

Some basic checks for the functionality of the different container builds are provided in ``<containers>/tests/``, implemented in Python.
The tests can be executed using the [Pytest](https://docs.pytest.org) testing framework.

To install Pytest in the current Python environment, issue:

```
pip install pytest  # --user optional
```

New virtual environment using [conda](https://docs.conda.io/en/latest/index.html):

```
conda create -n pytest python=3 pytest -y  # creates env "pytest"
conda activate pytest  # activates env "pytest"
```

Then, all checks can be executed by issuing:

```
cd <containers>
py.test -v tests  # with verbose output
```

Checks for individual containers (e.g., ``gwas.sif``) can be executed by issuing:

```
py.test -v tests/test_<container-prefix>.py
```

Note that the proper container files (*.sif files) corresponding to the different test scripts must exist in ``<containers>/singularity/>``,
not only git LFS pointer files.

## Git clone ignoring LFS

See [stackoverflow.com/questions/42019529/how-to-clone-pull-a-git-repository-ignoring-lfs](https://stackoverflow.com/questions/42019529/how-to-clone-pull-a-git-repository-ignoring-lfs)
```
GIT_LFS_SKIP_SMUDGE=1 git clone git@github.com:comorment/containers.git
```
