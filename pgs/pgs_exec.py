#!/usr/bin/env python3
# run script wrapping the class definitions in pgs/pgs.py as a command
# line tool

# package imports
import os
import sys
import datetime
import argparse
import yaml
from pgs import pgs


# list of method options
method_choices = ['plink', 'prsice2', 'ldpred2-inf', 'ldpred2-auto']

# list of runtype options
runtype_choices = ['sh', 'slurm', 'subprocess']

# shared
parser = argparse.ArgumentParser(
    prog='PGS',
    description="A pipeline for PGS analysis")

# first argument for method
parser.add_argument(
    "--method", type=str,
    help="Method for PGS",
    default='prsice2',
    choices=method_choices,
    action='store',
)
# create subparsers object
subparsers = parser.add_subparsers(dest='method')
subparsers.required = True


# method specific parsers
# method plink:
parser_plink = subparsers.add_parser('plink')
parser_plink.add_argument(
    "--Cov_file", type=str,
    help="covariance file (for method plink)",
    default="/REF/examples/prsice2/EUR.cov"
)
parser_plink.add_argument(
    "--Eigenvec-file", type=str,
    help="eigenvec file (for method plink)",
    default="/REF/examples/prsice2/EUR.eigenvec"
)
# method prsice2:
parser_prsice2 = subparsers.add_parser('prsice2')
parser_prsice2.add_argument(
    "--Cov_file", type=str,
    help="covariance file (for method prsice2)",
    default="/REF/examples/prsice2/EUR.cov"
)
parser_prsice2.add_argument(
    "--Eigenvec-file", type=str,
    help="eigenvec file (for method prsice2)",
    default="/REF/examples/prsice2/EUR.eigenvec"
)
# method ldpred2-inf:
parser_ldpred2_inf = subparsers.add_parser('ldpred2-inf')
# parser_ldpred2_inf.add_argument(
#     "--file_keep_snps", type=str,
#     help="File with RSIDs of SNPs to keep (for method ldpred2-inf)",
#     default="/REF/hapmap3/w_hm3.justrs"
# )
parser_ldpred2_inf.add_argument(
    "--Cov_file", type=str,
    help="covariance file (for model evaluation)",
    default="/REF/examples/prsice2/EUR.cov"
)
parser_ldpred2_inf.add_argument(
    "--Eigenvec-file", type=str,
    help="eigenvec file (for model evaluation)",
    default="/REF/examples/prsice2/EUR.eigenvec"
)

# method ldpred2-auto:
parser_ldpred2_auto = subparsers.add_parser('ldpred2-auto')
# parser_ldpred2_auto.add_argument(
#     "--file_keep_snps", type=str,
#     help="File with RSIDs of SNPs to keep (for method ldpred2-auto)",
#     default="/REF/hapmap3/w_hm3.justrs"
# )
parser_ldpred2_auto.add_argument(
    "--Cov_file", type=str,
    help="covariance file (for model evaluation)",
    default="/REF/examples/prsice2/EUR.cov"
)
parser_ldpred2_auto.add_argument(
    "--Eigenvec-file", type=str,
    help="eigenvec file (for model evaluation)",
    default="/REF/examples/prsice2/EUR.eigenvec"
)


# shared arguments
parser.add_argument(
    "--config", type=str,
    default='config.yaml',
    help="config YAML file")
parser.add_argument(
    "--Sumstats_file", type=str,
    default=os.path.join("QC_data", 'Height.QC.gz'),
    help="summary statistics file")
parser.add_argument(
    "--Pheno_file", type=str,
    default="/REF/examples/prsice2/EUR.height",
    help="Phenotype file")
parser.add_argument(
    "--Phenotype", type=str,
    default="Height",
    help="Phenotype name (must be a column header in Pheno_file)")
parser.add_argument(
    "--Phenotype_class", type=str,
    default="CONTINUOUS",
    help="Phenotype class",
    choices=['CONTINUOUS', 'BINARY', 'ORDINAL', 'NOMINAL'])
parser.add_argument(
    "--Geno_file", type=str,
    default="EUR",
    help="file path to .bed, .bim, .fam, etc. files")
parser.add_argument(
    "--Output_dir", type=str,
    help="Output file directory",
    default="PGS_prsice2")

# runtime specific
parser.add_argument(
    '--runtype', type=str,
    help="operation mode",
    default='subprocess',
    choices=runtype_choices
)

# NameSpace object
parsed_args, unknowns = parser.parse_known_args(sys.argv[1:])

# TODO: Find neater way of handling additional kwargs
if len(unknowns) > 0:
    print('arguments that will override config.yaml for method ' +
          f'{parsed_args.method}:')
    print(unknowns, '\n')
assert len(unknowns) % 2 == 0, 'number of arguments must be even!'

# convert to dict, remove skipped key/value pairs
args_dict = vars(parsed_args).copy()
for key in ['method', 'runtype']:
    args_dict.pop(key)


