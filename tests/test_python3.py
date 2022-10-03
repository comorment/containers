# encoding: utf-8

"""
Test module for ``python3.sif`` build
"""

import os
import subprocess

def test_python3():
    pth = os.path.join('singularity', 'python3.sif')
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
    