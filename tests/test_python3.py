# encoding: utf-8

"""
Test module for ``python3.sif`` build
"""

import os
import socket
import subprocess

# port used by tests
sock = socket.socket()
sock.bind(('', 0))
port = sock.getsockname()[1]

# Check that (1) apptainer exist, and (2) if not, check for docker.
# If neither are found, tests will fail
cwd = os.getcwd()
try:
    pth = os.path.join('containers', 'latest', 'python3.sif')
    subprocess.run('apptainer', check=False)
    PREFIX = f'apptainer run {pth}'
    PREFIX_MOUNT = f'apptainer run --home={cwd}:/home/ {pth}'
    PYTHON = f'{PREFIX} python'
    PYTHON_MOUNT = f'{PREFIX_MOUNT} python'
    PLINK = f'{PREFIX} plink'
    PLINK2 = f'{PREFIX} plink2'
    PRSICE = f'{PREFIX} PRSice_linux'
    MINIWDL = f'{PREFIX} miniwdl'
except FileNotFoundError:
    try:
        subprocess.run('docker', check=False)
        PREFIX = (f'docker run -p {port}:{port} ' +
                  'ghcr.io/comorment/python3')
        PREFIX_MOUNT = (
            f'docker run -p {port}:{port} ' +
            f'--mount type=bind,source={cwd},target={cwd} ' +
            '--platform linux/amd64 ' +
            'ghcr.io/comorment/python3')
        PYTHON = f'{PREFIX} python'
        PYTHON_MOUNT = f'{PREFIX_MOUNT} python'
        PLINK = f'{PREFIX} plink'
        PLINK2 = f'{PREFIX} plink2'
        PRSICE = f'{PREFIX} PRSice_linux'
        MINIWDL = f'{PREFIX} miniwdl'
    except FileNotFoundError:
        # neither apptainer nor docker found, fall back to plain python
        # presumably because we are running on the client
        PYTHON = 'python'
        PYTHON_MOUNT = 'python'
        PLINK = 'plink'
        PLINK2 = 'plink2'
        PRSICE = 'PRSice_linux'
        MINIWDL = 'miniwdl'

def test_python3_plink():
    call = f'{PLINK} --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0

def test_python3_plink2():
    """test plink2"""
    call = f'{PLINK2} --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0

def test_python3_prsice():
    call = f'{PRSICE} --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0

def test_python3_python():
    call = f'{PYTHON} --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0

def test_python3_fastlmm():
    call = f'{PYTHON_MOUNT} ' + \
          f'{cwd}/tests/extras/fastlmm_example_script.py'
    out = subprocess.run(call, shell=True, check=False)
    assert out.returncode == 0

def test_python3_python_convert():
    args = ['/tools/python_convert/sumstats.py -h',
            '/tools/python_convert/tests/test_consistent.py',
            '/tools/python_convert/tests/test_duplicated.py']
    for arg in args:
        call = f'{PYTHON} {arg}'
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0

def test_python3_ukb():
    arg = '/tools/ukb/ukb_helper.py -h'
    call = f'{PYTHON} {arg}'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0

def test_python3_miniwdl():
    arg = '--help'
    call = f'{MINIWDL} {arg}'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0

def test_python3_packages():
    packages = [
        'configparser',
        'dask',
        'fastparquet',
        'dxpy',
        'graphviz',
        'h5py',
        'imblearn',
        'intervaltree',
        'ldpred',
        'lifelines',
        'lightgbm',
        'matplotlib',
        'matplotlib_venn',
        'numba',
        'numdifftools',
        'numpy',
        'openpyxl',
        'pandas',
        'pandas_plink',
        'plinkio',
        'pyarrow',
        'pydot',
        'pyliftover',
        'pyreadstat',
        'redcap',  # pycap
        'scipy',
        'seaborn',
        'semantic_version',
        'shap',
        'sklearn',
        'sksurv',
        'statsmodels',
        'tables',
        'xlrd',
        'xmltodict',
        'xgboost',
        'yaml',  # pyyaml
        ]
    importstr = 'import ' + ', '.join(packages)
    call = f"{PYTHON} -c '{importstr}'"
    out = subprocess.run(call, shell=True, check=False)
    assert out.returncode == 0

def test_python3_import_pandas_scipy_stats():
    call = f'{PYTHON_MOUNT} -c "import pandas as pd; from scipy import *"'
    out = subprocess.run(call, shell=True, check=False)
    assert out.returncode == 0
