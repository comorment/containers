# Docker

This repository is used to develop and document [Singularity](https://sylabs.io) or [Apptainer](https://apptainer.org) containers with various software and analytical tools for GWAS and post-GWAS analysis via [Docker](https://www.docker.com).

## Getting started

For new users we recommend to go over introductory instructions in [docs/hello.md](https://github.com/comorment/containers/blob/main/docs/hello.md), which explain the basic usage of singularity containers, using a minimalistic example (singularity container with ``plink`` binary).

If you would like to contribute to developing these containers, please see  [docs/contributing.md](https://github.com/comorment/containers/blob/main/CONTRIBUTING.md).

For a tutorial on GWAS with synthetic data, see [docs/gwas.md](https://github.com/comorment/containers/blob/main/docs/gwas.md).

### Prerequisites (to running tutorials)

* download containers shared on the [Google Drive](https://drive.google.com/drive/folders/1mfxZJ-7A-4lDlCkarUCxEf2hBIxQGO69?usp=sharing).
* download ``comorment_ref.tar.gz`` file from the above Google Drive folder, extract it with ``tar -xzvf comorment_ref.tar.gz`` command,
  and create an environmental variable ``COMORMENT_REF`` pointing to the folder containing extracted ``comorment_ref.tar.gz`` data.
  If you want to see the content of ``comorment_ref.tar.gz`` without downloading and extracting,
  you may take a quick look [here](https://github.com/norment/comorment_data). This is a private repository, and you need to get access.
  Please contact Oleksandr and Bayram by e-mail and send us your github user name. If you don't have it, create one [here](http://github.com/join).
* create an empty folder called ``data``, for storing the results and intermediate files produced by running containers.
  (most instructinos mount this folder like this: ``-B data:/data``).

### Description of available containers

The detailed description of the available container [files](./../singularity) provided in this repository are found [here](./docs/singularity).

### Software versions

  Below is the list of tools included in the different Dockerfiles and installer bash scripts for each container.
  Please keep up to date (and update the main [README.md](./../README.md) when pushing new container builds):
  
  | container         | OS/tool             | version                                   | license
  | ----------------- | ------------------- | ----------------------------------------- | -------------
  | hello.sif         | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | hello.sif         | plink               | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | gwas.sif          | plink               | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | plink2              | v2.00a3.6LM 64-bit Intel (14 Aug 2022)    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | plink2_avx2         | v2.00a3.6LM AVX2 Intel (24 Jan 2020)      | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | PRSice_linux        | 2.3.3 (2020-08-05)                        | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | simu_linux          | v0.9.4                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | bolt                | v2.4 July 22, 2022                        | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | gcta64              | version 1.93.2 beta Linux                 | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | gctb                | 2.02                                      | [MIT](https://opensource.org/licenses/MIT)
  | gwas.sif          | qctool              | 2.0.6, revision 18b8f17                   | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | gwas.sif          | king                | 2.2.9 - (c)                               | [permissive](https://www.kingrelatedness.com/Download.shtml)
  | gwas.sif          | metal               | version released on 2011-03-25            | -
  | gwas.sif          | vcftools            | 0.1.17                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | bcftools            | 1.12 (using htslib 1.12)                  | [MIT/Expat/GPLv3](https://github.com/samtools/bcftools/blob/develop/LICENSE)
  | gwas.sif          | flashpca_x86-64     | 2.0                                       | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | regenie             | v2.0.2.gz                                 | [MIT/Boost](https://github.com/rgcgithub/regenie/blob/master/LICENSE)
  | gwas.sif          | GWAMA               | 2.2.2                                     | [BSD-3-Clause](https://opensource.org/licenses/BSD-3-Clause)
  | gwas.sif          | minimac4            | v4.1.0                                    | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | gwas.sif          | bgenix              | 1.1.7                                     | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | gwas.sif          | cat-bgen            | same version as bgenix                    | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | gwas.sif          | edit-bgen           | same version as bgenix                    | [Boost](https://www.boost.org/LICENSE_1_0.txt)
  | gwas.sif          | HTSlib              | 1.12                                      | [MIT/Expat/Modified-BSD](https://github.com/samtools/htslib/blob/develop/LICENSE)
  | gwas.sif          | shapeit4.2          | v4.2.2                                    | [MIT](https://opensource.org/licenses/MIT)
  | python3.sif       | ubuntu              | 20.04 (LTS)                               | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | python3.sif       | python3             | python 3.10.6 + numpy, pandas, etc.       | [PSF](https://docs.python.org/3.10/license.html)
  | python3.sif       | LDpred              | 1.0.11                                    | [MIT](https://opensource.org/licenses/MIT)
  | python3.sif       | python_convert      | github commit bcde562                     | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | python3.sif       | plink               | v1.90b6.18 64-bit (16 Jun 2020)           | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | r.sif             | ubuntu              | 20.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | r.sif             | R                   | 4.0.5 (2021-03-31) + data.table, ggplot, etc. | [misc](https://www.r-project.org/Licenses/)
  | r.sif             | gcta64              | version 1.93.2 beta Linux                 | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | r.sif             | seqminer            | [zhanxw/seqminer@142204d](https://github.com/zhanxw/seqminer/commit/142204d1005553ea87e1740ff97f0286291e41f9)  | [GPL](https://github.com/zhanxw/seqminer/blob/master/LICENSE)
  | r.sif             | rareGWAMA           | [dajiangliu/rareGWAMA@72e962d](https://github.com/dajiangliu/rareGWAMA/commit/72e962dae19dc07251244f6c33275ada189c2126)  | -
  | r.sif             | GenomicSEM          | [GenomicSEM/GenomicSEM@bcbbaff](https://github.com/GenomicSEM/GenomicSEM/commit/bcbbaffff5767acfc5c020409a4dc54fbf07876b)  | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | r.sif             | TwoSampleMR         | [MRCIEU/TwoSampleMR@c174107](https://github.com/MRCIEU/TwoSampleMR/commit/c174107cfd9ba47cf2f780849a263f37ac472a0e)  | [unknown/MIT](https://github.com/MRCIEU/TwoSampleMR#:~:text=Unknown%2C%20MIT%20licenses-,found,-Citation)
  | r.sif             | GSMR                | v1.0.9                                    | [GPL>=v2](https://www.gnu.org/licenses/gpl-2.0.html)
  | r.sif             | snpStats            | v1.40.0                                   | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)
  | saige.sif         | ubuntu              | 16.04                                     | [Creative Commons CC-BY-SA version 3.0 UK licence](https://ubuntu.com/legal/intellectual-property-policy)
  | saige.sif         | SAIGE               | version 0.43                              | [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

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
