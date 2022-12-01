

import os
import pgrs
import subprocess

if __name__ == '__main__':
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
            BASH_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif bash",
            GUNZIP_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif gunzip",
            GZIP_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif gzip",
            AWK_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif awk",
            RSCRIPT=f"singularity exec --home={PWD}:/home {SIF}/r.sif Rscript",
            PLINK=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif plink",
            PRSICE=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif PRSice_linux",
        ))

    # QC
    os.environ.update({
        'QCDIR': 'QC_data',
    })

    # Plink
    plink = pgrs.PGS_Plink(
        Sumstats_file=os.path.join(os.environ['QCDIR'], 'Height.QC.gz'),
        Pheno_file='/REF/examples/prsice2/EUR.height',
        Input_dir=os.environ['QCDIR'],
        Data_prefix='EUR',
        Output_dir='PGS_plink',
        Cov_file='/REF/examples/prsice2/EUR.cov',
        clump_p1=1,
        clump_r2=0.1,
        clump_kb=250,
        range_list=[0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
        strat_indep_pairwise=[250, 50, 0.25],
        nPCs=6,
        score_args=[3, 4, 12, 'header'],
    )
    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True)
        assert proc.returncode == 0    

    # run basic plink PGS
    for call in plink.get_str(mode='basic'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

    # run plink PGS with population stratification
    for call in plink.get_str(mode='stratification'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0


    # PRSice-2
    prsice2 = pgrs.PGS_PRSice2(
        Sumstats_file=os.path.join(os.environ['QCDIR'], 'Height.QC.gz'),
        Pheno_file=f'/REF/examples/prsice2/EUR.height',
        Input_dir=os.environ['QCDIR'],
        Data_prefix='EUR',
        Output_dir='PGS_prsice2',
        Cov_file='/REF/examples/prsice2/EUR.cov',
        Eigenvec_file='/REF/examples/prsice2/EUR.eigenvec',
        nPCs=6,
        MAF=0.01,
        INFO=0.8
    )

    for call in prsice2.get_str():
        print(f'evaluating: {call}')
        # os.system(cmd)
        proc = subprocess.run(call, shell=True)
        assert proc.returncode == 0
