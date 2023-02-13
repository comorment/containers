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
    Sumstats_file = '/REF/examples/ldpred2/trait1.sumstats.gz'
    Pheno_file = '/REF/examples/ldpred2/simu.pheno'
    Phenotype = 'trait1'
    Phenotype_class = 'CONTINUOUS'
    Geno_file = '/REF/examples/ldpred2/g1000_eur_chr21to22_hm3rnd1'
    Data_postfix = ''

    # Output root directory (will be created if it does not exist)
    Output_dir = 'output'
    os.makedirs(Output_dir, exist_ok=True)

    # LDpred2 specific
    fileGenoRDS = os.path.join(Output_dir, 'g1000_eur_chr21to22_hm3rnd1.rds')

    # method specific input
    Cov_file = '/REF/examples/prsice2/EUR.cov'  # seems valid, not 100% sure.

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
        'col-pheno': Phenotype,
        'chr2use': [21, 22],
    })

    #######################################
    # Preprocessing
    #######################################
    # Create <Data_prefix>.eigenval/eigenvec files using plink
    # written to output directory
    # TODO: move out
    Data_prefix = os.path.split(Geno_file)[-1]
    call = ' '.join(
        [os.environ['PLINK'],
         '--bfile', Geno_file,
         '--pca', str(config['plink']['nPCs']),
         '--out', os.path.join(Output_dir, Data_prefix)
         ]
    )
    pgs.run_call(call)

    # file names
    # Eigenval_file = f'{Data_prefix}.eigenval'
    Eigenvec_file = f'{os.path.join(Output_dir, Data_prefix)}.eigenvec'

    #######################################
    # Plink
    #######################################
    plink = pgs.PGS_Plink(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Phenotype_class=Phenotype_class,
        Geno_file=Geno_file,
        Output_dir=os.path.join(Output_dir, 'PGS_synthetic_plink'),
        Cov_file=Cov_file,
        Eigenvec_file=Eigenvec_file,
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
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file,
        Phenotype=Phenotype,
        Phenotype_class='CONTINUOUS',
        Geno_file=Geno_file,
        Output_dir=os.path.join(Output_dir, 'PGS_synthetic_prsice2'),
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
        ldpred2 = pgs.PGS_LDpred2(
            Sumstats_file=Sumstats_file,
            Pheno_file=Pheno_file,
            Phenotype=Phenotype,
            Phenotype_class='CONTINUOUS',
            Geno_file=Geno_file,
            Output_dir=os.path.join(
                Output_dir, f'PGS_synthetic_LDpred2_{method}'),
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
            nPCs=6,
            Cov_file=Cov_file)
        pgs.run_call(call)
