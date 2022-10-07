# encoding: utf-8

"""
Test module for ``r.sif`` build
"""

import os
import subprocess


pth = os.path.join('singularity', 'r.sif')

def test_r_R():
    call = f'singularity run {pth} R --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_r_Rscript():
    call = f'singularity run {pth} Rscript --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
