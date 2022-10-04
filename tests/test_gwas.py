# encoding: utf-8

"""
Test module for ``gwas.sif`` build
"""

import os
import subprocess

pth = os.path.join('singularity', 'gwas.sif')

def test_plink():
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_plink2()
    call = f'singularity run {pth} plink2 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_minimac4():
    call = f'singularity run {pth} minimac4 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
