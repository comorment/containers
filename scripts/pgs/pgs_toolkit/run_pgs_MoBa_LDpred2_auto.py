#!/usr/bin/env python3
# run script for PGS calling the class definitions in pgs/pgs.py directly

# package imports
import os
import subprocess
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
    sumstats_file = '/MOBA/out/run10_regenie_height_8y_rint.gz'
    pheno_file = '/MOBA/master_file.csv'
    phenotype = 'height_8y_rint'
    geno_file_prefix = '/MOBA/MoBaPsychGen_v1-500kSNPs-child'
    data_postfix = ''

    # LDpred2 specific
    fileGenoRDS = 'MoBaPsychGen_v1-500kSNPs-child.rds'

    # find suitable number of cores
    if 'SLURM_NTASKS' in os.environ:
        ncores = int(os.environ['SLURM_NTASKS'])
    else:
        ncores = int(
            subprocess.run(
                'nproc --all',
                shell=True,
                check=True,
                capture_output=True
            ).stdout.decode())
    if ncores > config['ldpred2']['cores']:
        ncores = config['ldpred2']['cores']

    # output directories
    Output_dirs = {
        'auto': os.path.join('output', 'PGS_MoBa_LDpred2_auto')
    }

    # Update ldpred2 config
    config['ldpred2'].update({
        'cores': ncores,
        'file_keep_snps': None,
    })

    #######################################
    # Preprocessing
    #######################################
    # some faffing around to produce files for
    # post run model evaluation
    for output_dir in Output_dirs.values():
        eigenvec_file = os.path.join(output_dir, 'master_file.eigenvec')
        covariate_file = os.path.join(output_dir, 'master_file.cov')

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

    ###########################################
    # run LDpred2 infinitesimal and auto model
    ###########################################

    # iterate over methods (inf or auto)
    for method, output_dir in Output_dirs.items():
        # instantiate
        ldpred2 = pgs.PGS_LDpred2(
            sumstats_file=sumstats_file,
            pheno_file=pheno_file,
            phenotype=phenotype,
            geno_file_prefix=geno_file_prefix,
            output_dir=output_dir,
            method=method,
            fileGenoRDS=os.path.join(output_dir, fileGenoRDS),
            **config['ldpred2']
        )
        # run
        for call in ldpred2.get_str(create_backing_file=True):
            pgs.run_call(call)

        # post run model evaluation
        call = ldpred2.get_model_evaluation_str(
            eigenvec_file=os.path.join(output_dir, 'master_file.eigenvec'),
            nPCs=str(config['plink']['nPCs']),
            covariate_file=os.path.join(output_dir, 'master_file.cov'))
        pgs.run_call(call)
