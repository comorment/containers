# encoding: utf-8

"""
Test module for ``r.sif`` build
"""

import os
import subprocess


def test_r():
    pth = os.path.join('singularity', 'r.sif')

    call = f'singularity run {pth} R --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

    call = f'singularity run {pth} Rscript --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
