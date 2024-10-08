# encoding: utf-8

"""
Test module for ``gwas.sif`` build
"""

import os
import subprocess
import tempfile
import platform
import pytest


# Check that (1) singularity exist, and (2) if not, check for docker.
# If neither are found, tests will fail
cwd = os.getcwd()
try:
    pth = os.path.join('singularity', 'gwas.sif')
    subprocess.run('singularity', check=False)
    PREFIX = f'singularity run {pth}'
    PREFIX_MOUNT = f'singularity run --home={cwd}:/home/ {pth}'
except FileNotFoundError:
    try:
        subprocess.run('docker', check=False)
        PREFIX = 'docker run ghcr.io/comorment/gwas'
        PREFIX_MOUNT = (
            'docker run ' +
            f'--mount type=bind,source={cwd},target={cwd} ' +
            '{custom_mount}' +
            '-w /home/ ' +
            # '--platform linux/amd64 ' +
            'ghcr.io/comorment/gwas')
    except FileNotFoundError as err:
        # neither singularity nor docker found, fall back to plain python
        # presumably because we are running on the client
        mssg = 'Neither singularity nor docker found, tests will fail'
        raise FileNotFoundError(mssg) from err


# def test_gwas_bcftools():
#     """test bcftools"""
#     call = f'{PREFIX} bcftools --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_beagle():
#     """test beagle"""
#     call = f'{PREFIX} beagle'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_bedtools():
#     """test bedtools"""
#     call = f'{PREFIX} bedtools --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_bgenix():
#     """test bgenix, cat-bgen, edit-bgen binaries"""
#     for binary in ['bgenix', 'cat-bgen', 'edit-bgen']:
#         call = f'{PREFIX} {binary} -help'
#         out = subprocess.run(call.split(' '), check=False)
#         assert out.returncode == 0

@pytest.mark.xfail(reason="unsupported on GH builder?")
def test_gwas_bolt():
    """test bolt"""
    call = f'{PREFIX} bolt -h'
    out = subprocess.run(call, shell=True, check=False, capture_output=True)
    try:
        assert out.returncode == 0
    except AssertionError as exc:
        print(out.stdout.decode('utf-8'))
        print(out.stderr.decode('utf-8'))
        raise AssertionError from exc


# def test_gwas_eagle():
#     """test eagle"""
#     call = f'{PREFIX} eagle -h'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_flashpca():
#     """test flashpca"""
#     call = f'{PREFIX} flashpca_x86-64 --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_gcta():
#     """test gcta"""
#     with tempfile.TemporaryDirectory() as d:
#         os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz -C {d}')
#         custom_mount = f'--mount type=bind,source={d},target={d} '
#         call = f'{PREFIX_MOUNT.format(custom_mount=custom_mount)} gcta64 ' + \
#             f'--bfile {d}/ex --out .'
#         out = subprocess.run(call, shell=True, check=True)
#         assert out.returncode == 0


# def test_gwas_gctb():
#     """test gctb"""
#     if platform.machine() == 'arm64':
#         pytest.skip('gctb is not available for arm64 architecture')
#     else:
#         with tempfile.TemporaryDirectory() as d:
#             os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz -C {d}')
#             custom_mount = f'--mount type=bind,source={d},target={d} '
#             call = f'{PREFIX_MOUNT.format(custom_mount=custom_mount)} ' + \
#                 f'gctb --bfile {d}/ex --out .'
#             out = subprocess.run(call, shell=True, check=True)
#             assert out.returncode == 0


# def test_gwas_gwama():
#     """test gwama"""
#     call = f'{PREFIX} GWAMA --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_king():
#     """test king"""
#     with tempfile.TemporaryDirectory() as d:
#         os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz -C {d}')
#         custom_mount = f'--mount type=bind,source={d},target={d} '
#         call = ' '.join(
#             [f'{PREFIX_MOUNT.format(custom_mount=custom_mount)} king -b',
#              f'{d}/ex.bed --fam {d}/ex.fam --bim {d}/ex.bim --related'])
#         out = subprocess.run(call.split(' '), check=False)
#         assert out.returncode == 0


# def test_gwas_ldak():
#     """test ldak"""
#     call = (f'{PREFIX} ldak ' +
#             '--make-snps 1 --num-samples 1 --num-snps 1')
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_liftover():
#     """test liftOver"""
#     call = f'{PREFIX} liftOver -errorHelp'
#     out = subprocess.run(call.split(' '), capture_output=True, check=False)
#     assert out.stdout.decode('utf-8').lower().rfind('error') <= 0


