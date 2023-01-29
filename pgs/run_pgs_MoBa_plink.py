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
        MOBAv1='/cluster/projects/p697/genotype/MoBaPsychGen_v1',
        SUMSTATS='/cluster/projects/p697/projects/SUMSTATv2',
    ))
    os.environ.update(dict(
        SINGULARITY_BIND=','.join([
            f'{os.environ["REFERENCE"]}:/REF',
            f'{os.environ["LDPRED2_REF"]}:/ldpred2_ref',
            f'{os.environ["MOBA"]}:/MOBA',
            f'{os.environ["SUMSTATS"]}:/SUMSTATS',
            f'{os.environ["MOBAv1"]}:/MOBAv1'
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
            PLINK=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif plink --debug",  # noqa: E501
            PRSICE=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif PRSice_linux",  # noqa: E501
            PYTHON=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/python3.sif python",  # noqa: E501

        ))

    # load config.yaml file as dict
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

    # input (shared)
    # Sumstats_file = '/SUMSTATS/STD/UKB_HEIGHT_2018_irnt.sumstats.gz'
    Sumstats_file = '/MOBA/out/run10_regenie_height_8y_rint.gz'
    Pheno_file = '/MOBA/master_file.csv'
    Phenotype = 'height_8y_rint'
    Geno_file = '/MOBA/MoBaPsychGen_v1-500kSNPs-child'
    Data_postfix = ''

    # output dir
    Output_dir = 'PGS_MoBa_plink'

    # method specific input
    # Eigenvec_file = '/MOBAv1/MoBaPsychGen_v1-ec-eur-batch-basic-qc-cov.txt'
    Eigenvec_file = os.path.join(Output_dir, 'master_file.eigenvec')
    Cov_file = os.path.join(Output_dir, 'master_file.cov')

    # update plink config
    config['plink'].update({
        'clump_p1': 1,
        'clump_r2': 0.1,
        'clump_kb': 250,
        'range_list': [0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
        'strat_indep_pairwise': [250, 50, 0.25],
        'nPCs': 6,
        'score_args': [1, 4, 9, 'header'], # SNP, A1, BETA
    })

    #######################################
    # Preprocessing
    #######################################
    # some faffing around to produce files that 
    # Plink will accept
    if not os.path.isdir(Output_dir):
        os.mkdir(Output_dir)

    # extract precomputed PCs from Pheno_file
    call = ' '.join(
        [os.environ['RSCRIPT'],
         'generate_eigenvec.R',
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
        'extract_columns.R',
        '--input-file', Pheno_file,
        '--columns', 'FID', 'IID', 'SEX',
        '--output-file', Cov_file,
        '--header', 'T',
    ])
    print(f'evaluating: {call}')
    proc = subprocess.run(call, shell=True, check=True)
    assert proc.returncode == 0

    
    # extract pheno file with FID, IID, <phenotype> columns
    # as PRSice.R script assumes FID and IID as first two cols, 
    # and aint f'n smart enough to work around this.
    Pheno_file_plink = os.path.join(Output_dir, f'master_file.{Phenotype}')
    call  = ' '.join([
        os.environ['RSCRIPT'],
        'extract_columns.R',
        '--input-file', Pheno_file,
        '--columns', 'FID', 'IID', Phenotype,
        '--output-file', Pheno_file_plink,
        '--header', 'T',
        '--na', 'NA',
        '--sep', '" "',
    ])
    print(f'evaluating: {call}')
    proc = subprocess.run(call, shell=True, check=True)
    assert proc.returncode == 0
    

    #######################################
    # Plink
    #######################################
    plink = pgs.PGS_Plink(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file_plink,
        Phenotype=Phenotype,
        Geno_file=Geno_file,
        Output_dir=Output_dir,
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
        **config['plink'],
    )

    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing', update_effect_size=False):
        if call is not None:
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
    
