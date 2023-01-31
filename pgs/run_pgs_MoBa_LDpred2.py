#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import subprocess
import yaml
from pgs import pgs


if __name__ == '__main__':
    # enviroment variables for test runs
    os.environ.update(dict(
        CONTAINERS=os.path.split(os.getcwd())[0],
    ))
    os.environ.update(dict(

    ))
    os.environ.update(dict(
        COMORMENT=os.path.split(os.environ['CONTAINERS'])[0],
        SIF=os.path.join(os.environ['CONTAINERS'], 'singularity'),
        REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference')
    ))
    os.environ.update(dict(
        LDPRED2_REF=os.path.join(os.environ['COMORMENT'], 'ldpred2_ref'),
        MOBA='/cluster/projects/p697/users/ofrei/2022_moba_height_traj',
        SUMSTATS='/cluster/projects/p697/projects/SUMSTATv2',
    ))
    os.environ.update(dict(
        SINGULARITY_BIND=','.join([
            f'{os.environ["REFERENCE"]}:/REF',
            f'{os.environ["LDPRED2_REF"]}:/ldpred2_ref',
            f'{os.environ["MOBA"]}:/MOBA',
            f'{os.environ["SUMSTATS"]}:/SUMSTATS',
        ])
    ))

    # Executables in containers
    SIF = os.environ['SIF']
    PWD = os.getcwd()
    os.environ.update(
        dict(
            # BASH_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif bash",  # noqa: E501
            GUNZIP_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif gunzip",  # noqa: E501
            GZIP_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif gzip",  # noqa: E501
            AWK_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif awk",  # noqa: E501
            RSCRIPT=f"singularity exec --home={PWD}:/home {SIF}/r.sif Rscript",  # noqa: E501
            PLINK=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif plink",  # noqa: E501
            PRSICE=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif PRSice_linux",  # noqa: E501
            PYTHON=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/python3.sif python",  # noqa: E501

        ))

    # load config.yaml file as dict
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    # input (shared)
    # Sumstats_file = '/SUMSTATS/STD/UKB_HEIGHT_2018_irnt.sumstats.gz'
    Sumstats_file = '/MOBA/out/run10_regenie_height_8y_rint.gz'
    Pheno_file = '/MOBA/master_file.csv'
    Phenotype = 'height_8y_rint'
    colPheno = Phenotype
    Geno_file = '/MOBA/MoBaPsychGen_v1-500kSNPs-child'
    Data_postfix = ''

    # LDpred2 specific
    fileGenoRDS = 'MoBaPsychGen_v1-500kSNPs-child.rds'

    # find suitable number of cores
    if 'SLURM_NTASKS' in os.environ:
        ncores = int(os.environ['SLURM_NTASKS'])
    else:
        ncores = int(
            subprocess.run(
                'nproc --all',
                shell=True,
                check=True,
                capture_output=True
            ).stdout.decode())
    if ncores > config['ldpred2']['cores']:
        ncores = config['ldpred2']['cores']

    # Update ldpred2 config
    config['ldpred2'].update({
        'col_stat': 'BETA',
        'col_stat_se': 'SE',
        'stat_type': 'BETA',
        # 'chr2use': list(range(1,23)),
        'cores': ncores,
        'col-pheno': colPheno,
        'file_keep_snps': None,
    })

    #######################################
    # Preprocessing
    #######################################
    # some faffing around to produce files for
    # post run model evaluation
    for Output_dir in ['PGS_MoBa_LDpred2_inf', 'PGS_MoBa_LDpred2_auto']:
        Eigenvec_file = os.path.join(Output_dir, 'master_file.eigenvec')
        Cov_file = os.path.join(Output_dir, 'master_file.cov')

        if not os.path.isdir(Output_dir):
            os.mkdir(Output_dir)

        # extract precomputed PCs from Pheno_file
        call = ' '.join(
            [os.environ['RSCRIPT'],
                os.path.join('Rscripts', 'generate_eigenvec.R'),
                '--pheno-file', Pheno_file,
                '--eigenvec-file', Eigenvec_file,
                '--pca', str(config['plink']['nPCs'])
             ]
        )
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

        # write .cov file with FID IID SEX columns
        call = ' '.join([
            os.environ['RSCRIPT'],
            os.path.join('Rscripts', 'extract_columns.R'),
            '--input-file', Pheno_file,
            '--columns', 'FID', 'IID', 'SEX',
            '--output-file', Cov_file,
            '--header', 'T',
        ])
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

    #######################################
    # LDpred2 infinitesimal model
    #######################################
    ldpred2_inf = pgs.PGS_LDpred2(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Geno_file=Geno_file,
        Output_dir='PGS_MoBa_LDpred2_inf',
        method='inf',
        fileGenoRDS=fileGenoRDS,
        **config['ldpred2']
    )
    # run
    for call in ldpred2_inf.get_str(create_backing_file=True):
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

    # post run model evaluation
    call = ldpred2_inf.get_model_evaluation_str(
        Eigenvec_file=os.path.join(Output_dir, 'master_file.eigenvec'),
        nPCs=str(config['plink']['nPCs']),
        Cov_file=os.path.join(Output_dir, 'master_file.cov'))
    print(f'\nevaluating: {call}\n')
    proc = subprocess.run(call, shell=True, check=True)
    assert proc.returncode == 0

    #######################################
    # LDpred2 automatic model
    #######################################
    ldpred2_auto = pgs.PGS_LDpred2(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Geno_file=Geno_file,
        Output_dir='PGS_MoBa_LDpred2_auto',
        method='auto',
        fileGenoRDS=fileGenoRDS,
        **config['ldpred2']
    )
    # run
    for call in ldpred2_auto.get_str(create_backing_file=True):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

    # post run model evaluation
    call = ldpred2_auto.get_model_evaluation_str(
        Eigenvec_file=os.path.join(Output_dir, 'master_file.eigenvec'),
        nPCs=str(config['plink']['nPCs']),
        Cov_file=os.path.join(Output_dir, 'master_file.cov'))
    print(f'\nevaluating: {call}\n')
    proc = subprocess.run(call, shell=True, check=True)
    assert proc.returncode == 0