# load config.yaml file as dict
config = args_dict.pop('config')
with open(config, 'r', encoding="utf-8") as f:
    config = yaml.safe_load(f)

#######################################
# set up environment variables
#######################################
# the config may contain some default paths to container files
# and reference data, but we may want to override these for clarity
pgs.set_env(config)

#######################################
# update config with additional kwargs
if len(unknowns) > 0:
    d = {k: v for k, v in zip(unknowns[::2], unknowns[1::2])}
    config[parsed_args.method.split('-')[0]].update(d)

# job file headers
currentDateAndTime = datetime.datetime.now()
now = currentDateAndTime.strftime('%y%d%d-%H:%M:%S')

bash_header = '''#\\!/bin/sh'''
jobname = '-'.join([config['slurm']['job_name'], parsed_args.method, now])
slurm_header = f'''#!/bin/sh
#SBATCH --job-name={jobname}
#SBATCH --output={os.path.join(parsed_args.Output_dir, jobname + now + '.txt')}
#SBATCH --error={os.path.join(parsed_args.Output_dir, jobname + now + '.txt')}
#SBATCH --account=$SBATCH_ACCOUNT  # project ID
#SBATCH --time={config['slurm']['time']}
#SBATCH --cpus-per-task={config['slurm']['cpus_per_task']}
#SBATCH --mem-per-cpu={config['slurm']['mem_per_cpu']}
#SBATCH --partition={config['slurm']['partition']}\n
'''

# environment variables for sh and slurm scripts
env_keys = [
    'ROOT_DIR', 'CONTAINERS', 'SIF', 'REFERENCE', 'LDPRED2_REF',
    'SINGULARITY_BIND', 'GUNZIP', 'GZIP', 'AWK',
    'RSCRIPT', 'PLINK', 'PRSICE', 'PYTHON'
]
env_variables_list = []
for key in env_keys:
    env_variables_list += [f'export {key}="{os.environ[key]}"']

# create PGS instances and commands


if parsed_args.method == 'plink':
    pgs_instance = pgs.PGS_Plink(
        **args_dict,
        **config['plink'])
    commands = (pgs_instance.get_str(mode='preprocessing') +
                pgs_instance.get_str(mode='stratification'))
elif parsed_args.method == 'prsice2':
    pgs_instance = pgs.PGS_PRSice2(
        **args_dict,
        **config['prsice2']
    )
    commands = pgs_instance.get_str()
elif parsed_args.method == 'ldpred2-inf':
    args = args_dict.copy()
    for key in ['Eigenvec_file', 'Cov_file']:
        args.pop(key)
    pgs_instance = pgs.PGS_LDpred2(
        method='inf',
        **args,
        **config['ldpred2']
    )
    commands = pgs_instance.get_str(create_backing_file=True)
elif parsed_args.method == 'ldpred2-auto':
    args = args_dict.copy()
    for key in ['Eigenvec_file', 'Cov_file']:
        args.pop(key)
    pgs_instance = pgs.PGS_LDpred2(
        method='auto',
        **args,
        **config['ldpred2']
    )
    commands = pgs_instance.get_str(create_backing_file=True)
else:
    raise NotImplementedError

# post run task(s)
if parsed_args.method in ['plink', 'prsice2']:
    commands += [pgs_instance.get_model_evaluation_str()]
elif parsed_args.method in ['ldpred2-inf', 'ldpred2-auto']:
    commands += [
        pgs_instance.get_model_evaluation_str(
            Eigenvec_file=args_dict['Eigenvec_file'],
            nPCs=str(config['plink']['nPCs']),
            Cov_file=args_dict['Cov_file'])]

# create tasks
if parsed_args.runtype == 'subprocess':
    for call in commands:
        pgs.run_call(call)

elif parsed_args.runtype == 'sh':
    # write bash script
    jobdir = 'bash_scripts'
    if not os.path.isdir(jobdir):
        os.mkdir(jobdir)

    with open(os.path.join(jobdir, f'{parsed_args.method}-{now}.sh'),
              'w', encoding="utf-8") as f:
        f.writelines('\n'.join([bash_header] + env_variables_list + commands))

        mssg = f'wrote {f.name}. To run, issue:\n$ bash {f.name}'
        print(mssg)

elif parsed_args.runtype == 'slurm':
    # write bash script
    jobdir = 'slurm_job_scripts'
    if not os.path.isdir(jobdir):
        os.mkdir(jobdir)

    with open(os.path.join(jobdir, f'{parsed_args.method}-{now}.job'),
              'w', encoding="utf-8") as f:
        f.writelines('\n'.join([slurm_header] + env_variables_list + commands))

        mssg = (f'wrote {f.name}.' +
                f'To submit job to the job queue, issue:\n$ sbatch {f.name}')
        print(mssg)
else:
    raise NotImplementedError(
        f'runtype {parsed_args.runtype} not implemented')
