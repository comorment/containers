#!/usr/bin/env python3

# README:
# gwas.py converts pheno+dict files into format compatible with plink or regenie analysis. Other association analyses can be added later.
# gwas.py automatically decides whether to run logistic or linear regression by looking at the data dictionary for requested phenotypes
# gwas.py generates all scripts needed to run the analysis, and to convert the results back to a standard summary statistics format

import argparse
import logging, time, sys, traceback, socket, getpass, six, os
import pandas as pd
import numpy as np
from scipy import stats
import tarfile, subprocess, collections, shutil

__version__ = '1.0.1'
MASTHEAD = "***********************************************************************\n"
MASTHEAD += "* gwas.py: pipeline for GWAS analysis\n"
MASTHEAD += "* Version {V}\n".format(V=__version__)
MASTHEAD += "* (C) 2021 Oleksandr Frei and Bayram Akdeniz\n"
MASTHEAD += "* Norwegian Centre for Mental Disorders Research / University of Oslo\n"
MASTHEAD += "* GNU General Public License v3\n"
MASTHEAD += "***********************************************************************\n"

# https://stackoverflow.com/questions/27433316/how-to-get-argparse-to-read-arguments-from-a-file-with-an-option-rather-than-pre
class LoadFromFile (argparse.Action):
    def __call__ (self, parser, namespace, values, option_string=None):
        with values as f:
            contents = '\n'.join([x for x in f.readlines() if (not x.strip().startswith('#'))])

        data = parser.parse_args(contents.split(), namespace=namespace)
        for k, v in vars(data).items():
            if v and k != option_string.lstrip('-'):
                setattr(namespace, k, v)

