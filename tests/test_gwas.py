# encoding: utf-8

"""
Test module for ``gwas.sif`` build
"""

import os
import subprocess
import tempfile


pth = os.path.join('singularity', 'gwas.sif')

def test_gwas_bgenix():
    call = f'singularity run {pth} bgenix -help'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_king():
    # prep test dataset:
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system('wget https://www.kingrelatedness.com/ex.tar.gz && tar -xvf ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run {pth} king -b {d}/ex.bed --fam {d}/ex.fam --bim {d}/ex.bim --related'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0

def test_gwas_minimac4():
    call = f'singularity run {pth} minimac4 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_plink():
    pth = os.path.join('singularity', 'gwas.sif')
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_plink2():
    pth = os.path.join('singularity', 'gwas.sif')
    call = f'singularity run {pth} plink2 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
