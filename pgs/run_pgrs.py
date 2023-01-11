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
        REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference'),
        LDPRED2_REF=os.path.join(os.environ['COMORMENT'], 'ldpred2_ref')
    ))
    os.environ.update(dict(
        
    ))
    os.environ.update(dict(
        SINGULARITY_BIND=f'{os.environ["REFERENCE"]}:/REF,{os.environ["LDPRED2_REF"]}:/ldpred2_ref'
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
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    # input (shared)
    Sumstats_file = '/REF/examples/prsice2/Height.gwas.txt.gz'
    Pheno_file = '/REF/examples/prsice2/EUR.height'
    # Input_dir='/REF/examples/prsice2',
    Data_prefix = 'EUR'
    Data_postfix = '.QC'

    # method specific input
    # Plink, PRSice2
    Cov_file = '/REF/examples/prsice2/EUR.cov'
    Eigenvec_file = '/REF/examples/prsice2/EUR.eigenvec'
    
    # LDpred2
    fileGeno = 'QC_data/EUR.QC.bed'
    fileGenoRDS = 'EUR.rds'
    
    # update ldpred2 config:
    # find suitable number of cores
    ncores = int(
        subprocess.run(
            'nproc --all', 
            shell=True, 
            check=True, 
            capture_output=True
            ).stdout.decode())
    if ncores > config['ldpred2']['cores']:
        ncores = config['ldpred2']['cores']
    config['ldpred2'].update({
        # key: value
        'cores': ncores
    })


    #######################################
    # Standard GWAS QC.
    # Note: This will perform the QC steps from
    # https://choishingwan.github.io/PRS-Tutorial/
    # but is probably something you should apply with caution.
    #######################################

    # output dir for QC'd data.
    QC_data = 'QC_data'

    # QC params
    Phenotype = 'Height'
    
    # perform some basic QC steps
    qc = pgrs.Standard_GWAS_QC(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Input_dir='/REF/examples/prsice2',
        Data_prefix=Data_prefix,
        Data_postfix=Data_postfix,
        Output_dir=QC_data,
        Phenotype=Phenotype,
    )
    for call in qc.get_str():
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0
    

    #######################################
    # Plink
    #######################################
    plink = pgrs.PGS_Plink(
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file=Pheno_file,
        Input_dir=QC_data,
        Data_prefix=Data_prefix + Data_postfix,
        Output_dir='PGS_plink',
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
        Phenotype=Phenotype,
        **config['plink'],
    )

    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing', update_effect_size=True):
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


    #######################################
    # PRSice-2
    #######################################
    prsice2 = pgrs.PGS_PRSice2(
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file=Pheno_file,
        Input_dir=QC_data,
        Data_prefix=Data_prefix + Data_postfix,
        Output_dir='PGS_prsice2',
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
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file=Pheno_file,
        Input_dir=None,
        Data_prefix=Data_prefix + Data_postfix,
        Output_dir='PGS_LDpred2_inf',
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
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file=Pheno_file,
        Input_dir=None,
        Data_prefix=Data_prefix + Data_postfix,
        Output_dir='PGS_LDpred2_auto',
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
