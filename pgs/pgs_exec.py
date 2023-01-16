#!/usr/bin/env python3
# run script wrapping the class definitions in pgs/pgs.py as a command line tool

# package imports
import os
import sys
from pgs import pgs
import subprocess
import yaml
import argparse


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
parser_ldpred2_inf.add_argument(
    "--keep_SNPs_file", type=str,
    help="File with RSIDs of SNPs to keep (for method ldpred2-inf)",
    default="/REF/hapmap3/w_hm3.justrs"
)

# method ldpred2-auto:
parser_ldpred2_auto = subparsers.add_parser('ldpred2-auto')
parser_ldpred2_auto.add_argument(
    "--keep_SNPs_file", type=str,
    help="File with RSIDs of SNPs to keep (for method ldpred2-auto)",
    default="/REF/hapmap3/w_hm3.justrs"
)



# shared arguments
parser.add_argument(
    "--Sumstats_file", type=str, 
    default=os.path.join("QC_data", 'Height.QC.gz'), 
    help="summary statistics file")
parser.add_argument(
    "--Pheno_file", type=str, 
    default="/REF/examples/prsice2/EUR.height", 
    help="Phenotype file")
parser.add_argument(
    "--Input_dir", type=str,
    help="input file directory",
    default="QC_data")
parser.add_argument(
    "--Data_prefix", type=str, 
    default="EUR", 
    help="file prefix for .bed, .bim, .fam, etc. files")
parser.add_argument(
    "--Output_dir", type=str,
    help="Output file directory",
    default="PGS_prsice2")

# runtime specific
parser.add_argument(
    '--runtype', type=str,
    help=f"operation mode",
    default='subprocess',
    choices=runtype_choices
)



# NameSpace object
parsed_args, unknowns = parser.parse_known_args(sys.argv[1:])

# TODO: Find neater way of handling additional kwargs
if len(unknowns) > 0:
    print(f'arguments that will override config.yaml for method {parsed_args.method}:')
    print(unknowns, '\n')
assert len(unknowns) % 2 == 0, 'number of arguments must be even!'

# convert to dict, remove skipped key/value pairs
args_dict = vars(parsed_args).copy()
for key in ['method', 'runtype']:
        args_dict.pop(key)


# enviroment variables for test runs
os.environ.update(dict(
    CONTAINERS=os.path.split(os.getcwd())[0],
))
os.environ.update(dict(
    COMORMENT=os.path.split(os.environ['CONTAINERS'])[0],
    SIF=os.path.join(os.environ['CONTAINERS'], 'singularity'),
    REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference')
))
os.environ.update(dict(
    LDPRED2_REF=os.path.join(os.environ['COMORMENT'], 'ldpred2_ref'),
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

# update config with additional kwargs
if len(unknowns) > 0:
    d = {k: v for k, v in zip(unknowns[::2], unknowns[1::2])}
    config[parsed_args.method.split('-')[0]].update(d)
    if parsed_args.method == 'prsice2':
        if 'beta' in d.keys():
            del config['prsice2']['or']


# job file headers
bash_header = '''#\!/bin/sh'''
jobname = '-'.join([config['slurm']['job_name'], parsed_args.method])
slurm_header = f'''#!/bin/sh
#SBATCH --job-name={jobname}
#SBATCH --output={os.path.join(parsed_args.Output_dir, jobname + '.txt')}
#SBATCH --error={os.path.join(parsed_args.Output_dir, jobname + '.txt')}
#SBATCH --account=$SBATCH_ACCOUNT  # project ID
#SBATCH --time={config['slurm']['time']}
#SBATCH --cpus-per-task={config['slurm']['cpus_per_task']}
#SBATCH --mem-per-cpu={config['slurm']['mem_per_cpu']}
#SBATCH --partition={config['slurm']['partition']}\n
'''

# environment variables for sh and slurm scripts
env_keys = [
    'COMORMENT', 'CONTAINERS', 'SIF', 'REFERENCE', 'LDPRED2_REF',
    'SINGULARITY_BIND', 'GUNZIP_EXEC', 'GZIP_EXEC', 'AWK_EXEC', 
    'RSCRIPT', 'PLINK', 'PRSICE', 'PYTHON'
    ]
env_variables_list = []
for key in env_keys:
    env_variables_list += [f'export {key}="{os.environ[key]}"']

# create PGS instances and commands


if parsed_args.method == 'plink':
    pgs = pgs.PGS_Plink(
        **args_dict,
        **config['plink'])
    commands = pgs.get_str(mode='preprocessing') + pgs.get_str(mode='stratification')
elif parsed_args.method == 'prsice2':
    pgs = pgs.PGS_PRSice2(
        **args_dict,
        **config['prsice2']
    )
    commands = pgs.get_str()
elif parsed_args.method == 'ldpred2-inf':
    pgs = pgs.PGS_LDpred2(
        method='inf',
        **args_dict,
        **config['ldpred2']
    )
    commands = pgs.get_str(create_backing_file=True)
elif parsed_args.method == 'ldpred2-auto':
    pgs = pgs.PGS_LDpred2(
        method='auto',
        **args_dict,
        **config['ldpred2']
    )
    commands = pgs.get_str(create_backing_file=True)
else:
    raise NotImplementedError

# create tasks
if parsed_args.runtype == 'subprocess':
    for call in commands:
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0
elif parsed_args.runtype == 'sh':
    # write bash script
    jobdir = 'bash_scripts'
    if not os.path.isdir(jobdir):
        os.mkdir(jobdir)
    
    with open(os.path.join(jobdir, f'{parsed_args.method}.sh'), 'w') as f:
        f.writelines('\n'.join([bash_header] + env_variables_list + commands))
    
        mssg = f'wrote {f.name}. To run, issue:\n$ bash {f.name}'
        print(mssg)

elif parsed_args.runtype == 'slurm':
    # write bash script
    jobdir = 'slurm_job_scripts'
    if not os.path.isdir(jobdir):
        os.mkdir(jobdir)
    
    with open(os.path.join(jobdir, f'{parsed_args.method}.job'), 'w') as f:
        f.writelines('\n'.join([slurm_header] + env_variables_list + commands))
    
        mssg = f'wrote {f.name}. To submit job to the job queue, issue:\n$ sbatch {f.name}'
        print(mssg)
else:
    raise NotImplementedError(
        f'runtype {parsed_args.runtype} not implemented')