import os
import subprocess

if __name__ == '__main__':
    # singularity exec --home=$PWD:/home singularity/python3.sif jupyter-server

    # enviroment variables for test runs
    os.environ.update(dict(
        CONTAINERS=os.path.split(os.getcwd())[0],
    ))
    os.environ.update(dict(
        SIF=os.path.join(os.environ['CONTAINERS'], 'singularity'),
        REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference')
    ))
    os.environ.update(dict(
        SINGULARITY_BIND=f'{os.environ["REFERENCE"]}:/REF'
    ))

    # Executables in containers
    SIF = os.environ['SIF']
    PWD = os.getcwd()
    os.environ.update(
        dict(
            JUPYTER_SERVER=f"singularity exec --home={PWD}:/home {SIF}/python3.sif jupyter-server",
        ))

    subprocess.run(os.environ['JUPYTER_SERVER'], shell=True)