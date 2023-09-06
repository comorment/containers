#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import yaml
from pgs import pgs


if __name__ == '__main__':
    # load config_p697.yaml file as dict
    with open("config_p697.yaml", 'r') as stream:
        config = yaml.safe_load(stream)

    #######################################
    # set up environment variables
    #######################################
    # the config may contain some default paths to container files
    # and reference data, but we may want to override these for clarity
    pgs.set_env(config)

    # input (shared)
    # sumstats_file = '/SUMSTATS/STD/UKB_HEIGHT_2018_irnt.sumstats.gz'
    sumstats_file = '/MOBA/out/run10_regenie_height_8y_rint.gz'
    pheno_file = '/MOBA/master_file.csv'
    phenotype = 'height_8y_rint'
    geno_file_prefix = '/MOBA/MoBaPsychGen_v1-500kSNPs-child'
    data_postfix = ''

    # output dir
    output_dir = os.path.join('output', 'PGS_MoBa_plink')

    # method specific input
    eigenvec_file = os.path.join(output_dir, 'master_file.eigenvec')
    covariate_file = os.path.join(output_dir, 'master_file.cov')

    # update plink config
    config['plink'].update({
        'clump_p1': 1,
        'clump_r2': 0.1,
        'clump_kb': 250,
        'range_list': [0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 1],
        'strat_indep_pairwise': [250, 50, 0.25],
        'nPCs': 6,
        'score_args': [1, 4, 9, 'header'],  # SNP, A1, BETA
    })

    #######################################
    # Preprocessing
    #######################################
    # some faffing around to produce files that
    # Plink will accept
    os.makedirs(output_dir, exist_ok=True)

    # extract precomputed PCs from pheno_file
    call = ' '.join([
        '$RSCRIPT',
        os.path.join('Rscripts', 'generate_eigenvec.R'),
        '--pheno-file', pheno_file,
        '--eigenvec-file', eigenvec_file,
        '--pca', str(config['plink']['nPCs'])
    ])
    pgs.run_call(call)

    # write .cov file with FID IID SEX columns
    call = ' '.join([
        '$RSCRIPT',
        os.path.join('Rscripts', 'extract_columns.R'),
        '--input-file', pheno_file,
        '--columns', 'FID', 'IID', 'SEX',
        '--output-file', covariate_file,
        '--header', 'T',
    ])
    pgs.run_call(call)

    # extract pheno file with FID, IID, <phenotype> columns
    # as PRSice.R script assumes FID and IID as first two cols,
    # and aint f'n smart enough to work around this.
    Pheno_file_plink = os.path.join(output_dir, f'master_file.{phenotype}')
    call = ' '.join([
        '$RSCRIPT',
        os.path.join('Rscripts', 'extract_columns.R'),
        '--input-file', pheno_file,
        '--columns', 'FID', 'IID', phenotype,
        '--output-file', Pheno_file_plink,
        '--header', 'T',
        '--na', 'NA',
        '--sep', '" "',
    ])
    pgs.run_call(call)

    #######################################
    # Plink
    #######################################
    plink = pgs.PGS_Plink(
        sumstats_file=sumstats_file,
        pheno_file=Pheno_file_plink,
        phenotype=phenotype,
        geno_file_prefix=geno_file_prefix,
        output_dir=output_dir,
        covariate_file=covariate_file,
        eigenvec_file=eigenvec_file,
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