class ActionStoreDeprecated(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        logger=logging.getLogger()
        logger.warn('DEPRECATED: using %s', '|'.join(self.option_strings))
        setattr(namespace, self.dest, values)


class ActionAppendDeprecated(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        logger=logging.getLogger()
        logger.warn('DEPRECATED: using %s', '|'.join(self.option_strings))
        if not getattr(namespace, self.dest):
            setattr(namespace, self.dest, [])
        getattr(namespace, self.dest).append(values)

def parse_args(args):
    parser = argparse.ArgumentParser(description="A pipeline for GWAS analysis")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--argsfile', type=open, action=LoadFromFile, default=None, help="file with additional command-line arguments, e.g. those configuration settings that are the same across all of your runs")
    parent_parser.add_argument("--out", type=str, default="gwas", help="prefix for the output files (<out>.covar, <out>.pheno, etc)")
    parent_parser.add_argument("--log", type=str, default=None, help="file to output log, defaults to <out>.log")
    parent_parser.add_argument("--log-sensitive", action="store_true", default=False, help="allow sensitive (individual-level) information in <out>.log. Use with caution. This may help debugging errors, but then you must pay close attention to avoid exporting the .log files out of your security environent. It's recommended to delete .log files after  you've investigate the problem.")

    slurm_parser = argparse.ArgumentParser(add_help=False)
    slurm_parser.add_argument("--slurm-job-name", type=str, default="gwas", help="SLURM --job-name argument")
    slurm_parser.add_argument("--slurm-account", type=str, default="p697_norment", help="SLURM --account argument")
    slurm_parser.add_argument("--slurm-time", type=str, default="06:00:00", help="SLURM --time argument")
    slurm_parser.add_argument("--slurm-cpus-per-task", type=int, default=16, help="SLURM --cpus-per-task argument")
    slurm_parser.add_argument("--slurm-mem-per-cpu", type=str, default="8000M", help="SLURM --mem-per-cpu argument")
    slurm_parser.add_argument("--module-load", type=str, nargs='+', default=['singularity/3.7.1'], help="list of modules to load")
    slurm_parser.add_argument("--comorment-folder", type=str, default='/cluster/projects/p697/github/comorment', help="folder containing 'containers' subfolder with a full copy of https://github.com/comorment/containers")
    slurm_parser.add_argument("--singularity-bind", type=str, default='$COMORMENT/containers/reference:/REF:ro', help="translates to SINGULARITY_BIND variable in SLURM scripts")

    # filtering options
    filter_parser = argparse.ArgumentParser(add_help=False)
    filter_parser.add_argument("--info-file", type=str, default=None, help="File with SNP and INFO columns. Values in SNP column must be unique.")
    filter_parser.add_argument("--info", type=float, default=None, help="threshold for filtering on imputation INFO score")
    filter_parser.add_argument("--maf", type=float, default=None, help="threshold for filtering on minor allele frequency")
    filter_parser.add_argument("--hwe", type=float, default=None, help="threshold for filtering on hardy weinberg equilibrium p-value")
    filter_parser.add_argument("--geno", type=float, default=None, help="threshold for filtering on per-variant missingness rate)")

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    parser_gwas_add_arguments(args=args, func=execute_gwas, parser=subparsers.add_parser("gwas", parents=[parent_parser, slurm_parser, filter_parser], help='perform gwas analysis'))
    parser_merge_plink2_add_arguments(args=args, func=merge_plink2, parser=subparsers.add_parser("merge-plink2", parents=[parent_parser, filter_parser], help='merge plink2 sumstats files'))
    parser_merge_regenie_add_arguments(args=args, func=merge_regenie, parser=subparsers.add_parser("merge-regenie", parents=[parent_parser, filter_parser], help='merge regenie sumstats files'))

    loci_parser_descr = """Perform LD-based clumping of summary stats, using a procedure that is similar to FUMA snp2gene functionality (http://fuma.ctglab.nl/tutorial#snp2gene):
Step 1. Re-save summary stats into one file for each chromosome.
Step 2a Use 'plink --clump' to find independent significant SNPs (default r2=0.6);
Step 2b Use 'plink --clump' to find lead SNPs, by clumping independent significant SNPs (default r2=0.1);
Step 3. Use 'plink --ld' to find genomic loci around each independent significant SNP (default r2=0.6);
Step 4. Merge together genomic loci which are closer than certain threshold (250 KB);
Step 5. Merge together genomic loci that fall into exclusion regions, such as MHC;
Step 6. Output genomic loci report, indicating lead SNPs for each loci;
Step 7. Output candidate SNP report;"""
    parser_loci_add_arguments(args=args, func=make_loci_implementation, parser=subparsers.add_parser("loci", parents=[parent_parser], help="LD-based clumping of summary stats", description=loci_parser_descr))

    return parser.parse_args(args)

def parser_gwas_add_arguments(args, func, parser):
    parser.add_argument("--pheno-file", type=str, default=None, help="phenotype file, according to CoMorMent spec")
    parser.add_argument("--dict-file", type=str, default=None, help="phenotype dictionary file, defaults to <pheno>.dict")

    # genetic files to use. All must share the same set of individuals. Currently this assumption is not validated.
    parser.add_argument("--geno-file", type=str, default=None, help="required argument pointing to a genetic file: (1) plink's .bed file, or (2) .bgen file, or (3) .pgen file, or (4) .vcf file. Note that a full name of .bed (or .bgen, .pgen, .vcf) file is expected here. Corresponding files should have standard names, e.g. for plink's format it is expected that .fam and .bim file can be obtained by replacing .bed extension accordingly. supports '@' as a place holder for chromosome labels")
    parser.add_argument("--geno-fit-file", type=str, default=None, help="genetic file to use in a first stage of mixed effect model. Expected to have the same set of individuals as --geno-file (this is NOT validated by the gwas.py script, and it is your responsibility to follow this assumption). Optional for standard association analysis (e.g. if for plink's glm). The argument supports the same file types as the --geno-file argument. Noes not support '@' (because mixed effect tools typically expect a single file at the first stage.")
    parser.add_argument("--fam", type=str, default=None, help="an argument pointing to a plink's .fam file, use by gwas.py script to pre-filter phenotype information (--pheno) with the set of individuals available in the genetic file (--geno-file / --geno-fit-file). Optional when either --geno-file or --geno-fit-file is in plink's format, otherwise required - but IID in this file must be consistent with identifiers of the genetic file.")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use "
         "(e.g. 1,2,3 or 1-4,12,16-20). Used when '@' is present in --geno-file, and allows to specify for which chromosomes to run the association testing.")

    # deprecated options for genetic files
    parser.add_argument("--bed-fit", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-fit-file instead (but remember to add .bed to your argument)] plink bed/bim/fam file to use in a first step of mixed effect models")
    parser.add_argument("--bed-test", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-file instead (but remember to add .bed to your argument)] plink bed/bim/fam file to use in association testing; supports '@' as a place holder for chromosome labels (see --chr2use argument)")
    parser.add_argument("--bgen-fit", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-fit-file instead] .bgen file to use in a first step of mixed effect models")
    parser.add_argument("--bgen-test", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-file instead] .bgen file to use in association testing; supports '@' as a place holder for chromosome labels")

    parser.add_argument("--covar", type=str, default=[], nargs='+', help="covariates to control for (must be columns of the --pheno-file); individuals with missing values for any covariates will be excluded not just from <out>.covar, but also from <out>.pheno file")
    parser.add_argument("--variance-standardize", type=str, default=None, nargs='*', help="the list of continuous phenotypes to standardize variance; accept the list of columns from the --pheno file (if empty, applied to all); doesn't apply to dummy variables derived from NOMINAL or BINARY covariates.")
    parser.add_argument("--pheno", type=str, default=[], nargs='+', help="target phenotypes to run GWAS (must be columns of the --pheno-file")
    parser.add_argument("--pheno-na-rep", type=str, default='NA', help="missing data representation for phenotype file (regenie: NA, plink: -9)")
    parser.add_argument('--analysis', type=str, default=['plink2', 'regenie'], nargs='+', choices=['plink2', 'regenie'])

    parser.set_defaults(func=func)

def parser_merge_plink2_add_arguments(args, func, parser):
    parser.add_argument("--sumstats", type=str, default=None, help="sumstat file produced by plink2, containing @ as chromosome label place holder")
    parser.add_argument("--basename", type=str, default=None, help="basename for .vmiss, .afreq and .hardy files, with @ as chromosome label place holder")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use, (e.g. 1,2,3 or 1-4,12,16-20).")
    parser.set_defaults(func=func)

def parser_merge_regenie_add_arguments(args, func, parser):
    parser.add_argument("--sumstats", type=str, default=None, help="sumstat file produced by plink2, containing @ as chromosome label place holder")
    parser.add_argument("--basename", type=str, default=None, help="basename for .vmiss, .afreq and .hardy files, with @ as chromosome label place holder")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use, (e.g. 1,2,3 or 1-4,12,16-20).")
    parser.set_defaults(func=func)

def parser_loci_add_arguments(args, func, parser):
    parser.add_argument("--sumstats", type=str, help="Input file with summary statistics")
    parser.add_argument("--sumstats-chr", type=str, help="Input file with summary statistics, one file per chromosome")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use, (e.g. 1,2,3 or 1-4,12,16-20).")

    parser.add_argument("--clump-field", type=str, default='P', help="Column to clump on.")
    parser.add_argument("--clump-snp-field", type=str, default='SNP', help="Column with marker name.")
    parser.add_argument("--chr", type=str, default='CHR', help="Column name with chromosome labels. ")

    parser.add_argument("--indep-r2", type=float, default=0.6, help="LD r2 threshold for clumping independent significant SNPs.")
    parser.add_argument("--lead-r2", type=float, default=0.1, help="LD r2 threshold for clumping lead SNPs.")
    parser.add_argument("--clump-p1", type=float, default=5e-8, help="p-value threshold for independent significant SNPs.")
    parser.add_argument("--bfile", type=str,
        help="prefix for plink .bed/.bim/.fam file. Can work with files split across 22 chromosomes: "
        "if the filename prefix contains the symbol @, sumstats.py will replace the @ symbol with chromosome numbers. ")

    parser.add_argument("--ld-window-kb", type=float, default=10000, help="Window size in KB to search for clumped SNPs. ")
    parser.add_argument("--loci-merge-kb", type=float, default=250, help="Maximum distance in KB of LD blocks to merge. ")
    parser.add_argument("--exclude-ranges", type=str, nargs='+',
        help='Exclude SNPs in ranges of base pair position, for example MHC. '
        'The syntax is chr:from-to, for example 6:25000000-35000000. Multiple regions can be excluded.')
    parser.add_argument("--plink", type=str, default='plink', help="Path to plink executable.")
    parser.set_defaults(func=func)

def extract_variables(df, variables, pheno_dict_map, log):
    cat_vars = [x for x in variables if pheno_dict_map[x] == 'NOMINAL']
    other_vars =  ['FID', 'IID'] + [x for x in variables if pheno_dict_map[x] != 'NOMINAL']

    dummies=df[other_vars]
    for var in cat_vars:
        new = pd.get_dummies(df[var], prefix=var)
        dummies = dummies.join(new)

        #drop most frequent variable for ref category
        drop_col = df.groupby([var]).size().idxmax()
        dummies.drop('{}_{}'.format(var, drop_col), axis=1, inplace=True)

        log.log('Variable {} will be extracted as dummie, dropping {} label (most frequent)'.format(var, drop_col))
    return dummies.copy()

def is_bed_file(fname):
    return fname.endswith('.bed')
def is_bgen_file(fname):
    return fname.endswith('.bgen')
def is_pgen_file(fname):
    return fname.endswith('.pgen')
def is_vcf_file(fname):
    return fname.endswith('.vcf')
def remove_suffix(text, suffix):
    return text[:-len(suffix)] if text.endswith(suffix) and len(suffix) != 0 else text
def replace_suffix(text, suffix, new_suffix):
    return remove_suffix(text, suffix) + new_suffix

def fix_and_validate_chr2use(args, log):
    arg_dict = vars(args)
    chr2use_arg = arg_dict["chr2use"]
    chr2use = []
    for a in chr2use_arg.split(","):
        if "-" in a:
            start, end = [int(x) for x in a.split("-")]
            chr2use += [str(x) for x in range(start, end+1)]
        else:
            chr2use.append(a.strip())
    arg_dict["chr2use"] = chr2use

def fix_and_validate_args(args, log):
    if not args.pheno_file: raise ValueError('--pheno-file is required.')
    if not args.pheno: raise ValueError('--pheno is required.')

    # fix deprecated arguments
    if args.bed_fit: args.geno_fit_file = args.bed_fit + '.bed'; args.bed_fit=None
    if args.bed_test: args.geno_file = args.bed_test + '.bed'; args.bed_test=None
    if args.bgen_fit: args.geno_fit_file = args.bgen_fit; args.bgen_fit=None
    if args.bgen_test: args.geno_file = args.bgen_test; args.bgen_test=None

    if ('plink2' in args.analysis) and ('regenie' in args.analysis):
        raise ValueError('--analysis can not have both --plink2 and --regenie, please choose one of these.')

    if (args.info is not None) or (args.info_file is not None):
        if (args.info is None) or (args.info_file is None):
            raise ValueError('both --info and --info-file must be used at the same time')
        check_input_file(args.info_file, chr2use=args.chr2use)

    # validate that some of genetic data is provided as input
    if not args.geno_file:
        raise ValueError('--geno-file must be specified')
    if ('regenie' in 'analysis') and (not args.geno_fit_file):
        raise ValueError('--geno-fit-file must be specified for --analysis regenie')

    if args.fam is None:
        if is_bed_file(args.geno_file):
            args.fam = replace_suffix(args.geno_file, '.bed', '.fam')
        elif is_bed_file(args.geno_fit_file):
            args.fam = replace_suffix(args.geno_fit_file, '.bed', '.fam')
        else:
            raise ValueError('please specify --fam argument in plink format, containing the same set of individuals as your --geno-file / --geno-fit-file')
        if '@' in args.fam: args.fam = args.fam.replace('@', args.chr2use[0])
    check_input_file(args.fam)

    check_input_file(args.pheno_file)
    if not args.dict_file: args.dict_file = args.pheno_file + '.dict'
    check_input_file(args.dict_file)

def make_regenie_commands(args, logistic, step):
    geno_fit_file = args.geno_fit_file
    geno_file = args.geno_file.replace('@', '${SLURM_ARRAY_TASK_ID}')
    sample = replace_suffix(geno_file, ".bgen", ".sample")

    if ('@' in geno_fit_file): raise(ValueError('--geno-fit-file contains "@", hense it is incompatible with regenie step1 which require a single file'))
    if (is_vcf_file(geno_fit_file) or is_vcf_file(geno_file)): raise(ValueError('--geno-file / --geno-fit-file can not point to a .vcf file for REGENIE analysis'))

    cmd = "$REGENIE " + \
        " --phenoFile {}.pheno".format(args.out) + \
        (" --covarFile {}.covar".format(args.out) if args.covar else "") + \
        " --loocv "

    cmd_step1 = ' --step 1 --bsize 1000' + \
        " --out {}.regenie.step1".format(args.out) + \
        (" --bed {} --ref-first".format(remove_suffix(geno_fit_file, '.bed')) if is_bed_file(geno_fit_file) else "") + \
        (" --pgen {} --ref-first".format(remove_suffix(geno_fit_file, '.pgen')) if is_pgen_file(geno_fit_file) else "") + \
        (" --bgen {} --ref-first".format(geno_fit_file) if is_bgen_file(geno_fit_file) else "") + \
        (" --bt" if logistic else "") + \
        " --lowmem --lowmem-prefix {}.regenie_tmp_preds".format(args.out)

    cmd_step2 = ' --step 2 --bsize 400' + \
        " --out {}_chr${{SLURM_ARRAY_TASK_ID}}".format(args.out) + \
        (" --bed {} --ref-first".format(remove_suffix(geno_file, '.bed')) if  is_bed_file(geno_file) else "") + \
        (" --pgen {} --ref-first".format(remove_suffix(geno_file, '.pgen')) if is_pgen_file(geno_file) else "") + \
        (" --bgen {} --ref-first --sample {}".format(geno_file, sample) if is_bgen_file(geno_file) else "") + \
        (" --bt --firth 0.01 --approx" if logistic else "") + \
        " --pred {}.regenie.step1_pred.list".format(args.out) + \
        " --chr ${SLURM_ARRAY_TASK_ID}"

    return (cmd + cmd_step1) if step==1 else (cmd + cmd_step2)

# this function works similarly to ** in python:
# all args from args_list that are not None are passed to the caller
# see make_regenie_merge and make_plink2_merge for a usage example.
def pass_arguments_along(args, args_list):
    opts = vars(args)
    vals = [opts[arg.replace('-', '_')] for arg in args_list]
    return ''.join([('--{} {} '.format(arg, val) if (val is not None) else '') for arg, val in zip(args_list, vals)])

def make_loci(args):
    # $PYTHON gwas.py loci --sumstats run1_CASE2.regenie.gz --out run1_CASE2.regenie --bfile /REF/examples/regenie/example_3chr --chr2use 1-3 --clump-p1 0.1
    pass

def make_manh(args):
    # $PYTHON manhattan.py run1_CASE2.regenie.gz --out run1_CASE2.regenie.png --chr2use 1-3 --lead run1_CASE2.regenie.lead.csv --indep run1_CASE2.regenie.indep.csv --downsample-frac 1
    pass

def make_qq(args):
    # $PYTHON qq.py run1_CASE2.regenie.gz --out run1_CASE2.regenie.png
    pass

def make_regenie_merge(args, logistic):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py merge-regenie ' + \
            pass_arguments_along(args, ['info-file', 'info', 'maf', 'hwe', 'geno']) + \
            ' --sumstats {out}_chr@_{pheno}.regenie'.format(out=args.out, pheno=pheno) + \
            ' --basename {out}_chr@'.format(out=args.out) + \
            ' --out {out}_{pheno}.regenie '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use)) + \
            '\n'

    return cmd

def make_plink2_merge(args, logistic):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py merge-plink2 ' + \
            pass_arguments_along(args, ['info-file', 'info', 'maf', 'hwe', 'geno']) + \
            ' --sumstats {out}_chr@.{pheno}.glm.{what}'.format(out=args.out, pheno=pheno, what=('logistic' if logistic else 'linear')) + \
            ' --basename {out}_chr@'.format(out=args.out) + \
            ' --out {out}_{pheno}.plink2 '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use)) + \
            '\n'
    return cmd

def make_plink2_commands(args):
    geno_file = args.geno_file.replace('@', '${SLURM_ARRAY_TASK_ID}')

    cmd = "$PLINK2 " + \
        (" --bfile {} --no-pheno".format(remove_suffix(geno_file ,'.bed')) if is_bed_file(geno_file) else "") + \
        (" --pfile {} --no-pheno".format(remove_suffix(geno_file ,'.pgen')) if is_pgen_file(geno_file) else "") + \
        (" --bgen {} ref-first --sample {}".format(geno_file, replace_suffix(geno_file, ".bgen", ".sample")) if is_bgen_file(geno_file) else "") + \
        (" --vcf {}".format(geno_file) if is_vcf_file(geno_file) else "") + \
        " --chr ${SLURM_ARRAY_TASK_ID}"
    return cmd

def make_plink2_glm_commands(args, logistic):
    cmd = make_plink2_commands(args) + \
        " --glm cols=+a1freq{} hide-covar --ci 0.95".format(",+totallelecc" if (logistic) else "") + \
        " --pheno {}.pheno".format(args.out) + \
        (" --covar {}.covar".format(args.out) if args.covar else "") + \
        " --out {}_chr${{SLURM_ARRAY_TASK_ID}}".format(args.out)
    return cmd

def make_plink2_info_commands(args):
    cmd = make_plink2_commands(args) + \
        " --missing --freq --hardy " + \
        " --keep {}.pheno".format(args.out) + \
        " --out {}_chr${{SLURM_ARRAY_TASK_ID}}".format(args.out)
    return cmd

def make_slurm_header(args, array=False):
    return """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --account={account}
#SBATCH --time={time}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --mem-per-cpu={mem_per_cpu}
{array}

{modules}

export COMORMENT={comorment_folder}
export SINGULARITY_BIND="{singularity_bind}"
export SIF=$COMORMENT/containers/singularity

export PLINK2="singularity exec --home $PWD:/home $SIF/gwas.sif plink2"
export REGENIE="singularity exec --home $PWD:/home $SIF/gwas.sif regenie"
export PYTHON="singularity exec --home $PWD:/home $SIF/python3.sif python"

""".format(array="#SBATCH --array={}".format(','.join(args.chr2use)) if array else "",
           modules = '\n'.join(['module load {}'.format(x) for x in args.module_load]),
           job_name = args.slurm_job_name,
           account = args.slurm_account,
           time = args.slurm_time,
           cpus_per_task = args.slurm_cpus_per_task,
           mem_per_cpu = args.slurm_mem_per_cpu,
           comorment_folder = args.comorment_folder,
           singularity_bind = args.singularity_bind)

def execute_gwas(args, log):
    fix_and_validate_chr2use(args, log)
    fix_and_validate_args(args, log)

    fam = read_fam(args, args.fam)
    pheno, pheno_dict = read_comorment_pheno(args, args.pheno_file, args.dict_file)
    pheno_dict_map = dict(zip(pheno_dict['FIELD'], pheno_dict['TYPE']))

    missing_cols = [str(c) for c in args.pheno if (c not in pheno.columns)]
    if missing_cols: raise(ValueError('--pheno not present in --pheno-file: {}'.format(', '.join(missing_cols))))

    pheno_types = [pheno_dict_map[pheno] for pheno in args.pheno]
    for pheno_type in pheno_types:
        if pheno_type not in ['BINARY', 'CONTINUOUS']:
            raise(ValueError('only BINARY or CONTINOUS varibales can be used as --pheno'))
    pheno_type = list(set(pheno_types))
    if len(pheno_type) != 1:
        raise(ValueError('--pheno variables has a mix of BINARY and CONTINUOS types'))
    pheno_type = pheno_type[0]
    logistic = (pheno_type=='BINARY')

    if 'FID' in pheno.columns:
        log.log("FID column is present in --pheno-file; this values will be ignored and replaced with FID column from --fam file")
        del pheno['FID']

    log.log("merging --pheno and --fam file...")
    n = len(pheno); pheno = pd.merge(pheno, fam[['IID', 'FID']], on='IID', how='inner')
    pheno_dict_map['FID'] = 'FID'
    log.log("n={} individuals remain after merging, n={} removed".format(len(pheno), n-len(pheno)))

    if args.covar:
        missing_cols = [str(c) for c in args.covar if (c not in pheno.columns)]
        if missing_cols: raise(ValueError('--covar not present in --pheno-file: {}'.format(', '.join(missing_cols))))

        log.log("filtering individuals with missing covariates...")
        for var in args.covar:
            mask = pheno[var].isnull()
            if np.any(mask):
                n = len(pheno)
                pheno = pheno[~mask].copy()
                log.log("n={} individuals remain after removing n={} individuals with missing value in {} covariate".format(len(pheno), n-len(pheno), var))

    if len(pheno) <= 1:
        raise ValueError('Too few individuals remain for analysis, exit.')

    if args.variance_standardize is not None:
        if len(args.variance_standardize) == 0:
            args.variance_standardize = [col for col in pheno.columns if (pheno_dict_map[col] == 'CONTINUOUS')]

        for col in args.variance_standardize:
            if (col not in pheno.columns) or (pheno_dict_map[col] != 'CONTINUOUS'):
                raise ValueError('Can not apply --variance-standardize to {}, column is missing or its type is other than CONTINUOUS'.fromat(col))

            mean = np.nanmean(pheno[col].values)
            std = np.nanstd(pheno[col].values, ddof=1)
            log.log('phenotype {} has mean {:.5f} and std {:.5f}. Normalizing to 0.0 mean and 1.0 std'.format(col, mean, std))
            pheno[col] = (pheno[col].values - mean) / std

    log.log("extracting covariates...")
    if args.covar:
        covar_output = extract_variables(pheno, args.covar, pheno_dict_map, log)
        log.log('writing {} columns (including FID, IID) for n={} individuals to {}.covar'.format(covar_output.shape[1], len(covar_output), args.out))
        covar_output.to_csv(args.out + '.covar', index=False, sep='\t')
    else:
        log.log('--covar not specified')

    log.log("extracting phenotypes...")
    pheno_output = extract_variables(pheno, args.pheno, pheno_dict_map, log)
    for var in args.pheno:
        if logistic:
            log.log('variable: {}, cases: {}, controls: {}, missing: {}'.format(var, np.sum(pheno[var]=='1'), np.sum(pheno[var]=='0'), np.sum(pheno[var].isnull())))
        else:
            log.log('variable: {}, missing: {}'.format(var, np.sum(pheno[var].isnull())))

    if ('plink2' in args.analysis) and logistic:
        log.log('mapping case/control variables from 1/0 to 2/1 coding')
        for var in args.pheno:
            pheno_output[var] = pheno_output[var].map({'0':'1', '1':'2'}).values

    log.log('writing {} columns (including FID, IID) for n={} individuals to {}.pheno'.format(pheno_output.shape[1], len(pheno_output), args.out))
    pheno_output.to_csv(args.out + '.pheno', na_rep='NA', index=False, sep='\t')

    log.log('all --pheno variables have type: {}, selected analysis: {}'.format(pheno_type, 'logistic' if logistic else 'linear'))

    cmd_file = args.out + '_cmd.sh'
    if os.path.exists(cmd_file): os.remove(cmd_file)
    submit_jobs = []
    if 'plink2' in args.analysis:
        with open(args.out + '_plink2.1.job', 'w') as f:
            f.write(make_slurm_header(args, array=True) + \
                    make_plink2_info_commands(args) + '\n' + \
                    make_plink2_glm_commands(args, logistic) + '\n')
        with open(args.out + '_plink2.2.job', 'w') as f:
            f.write(make_slurm_header(args, array=False) + make_plink2_merge(args, logistic) + '\n')
        with open(cmd_file, 'a') as f:
            f.write('for SLURM_ARRAY_TASK_ID in {}; do {}; done\n'.format(' '.join(args.chr2use), make_plink2_info_commands(args)))
            f.write('for SLURM_ARRAY_TASK_ID in {}; do {}; done\n'.format(' '.join(args.chr2use), make_plink2_glm_commands(args, logistic)))
            f.write(make_plink2_merge(args, logistic) + '\n')
        append_job(args.out + '_plink2.1.job', False, submit_jobs)
        append_job(args.out + '_plink2.2.job', True, submit_jobs)
    if 'regenie' in args.analysis:
        with open(args.out + '_regenie.1.job', 'w') as f:
            f.write(make_slurm_header(args, array=False) + \
                    make_regenie_commands(args, logistic, step=1) + '\n')
        with open(args.out + '_regenie.2.job', 'w') as f:
            f.write(make_slurm_header(args, array=True) + \
                    make_plink2_info_commands(args) + '\n' + \
                    make_regenie_commands(args, logistic, step=2) + '\n')
        with open(args.out + '_regenie.3.job', 'w') as f:
            f.write(make_slurm_header(args, array=False) + make_regenie_merge(args, logistic) + '\n')
        with open(cmd_file, 'a') as f:
            f.write(make_regenie_commands(args, logistic, step=1) + '\n')
            f.write('for SLURM_ARRAY_TASK_ID in {}; do {}; done\n'.format(' '.join(args.chr2use), make_plink2_info_commands(args)))
            f.write('for SLURM_ARRAY_TASK_ID in {}; do {}; done\n'.format(' '.join(args.chr2use), make_regenie_commands(args, logistic, step=2)))
            f.write(make_regenie_merge(args, logistic) + '\n')
        append_job(args.out + '_regenie.1.job', False, submit_jobs)
        append_job(args.out + '_regenie.2.job', True, submit_jobs)
        append_job(args.out + '_regenie.3.job', True, submit_jobs)
    log.log('To submit all jobs via SLURM, use the following scripts, otherwise execute commands from {}'.format(cmd_file))
    print('\n'.join(submit_jobs))

def apply_filters(args, df):
    info_col = []
    if (args.info is not None) or (args.info_file is not None):
        if (args.info is None) or (args.info_file is None):
            raise ValueError('both --info and --info-file must be used at the same time')
        log.log('reading {}...'.format(args.info_file))
        chr2use = args.chf2use if ('@' in args.info_file) else ['@']
        info=pd.concat([pd.read_csv(args.info_file.replace('@', chri), delim_whitespace=True, dtype={'INFO':np.float32})[['SNP', 'INFO']] for chri in chr2use])
        log.log('done, {} rows, {} cols'.format(len(info), info.shape[1]))

        log.log("merging --sumstats (n={} rows) and --info-file...".format(len(df)))
        df = pd.merge(df, info, how='inner', on='SNP')
        log.log("n={} SNPs remain after merging, n={} with missing INFO score".format(len(df), np.sum(df['INFO'].isnull())))

        n = len(df); df = df[~(df['INFO'] < args.info)].copy()
        log.log("n={} SNPs remain after filtering INFO>={}, n={} removed".format(len(df), args.info, n-len(df)))
        info_col = ['INFO']

    if args.maf is not None:
        maf=pd.concat([pd.read_csv(args.basename.replace('@', chri) + '.afreq', delim_whitespace=True)[['ID', 'ALT_FREQS']] for chri in args.chr2use])
        maf.rename(columns={'ID':'SNP'}, inplace=True)
        df = pd.merge(df, maf, how='left', on='SNP')
        n=len(df); df = df[(df['ALT_FREQS'] >= args.maf) & (df['ALT_FREQS'] <= (1-args.maf))].copy()
        log.log("n={} SNPs remain after filtering allele frequency on {}<=FRQ<={}, n={} removed".format(len(df), args.maf, 1-args.maf, n-len(df)))

    if args.hwe is not None:
        hwe=pd.concat([pd.read_csv(args.basename.replace('@', chri) + '.hardy', delim_whitespace=True)[['ID', 'P']] for chri in args.chr2use])
        hwe.rename(columns={'ID':'SNP', 'P':'P_HWE'}, inplace=True)
        df = pd.merge(df, hwe, how='left', on='SNP')
        n=len(df); df = df[df['P_HWE'] >= args.hwe].copy()
        log.log("n={} SNPs remain after filtering Hardy Weinberg equilibrium P>={}, n={} removed".format(len(df), args.hwe, n-len(df)))
        del df['P_HWE']

    if args.geno is not None:
        vmiss=pd.concat([pd.read_csv(args.basename.replace('@', chri) + '.vmiss', delim_whitespace=True)[['ID', 'F_MISS']] for chri in args.chr2use])
        vmiss.rename(columns={'ID':'SNP'}, inplace=True)
        df = pd.merge(df, vmiss, how='left', on='SNP')
        n=len(df); df = df[df['F_MISS'] <= args.geno].copy()
        log.log("n={} SNPs remain after filtering SNPs missingness F_MISS>={}, n={} removed".format(len(df), args.geno, n-len(df)))
        del df['F_MISS']

    return df, info_col

def write_readme_file(args):
    with open(args.out + '.README.txt', 'w') as f:
        f.write('''Columns are defined as follows:
SNP      - marker name, for example rs#.
CHR      - chromosome label
BP       - base-pair position
A1       - effect allele for ``Z`` and ``BETA`` columns
A2       - other allele
N        - sample size
CaseN    - sample size for cases (logistic regression only)
ControlN - sample size for controls (logistic regression only)
INFO     - imputation INFO score
FRQ      - frequency of A1 allele
Z        - z-score or t-score of association
BETA     - effect size; for logistic regression, this contains log(OR)
SE       - standard error of the BETA column
L95      - lower 95% confidence interval of the BETA
U95      - upper 95% confidence interval of the BETA
P        - p-value

For more information, see .log files produced by gwas.py and sebsequent runs.
''')

def merge_plink2(args, log):
    fix_and_validate_chr2use(args, log)
    pattern = args.sumstats
    stat = 'T_STAT' if  pattern.endswith('.glm.linear') else 'Z_STAT'
    effect_cols = (['BETA', "SE"] if  pattern.endswith('.glm.linear') else ['OR', 'LOG(OR)_SE'])
    ct_cols = ([] if pattern.endswith('.glm.linear') else ["CASE_ALLELE_CT", "CTRL_ALLELE_CT"])
    df=pd.concat([pd.read_csv(pattern.replace('@', chri), delim_whitespace=True)[['ID', '#CHROM', 'POS', 'REF', 'ALT', 'A1', 'A1_FREQ', 'OBS_CT', stat, 'P', 'L95', 'U95']+ct_cols+effect_cols] for chri in args.chr2use])
    df['A2'] = df['REF']; idx=df['A2']==df['A1']; df.loc[idx, 'A2']=df.loc[idx, 'ALT']; del df['REF']; del df['ALT']

    if not pattern.endswith('.glm.linear'):
        df['BETA'] = np.log(df['OR']).astype(np.float32)
        df['L95'] = np.log(df['L95']).astype(np.float32)
        df['U95'] = np.log(df['U95']).astype(np.float32)
        df.rename(columns={'LOG(OR)_SE':'SE'}, inplace=True)
        df['CaseN'] = (df['CASE_ALLELE_CT'].values / 2).astype(int)
        df['ControlN'] = (df['CTRL_ALLELE_CT'].values / 2).astype(int)
        ct_cols = ['CaseN', 'ControlN']

    df.dropna(inplace=True)
    df.rename(columns={'ID':'SNP', '#CHROM':'CHR', 'POS':'BP', 'OBS_CT':'N', stat:'Z', 'A1_FREQ':'FRQ'}, inplace=True)
    df, info_col = apply_filters(args, df)
    df[['SNP', 'CHR', 'BP', 'A1', 'A2', 'N'] + ct_cols + info_col + ['FRQ', 'Z', 'BETA', 'SE', 'L95', 'U95', 'P']].to_csv(args.out, index=False, sep='\t')
    os.system('gzip -f ' + args.out)
    write_readme_file(args)    

def merge_regenie(args, log):
    fix_and_validate_chr2use(args, log)
    pattern = args.sumstats
    df=pd.concat([pd.read_csv(pattern.replace('@', chri), delim_whitespace=True)[['ID', 'CHROM', 'BETA', 'SE', 'GENPOS', 'ALLELE0', 'ALLELE1', 'A1FREQ', 'N', 'LOG10P']] for chri in args.chr2use])
    df['P']=np.power(10, -df['LOG10P'])
    df['Z'] = -stats.norm.ppf(df['P'].values*0.5)*np.sign(df['BETA']).astype(np.float64)
    df.dropna(inplace=True)
    df.rename(columns={'ID':'SNP', 'CHROM':'CHR', 'GENPOS':'BP', 'ALLELE0':'A2', 'ALLELE1':'A1', 'A1FREQ':'FRQ'}, inplace=True)
    df, info_col = apply_filters(args, df)
    df[['SNP', 'CHR', 'BP', 'A1', 'A2', 'N'] + info_col + ['FRQ', 'Z', 'BETA', 'SE', 'P']].to_csv(args.out,index=False, sep='\t')
    os.system('gzip -f ' + args.out)
    write_readme_file(args)

def check_input_file(fname, chr2use=None):
    if (chr2use is not None) and ('@' in fname):
        for chri in chr2use:
            if not os.path.isfile(fname.replace('@', str(chri))):
                raise ValueError("Input file does not exist: {f}".format(f=fname.replace('@', str(chri))))
    else:
        if not os.path.isfile(fname):
            raise ValueError("Input file does not exist: {f}".format(f=fname))

def sec_to_str(t):
    '''Convert seconds to days:hours:minutes:seconds'''
    [d, h, m, s, n] = six.moves.reduce(lambda ll, b : divmod(ll[0], b) + ll[1:], [(t, 1), 60, 60, 24])
    f = ''
    if d > 0:
        f += '{D}d:'.format(D=d)
    if h > 0:
        f += '{H}h:'.format(H=h)
    if m > 0:
        f += '{M}m:'.format(M=m)

    f += '{S}s'.format(S=s)
    return f

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Logger(object):
    '''
    Lightweight logging.
    '''
    def __init__(self, fh, mode):
        self.fh = fh
        self.log_fh = open(fh, mode) if (fh is not None) else None

        # remove error file from previous run if it exists
        try:
            if fh is not None: os.remove(fh + '.error')
        except OSError:
            pass

    def log(self, msg):
        '''
        Print to log file and stdout with a single command.
        '''
        eprint(msg)
        if self.log_fh:
            self.log_fh.write(str(msg).rstrip() + '\n')
            self.log_fh.flush()

    def error(self, msg):
        '''
        Print to log file, error file and stdout with a single command.
        '''
        eprint(msg)
        if self.log_fh:
            self.log_fh.write(str(msg).rstrip() + '\n')
            with open(self.fh + '.error', 'w') as error_fh:
                error_fh.write(str(msg).rstrip() + '\n')

def read_fam(args, fam_file):
    log.log('reading {}...'.format(fam_file))
    fam = pd.read_csv(fam_file, delim_whitespace=True, header=None, names='FID IID FatherID MotherID SEX PHENO'.split(), dtype=str)
    log.log('done, {} rows, {} cols'.format(len(fam), fam.shape[1]))
    if args.log_sensitive: log.log(fam.head())
    if np.any(fam['IID'].duplicated()): raise(ValueError("IID column has duplicated values in --fam file"))
    return fam

def append_job(job, depends_on_previous, job_list):
    if depends_on_previous:
        job_list.append('RES=$(sbatch --dependency=afterany:${{RES##* }} {})'.format(job))
    else:
        job_list.append('RES=$(sbatch {})'.format(job))

def read_comorment_pheno(args, pheno_file, dict_file):
    log.log('reading {}...'.format(pheno_file))
    pheno = pd.read_csv(pheno_file, sep=',', dtype=str)
    log.log('done, {} rows, {} cols'.format(len(pheno), pheno.shape[1]))
    if args.log_sensitive: log.log(pheno.head())

    log.log('reading {}...'.format(pheno_file))
    pheno_dict = pd.read_csv(dict_file, sep=',')
    log.log('done, {} rows, {} cols, header:'.format(len(pheno_dict), pheno_dict.shape[1]))
    log.log(pheno_dict.head())

    # validation logic for dict file
    if 'COLUMN' in pheno_dict.columns: pheno_dict.rename(columns={'COLUMN':'FIELD'}, inplace=True)
    if 'FIELD' not in pheno_dict.columns: raise(ValueError('--dict must include FIELD column'))
    if 'TYPE' not in pheno_dict.columns: raise(ValueError('--dict must include TYPE column'))
    pheno_dict['TYPE'] = pheno_dict['TYPE'].str.upper()
    extra_values = list(set(pheno_dict['TYPE'].values).difference({'IID', 'CONTINUOUS', 'BINARY', 'NOMINAL'}))
    if len(extra_values) > 0: raise(ValueError('TYPE column in --dict can only have IID, CONTINUOUS, BINARY and NOMINAL - found other values, e.g. {}'.format(extra_values[0])))

    # validation logic for pheno file
    if 'IID' not in pheno: raise(ValueError('IID column not present in --pheno-file'))
    if np.any(pheno['IID'].duplicated()): raise(ValueError('IID column has duplicated values in --pheno-file'))
    missing_cols = [str(c) for c in pheno.columns if (c not in pheno_dict['FIELD'].values)]
    if missing_cols: raise(ValueError('--pheno-file columns not present in --dict: {}'.format(', '.join(missing_cols))))

    pheno_dict_map = dict(zip(pheno_dict['FIELD'], pheno_dict['TYPE']))
    for c in pheno.columns:
        if pheno_dict_map[c]=='BINARY':
            bad_format = pheno[~pheno[c].isnull() & ~pheno[c].isin(['1', '0'])]
            if len(bad_format)>0:
                if args.log_sensitive: log.log(bad_format.head())
                raise(ValueError('BINARY column {} has values other than 0 or 1; see above for offending rows (if not shown, re-run with --log-sensitive argument)'.format(c)))
        if pheno_dict_map[c]=='CONTINUOUS':
            pheno[c] = pheno[c].astype(float)

    return pheno, pheno_dict

###################################################
# implement parser_loci
###################################################

def tar_filter(tarinfo):
    if os.path.basename(tarinfo.name).startswith('sumstats'): return None
    return tarinfo

def clump_cleanup(args, log):
    temp_out = args.out + '.temp'
    log.log('Saving intermediate files to {out}.temp.tar.gz'.format(out=args.out))
    with tarfile.open('{out}.temp.tar.gz'.format(out=args.out), "w:gz") as tar:
        tar.add(temp_out, arcname=os.path.basename(temp_out), filter=tar_filter)
    shutil.rmtree(temp_out)

def sub_chr(s, chr):
    return s.replace('@', str(chr))

def execute_command(command, log):
    log.log("Execute command: {}".format(command))
    exit_code = subprocess.call(command.split())
    log.log('Done. Exit code: {}'.format(exit_code))
    return exit_code

def make_ranges(args_exclude_ranges, log):
    # Interpret --exclude-ranges input
    ChromosomeRange = collections.namedtuple('ChromosomeRange', ['chr', 'from_bp', 'to_bp'])
    exclude_ranges = []
    if args_exclude_ranges is not None:
        for exclude_range in args_exclude_ranges:
            try:
                range = ChromosomeRange._make([int(x) for x in exclude_range.replace(':', ' ').replace('-', ' ').split()[:3]])
            except Exception as e:
                raise(ValueError('Unable to interpret exclude range "{}", chr:from-to format is expected.'.format(exclude_range)))
            exclude_ranges.append(range)
            log.log('Exclude range: chromosome {} from BP {} to {}'.format(range.chr, range.from_bp, range.to_bp))
    return exclude_ranges

def make_loci_implementation(args, log):
    """
    Clump summary stats, produce lead SNP report, produce candidate SNP report
    TBD: refine output tables
    TBD: in snps table, do an outer merge - e.i, include SNPs that pass p-value threshold (some without locus number), and SNPs without p-value (e.i. from reference genotypes)
    """
    fix_and_validate_chr2use(args, log)    
    exclude_ranges = make_ranges(args.exclude_ranges, log)

    temp_out = args.out + '.temp'
    if not os.path.exists(temp_out):
        os.makedirs(temp_out)

    if (not args.sumstats) and (not args.sumstats_chr):
        raise ValueError('At least one of --sumstats or --sumstats-chr must be specified')

    if args.sumstats_chr:
        args.sumstats_chr = [sub_chr(args.sumstats_chr, chri) for chri in args.chr2use]
    else:
        args.sumstats_chr = ['{}/sumstats.chr{}.csv'.format(temp_out, chri) for chri in args.chr2use]

    def validate_columns(df):
        for cname in [args.clump_field, args.clump_snp_field, args.chr]:
            if cname not in df.columns:
                raise ValueError('{} column not found in {}; available columns: '.format(cname, args.sumstats, df.columns))

    if args.sumstats:
        check_input_file(args.sumstats)
        log.log('Reading {}...'.format(args.sumstats))
        df_sumstats = pd.read_csv(args.sumstats, delim_whitespace=True)
        log.log('Read {} SNPs from --sumstats file'.format(len(df_sumstats)))
        validate_columns(df_sumstats)
        for chri, df_chr_file in zip(args.chr2use, args.sumstats_chr):
            df_sumstats[df_sumstats[args.chr] == int(chri)].to_csv(df_chr_file, sep='\t',index=False)
    else:
        for df_chr_file in args.sumstats_chr:
            check_input_file(df_chr_file)
        log.log('Reading {}...'.format(args.sumstats_chr))
        df_sumstats = pd.concat([pd.read_csv(df_chr_file, delim_whitespace=True) for df_chr_file in args.sumstats_chr])
        log.log('Read {} SNPs'.format(len(df_sumstats)))

    for chri, df_chr_file in zip(reversed(args.chr2use), reversed(args.sumstats_chr)):
        # Step1 - find independent significant SNPs
        execute_command(
            "{} ".format(args.plink) +
            "--bfile {} ".format(sub_chr(args.bfile, chri)) +
            "--clump {} ".format(df_chr_file) +
            "--clump-p1 {} --clump-p2 1 ".format(args.clump_p1) +
            "--clump-r2 {} --clump-kb 1e9 ".format(args.indep_r2) +
            "--clump-snp-field {} --clump-field {} ".format(args.clump_snp_field, args.clump_field) +
            "--out {}/indep.chr{} ".format(temp_out, chri),
            log)

        if not os.path.isfile('{}/indep.chr{}.clumped'.format(temp_out, chri)):
            log.log('On CHR {} no variants pass significance threshold'.format(chri)) 
            continue

        # Step 2 - find lead SNPs by clumping together independent significant SNPs
        execute_command(
            "{} ".format(args.plink) +
            "--bfile {} ".format(sub_chr(args.bfile, chri)) +
            "--clump {} ".format('{}/indep.chr{}.clumped'.format(temp_out, chri)) +
            "--clump-p1 {} --clump-p2 1 ".format(args.clump_p1) +
            "--clump-r2 {} --clump-kb 1e9 ".format(args.lead_r2) +
            "--clump-snp-field SNP --clump-field P " +
            "--out {}/lead.chr{} ".format(temp_out, chri),
            log)

        # Step 3 - find loci around independent significant SNPs
        pd.read_csv('{}/indep.chr{}.clumped'.format(temp_out, chri), delim_whitespace=True)['SNP'].to_csv('{}/indep.chr{}.clumped.snps'.format(temp_out, chri), index=False, header=False)
        execute_command(
            "{} ".format(args.plink) + 
            "--bfile {} ".format(sub_chr(args.bfile, chri)) +
            "--r2 --ld-window {} --ld-window-r2 {} ".format(args.ld_window_kb, args.indep_r2) +
            "--ld-snp-list {out}/indep.chr{chri}.clumped.snps ".format(out=temp_out, chri=chri) +
            "--out  {out}/indep.chr{chri} ".format(out=temp_out, chri=chri),
            log)

    # find indep to lead SNP mapping (a data frame with columns 'LEAD' and 'INDEP')
    files = ["{}/lead.chr{}.clumped".format(temp_out, chri) for chri in args.chr2use]
    files = [file for file in files if os.path.isfile(file)]
    if not files: 
        log.log('WARNING: No .clumped files found - could it be that no variants pass significance threshold?')
        clump_cleanup(args, log)
        return

    lead_to_indep = []
    for file in files:
        df=pd.read_csv(file,delim_whitespace=True)
        lead_to_indep.append(pd.concat([pd.DataFrame(data=[(lead, indep_snp.split('(')[0]) for indep_snp in indep_snps.split(',') if indep_snp != 'NONE'] + [(lead, lead)], columns=['LEAD', 'INDEP']) for lead, indep_snps in zip(df['SNP'].values, df['SP2'].values)]))
    lead_to_indep = pd.concat(lead_to_indep).reset_index(drop=True)
    if lead_to_indep.duplicated(subset=['INDEP'], keep=False).any():
        raise ValueError('Some independent significant SNP belongs to to lead SNPs; this is an internal error in sumstats.py logic - please report this bug.')
    log.log('{} independent significant SNPs, {} lead SNPs'.format(len(set(lead_to_indep['INDEP'])), len(set(lead_to_indep['LEAD']))))

    # group loci together:
    # SNP_A is an indepependent significant SNP
    # SNP_B is a candidate SNP
    # LEAD_SNP is lead SNP
    # R2 is always correlation between candidate and independent significant SNP
    files = ["{out}/indep.chr{chri}.ld".format(out=temp_out, chri=chri) for chri in args.chr2use]
    files = [file for file in files if os.path.isfile(file)]
    if not files: raise ValueError('No .ld files found')
    df_cand=pd.concat([pd.read_csv(file, delim_whitespace=True) for file in files])
    df_cand=pd.merge(df_cand, lead_to_indep.rename(columns={'INDEP':'SNP_A', 'LEAD':'LEAD_SNP'}), how='left', on='SNP_A')
    df_sumstats.drop_duplicates(subset=args.clump_snp_field, inplace=True)
    df_cand = pd.merge(df_cand, df_sumstats.rename(columns={args.clump_snp_field: 'SNP_B'}), how='left', on='SNP_B')
    df_lead=df_cand.groupby(['LEAD_SNP', 'CHR_A']).agg({'BP_B':['min', 'max']})
    df_lead.reset_index(inplace=True)
    df_lead.columns=['LEAD_SNP', 'CHR_A', 'MinBP', 'MaxBP']
    df_lead=df_lead.sort_values(['CHR_A', 'MinBP']).reset_index(drop=True)
    df_lead['locusnum'] = df_lead.index + 1
    df_lead = pd.merge(df_lead, df_sumstats[[args.clump_snp_field, args.clump_field]].rename(columns={args.clump_snp_field: 'LEAD_SNP'}), how='left', on='LEAD_SNP')
    df_lead['MaxBP_locus'] = df_lead['MaxBP']
    while True:
        has_changes = False
        for i in range(1, len(df_lead)):
            if df_lead['CHR_A'][i] != df_lead['CHR_A'][i-1]: continue

            merge_to_previous = False
            if (df_lead['MinBP'][i] - df_lead['MaxBP_locus'][i-1]) < (1000 * 250):
                merge_to_previous = True
            for exrange in exclude_ranges:
                if df_lead['CHR_A'][i] != exrange.chr: continue
                if (df_lead['MaxBP_locus'][i-1] >= exrange.from_bp) and (df_lead['MinBP'][i] <= exrange.to_bp):
                    merge_to_previous = True
            if merge_to_previous and (df_lead['locusnum'][i] != df_lead['locusnum'][i-1]):
                log.log('Merge locus {} to {}'.format(df_lead['locusnum'][i], df_lead['locusnum'][i-1]))
                df_lead.loc[i, 'locusnum'] = df_lead.loc[i-1, 'locusnum']
                df_lead.loc[i, 'MaxBP_locus'] = np.max([df_lead['MaxBP_locus'][i-1], df_lead['MaxBP_locus'][i]])
                has_changes = True
                break

        if not has_changes:
            df_lead.drop(['MaxBP_locus'], axis=1, inplace=True)
            break  # exit from "while True:" loop

    df_lead['locusnum'] = df_lead['locusnum'].map({l:i+1 for (i, l) in enumerate(df_lead['locusnum'].unique())})
    df_lead['is_locus_lead'] = (df_lead[args.clump_field] == df_lead.groupby(['locusnum'])[args.clump_field].transform(min))
    df_lead = pd.merge(df_lead, df_cand[['SNP_B', 'BP_B']].drop_duplicates().rename(columns={'SNP_B':'LEAD_SNP', 'BP_B':'LEAD_BP'}), how='left', on='LEAD_SNP')
    cols = list(df_lead)
    cols.insert(0, cols.pop(cols.index('LEAD_BP')))
    cols.insert(0, cols.pop(cols.index('LEAD_SNP')))
    cols.insert(0, cols.pop(cols.index('CHR_A')))
    cols.insert(0, cols.pop(cols.index('locusnum')))
    df_lead[cols].rename(columns={'CHR_A':'CHR'}).to_csv('{}.lead.csv'.format(args.out), sep='\t', index=False)
    log.log('{} lead SNPs reported to {}.lead.csv'.format(len(df_lead), args.out))

    df_loci=df_lead.groupby(['locusnum']).agg({'MinBP':'min', 'MaxBP':'max', 'CHR_A':'min', args.clump_field:'min'})
    df_loci.reset_index(inplace=True)
    df_loci=pd.merge(df_loci, df_lead[df_lead['is_locus_lead'].values][['locusnum', 'LEAD_SNP', 'LEAD_BP']], on='locusnum', how='left')
    df_loci.rename(columns={'CHR_A':'CHR'})[['locusnum', 'CHR', 'LEAD_SNP', 'LEAD_BP', 'MinBP', 'MaxBP', args.clump_field]].to_csv('{}.loci.csv'.format(args.out), sep='\t', index=False)
    log.log('{} loci reported to {}.loci.csv'.format(len(df_loci), args.out))

    if 'BP' in df_cand: del df_cand['BP']
    if 'CHR' in df_cand: del df_cand['CHR']
    df_cand = pd.merge(df_cand, df_lead[['LEAD_SNP', 'locusnum']], how='left', on='LEAD_SNP')
    cols = list(df_cand); cols.insert(0, cols.pop(cols.index('locusnum')))
    df_cand = df_cand[cols].drop(['CHR_B'], axis=1).rename(columns={'CHR_A':'CHR', 'BP_A':'INDEP_BP', 'SNP_A':'INDEP_SNP', 'BP_B':'CAND_BP', 'SNP_B':'CAND_SNP'}).copy()
    df_cand.to_csv('{}.snps.csv'.format(args.out), sep='\t', index=False)
    log.log('{} candidate SNPs reported to {}.snps.csv'.format(len(df_cand), args.out))

    df_indep=df_cand[df_cand['CAND_SNP'] == df_cand['INDEP_SNP']].copy()
    df_indep.drop(['CAND_BP','CAND_SNP'], axis=1, inplace=True)
    df_indep.to_csv('{}.indep.csv'.format(args.out), sep='\t', index=False)
    log.log('{} independent significant SNPs reported to {}.snps.csv'.format(len(df_indep), args.out))

    clump_cleanup(args, log)

###################################################

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.out is None:
        raise ValueError('--out is required.')

    log = Logger(args.log if args.log else (args.out + '.log'), 'w')
    start_time = time.time()

    try:
        defaults = vars(parse_args([sys.argv[1]]))
        opts = vars(args)
        non_defaults = [x for x in opts.keys() if opts[x] != defaults[x]]
        header = MASTHEAD
        header += "Call: \n"
        header += './gwas.py {} \\\n'.format(sys.argv[1])
        options = ['\t--'+x.replace('_','-')+' '+str(opts[x]).replace('\t', '\\t')+' \\' for x in non_defaults]
        header += '\n'.join(options).replace('True','').replace('False','')
        header = header[0:-1]+'\n'
        log.log(header)
        log.log('Beginning analysis at {T} by {U}, host {H}'.format(T=time.ctime(), U=getpass.getuser(), H=socket.gethostname()))

        # run the analysis
        args.func(args, log)

    except Exception:
        log.error( traceback.format_exc() )
        raise

    finally:
        log.log('Analysis finished at {T}'.format(T=time.ctime()) )
        time_elapsed = round(time.time()-start_time,2)
        log.log('Total time elapsed: {T}'.format(T=sec_to_str(time_elapsed)))
