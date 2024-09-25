# encoding: utf-8

"""
Test module for ``hello.sif`` build
"""

import os
import socket
import subprocess

# port used by tests
sock = socket.socket()
sock.bind(('', 0))
port = sock.getsockname()[1]

# Check that (1) singularity exist, and (2) if not, check for docker.
# If neither are found, tests will fail
try:
    pth = os.path.join('singularity', 'hello.sif')
    subprocess.run('singularity', check=False)
    PREFIX = f'singularity run {pth}'
    PLINK = f'{PREFIX} plink'
except FileNotFoundError:
    try:
        subprocess.run('docker', check=False)
        PREFIX = (f'docker run -p {port}:{port} ' +
                  'ghcr.io/comorment/hello')
        PLINK = f'{PREFIX} plink'
    except FileNotFoundError:
        # neither singularity nor docker found, fall back to plain python
        # presumably because we are running on the client
        PLINK = 'plink'

def test_hello_plink():
    call = f'{PLINK} --version'
    out = subprocess.run(call.split(' '), check=False)
    assert out.returncode == 0
