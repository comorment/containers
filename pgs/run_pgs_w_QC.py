#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import yaml
from pgs import pgs


if __name__ == '__main__':
    # enviroment variables for test runs
    os.environ.update(dict(
        CONTAINERS=os.path.split(os.getcwd())[0],
    ))
    os.environ.update(dict(
        COMORMENT=os.path.split(os.environ['CONTAINERS'])[0],
        SIF=os.path.join(os.environ['CONTAINERS'], 'singularity'),
        REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference'),
    ))
    os.environ.update(dict(
        LDPRED2_REF=os.path.join(os.environ['COMORMENT'], 'ldpred2_ref')
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
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    # input (shared)
    Sumstats_file = '/REF/examples/prsice2/Height.gwas.txt.gz'
    Pheno_file = '/REF/examples/prsice2/EUR.height'
    Phenotype = 'Height'
    Geno_file = '/REF/examples/prsice2/EUR'
    Data_postfix = '.QC'

    # method specific input
    # Plink, PRSice2, LDpred2
    Cov_file = '/REF/examples/prsice2/EUR.cov'
    Eigenvec_file = '/REF/examples/prsice2/EUR.eigenvec'

    # LDpred2
    fileGenoRDS = 'EUR.rds'  # put in working directory as both LDpred2 methods use it

    #######################################
    # Update method-specific configs
    #######################################
    # The purpose of this is to make parse additional keyword arguments
    # to each main method (ldpred2, prsice2, plink) on the command line.
    # Refer to the documentation of each tool for more information.

    # update plink config
    config['plink'].update({
        'score_args': [3, 4, 12, 'header'],  # SNP, A1, OR columns in sumstats
    })

    # update prsice2 config
    config['prsice2'].update({
        'or': '',  # use OR as effect size
    })

    # update ldpred2 config:
    config['ldpred2'].update({
        'col-stat': 'OR',  # use OR as effect size
        'stat-type': 'OR',
        'col-stat-se': 'SE',
        'col-pheno': Phenotype,
        # 'chr2use': [21, 22],
    })

    #######################################
    # Standard GWAS QC.
    # Note: This will perform the QC steps from
    # https://choishingwan.github.io/PRS-Tutorial/
    # but is probably something you should apply with caution.
    #######################################

    # output dir for QC'd data.
    QC_data = os.path.join('results', 'QC_data')

    # perform some basic QC steps
    qc = pgs.Standard_GWAS_QC(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Geno_file=Geno_file,
        Data_postfix=Data_postfix,
        Output_dir=QC_data,
    )
    for call in qc.get_str():
        pgs.run_call(call)

    # "Cleaned" Geno_file from QC step
    Geno_file_post_QC = os.path.join(
        qc.Output_dir,
        qc.Data_prefix + qc.Data_postfix)
    # "Cleaned" summary statistics
    Sumstats_file_post_QC = os.path.join(QC_data, 'Height.QC.gz')

    #######################################
    # Plink
    #######################################
    plink = pgs.PGS_Plink(
        Sumstats_file=Sumstats_file_post_QC,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Geno_file=Geno_file_post_QC,
        Output_dir=os.path.join('results', 'PGS_plink'),
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
        **config['plink'],
    )

    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing', update_effect_size=True):
        pgs.run_call(call)

    # run basic plink PGS
    for call in plink.get_str(mode='basic'):
        pgs.run_call(call)

    # run plink PGS with population stratification
    for call in plink.get_str(mode='stratification'):
        pgs.run_call(call)

    # post run model evaluation
    call = plink.get_model_evaluation_str()
    pgs.run_call(call)

    #######################################
    # PRSice-2
    #######################################
    prsice2 = pgs.PGS_PRSice2(
        Sumstats_file=Sumstats_file_post_QC,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Geno_file=Geno_file_post_QC,
        Output_dir=os.path.join('results', 'PGS_prsice2'),
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
        **config['prsice2'],
    )

    # run commands
    for call in prsice2.get_str():
        pgs.run_call(call)

    # post run model evaluation
    call = prsice2.get_model_evaluation_str()
    pgs.run_call(call)

    ############################################
    # LDpred2 infinitesimal and automatic models
    ############################################
    for method in ['inf', 'auto']:
        # instantiate
        ldpred2 = pgs.PGS_LDpred2(
            Sumstats_file=Sumstats_file_post_QC,
            Pheno_file=Pheno_file,
            Phenotype=Phenotype,
            Geno_file=Geno_file_post_QC,
            Output_dir=os.path.join('results', f'PGS_LDpred2_{method}'),
            method=method,
            fileGenoRDS=fileGenoRDS,
            **config['ldpred2']
        )
        # run
        for call in ldpred2.get_str(create_backing_file=True):
            pgs.run_call(call)

        # post run model evaluation
        call = ldpred2.get_model_evaluation_str(
            Eigenvec_file=Eigenvec_file,
            nPCs=config['plink']['nPCs'],
            Cov_file=Cov_file)
        pgs.run_call(call)
