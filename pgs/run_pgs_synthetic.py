#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import yaml
from pgs import pgs


if __name__ == '__main__':
    # load config.yaml file as dict
    with open('config.yaml', 'r', encoding='utf-8') as stream:
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
    sumstats_file = '/REF/examples/ldpred2/trait1.sumstats.gz'
    pheno_file = '/REF/examples/ldpred2/simu.pheno'
    phenotype = 'trait1'
    phenotype_class = 'CONTINUOUS'
    geno_file_prefix = '/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1'
    data_postfix = ''

    # Output root directory (will be created if it does not exist)
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # LDpred2 specific
    fileGenoRDS = os.path.join(output_dir, 'g1000_eur_chr21to22_hm3rnd1.rds')

    # method specific input
    covariate_file = '/REF/examples/prsice2/EUR.cov'  # seems valid, not 100% sure.

    #######################################
    # Update method-specific configs
    #######################################
    # The purpose of this is to make parse additional keyword arguments
    # to each main method (ldpred2, prsice2, plink) on the command line.
    # Refer to the documentation of each tool for more information.

    # update plink config
    config['plink'].update({
        'score_args': [9, 1, 3, 'header'],  # SNP, A1, BETA columns in sumstats
    })

    # update prsice2 config
    config['prsice2'].update({
    })

    # update ldpred2 config:
    config['ldpred2'].update({
        'chr2use': [21, 22],
    })

    #######################################
    # Preprocessing
    #######################################
    # Create <data_prefix>.eigenval/eigenvec files using plink
    # written to output directory
    # TODO: move out
    data_prefix = os.path.split(geno_file_prefix)[-1]
    # call = ' '.join(
    #     [os.environ['PLINK'],
    #      '--bfile', geno_file_prefix,
    #      '--pca', str(config['plink']['nPCs']),
    #      '--out', os.path.join(output_dir, data_prefix)
    #      ]
    # )
    # pgs.run_call(call)

    # # file names
    # eigenvec_file = f'{os.path.join(output_dir, data_prefix)}.eigenvec'

    #######################################
    # Plink
    #######################################
    plink = pgs.PGS_Plink(
        sumstats_file=sumstats_file,
        pheno_file=pheno_file,
        phenotype=phenotype,
        phenotype_class=phenotype_class,
        geno_file_prefix=geno_file_prefix,
        output_dir=os.path.join(output_dir, 'PGS_synthetic_plink'),
        covariate_file=covariate_file,
        eigenvec_file=f'{os.path.join(output_dir, "PGS_synthetic_plink", data_prefix)}.eigenvec',
        **config['plink'],
    )

    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing', update_effect_size=False):
        if call is not None:
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
        sumstats_file=sumstats_file,
        pheno_file=pheno_file,
        phenotype=phenotype,
        phenotype_class='CONTINUOUS',
        geno_file_prefix=geno_file_prefix,
        output_dir=os.path.join(output_dir, 'PGS_synthetic_prsice2'),
        covariate_file=covariate_file,
        eigenvec_file=f'{os.path.join(output_dir, "PGS_synthetic_prsice2", data_prefix)}.eigenvec',
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
        ldpred2 = pgs.PGS_LDpred2(
            sumstats_file=sumstats_file,
            pheno_file=pheno_file,
            phenotype=phenotype,
            phenotype_class='CONTINUOUS',
            geno_file_prefix=geno_file_prefix,
            output_dir=os.path.join(
                output_dir, f'PGS_synthetic_LDpred2_{method}'),
            method=method,
            fileGenoRDS=fileGenoRDS,
            **config['ldpred2']
        )
        # run
        for call in ldpred2.get_str(create_backing_file=True):
            pgs.run_call(call)

        # create .eigenvec and .cov files in ``output_dir`` 
        # for post run model evaluation:
        call = ldpred2.generate_eigenvec_eigenval_files(nPCs=6)
        pgs.run_call(call)

        # post run model evaluation
        call = ldpred2.get_model_evaluation_str(
            eigenvec_file=f'{os.path.join(ldpred2.output_dir, data_prefix)}.eigenvec',
            nPCs=6,
            covariate_file=covariate_file)
        pgs.run_call(call)
