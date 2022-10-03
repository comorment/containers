# encoding: utf-8

"""
Test module for ``gwas.sif`` build
"""

import os
import subprocess

def test_gwas():
    pth = os.path.join('singularity', 'gwas.sif')
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
    