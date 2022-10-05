# encoding: utf-8

"""
Test module for ``hello.sif`` build
"""

import os
import subprocess


def test_hello():
    pth = os.path.join('singularity', 'hello.sif')
    call = f'singularity run {pth} plink --version'
    out = subprocess.run(call.split(' '))
    assert out.returncode == 0
