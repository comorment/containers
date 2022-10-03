# encoding: utf-8

"""
Test module for ``saige.sif`` build
"""

import os
import subprocess


def test_saige():
    pth = os.path.join('singularity', 'saige.sif')
    call = f'singularity run {pth} R --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
