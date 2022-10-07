# encoding: utf-8

"""
Test module for ``saige.sif`` build
"""

import os
import subprocess


pth = os.path.join('singularity', 'saige.sif')

def test_saige_R():
    call = f'singularity run {pth} R --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_saige_Rscript():
    call = f'singularity run {pth} Rscript --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0