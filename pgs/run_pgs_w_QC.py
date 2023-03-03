#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import yaml
from pgs import pgs


if __name__ == '__main__':
    # load config.yaml file as dict
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

    #######################################
    # set up environment variables
    #######################################
    # the config may contain some default paths to container files
    # and reference data, but we may want to override these for clarity
    pgs.set_env(config)

    #######################################
    # Setup inputs and outputs
    #######################################
    # input (shared)
    Sumstats_file = '/REF/examples/prsice2/Height.gwas.txt.gz'
    Pheno_file = '/REF/examples/prsice2/EUR.height'
    Phenotype = 'Height'
    Phenotype_class = 'CONTINUOUS'
    Geno_file = '/REF/examples/prsice2/EUR'
    Data_postfix = '.QC'

    # Output root directory (will be created if it does not exist)
    Output_dir = 'output'
    os.makedirs(Output_dir, exist_ok=True)

    # method specific input
    # Plink, PRSice2, LDpred2
    Cov_file = '/REF/examples/prsice2/EUR.cov'
    Eigenvec_file = '/REF/examples/prsice2/EUR.eigenvec'

    # LDpred2
    fileGenoRDS = os.path.join(Output_dir, 'EUR.rds')  # put in working directory as both LDpred2 methods use it

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
    })

    #######################################
    # Standard GWAS QC.
    # Note: This will perform the QC steps from
    # https://choishingwan.github.io/PRS-Tutorial/
    # but is probably something you should apply with caution.
    #######################################

    # output dir for QC'd data.
    QC_data = os.path.join(Output_dir, 'QC_data')

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
        Phenotype_class=Phenotype_class,
        Geno_file=Geno_file_post_QC,
        Output_dir=os.path.join(Output_dir, 'PGS_plink'),
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
        Phenotype_class=Phenotype_class,
        Geno_file=Geno_file_post_QC,
        Output_dir=os.path.join(Output_dir, 'PGS_prsice2'),
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
            Phenotype_class=Phenotype_class,
            Geno_file=Geno_file_post_QC,
            Output_dir=os.path.join(Output_dir, f'PGS_LDpred2_{method}'),
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
