# encoding: utf-8

"""
Test module for ``gwas.sif`` build
"""

import os
import pytest
import subprocess
import tempfile


pth = os.path.join('singularity', 'gwas.sif')

def test_gwas_bcftools():
    call = f'singularity run {pth} bcftools --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_bgenix():
    for bin in ['bgenix', 'cat-bgen', 'edit-bgen']:
        call = f'singularity run {pth} {bin} -help'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0

def test_gwas_bolt():
    call = f'singularity run {pth} /tools/bolt/bolt -h'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_flashpca():
    call = f'singularity run {pth} flashpca_x86-64 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_gcta():
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run {pth} gcta64 --bfile {d}/ex --out {d}'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0

def test_gwas_gctb():
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run {pth} gctb --bfile {d}/ex --out {d}'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0

def test_gwas_gwama():
    call = f'singularity run --home=/tmp/:/home/ {pth} GWAMA --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0    
    
def test_gwas_king():
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run --home=/tmp/:/home/ {pth} king -b {d}/ex.bed --fam {d}/ex.fam --bim {d}/ex.bim --related'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0

@pytest.mark.skip(reason="Not implemented")
def test_gwas_metal():
    raise NotImplementedError

def test_gwas_minimac4():
    call = f'singularity run {pth} minimac4 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_plink():
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_plink2():
    call = f'singularity run {pth} plink2 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_plink2_avx2():
    call = f'singularity run {pth} plink2_avx2 --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_prsice():
    call = f'singularity run {pth} PRSice_linux --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

@pytest.mark.skip(reason="Not implemented")
def test_gwas_qctools():
    raise NotImplementedError

def test_gwas_regenie():
    call = f'singularity run {pth} regenie option --help'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_shapeit4():
    call = f'singularity run {pth} shapeit4.2 --help'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

def test_gwas_simu():
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run --home=/tmp/:/home/ {pth} simu_linux --bfile {d}/ex --qt --causal-pi 0.01 --num-traits 2 --hsq 0.2 0.6 --rg 0.8'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0
    
def test_gwas_vcftools():
    call = f'singularity run {pth} vcftools --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0

