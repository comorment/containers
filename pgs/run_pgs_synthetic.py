#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgrs.py directly

# package imports
import os
import pgrs
import subprocess
import yaml


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
    ))
    os.environ.update(dict(
        SINGULARITY_BIND=f'{os.environ["REFERENCE"]}:/REF,{os.environ["LDPRED2_REF"]}:/ldpred2_ref'  # noqa: E501
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
            PLINK=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif plink",  # noqa: E501
            PRSICE=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif PRSice_linux",  # noqa: E501
            PYTHON=f"singularity exec --home={PWD}:/home {SIF}/python3.sif python",  # noqa: E501

        ))

    # load config.yaml file as dict
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

    # input (shared)
    Sumstats_file = '/REF/examples/ldpred2/trait1.sumstats.gz'
    Pheno_file = '/REF/examples/ldpred2/simu.pheno'
    Input_dir= '/REF/examples/ldpred2'
    Data_prefix = 'g1000_eur_chr21to22_hm3rnd1'
    Data_postfix = ''

    # LDpred2 specific
    fileGeno = '/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1.bed'
    fileGenoRDS = 'g1000_eur_chr21to22_hm3rnd1.rds'

    # method specific input
    Cov_file = '/REF/examples/prsice2/EUR.cov'  # seems valid, not 100% sure.
    

    # update ldpred2 config:
    config['ldpred2'].update({
        'col_stat': 'BETA', 
        'col_stat_se': 'SE', 
        'stat_type': 'BETA',
        'col-pheno': 'trait1', 
        'chr2use': [21, 22]
    })

    # update prsice2 config
    config['prsice2'].update({
        'stat': 'BETA',
        'beta': ''
    })
    del config['prsice2']['or']

    # update plink config
    config['plink'].update({
        'score_args': [9, 1, 3, 'header']  # SNP, A1, BETA
    })

    '''
    #######################################
    # Preprocessing
    #######################################
    Create <Data_prefix>.eigenval/eigenvec files using plink
    written to this directory
    '''
    call = ' '.join(
        [os.environ['PLINK'],
         '--bfile', os.path.join(Input_dir, Data_prefix),
         '--pca', str(config['plink']['nPCs']),
         '--out', Data_prefix
        ]
    )
    
    print(f'evaluating: {call}')
    proc = subprocess.run(call, shell=True)
    assert proc.returncode == 0

    # file names
    Eigenval_file = f'{Data_prefix}.eigenval'
    Eigenvec_file = f'{Data_prefix}.eigenvec'


    #######################################
    # Plink
    #######################################
    plink = pgrs.PGS_Plink(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Input_dir=Input_dir,
        Data_prefix=Data_prefix,
        Data_postfix=Data_postfix,
        Output_dir='PGS_synthetic_plink',
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
        Phenotype='trait1',
        **config['plink'],
    )

    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing', update_effect_size=False):
        if call is not None:
            print(f'evaluating: {call}')
            proc = subprocess.run(call, shell=True)
            assert proc.returncode == 0

    
    # run basic plink PGS
    '''
    for call in plink.get_str(mode='basic'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0
    
    '''
    # run plink PGS with population stratification
    for call in plink.get_str(mode='stratification'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0
    
    # raise Exception

    #######################################
    # PRSice-2
    #######################################
    prsice2 = pgrs.PGS_PRSice2(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Input_dir=Input_dir,
        Data_prefix=Data_prefix,
        Data_postfix=Data_postfix,
        Output_dir='PGS_synthetic_prsice2',
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
        **config['prsice2'],
    )

    # run commands
    for call in prsice2.get_str():
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0
    

    #######################################
    # LDpred2 infinitesimal model
    #######################################
    ldpred2_inf = pgrs.PGS_LDpred2(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Input_dir=None,
        Data_prefix=Data_prefix,
        Data_postfix=Data_postfix,
        Output_dir='PGS_synthetic_LDpred2_inf',
        method='inf',
        fileGeno=fileGeno,
        fileGenoRDS=fileGenoRDS,
        **config['ldpred2']
    )
    # run
    for call in ldpred2_inf.get_str(create_backing_file=True):
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0


    #######################################
    # LDpred2 automatic model
    #######################################
    ldpred2_auto = pgrs.PGS_LDpred2(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Input_dir=Input_dir,
        Data_prefix=Data_prefix,
        Data_postfix=Data_postfix,
        Output_dir='PGS_synthetic_LDpred2_auto',
        method='auto',
        fileGeno=fileGeno,
        fileGenoRDS=fileGenoRDS,
        **config['ldpred2']
    )
    # run
    for call in ldpred2_auto.get_str(create_backing_file=True):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0