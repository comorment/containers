#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import yaml
from pgs import pgs


if __name__ == '__main__':
    # load config.yaml file as dict
    with open("config.yaml", 'r', encoding='utf-8') as stream:
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
    sumstats_file = '/REF/examples/prsice2/Height.gwas.txt.gz'
    pheno_file = '/REF/examples/prsice2/EUR.height'
    phenotype = 'Height'
    phenotype_class = 'CONTINUOUS'
    geno_file_prefix = '/REF/examples/prsice2/EUR'
    data_postfix = '.QC'

    # Output root directory (will be created if it does not exist)
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # method specific input
    # Plink, PRSice2, LDpred2
    covariate_file = '/REF/examples/prsice2/EUR.cov'
    eigenvec_file = '/REF/examples/prsice2/EUR.eigenvec'

    # LDpred2
    # put in working directory as both LDpred2 methods use it
    file_geno_rds = os.path.join(output_dir, 'EUR.rds')

    #######################################
    # Update method-specific configs
    #######################################
    # The purpose of this is to make parse additional keyword arguments
    # to each main method (ldpred2, prsice2, plink) on the command line.
    # Refer to the documentation of each tool for more information.

    # update plink config
    config['plink'].update({
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
    QC_data = os.path.join(output_dir, 'QC_data')

    # perform some basic QC steps
    qc = pgs.Standard_GWAS_QC(
        sumstats_file=sumstats_file,
        pheno_file=pheno_file,
        phenotype=phenotype,
        geno_file_prefix=geno_file_prefix,
        data_postfix=data_postfix,
        output_dir=QC_data,
    )
    for call in qc.get_str():
        pgs.run_call(call)

    # "Cleaned" geno_file_prefix from QC step
    geno_file_post_qc = os.path.join(
        qc.output_dir,
        qc.data_prefix + qc.data_postfix)
    # "Cleaned" summary statistics
    Sumstats_file_post_QC = os.path.join(QC_data, 'Height.QC.gz')

    #######################################
    # Plink
    #######################################
    plink = pgs.PGS_Plink(
        sumstats_file=Sumstats_file_post_QC,
        pheno_file=pheno_file,
        phenotype=phenotype,
        phenotype_class=phenotype_class,
        geno_file_prefix=geno_file_post_qc,
        output_dir=os.path.join(output_dir, 'PGS_plink'),
        covariate_file=covariate_file,
        eigenvec_file=eigenvec_file,
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
        sumstats_file=Sumstats_file_post_QC,
        pheno_file=pheno_file,
        phenotype=phenotype,
        phenotype_class=phenotype_class,
        geno_file_prefix=geno_file_post_qc,
        output_dir=os.path.join(output_dir, 'PGS_prsice2'),
        covariate_file=covariate_file,
        eigenvec_file=eigenvec_file,
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
            sumstats_file=Sumstats_file_post_QC,
            pheno_file=pheno_file,
            phenotype=phenotype,
            phenotype_class=phenotype_class,
            geno_file_prefix=geno_file_post_qc,
            output_dir=os.path.join(output_dir, f'PGS_LDpred2_{method}'),
            method=method,
            file_geno_rds=file_geno_rds,
            **config['ldpred2']
        )
        # run
        for call in ldpred2.get_str(create_backing_file=True):
            pgs.run_call(call)

        # post run model evaluation
        call = ldpred2.get_model_evaluation_str(
            eigenvec_file=eigenvec_file,
            nPCs=config['ldpred2']['nPCs'],
            covariate_file=covariate_file)
        pgs.run_call(call)
