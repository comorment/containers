#!/usr/bin/env python3
# run script wrapping the class definitions in pgrs.py as a command line tool

# package imports
import os
import sys
import pgrs
import subprocess
import yaml
import argparse


# list of method options
method_choices = ['plink', 'prsice2', 'ldpred2-inf', 'ldpred2-auto']

# list of runtype options
runtype_choices = ['sh', 'slurm', 'subprocess']

# shared
parser = argparse.ArgumentParser(
    prog='PGRS', 
    description="A pipeline for PGRS analysis")
parser.add_argument(
    "--Sumstats_file", type=str, 
    default=os.path.join("QC_data", 'Height.QC.gz'), 
    # default="/REF/examples/prsice2/Height.gwas.txt.gz", 
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
    "--Data_postfix", type=str, 
    default=".QC", help="")
parser.add_argument(
    "--Output_dir", type=str,
    help="Output file directory",
    default="PGS_prsice2")

# runtime specific
parser.add_argument(
    "--method", type=str, 
    help="Method for PGRS", 
    default='prsice2', 
    choices=method_choices)
parser.add_argument(
    '--runtype', type=str,
    help=f"operation mode",
    default='subprocess',
    choices=runtype_choices
)

# method specific
parser.add_argument(
    "--Cov_file", type=str,
    help="covariance file (for method=[plink, prsice2])",
    default="/REF/examples/prsice2/EUR.cov")
parser.add_argument(
    "--Eigenvec-file", type=str,
    help="eigenvec file (for method=[plink, prsice2])",
    default="/REF/examples/prsice2/EUR.eigenvec")
parser.add_argument(
    "--keep_SNPs_file", type=str,
    help="File with RSIDs of SNPs to keep (for method=[ldpred2-inf, ldpred2-auto])",
    default="/REF/hapmap3/w_hm3.justrs")


# NameSpace object
parsed_args = parser.parse_args(sys.argv[1:])
args_dict = vars(parsed_args)

# check that method is allowed:
try:
    assert parsed_args.method in method_choices
except AssertionError as ae:
    raise NotImplementedError('method {parsed_args.method} not in {method_choices}')


# enviroment variables for test runs
os.environ.update(dict(
    CONTAINERS=os.path.split(os.getcwd())[0],
))
os.environ.update(dict(
    SIF=os.path.join(os.environ['CONTAINERS'], 'singularity'),
    REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference')
))
os.environ.update(dict(
    SINGULARITY_BIND=f'{os.environ["REFERENCE"]}:/REF'
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

# print input and config dicts
print(args_dict, '\n')
print(config, '\n')


# create PGRS instances and commands 
if parsed_args.method == 'plink':
    args_dict_plink = args_dict.copy()
    for key in ['method', 'runtype', 'keep_SNPs_file']:
        args_dict_plink.pop(key)
    pgs = pgrs.PGS_Plink(
        **args_dict_plink,
        **config['plink'])
    commands = pgs.get_str(mode='preprocessing') + pgs.get_str(mode='stratification')
elif parsed_args.method == 'prsice2':
    args_dict_prsice2 = args_dict.copy()
    for key in ['method', 'runtype', 'keep_SNPs_file']:
        args_dict_prsice2.pop(key)
    pgs = pgrs.PGS_PRSice2(
        **args_dict_prsice2,
        **config['prsice2']
    )
    commands = pgs.get_str()
elif parsed_args.method == 'ldpred2-inf':
    args_dict_ldpred2 = args_dict.copy()
    for key in ['method', 'runtype', 'Cov_file', 'Eigenvec_file']:
        args_dict_ldpred2.pop(key)
    pgs = pgrs.PGS_LDpred2(
        method='inf',
        **args_dict_ldpred2,
        **config['ldpred2']
    )
    commands = pgs.get_str(create_backing_file=True)
elif parsed_args.method == 'ldpred2-auto':
    args_dict_ldpred2 = args_dict.copy()
    for key in ['method', 'runtype', 'Cov_file', 'Eigenvec_file']:
        args_dict_ldpred2.pop(key)
    pgs = pgrs.PGS_LDpred2(
        method='auto',
        **args_dict_ldpred2,
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
    raise NotImplementedError
elif parsed_args.runtype == 'slurm':
    # write slurm jobscript
    raise NotImplementedError
else:
    raise NotImplementedError('runtype not implemented')