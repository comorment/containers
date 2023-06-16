# encoding: utf-8

"""
Test module for ``matlab.sif`` build
"""

import os
import subprocess


def test_matlab():
    pth = os.path.join('singularity', 'matlab.sif')
    os.environ['SINGULARITYENV_MLM_LICENSE_FILE'] = '/licenses/license.dat'
    call = f'singularity run --home=/tmp/:/home/ --bind tests/licenses:/licenses:ro {pth} -batch fprintf(version)'
    out = subprocess.run(call.split(' '), check=True, capture_output=True)
    assert out.returncode == 0
    assert out.stdout.decode().split('\n')[-1] == '9.14.0.2254940 (R2023a) Update 2'
