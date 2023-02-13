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
    # Sumstats_file = '/SUMSTATS/STD/UKB_HEIGHT_2018_irnt.sumstats.gz'
    Sumstats_file = '/MOBA/out/run10_regenie_height_8y_rint.gz'
    Pheno_file = '/MOBA/master_file.csv'
    Phenotype = 'height_8y_rint'
    Geno_file = '/MOBA/MoBaPsychGen_v1-500kSNPs-child'
    Data_postfix = ''

    # output dir
    Output_dir = os.path.join('output', 'PGS_MoBa_prsice2')

    # method specific input
    Eigenvec_file = os.path.join(Output_dir, 'master_file.eigenvec')
    Cov_file = os.path.join(Output_dir, 'master_file.cov')

    # for "PRSice --extract" arg (throws an error othervise):
    Valid_file = os.path.join(Output_dir,
                              os.path.split(Geno_file)[1]) + '.valid'

    # update prsice2 config
    config['prsice2'].update({
        'pheno-col': Phenotype,  # redundant with the preprocessing
        'pvalue': 'P',  # 'PVAL'   # for UKB_HEIGHT sumstats
        # 'extract': Valid_file,  # for UKB_HEIGHT sumstats
        # 'ignore-fid': ''
    })

    #######################################
    # Preprocessing
    #######################################
    # some faffing around to produce files that
    # PRSice will accept
    os.makedirs(Output_dir, exist_ok=True)

    # extract precomputed PCs from Pheno_file
    call = ' '.join([
        '$RSCRIPT',
        os.path.join('Rscripts', 'generate_eigenvec.R'),
        '--pheno-file', Pheno_file,
        '--eigenvec-file', Eigenvec_file,
        '--pca', str(config['plink']['nPCs'])
    ])
    pgs.run_call(call)

    # write .cov file with FID IID SEX columns
    call = ' '.join([
        '$RSCRIPT',
        os.path.join('Rscripts', 'extract_columns.R'),
        '--input-file', Pheno_file,
        '--columns', 'FID', 'IID', 'SEX',
        '--output-file', Cov_file,
        '--header', 'T',
    ])
    pgs.run_call(call)

    # extract pheno file with FID, IID, <phenotype> columns
    # as PRSice.R script assumes FID and IID as first two cols,
    # and aint f'n smart enough to work around this.
    Pheno_file_prsice = os.path.join(Output_dir, f'master_file.{Phenotype}')
    call = ' '.join([
        '$RSCRIPT',
        os.path.join('Rscripts', 'extract_columns.R'),
        '--input-file', Pheno_file,
        '--columns', 'FID', 'IID', Phenotype,
        '--output-file', Pheno_file_prsice,
        '--header', 'T',
        '--na', 'NA',
        '--sep', '" "',
    ])
    pgs.run_call(call)

    #######################################
    # PRSice-2
    #######################################
    prsice2 = pgs.PGS_PRSice2(
        Sumstats_file=Sumstats_file,
        Pheno_file=Pheno_file_prsice,
        Phenotype=Phenotype,
        Geno_file=Geno_file,
        Output_dir=Output_dir,
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
