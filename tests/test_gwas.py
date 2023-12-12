# encoding: utf-8

"""
Test module for ``gwas.sif`` build
"""

import os
import subprocess
import tempfile
import pytest


pth = os.path.join('singularity', 'gwas.sif')


def test_gwas_bcftools():
    """test bcftools"""
    call = f'singularity run {pth} bcftools --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_beagle():
    """test beagle"""
    call = f'singularity run {pth} beagle'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_bgenix():
    """test bgenix, cat-bgen, edit-bgen binaries"""
    for binary in ['bgenix', 'cat-bgen', 'edit-bgen']:
        call = f'singularity run {pth} {binary} -help'
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_bolt():
    """test bolt"""
    call = f'singularity run {pth} bolt -h'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_eagle():
    """test eagle"""
    call = f'singularity run {pth} eagle -h'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_flashpca():
    """test flashpca"""
    call = f'singularity run {pth} flashpca_x86-64 --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_gcta():
    """test gcta"""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run {pth} gcta64 --bfile {d}/ex --out {d}'
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_gctb():
    """test gctb"""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = f'singularity run {pth} gctb --bfile {d}/ex --out {d}'
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_gwama():
    """test gwama"""
    call = f'singularity run --home=/tmp/:/home/ {pth} GWAMA --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_king():
    """test king"""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = ' '.join(
            [f'singularity run --home={d}:/home/ {pth} king -b',
             f'{d}/ex.bed --fam {d}/ex.fam --bim {d}/ex.bim --related'])
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_ldak():
    """test ldak"""
    call = f'singularity run {pth} ldak --make-snps 1 --num-samples 1 --num-snps 1'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_metal():
    """test metal"""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/GlucoseExample.tar.gz')
        os.chdir('GlucoseExample')
        call = \
            f'singularity run --home=$PWD:/home/ {cwd}/{pth} metal metal.txt'
        out = subprocess.run(call.split(' '), capture_output=True, check=False)
        assert out.returncode == 0
        # software may not crash on error, checking captured output
        assert out.stdout.decode('utf-8').rfind('Error') <= 0
        assert out.stdout.decode(
            'utf-8').rfind(
                "## Smallest p-value is 1.491e-12 at marker 'rs560887'") > 0
    os.chdir(cwd)


def test_gwas_minimac4():
    """test minimac4"""
    call = f'singularity run {pth} minimac4 --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_plink():
    """test plink"""
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_plink2():
    """test plink2"""
    call = f'singularity run {pth} plink2 --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_plink2_avx2():
    """test plink2_avx2"""
    call = f'singularity run {pth} plink2_avx2 --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_prsice():
    """test prsice"""
    call = f'singularity run {pth} PRSice_linux --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_qctools():
    """test qctools"""
    for binary in ['inthinnerator', 'hptest', 'ldbird', 'qctool', 'selfmap']:
        call = f'singularity run {pth} {binary} -help'
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_regenie():
    """test regenie"""
    call = f'singularity run {pth} regenie option --help'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_shapeit4():
    """test shapeit4"""
    call = f'singularity run {pth} shapeit4.2 --help'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_shapeit5():
    """test shapeit5"""
    for binary in ['phase_common', 'phase_rare',
                   'ligate', 'switch', 'xcftools']:
        call = f'singularity run {pth} {binary} --help'
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_snptest():
    """test snptest"""
    call = f'singularity run {pth} snptest -help'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


@pytest.mark.xfail(reason="no help function for switchError")
def test_gwas_switchError():
    """test switchError"""
    call = f'singularity run {pth} switchError --reg foo --gen foo --hap foo --fam foo --ps foo --out foo --maf 0.0'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_simu():
    """test simu"""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz')
        os.chdir(cwd)
        call = ' '.join(
            [f'singularity run --home=/tmp/:/home/ {pth}',
             f'simu_linux --bfile {d}/ex --qt ',
             '--causal-pi 0.01 --num-traits 2 --hsq 0.2 0.6 --rg 0.8'])
        out = subprocess.run(call.split(' '), check=False)
        assert out.returncode == 0


def test_gwas_vcftools():
    """test vcftools"""
    call = f'singularity run {pth} vcftools --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0


def test_gwas_duohmm():
    """test duohmm"""
    call = f'singularity run {pth} duohmm'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0