def test_gwas_metal():
    """test metal"""
    with tempfile.TemporaryDirectory() as d:
        os.system(
            f'tar -xvf {cwd}/tests/extras/GlucoseExample.tar.gz -C {d} ' +
            '--strip-components=1')
        # os.chdir(d)  # test must be run in temporary directory
        custom_mount = f'--mount type=bind,source={d},target={d} '
        call = \
            f'{PREFIX_MOUNT.format(custom_mount=custom_mount)} metal metal.txt'

        out = subprocess.run(call.replace('-w /home', f'-w {d}'),
                             shell=True, capture_output=True, check=False)
        assert out.returncode == 0
        # software may not crash on error, checking captured output
        assert out.stdout.decode('utf-8').rfind('Error') <= 0
        assert out.stdout.decode(
            'utf-8').rfind(
                "## Smallest p-value is 1.491e-12 at marker 'rs560887'") > 0


# def test_gwas_minimac4():
#     """test minimac4"""
#     call = f'{PREFIX} minimac4 --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_plink():
#     """test plink"""
#     call = f'{PREFIX} plink --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_plink2():
#     """test plink2"""
#     call = f'{PREFIX} plink2 --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_plink2_avx2():
#     """test plink2_avx2"""
#     if platform.machine() == 'arm64':
#         pytest.skip('plink2_avx2 is not available for arm64 architecture')
#     else:
#         call = f'{PREFIX} plink2_avx2 --version'
#         out = subprocess.run(call.split(' '), check=False)
#         assert out.returncode == 0


# def test_gwas_prsice():
#     """test prsice"""
#     call = f'{PREFIX} PRSice_linux --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_qctools():
#     """test qctools"""
#     if platform.machine() == 'arm64':
#         pytest.skip('qctools is not available for arm64 architecture')
#     else:
#         for binary in ['inthinnerator', 'hptest',
#                        'ldbird', 'qctool', 'selfmap']:
#             call = f'{PREFIX} {binary} -help'
#             out = subprocess.run(call.split(' '), check=False)
#             assert out.returncode == 0


# def test_gwas_regenie():
#     """test regenie"""
#     call = f'{PREFIX} regenie option --help'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_samtools():
#     """test samtools"""
#     call = f'{PREFIX} samtools --help'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_shapeit4():
#     """test shapeit4"""
#     if platform.machine() == 'arm64':
#         pytest.skip('shapeit4 is not available for arm64 architecture')
#     else:
#         call = f'{PREFIX} shapeit4.2 --help'
#         out = subprocess.run(call.split(' '), check=False)
#         assert out.returncode == 0


# def test_gwas_shapeit5():
#     """test shapeit5"""
#     if platform.machine() == 'arm64':
#         pytest.skip('shapeit5 is not available for arm64 architecture')
#     else:
#         for binary in ['phase_common', 'phase_rare',
#                        'ligate', 'switch', 'xcftools']:
#             call = f'{PREFIX} {binary} --help'
#             out = subprocess.run(call.split(' '), check=False)
#             assert out.returncode == 0


# def test_gwas_snptest():
#     """test snptest"""
#     if platform.machine() == 'arm64':
#         pytest.skip('snptest is not available for arm64 architecture')
#     else:
#         call = f'{PREFIX} snptest -help'
#         out = subprocess.run(call.split(' '), check=False)
#         assert out.returncode == 0


# @pytest.mark.xfail(reason="no help function for switchError")
# def test_gwas_switchError():
#     """test switchError"""
#     call = (f'{PREFIX} switchError' +
#             '--reg foo --gen foo --hap foo --fam foo ' +
#             '--ps foo --out foo --maf 0.0')
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_simu():
#     """test simu"""
#     with tempfile.TemporaryDirectory() as d:
#         os.system(f'tar -xvf {cwd}/tests/extras/ex.tar.gz -C {d}')
#         custom_mount = f'--mount type=bind,source={d},target={d} '
#         call = ' '.join(
#             [f'{PREFIX_MOUNT.format(custom_mount=custom_mount)} ' +
#              f'simu_linux --bfile {d}/ex --qt ',
#              '--causal-pi 0.01 --num-traits 2 --hsq 0.2 0.6 --rg 0.8'])
#         out = subprocess.run(call.split(' '), check=False)
#         assert out.returncode == 0


# def test_gwas_vcftools():
#     """test vcftools"""
#     call = f'{PREFIX} vcftools --version'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0


# def test_gwas_duohmm():
#     """test duohmm"""
#     call = f'{PREFIX} duohmm'
#     out = subprocess.run(call.split(' '), check=False)
#     assert out.returncode == 0
