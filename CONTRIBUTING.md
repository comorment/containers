# Contributing

Thanks for considering contributing! Please read this document to learn the various ways you can contribute to this project and how to go about doing it.

## Bug reports and feature requests

### Did you find a bug?

First, do [a quick search](https://github.com/comorment/containers/issues) to see whether your issue has already been reported.
If your issue has already been reported, please comment on the existing issue.

Otherwise, open [a new GitHub issue](https://github.com/comorment/containers/issues).  Be sure to include a clear title
and description.  The description should include as much relevant information as possible.  The description should
explain how to reproduce the erroneous behavior as well as the behavior you expect to see.  Ideally you would include a
code sample or an executable test case demonstrating the expected behavior.

### Do you have a suggestion for an enhancement or new feature?

We use GitHub issues to track feature requests. Before you create a feature request:

* Make sure you have a clear idea of the enhancement you would like. If you have a vague idea, consider discussing
it first on a GitHub issue.
* Check the documentation to make sure your feature does not already exist.
* Do [a quick search](https://github.com/comorment/containers/issues) to see whether your feature has already been suggested.

When creating your request, please:

* Provide a clear title and description.
* Explain why the enhancement would be useful. It may be helpful to highlight the feature in other libraries.
* Include code examples to demonstrate how the enhancement would be used.

## Making a pull request

When you're ready to contribute code to address an open issue, please follow these guidelines to help us be able to review your pull request (PR) quickly.

1. **Initial setup** (only do this once)

    <details><summary>Expand details 👇</summary><br/>

    If you haven't already done so, please [fork](https://help.github.com/en/enterprise/2.13/user/articles/fork-a-repo) this repository on GitHub.

    Then clone your fork locally with

        git clone https://github.com/USERNAME/containers.git

    or 

        git clone git@github.com:USERNAME/containers.git

    At this point the local clone of your fork only knows that it came from *your* repo, github.com/USERNAME/containers.git, but doesn't know anything the *main* repo, [https://github.com/comorment/containers.git](https://github.com/comorment/containers). You can see this by running

        git remote -v

    which will output something like this:

        origin https://github.com/USERNAME/containers.git (fetch)
        origin https://github.com/USERNAME/containers.git (push)

    This means that your local clone can only track changes from your fork, but not from the main repo, and so you won't be able to keep your fork up-to-date with the main repo over time. Therefore you'll need to add another "remote" to your clone that points to [https://github.com/comorment/containers.git](https://github.com/comorment/containers). To do this, run the following:

        git remote add upstream https://github.com/comorment/containers.git

    Now if you do `git remote -v` again, you'll see

        origin https://github.com/USERNAME/containers.git (fetch)
        origin https://github.com/USERNAME/containers.git (push)
        upstream https://github.com/comorment/containers.git (fetch)
        upstream https://github.com/comorment/containers.git (push)

2. **Ensure your fork is up-to-date**

    <details><summary>Expand details 👇</summary><br/>

    Once you've added an "upstream" remote pointing to [https://github.com/comorment/containers.git](https://github.com/comorment/containers), keeping your fork up-to-date is easy:

        git checkout main  # if not already on main
        git pull --rebase upstream main
        git push

    </details>

3. **Create a new branch to work on your fix or enhancement**

    <details><summary>Expand details 👇</summary><br/>

    Committing directly to the main branch of your fork is not recommended. It will be easier to keep your fork clean if you work on a separate branch for each contribution you intend to make.

    You can create a new branch with

        # replace BRANCH with whatever name you want to give it
        git checkout -b BRANCH
        git push -u origin BRANCH

    </details>

4. **Test your changes**

    <details><summary>Expand details 👇</summary><br/>

    Our continuous integration (CI) testing runs [a number of checks](https://github.com/comorment/containers/actions) for each pull request on [GitHub Actions](https://github.com/features/actions). 
    You can run most of these tests locally, which is something you should do *before* opening a PR to help speed up the review process and make it easier for us.

    And finally, please update the [CHANGELOG](CHANGELOG.md) with notes on your contribution in the "Unreleased" section at the top.

    After all of the above checks have passed, you can now open [a new GitHub pull request](https://github.com/comorment/containers/pulls).
    Make sure you have a clear description of the problem and the solution, and include a link to relevant issues.

    We look forward to reviewing your PR!

    </details>

## Information for developers

The list of tools included in the different Dockerfiles and installer bash scripts for each container
is provided [here](docker/README.md). Please keep this up to date when pushing new container builds.

### Release checklist

- Stick to the [semantic versioning scheme](https://semver.org), with the `<MAJOR>.<MINOR>.<PATCH>` numbering [scheme](https://semver.org/#summary) with possible extensions.
- Every merged PR should bump the version info in ``version/version.py`` depending on the nature of the change (minor fix means bumping `<PATCH>` and so forth).
  Reset the lesser version number (e.g., `<PATCH>`) if the higher version level is incremented (e.g, `<MINOR>`).
- [cosgap.readthedocs.io](https://cosgap.rtfd.io) should trigger docs builds automatically with each merged PR.
- Make sure that the [CHANGELOG](CHANGELOG.md) is kept up to date.
- Create a tag for each change in version (excluding `dev`,`rc#` extensions, and similar).
  This can be done by issuing (post merge):
  ```
  git pull
  git tag -a v<MAJOR>.<MINOR>.<PATCH> -m "Release v<MAJOR>.<MINOR>.<PATCH>"
  git push --tags
  ```
- Each new tag warrants a new release. This is presently done via [Draft new release](https://github.com/comorment/containers/releases/new).
  Here, choose the corresponding tag ID and Target, and set the appropriate title as `CoMorMent-Containers-v<MAJOR>.<MINOR>.<PATCH>`.
  Press the "Generate release notes" to list changes since the last appropriate tag (e.g., `v<MAJOR>.<MINOR>` for a bump to `<PATCH>`, and similar).
  Then, press "Publish release".
- New releases should trigger Zenodo.org code deposit automatically at [https://doi.org/10.5281/zenodo.7385620](https://doi.org/10.5281/zenodo.7385620).
- Sync github.com/comorment/containers to TSD p697 project, following steps outlined [here](https://github.com/comorment/containers/issues/174)

### Sphinx

We use sphinx to generate online documentation from README.md files of this repository.
This uses [MyST](https://myst-parser.readthedocs.io) package to generate links in the documentation.
Here are few rules that we follow across ``.md`` files to make it work well:

* use full path to the file in this repository

### Folder structure

These folders are relevant to the users:
* ``docs`` folder contain user documentation
* ``usecases`` folder contain extended examples / tutorials
* ``singularity`` folder contain pre-build containers
* ``reference`` folder contain reference data used in use-cases
* ``scripts`` folder contain pipelines such as ``gwas.py`` and ``pgs-toolkit``, as well as other helper scripts.

These folders are relevant to developers:
* ``docker`` folder contains several ``Dockerfile`` files (container definitions) 
and relevant shell scripts (in ``docker/scripts/``) used within those Dockerfile's. Unit-tests validating functionality of the resulting containers are available in the ``tests`` folder.
* ``sphinx-docs`` provides scripts used to build sphinx documentation.

### Note about NREC machine

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

### Testing container builds

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

### Git clone ignoring LFS

See [stackoverflow.com/questions/42019529/how-to-clone-pull-a-git-repository-ignoring-lfs](https://stackoverflow.com/questions/42019529/how-to-clone-pull-a-git-repository-ignoring-lfs)
```
GIT_LFS_SKIP_SMUDGE=1 git clone git@github.com:comorment/containers.git
```
