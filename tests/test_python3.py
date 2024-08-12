# encoding: utf-8

"""
Test module for ``python3.sif`` build
"""

import os
import subprocess

# https://github.com/comorment/containers/issues/267:
os.environ.update({'SINGULARITYENV_LD_LIBRARY_PATH': 
                   '/usr/local/lib:$LD_LIBRARY_PATH'})

pth = os.path.join('singularity', 'python3.sif')


def test_python3_plink():
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0


def test_python3_python():
    call = f'singularity run {pth} python --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0


def test_python3_fastlmm():
    pwd = os.getcwd()
    call = f'singularity run --home={pwd} {pth} python ' + \
           f'{pwd}/tests/extras/fastlmm_example_script.py'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0


def test_python3_python_convert():
    args = ['/tools/python_convert/sumstats.py -h',
            '/tools/python_convert/tests/test_consistent.py',
            '/tools/python_convert/tests/test_duplicated.py']
    for arg in args:
        call = f'singularity run {pth} python {arg}'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0


def test_python3_ukb():
    arg = '/tools/ukb/ukb_helper.py -h'
    call = f'singularity run {pth} python {arg}'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0


def test_python3_packages():
    packages = [
        'h5py',
        'ldpred',
        'lifelines',
        'matplotlib',
        'matplotlib_venn',
        'numdifftools',
        'numpy',
        'pandas',
        'plinkio',
        'redcap',  # pycap
        'pyreadstat',
        'yaml',  # pyyaml
        'scipy',
        'seaborn',
        'semantic_version',
        'statsmodels',
        'xlrd']
    for pkg in packages:
        call = f'singularity run {pth} python -c "import {pkg}"'
        out = subprocess.run(call.split(' '))
        assert out.returncode == 0

def test_python3_import_pandas_scipy_stats():
    pwd = os.getcwd()
    call = f'singularity run --home={pwd} {pth} python -c "import pandas as pd; from scipy import *"'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
