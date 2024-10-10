# encoding: utf-8

"""
Test module for ``r.sif`` build
"""

import os
import subprocess
import tempfile


# Check that (1) singularity exist, and (2) if not, check for docker.
# If neither are found, tests will fail
cwd = os.getcwd()
try:
    pth = os.path.join(cwd, 'singularity', 'r.sif')
    try:
        runtime = 'apptainer'
        subprocess.run(runtime, check=False)
    except FileNotFoundError:
        try:
            runtime = 'singularity'
            subprocess.run(runtime, check=False)
        except FileNotFoundError as exc:
            raise FileNotFoundError from exc
    PREFIX = f'{runtime} run {pth}'
    PREFIX_MOUNT = f'{runtime} run --home={cwd}:/home/ ' + pth
    PREFIX_CUSTOM_MOUNT = f'{runtime} run --home={cwd}:/home/ ' + \
        '{custom_mount}' + pth
except FileNotFoundError:
    try:
        runtime = 'docker'
        subprocess.run(runtime, check=False)
        PREFIX = f'{runtime} run ghcr.io/comorment/r'
        PREFIX_MOUNT = (
            f'{runtime} run ' +
            f'--mount type=bind,source={cwd},target={cwd} ' +
            '-w /home/ ' +
            'ghcr.io/comorment/r')
        PREFIX_CUSTOM_MOUNT = (
            f'{runtime} run ' +
            f'--mount type=bind,source={cwd},target={cwd} ' +
            '{custom_mount}' +
            '-w /home/ ' +
            'ghcr.io/comorment/r')
    except FileNotFoundError as err:
        # neither singularity nor docker found, fall back to plain python
        # presumably because we are running on the client
        mssg = 'apptainer, singularity nor docker found, tests will fail'
        raise FileNotFoundError(mssg) from err


def test_r_R():
    call = f'{PREFIX} R --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_r_Rscript():
    call = f'{PREFIX} Rscript --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_r_R_packages():
    call = f'{PREFIX_MOUNT} Rscript {cwd}/tests/extras/r.R'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_r_R_rmarkdown():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(
            f"cp {os.path.join(cwd, 'tests', 'extras', 'cars.Rmd')} {d}/")
        os.system(f"cp {os.path.join(cwd, 'tests', 'extras', 'cars.R')} {d}/")
        custom_mount = f'--mount type=bind,source={d},target={d} '
        call = (f'{PREFIX_CUSTOM_MOUNT.format(custom_mount=custom_mount)} ' +
                'Rscript cars.R')
        out = subprocess.run(call.replace('-w /home', f'-w {d}'),
                             shell=True, check=False)
        pdf_output = os.path.isfile('cars.pdf')
        assert out.returncode == 0
        assert pdf_output


def test_gwas_gcta():
    """test gcta"""
    with tempfile.TemporaryDirectory() as d:
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz -C {d}')
        if runtime == 'docker':
            custom_mount = f'--mount type=bind,source={d},target={d} '
        else:
            custom_mount = f'--bind {d}:{d} '
        call = (f'{PREFIX_CUSTOM_MOUNT.format(custom_mount=custom_mount)} ' +
                'gcta64 ' +
                f'--bfile {d}/ex --out .')
        out = subprocess.run(call, shell=True, check=True)
        assert out.returncode == 0


def test_r_bigsnpr():
    with tempfile.TemporaryDirectory() as d:
        os.system(
            f"cp {os.path.join(cwd, 'tests', 'extras', 'bigsnpr.R')} {d}/")
        custom_mount = f'--mount type=bind,source={d},target={d} '
        call = (f'{PREFIX_CUSTOM_MOUNT.format(custom_mount=custom_mount)} ' +
                f'Rscript {d}/bigsnpr.R')
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_r_prsice():
    call = f'{PREFIX} PRSice_linux --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0
