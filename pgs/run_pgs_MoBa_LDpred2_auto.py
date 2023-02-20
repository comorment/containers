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
    Sumstats_file = '/MOBA/out/run10_regenie_height_8y_rint.gz'
    Pheno_file = '/MOBA/master_file.csv'
    Phenotype = 'height_8y_rint'
    Geno_file = '/MOBA/MoBaPsychGen_v1-500kSNPs-child'
    Data_postfix = ''

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
        'auto': os.path.join('results', 'PGS_MoBa_LDpred2_auto')
    }

    # Update ldpred2 config
    config['ldpred2'].update({
        'cores': ncores,
        'col-pheno': Phenotype,
        'file_keep_snps': None,
    })

    #######################################
    # Preprocessing
    #######################################
    # some faffing around to produce files for
    # post run model evaluation
    for Output_dir in Output_dirs.values():
        Eigenvec_file = os.path.join(Output_dir, 'master_file.eigenvec')
        Cov_file = os.path.join(Output_dir, 'master_file.cov')

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

    ###########################################
    # run LDpred2 infinitesimal and auto model
    ###########################################

    # iterate over methods (inf or auto)
    for method, Output_dir in Output_dirs.items():
        # instantiate
        ldpred2 = pgs.PGS_LDpred2(
            Sumstats_file=Sumstats_file,
            Pheno_file=Pheno_file,
            Phenotype=Phenotype,
            Geno_file=Geno_file,
            Output_dir=Output_dir,
            method=method,
            fileGenoRDS=fileGenoRDS,
            **config['ldpred2']
        )
        # run
        for call in ldpred2.get_str(create_backing_file=True):
            pgs.run_call(call)

        # post run model evaluation
        call = ldpred2.get_model_evaluation_str(
            Eigenvec_file=os.path.join(Output_dir, 'master_file.eigenvec'),
            nPCs=str(config['plink']['nPCs']),
            Cov_file=os.path.join(Output_dir, 'master_file.cov'))
        pgs.run_call(call)
