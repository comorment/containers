# encoding: utf-8

"""
Test module for ``python3.sif`` build
"""

import os
import subprocess


pth = os.path.join('singularity', 'python3.sif')

def test_python3_plink():
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_python3_python():
    call = f'singularity run {pth} python --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
