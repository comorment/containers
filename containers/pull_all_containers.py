#!/usr/bin/env python
# -*- coding: utf-8 -*-
# script to pull/build singularity image format files from
# pushed registry builds.

import os
import tempfile
import shutil
import argparse
from packaging.version import Version, InvalidVersion

# Manually curated list of containers to pull.
# Defining things manually as some registries may have many tags and we
# don't want them all.
# We may also choose to sync only registry pulls without git repos/codes

# parse input tags
parser = argparse.ArgumentParser(
    description='Pull all containers from registry')
parser.add_argument('tags', nargs='+', help='list of tags to pull')
tags = parser.parse_args().tags

docker_packages_dest_prefix_tags = {
    'ghcr.io/comorment/hello': {
        'dest': os.getcwd(),   # destination directory
        'prefix': 'hello',  # file prefix
        'tags': tags,  # list of tags
        'create_tag_dir': True   # create target directory for each tag
    },
    'ghcr.io/comorment/gwas': {
        'dest': os.getcwd(),
        'prefix': 'gwas',
        'tags': tags,
        'create_tag_dir': True
    },
    'ghcr.io/comorment/python3': {
        'dest': os.getcwd(),
        'prefix': 'python3',
        'tags': tags,
        'create_tag_dir': True
    },
    'ghcr.io/comorment/r': {
        'dest': os.getcwd(),
        'prefix': 'r',
        'tags': tags,
        'create_tag_dir': True
    },
}

# recursively pull and create .sif files if they don't exist:
for ref, dest_prefix_tags in docker_packages_dest_prefix_tags.items():
    dest = dest_prefix_tags['dest']
    prefix = dest_prefix_tags['prefix']
    tags = dest_prefix_tags['tags']
    create_tag_dir = dest_prefix_tags['create_tag_dir']

    # make destination directory
    os.makedirs(dest, exist_ok=True)

    for tag in tags:
        # pull the image if it does not exist
        if create_tag_dir:
            os.makedirs(os.path.join(dest, tag), exist_ok=True)
            fname = os.path.join(dest, tag, f'{prefix}.sif')
        else:
            fname = os.path.join(dest, f'{prefix}_{tag}.sif')
        if not os.path.isfile(fname):
            try:
                assert shutil.which('oras') is not None
                print(f'pulling build {fname}')
                # note "_sif" suffix
                os.system(f'oras pull -o {tag} {ref}_sif:{tag}')
            except AssertionError:
                try:
                    shutil.which('apptainer') is not None
                except AssertionError:
                    mssg = 'Neither oras nor apptainer executables found.'
                    raise Exception(mssg)
                print(f'creating build {fname}:')
                with tempfile.TemporaryDirectory() as tmpdir:
                    cmmd = f'''export APPTAINER_CACHEDIR={tmpdir} && \n
                    apptainer pull {fname} docker://{ref}:{tag}'''
                    os.system(cmmd)

    # if 'latest' not in tags, symlink tag with highest semantic version:
    cwd = os.getcwd()
    if 'latest' not in tags:
        try:
            max_version = max([Version(t) for t in tags])
            for tag in tags:
                if Version(tag) == max_version:
                    break
        except InvalidVersion:
            # deal with unsupported tag formats
            max_version = max([Version(t.split('-')[0]) for t in tags])
            for tag in tags:
                if tag.split('-')[0] == str(max_version):
                    break

        os.chdir(dest)
        if create_tag_dir:
            # symlink tag dir as latest
            os.system(f"ln -s -f -n {tag} latest")
        else:
            # symlink tagged file as latest
            os.system(
                f"ln -s -f {f'{prefix}_{tag}.sif'} {f'{prefix}_latest.sif'}")
        os.chdir(cwd)
