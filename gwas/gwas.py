#!/usr/bin/env python3

# README:
# gwas.py converts pheno+dict files into format compatible with plink or regenie analysis. Other association analyses can be added later.
# gwas.py automatically decides whether to run logistic or linear regression by looking at the data dictionary for requested phenotypes
# gwas.py generates all scripts needed to run the analysis, and to convert the results back to a standard summary statistics format

import argparse
import logging, time, sys, traceback, socket, getpass, six, os
import json
import yaml
import pandas as pd
import numpy as np
from scipy import stats

__version__ = '1.0.1'
MASTHEAD = "***********************************************************************\n"
MASTHEAD += "* gwas.py: pipeline for GWAS analysis\n"
MASTHEAD += "* Version {V}\n".format(V=__version__)
MASTHEAD += "* (C) 2021 Oleksandr Frei, Bayram Akdeniz and Alexey A. Shadrin\n"
MASTHEAD += "* Norwegian Centre for Mental Disorders Research / University of Oslo\n"
MASTHEAD += "* Centre for Bioinformatics / University of Oslo\n"
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

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if callable(obj):
            return str(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series) or isinstance(obj, pd.Index):
            return obj.values.tolist()
        if isinstance(obj, np.float32):
            return np.float64(obj)
        return json.JSONEncoder.default(self, obj)

def parse_args(args):
    parser = argparse.ArgumentParser(description="A pipeline for GWAS analysis")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--argsfile', type=open, action=LoadFromFile, default=None, help="file with additional command-line arguments, e.g. those configuration settings that are the same across all of your runs")
    parent_parser.add_argument("--out", type=str, default="gwas", help="prefix for the output files (<out>.covar, <out>.pheno, etc)")
    parent_parser.add_argument("--log", type=str, default=None, help="file to output log, defaults to <out>.log")
    parent_parser.add_argument("--log-append", action="store_true", default=False, help="append to existing log file. Default is to erase previous log file if it exists.")    
    parent_parser.add_argument("--log-sensitive", action="store_true", default=False, help="allow sensitive (individual-level) information in <out>.log. Use with caution. This may help debugging errors, but then you must pay close attention to avoid exporting the .log files out of your security environent. It's recommended to delete .log files after  you've investigate the problem.")

    pheno_parser = argparse.ArgumentParser(add_help=False)
    pheno_parser.add_argument("--pheno-file", type=str, default=None, help="phenotype file, according to CoMorMent spec")
    pheno_parser.add_argument("--dict-file", type=str, default=None, help="phenotype dictionary file, defaults to <pheno>.dict")
    pheno_parser.add_argument("--pheno-sep", default=',', type=str, choices=[',', 'comma', ';', 'semicolon', '\t', 'tab', ' ', 'space', 'delim-whitespace'],
        help="Delimiter to use when reading --pheno-file (',' ';' $' ', $'\\t' or 'delim-whitespace', the later triggers delim_whitespace=True option in pandas")
    pheno_parser.add_argument("--dict-sep", default=None, type=str, choices=[None, ',', 'comma', ';', 'semicolon', '\t', 'tab', ' ', 'space', 'delim-whitespace'],
        help="Delimiter to use when reading --dict-file; by default uses delimiter provided to --pheno-sep")
    pheno_parser.add_argument("--fam", type=str, default=None, help="an argument pointing to a plink's .fam file, use by gwas.py script to pre-filter phenotype information (--pheno) with the set of individuals available in the genetic file (--geno-file / --geno-fit-file). Optional when either --geno-file (or --geno-fit-file) is in plink's format, otherwise required - but IID in this file must be consistent with identifiers of the genetic file.")
    pheno_parser.add_argument("--bim", type=str, default=None, help="an optional argument pointing to a plink's .bim file, used by gwas.py script whenever it needs to know genomic positions or marker names (for example, this is needed when SAIGE GWAS uses --chunk-size-bp option)")
    pheno_parser.add_argument("--pheno", type=str, default=[], nargs='+', help="target phenotypes to run GWAS (must be columns of the --pheno-file")
    pheno_parser.add_argument("--covar", type=str, default=[], nargs='+', help="covariates to control for (must be columns of the --pheno-file); individuals with missing values for any covariates will be excluded not just from <out>.covar, but also from <out>.pheno file")
    pheno_parser.add_argument("--variance-standardize", type=str, default=None, nargs='*', help="the list of continuous phenotypes to standardize variance; accept the list of columns from the --pheno file (if empty, applied to all); doesn't apply to dummy variables derived from NOMINAL or BINARY covariates.")
    pheno_parser.add_argument("--keep", type=str, default=[], nargs='+', help="filename(s) with IID identifiers to keep for GWAS analysis; see https://www.cog-genomics.org/plink/2.0/filter#sample for more details.")
    pheno_parser.add_argument("--remove", type=str, default=[], nargs='+', help="filename(s) with IID identifiers to remove from GWAS analysis;  this option takes precedence over --remove option, i.e. when both lists are provided, an individual will be removed as long as it's specified in --remove list (even if it's also present in --keep)")
    pheno_parser.add_argument('--config', type=str, default="config.yaml", help="file with misc configuration options")

    # filtering options
    filter_parser = argparse.ArgumentParser(add_help=False)
    filter_parser.add_argument("--info-file", type=str, default=None, help="File with SNP and INFO columns. Values in SNP column must be unique.")
    filter_parser.add_argument("--info", type=float, default=None, help="threshold for filtering on imputation INFO score")
    filter_parser.add_argument("--maf", type=float, default=None, help="threshold for filtering on minor allele frequency")
    filter_parser.add_argument("--hwe", type=float, default=None, help="threshold for filtering on hardy weinberg equilibrium p-value")
    filter_parser.add_argument("--geno", type=float, default=None, help="threshold for filtering on per-variant missingness rate)")

    subparsers = parser.add_subparsers(dest='cmd')
    subparsers.required = True

    parser_gwas_add_arguments(args=args, func=execute_gwas, parser=subparsers.add_parser("gwas", parents=[parent_parser, pheno_parser, filter_parser], help='perform GWAS (genome-wide association) analysis'))
    parser_pgrs_add_arguments(args=args, func=execute_pgrs, parser=subparsers.add_parser("pgrs", parents=[parent_parser, pheno_parser], help='compute polygenic risk score'))
    
    parser_merge_plink2_add_arguments(args=args, func=merge_plink2, parser=subparsers.add_parser("merge-plink2", parents=[parent_parser, filter_parser], help='merge plink2 sumstats files'))
    parser_merge_regenie_add_arguments(args=args, func=merge_regenie, parser=subparsers.add_parser("merge-regenie", parents=[parent_parser, filter_parser], help='merge regenie sumstats files'))
    parser_merge_saige_add_arguments(args=args, func=merge_saige, parser=subparsers.add_parser("merge-saige", parents=[parent_parser, filter_parser], help='merge saige sumstats files'))

    return parser.parse_args(args)

# compute polygenic risk scores
def parser_pgrs_add_arguments(args, func, parser):
    parser.add_argument("--geno-file", type=str, default=None, help="required argument pointing to a genetic file: (1) plink's .bed file, or (2) .bgen file, or (3) .pgen file, or (4) .vcf file. Note that a full name of .bed (or .bgen, .pgen, .vcf) file is expected here. Corresponding files should have standard names, e.g. for plink's format it is expected that .fam and .bim file can be obtained by replacing .bed extension accordingly. supports '@' as a place holder for chromosome labels")
    parser.add_argument("--geno-ld-file", type=str, default=None, help="plink file to use for LD structure estimation")
    parser.add_argument("--sumstats", type=str, help="Input file with summary statistics")
    parser.add_argument('--analysis', type=str, default=['prsice2'], nargs='+', choices=['prsice2'], help='list of analyses to perform.')
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use, (e.g. 1,2,3 or 1-4,12,16-20).")
    parser.add_argument("--clump-p1", type=float, nargs='+', default=[5e-8, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.05, 0.1, 0.5, 1.0], help="p-value threshold for independent significant SNPs.")
    parser.add_argument("--keep-ambig", action="store_true", help='Keep ambiguous SNPs. Only use this option if you are certain that the base and target has the same A1 and A2 alleles')
    parser.set_defaults(func=func)

def parser_gwas_add_arguments(args, func, parser):
    # genetic files to use. All must share the same set of individuals. Currently this assumption is not validated.
    parser.add_argument("--geno-file", type=str, default=None, help="required argument pointing to a genetic file: (1) plink's .bed file, or (2) .bgen file, or (3) .pgen file, or (4) .vcf file. Note that a full name of .bed (or .bgen, .pgen, .vcf, .or .vcf.gz) file is expected here. Corresponding files should have standard names, e.g. for plink's format it is expected that .fam and .bim file can be obtained by replacing .bed extension accordingly. supports '@' as a place holder for chromosome labels")
    parser.add_argument("--geno-fit-file", type=str, default=None, help="genetic file to use in a first stage of mixed effect model. Expected to have the same set of individuals as --geno-file (this is NOT validated by the gwas.py script, and it is your responsibility to follow this assumption). Optional for standard association analysis (e.g. if for plink's glm). The argument supports the same file types as the --geno-file argument. Noes not support '@' (because mixed effect tools typically expect a single file at the first stage.")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use "
         "(e.g. 1,2,3 or 1-4,12,16-20). Used when '@' is present in --geno-file, and allows to specify for which chromosomes to run the association testing.")
    parser.add_argument("--chunk-size-bp", type=int, default=None, help="chunk size (in base pairs); used when GWAS is done with SAIGE; require --bim argument")

    parser.add_argument('--analysis', type=str, default=['plink2', 'figures'],
        nargs='+', choices=['plink2', 'regenie', 'saige', 'figures'],
        help='list of analyses to perform. '
        '"plink2", "saige" and "regenie" options can not be combined. ' 
        '"figures" option can be added to plink2/regenie/saige commands. ')

    parser.add_argument('--vcf-field', type=str, default='DS', choices=['DS', 'GT'], help='field to read for vcf files')
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

def parser_merge_saige_add_arguments(args, func, parser):
    parser.add_argument("--sumstats", type=str, default=None, help="sumstat file produced by plink2, containing @ as chromosome label place holder")
    parser.add_argument("--basename", type=str, default=None, help="basename for .vmiss, .afreq and .hardy files, with @ as chromosome label place holder")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use, (e.g. 1,2,3 or 1-4,12,16-20).")
    parser.add_argument("--chunks", type=int, default=None, help="How many chunks to merge; mutually exclusive with --chr2use")
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
    return fname.endswith('.vcf') or fname.endswith('.vcf.gz')
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

def fix_and_validate_pheno_args(args, log):
    if not args.pheno_file: raise ValueError('--pheno-file is required.')
    if not args.pheno: raise ValueError('--pheno is required.')

    if len(set(args.pheno)) != len(args.pheno):
        raise ValueError('check you --pheno argument, some phenotypes listed more then once')
    if len(set(args.covar)) != len(args.covar):
        raise ValueError('check you --covar argument, some covariates listed more then once')

    # '\s+' is equivalent to delim_whitespace=True option in pandas.read_csv
    sep_map = {'delim-whitespace': '\s+', 'comma':',', 'semicolon':';', 'tab':'\t', 'space':' '}
    if args.pheno_sep in sep_map: args.pheno_sep = sep_map[args.pheno_sep]
    if args.dict_sep is None: args.dict_sep = args.pheno_sep
    if args.dict_sep in sep_map: args.dict_sep = sep_map[args.dict_sep]

    # validate that some of genetic data is provided as input
    if not args.geno_file:
        raise ValueError('--geno-file must be specified')

    if args.fam is None:
        if is_bed_file(args.geno_file):
            args.fam = replace_suffix(args.geno_file, '.bed', '.fam')
        elif ('geno_fit_file' in vars(args)) and is_bed_file(args.geno_fit_file):
            args.fam = replace_suffix(args.geno_fit_file, '.bed', '.fam')
        else:
            raise ValueError('please specify --fam argument in plink format, containing the same set of individuals as your --geno-file / --geno-fit-file')
        if '@' in args.fam: args.fam = args.fam.replace('@', args.chr2use[0])
    check_input_file(args.fam)

    check_input_file(args.pheno_file)
    if not args.dict_file: args.dict_file = args.pheno_file + '.dict'
    check_input_file(args.dict_file)
    for fname in args.keep: check_input_file(fname)
    for fname in args.remove: check_input_file(fname)

def fix_and_validate_gwas_args(args, log):
    if len(set(['plink2', 'regenie', 'saige']).intersection(set(args.analysis))) > 1:
        raise ValueError('--analysis can have only one of plink2, regenie, saige; please choose one of these.')

    if (args.info is not None) or (args.info_file is not None):
        if (args.info is None) or (args.info_file is None):
            raise ValueError('both --info and --info-file must be used at the same time')
        check_input_file(args.info_file, chr2use=args.chr2use)

    if ('regenie' in args.analysis) and (not args.geno_fit_file):
        raise ValueError('--geno-fit-file must be specified for --analysis regenie')

    if ('saige' in args.analysis) and (not args.geno_fit_file):
        raise ValueError('--geno-fit-file must be specified for --analysis saige')

    if ('saige' in args.analysis) and (args.chunk_size_bp is not None) and (not args.bim):
        raise ValueError('--bim must be specified together with --chunk-size-bp in case of --analysis saige')

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
        " --out {}.step1".format(args.out) + \
        (" --bed {} --ref-first".format(remove_suffix(geno_fit_file, '.bed')) if is_bed_file(geno_fit_file) else "") + \
        (" --pgen {} --ref-first".format(remove_suffix(geno_fit_file, '.pgen')) if is_pgen_file(geno_fit_file) else "") + \
        (" --bgen {} --ref-first".format(geno_fit_file) if is_bgen_file(geno_fit_file) else "") + \
        (" --bt" if logistic else "") + \
        " --lowmem --lowmem-prefix {}_tmp_preds".format(args.out)

    cmd_step2 = ' --step 2 --bsize 400' + \
        " --out {}_chr${{SLURM_ARRAY_TASK_ID}}".format(args.out) + \
        (" --bed {} --ref-first".format(remove_suffix(geno_file, '.bed')) if  is_bed_file(geno_file) else "") + \
        (" --pgen {} --ref-first".format(remove_suffix(geno_file, '.pgen')) if is_pgen_file(geno_file) else "") + \
        (" --bgen {} --ref-first --sample {}".format(geno_file, sample) if is_bgen_file(geno_file) else "") + \
        (" --bt --firth 0.01 --approx" if logistic else "") + \
        " --pred {}.step1_pred.list".format(args.out) + \
        " --chr ${SLURM_ARRAY_TASK_ID}"

    return (cmd + cmd_step1) if step==1 else (cmd + cmd_step2)

def make_saige_commands(args, logistic, step):
    geno_fit_file = args.geno_fit_file
    geno_file = args.geno_file.replace('@', '${SLURM_ARRAY_TASK_ID}')

    use_chunks = (args.chunk_size_bp is not None)
    if use_chunks:
        bim = read_bim(args, args.bim)
        chunk_def = {'chr':[], 'chunk':[], 'num_snps_in_chunk':[], 'a':[], 'b':[]}
        chunk_index = 0
        for chr_label in args.chr2use:
            bim_chr = bim[bim['CHR'].astype(str) == chr_label]

            min_bp = 1e6 * int(bim_chr.BP.min()/1e6)
            max_bp = bim_chr.BP.max() + 1

            chunks=[(x, x+args.chunk_size_bp) for x in range(int(min_bp), int(max_bp), int(args.chunk_size_bp))]
            for (a, b) in chunks:
                num_snps = np.sum((bim_chr.BP > a) & (bim_chr.BP <= b))
                if num_snps == 0: continue
                chunk_index += 1
                chunk_def['chr'].append(chr_label)
                chunk_def['chunk'].append(chunk_index)
                chunk_def['a'].append(a)
                chunk_def['b'].append(b)
                chunk_def['num_snps_in_chunk'].append(num_snps)

        chrom_def = ' '.join(['[{}]={}'.format(index+1, value) for index, value in enumerate(chunk_def['chr'])])
        start_def = ' '.join(['[{}]={}'.format(index+1, value+1) for index, value in enumerate(chunk_def['a'])])
        end_def = ' '.join(['[{}]={}'.format(index+1, value) for index, value in enumerate(chunk_def['b'])])
        snps_def = ' '.join(['[{}]={}'.format(index+1, value) for index, value in enumerate(chunk_def['num_snps_in_chunk'])])
        array_spec = [str(x) for x in range(1, len(chunk_def['chr']) + 1)]
    else:
        array_spec = args.chr2use

    if ('@' in geno_fit_file): raise(ValueError('--geno-fit-file contains "@", hense it is incompatible with SAIGE step1 which require a single file'))
    if (is_pgen_file(geno_fit_file) or is_pgen_file(geno_file)): raise(ValueError('--geno-file / --geno-fit-file can not point to plink2 pgen file for SAIGE analysis'))

    cmd_step1 = ''; cmd_step2 = ''

    for pheno_index, pheno in enumerate(args.pheno):
        cmd_step1 += '\n$SAIGE step1_fitNULLGLMM.R ' + \
            (" --plinkFile={} ".format(remove_suffix(geno_fit_file, '.bed')) if is_bed_file(geno_fit_file) else "") + \
            (" --vcfFile={f} --vcfFileIndex={f}.tbi --vcfField={vf} ".format(f=geno_fit_file, vf=args.vcf_field) if is_vcf_file(geno_fit_file) else "") + \
            (" --bgenFile={f} --bgenFileIndex={f}.bgi ".format(f=geno_fit_file) if is_bgen_file(geno_fit_file) else "") + \
            " --phenoFile={}.pheno".format(args.out) + \
            " --phenoCol={}".format(pheno) + \
            " --covarColList={}".format(','.join(args.covar)) + \
            " --sampleIDColinphenoFil=IID " + \
            " --traitType={}".format('binary' if logistic else 'quantitative') + \
            " --outputPrefix={}_{}.step1".format(args.out, pheno) + \
            " --nThreads={} ".format(args.config_object['slurm']['cpus_per_task']) + \
            " --LOCO=TRUE " + \
            " --minMAFforGRM=0.01" + \
            " --tauInit=1,0 "

        if use_chunks and (pheno_index==0):
            cmd_step2 += f"\ndeclare -A CHUNKS_CHR=({chrom_def})"
            cmd_step2 += f"\ndeclare -A CHUNKS_START=({start_def})"
            cmd_step2 += f"\ndeclare -A CHUNKS_END=({end_def})"
            cmd_step2 += f"\ndeclare -A CHUNKS_SNPS=({snps_def})"
            cmd_step2 += "\n"

        cmd_step2 += '\n$SAIGE step2_SPAtests.R ' + \
            (" --plinkFile={} ".format(remove_suffix(geno_file, '.bed')) if is_bed_file(geno_file) else "") + \
            (" --vcfFile={f} --vcfFileIndex={f}.tbi --vcfField={vf} ".format(f=geno_file, vf=args.vcf_field) if is_vcf_file(geno_file) else "") + \
            (" --bgenFile={f} --bgenFileIndex={f}.bgi ".format(f=geno_file) if is_bgen_file(geno_file) else "") + \
            (" --chr ${SLURM_ARRAY_TASK_ID}" if (not use_chunks) else "") + \
            (" --chr ${CHUNKS_CHR[${SLURM_ARRAY_TASK_ID}]}" if (use_chunks) else "") + \
            (" --start ${CHUNKS_START[${SLURM_ARRAY_TASK_ID}]}" if (use_chunks) else "") + \
            (" --end ${CHUNKS_END[${SLURM_ARRAY_TASK_ID}]}" if (use_chunks) else "") + \
            (" --minMAF={}".format(args.maf) if (args.maf is not None) else '') + \
            " --minMAC=1" + \
            " --sampleFile={}.sample".format(args.out) + \
            " --GMMATmodelFile={}_{}.step1.rda".format(args.out, pheno) + \
            " --varianceRatioFile={}_{}.step1.varianceRatio.txt".format(args.out, pheno) + \
            (" --SAIGEOutputFile={}_chunk${{SLURM_ARRAY_TASK_ID}}_{}.saige".format(args.out, pheno) if use_chunks else "") + \
            (" --SAIGEOutputFile={}_chr${{SLURM_ARRAY_TASK_ID}}_{}.saige".format(args.out, pheno) if not use_chunks else "") + \
            " --numLinesOutput=2" + \
            (" --IsOutputAFinCaseCtrl=TRUE" if logistic else '')+ \
            (" --IsOutputNinCaseCtrl=TRUE" if logistic else '') + \
            " --LOCO=TRUE "

    return (cmd_step1, None) if step==1 else (cmd_step2, array_spec)

# this function works similarly to ** in python:
# all args from args_list that are not None are passed to the caller
# see make_regenie_merge and make_plink2_merge for a usage example.
def pass_arguments_along(args, args_list):
    opts = vars(args)
    vals = [opts[arg.replace('-', '_')] for arg in args_list]
    return ''.join([(' --{} {} '.format(arg, '' if (val==True) else val) if val else '') for arg, val in zip(args_list, vals)])

def make_figures_commands(args):
    cmd = ''
    for pheno in args.pheno:
        Rcmd = 'library(data.table);library(qqman);library(ggplot2);'
        Rcmd += 'library(GWASTools);'
        Rcmd += 'df=read.table("{out}_{pheno}.gz", header=TRUE);'.format(out=args.out, pheno=pheno)
        Rcmd += 'png("{out}_{pheno}.qq.png", width=600, unit="px", pointsize=12, bg="white");'.format(out=args.out, pheno=pheno)
        Rcmd += 'qqPlot(df$P, ci=T, main="{pheno}");'.format(pheno=pheno)
        Rcmd += 'dev.off();'
        Rcmd += 'df=df[df$P < 0.05, ];'
        Rcmd += 'png("{out}_{pheno}.manh.png", width=1200, unit="px", pointsize=12, bg="white");'.format(out=args.out, pheno=pheno)
        Rcmd += 'manhattan(df, chr="CHR", bp="BP", snp="SNP", p="P", main="{pheno}");'.format(pheno=pheno)
        Rcmd += 'dev.off();'
        cmd += "$RSCRIPT -e '{}'\n".format(Rcmd)
    return cmd

def make_regenie_merge_commands(args, logistic):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py merge-regenie ' + \
            pass_arguments_along(args, ['info-file', 'info', 'maf', 'hwe', 'geno']) + \
            ' --sumstats {out}_chr@_{pheno}.regenie'.format(out=args.out, pheno=pheno) + \
            ' --basename {out}_chr@'.format(out=args.out) + \
            ' --out {out}_{pheno} '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use)) + \
            '\n'
    return cmd

def make_saige_merge_commands(args, logistic, array_spec):
    cmd = ''
    use_chunks = (args.chunk_size_bp is not None)
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py merge-saige ' + \
            pass_arguments_along(args, ['info-file', 'info', 'maf', 'hwe', 'geno']) + \
            (' --sumstats {out}_chr@_{pheno}.saige'.format(out=args.out, pheno=pheno) if (not use_chunks) else "") + \
            (' --sumstats {out}_chunk@_{pheno}.saige'.format(out=args.out, pheno=pheno) if use_chunks else "") + \
            ' --basename {out}_chr@'.format(out=args.out) + \
            ' --out {out}_{pheno} '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use)) + \
            (' --chunks {}'.format(len(array_spec)) if use_chunks else "") + \
            '\n'
    return cmd

def make_plink2_merge_commands(args, logistic):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py merge-plink2 ' + \
            pass_arguments_along(args, ['info-file', 'info', 'maf', 'hwe', 'geno']) + \
            ' --sumstats {out}_chr@.{pheno}.glm.{what}'.format(out=args.out, pheno=pheno, what=('logistic' if logistic else 'linear')) + \
            ' --basename {out}_chr@'.format(out=args.out) + \
            ' --out {out}_{pheno} '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use)) + \
            '\n'
    return cmd

def make_plink2_commands(args):
    geno_file = args.geno_file.replace('@', '${SLURM_ARRAY_TASK_ID}')

    cmd = "$PLINK2 " + \
        (" --bfile {} --no-pheno".format(remove_suffix(geno_file ,'.bed')) if is_bed_file(geno_file) else "") + \
        (" --pfile {} --no-pheno".format(remove_suffix(geno_file ,'.pgen')) if is_pgen_file(geno_file) else "") + \
        (" --bgen {} ref-first --sample {}".format(geno_file, replace_suffix(geno_file, ".bgen", ".sample")) if is_bgen_file(geno_file) else "") + \
        (" --vcf {} --double-id".format(geno_file) if is_vcf_file(geno_file) else "") + \
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

def make_prsice2_commands(args, logistic):
    geno_file = args.geno_file.replace('@', '${SLURM_ARRAY_TASK_ID}')

    cmd = "$PRSICE2 " + \
        " --base {} ".format(args.sumstats) + \
        " --binary-target {}".format(','.join([('T' if logistic else 'F') for pheno in args.pheno])) + \
        " --pheno {}.pheno".format(args.out) + \
        " --pheno-col {}".format(','.join(args.pheno)) + \
        " --target {}".format(remove_suffix(geno_file ,'.bed')) + \
        " --type {}".format('bgen' if is_bgen_file(geno_file) else 'bed') + \
        " --ld {}".format(remove_suffix(args.geno_ld_file ,'.bed')) + \
        " --ld-type {}".format('bgen' if is_bgen_file(args.geno_ld_file) else 'bed') + \
        " --cov {}.covar".format(args.out) + \
        " --bar-levels {} --fastscore --no-full".format(','.join([str(x) for x in args.clump_p1])) + \
        " --out {}".format(args.out) + \
        pass_arguments_along(args, ['keep-ambig']) \

    return cmd

def make_slurm_header(args, array_spec=None):
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
export RSCRIPT="singularity exec --home $PWD:/home $SIF/r.sif Rscript"
export PRSICE2="singularity exec --home $PWD:/home $SIF/gwas.sif PRSice_linux"
export SAIGE="singularity exec --home $PWD:/home $SIF/saige.sif"

""".format(array="#SBATCH --array={}".format(','.join(array_spec)) if (array_spec is not None) else "",
           modules = '\n'.join(['module load {}'.format(x) for x in args.config_object['slurm']['module_load']]),
           job_name = args.config_object['slurm']['job_name'],
           account = args.config_object['slurm']['account'],
           time = args.config_object['slurm']['time'],
           cpus_per_task = args.config_object['slurm']['cpus_per_task'],
           mem_per_cpu = args.config_object['slurm']['mem_per_cpu'],
           comorment_folder = args.config_object['comorment_folder'],
           singularity_bind = args.config_object['singularity_bind'])

def prepare_covar_and_phenofiles(args, log, cc12, join_covar_into_pheno):
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

    if 'FID' in pheno.columns:
        log.log("FID column is present in --pheno-file; this values will be ignored and replaced with FID column from --fam file")
        del pheno['FID']

    log.log("merging --pheno and --fam file...")
    num_jobs = len(pheno); pheno = pd.merge(pheno, fam[['IID', 'FID']], on='IID', how='inner')
    pheno_dict_map['FID'] = 'FID'
    log.log("n={} individuals remain after merging, n={} removed".format(len(pheno), num_jobs-len(pheno)))

    if args.covar:
        missing_cols = [str(c) for c in args.covar if (c not in pheno.columns)]
        if missing_cols: raise(ValueError('--covar not present in --pheno-file: {}'.format(', '.join(missing_cols))))

        log.log("filtering individuals with missing covariates...")
        for var in args.covar:
            mask = pheno[var].isnull()
            if np.any(mask):
                num_jobs = len(pheno)
                pheno = pheno[~mask].copy()
                log.log("n={} individuals remain after removing n={} individuals with missing value in {} covariate".format(len(pheno), num_jobs-len(pheno), var))

    if len(pheno) <= 1:
        raise ValueError('Too few individuals remain for analysis, exit.')

    if args.variance_standardize is not None:
        if len(args.variance_standardize) == 0:
            args.variance_standardize = [col for col in pheno.columns if (pheno_dict_map[col] == 'CONTINUOUS')]

        for col in args.variance_standardize:
            if (col not in pheno.columns) or (pheno_dict_map[col] != 'CONTINUOUS'):
                raise ValueError(
                    f"Can not apply --variance-standardize to {col},"
                    " column is missing or its type is other than CONTINUOUS"
                )

            mean = np.nanmean(pheno[col].values)
            std = np.nanstd(pheno[col].values, ddof=1)
            if np.isclose(std, 0, atol=1e-6):
                raise ValueError(
                    "Can not apply --variance-standardize to"
                    f" {col}, column has no variation"
                    )
            log.log('phenotype {} has mean {:.5f} and std {:.5f}. Normalizing to 0.0 mean and 1.0 std'.format(col, mean, std))
            pheno[col] = (pheno[col].values - mean) / std

    if not join_covar_into_pheno:
        log.log("extracting covariates...")
        if args.covar:
            covar_output = extract_variables(pheno, args.covar, pheno_dict_map, log)
            log.log('writing {} columns (including FID, IID) for n={} individuals to {}.covar'.format(covar_output.shape[1], len(covar_output), args.out))
            covar_output.to_csv(args.out + '.covar', index=False, sep='\t')
        else:
            log.log('--covar not specified')

    log.log("extracting phenotypes{}...".format(' and covariates' if join_covar_into_pheno else ''))
    pheno_and_covar_cols = args.pheno + (args.covar if join_covar_into_pheno else [])
    pheno_output = extract_variables(pheno, pheno_and_covar_cols, pheno_dict_map, log)
    for var in pheno_and_covar_cols:
        if pheno_dict_map[var]=='BINARY':
            log.log('variable: {} ({}), cases: {}, controls: {}, missing: {}'.format(var, pheno_dict_map[var], np.sum(pheno[var]=='1'), np.sum(pheno[var]=='0'), np.sum(pheno[var].isnull())))
        elif pheno_dict_map[var] in ['NOMINAL', 'ORDINAL']:
            counts = '; '.join(["'{}' - {}".format(val, np.sum(pheno[var]==val)) for val in pheno[var].unique()])
            log.log('variable: {} ({}), value counts: {}'.format(var, pheno_dict_map[var], counts))
        else:
            log.log('variable: {} ({}), missing: {}'.format(var, pheno_dict_map[var], np.sum(pheno[var].isnull())))

    if cc12 and (pheno_type=='BINARY'):
        log.log('mapping case/control variables from 1/0 to 2/1 coding')
        for var in args.pheno:
            pheno_output[var] = pheno_output[var].map({'0':'1', '1':'2'}).values

    log.log('writing {} columns (including FID, IID) for n={} individuals to {}.pheno'.format(pheno_output.shape[1], len(pheno_output), args.out))
    pheno_output.to_csv(args.out + '.pheno', na_rep='NA', index=False, sep='\t')
    fam[['IID']].to_csv(args.out + '.sample', na_rep='NA', header=None, index=False, sep='\t')

    if join_covar_into_pheno:
        # update args.covar so that it reflects dummies
        args.covar = [col for col in pheno_output.columns if (col not in (['IID', 'FID'] + args.pheno))]

    log.log('all --pheno variables have type: {}'.format(pheno_type))
    return pheno_type    

def execute_pgrs(args, log):
    fix_and_validate_chr2use(args, log)
    fix_and_validate_pheno_args(args, log)

    if not args.geno_file: raise ValueError('--geno-file is required.')
    if (not is_bed_file(args.geno_file)) and (not is_bgen_file(args.geno_file)): raise ValueError('--geno-file must be .bed or .bgen')

    if not args.geno_ld_file: raise ValueError('--geno-ld-file is required.')
    if (not is_bed_file(args.geno_ld_file)) and (not is_bgen_file(args.geno_ld_file)): raise ValueError('--geno-ld-file must be .bed or .bgen')
    

    pheno_type = prepare_covar_and_phenofiles(args, log, cc12=True, join_covar_into_pheno=False)
    logistic = (pheno_type=='BINARY')

    cmd_file = args.out + '_cmd.sh'
    if os.path.exists(cmd_file): os.remove(cmd_file)
    submit_jobs = []

    num_jobs=0

    if 'prsice2' in args.analysis:
        commands = [make_prsice2_commands(args, logistic)]
        num_jobs = append_job(args, commands, args.chr2use, num_jobs+1, cmd_file, submit_jobs)

    log.log('To submit all jobs via SLURM, use the following scripts, otherwise execute commands from {}'.format(cmd_file))
    print('\n'.join(submit_jobs))

def execute_gwas(args, log):
    fix_and_validate_chr2use(args, log)
    fix_and_validate_pheno_args(args, log)
    fix_and_validate_gwas_args(args, log)

    cc12 = ('plink2' in args.analysis)  # for plink, case=2, control=1; other tools use case=1, control=0
    join_covar_into_pheno = ('saige' in args.analysis)  # SAIGE require covars and target phenotype to be in the same file
    pheno_type = prepare_covar_and_phenofiles(args, log, cc12, join_covar_into_pheno=join_covar_into_pheno)
    logistic = (pheno_type=='BINARY')
    log.log('selected analysis: {}'.format('logistic' if logistic else 'linear'))

    cmd_file = args.out + '_cmd.sh'
    if os.path.exists(cmd_file): os.remove(cmd_file)
    submit_jobs = []

    num_jobs=0

    if 'plink2' in args.analysis:
        commands = [make_plink2_info_commands(args),
                    make_plink2_glm_commands(args, logistic)]
        num_jobs = append_job(args, commands, args.chr2use, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_plink2_merge_commands(args, logistic)]
        num_jobs = append_job(args, commands, None, num_jobs+1, cmd_file, submit_jobs)

    if 'regenie' in args.analysis:
        commands = [make_regenie_commands(args, logistic, step=1)]
        num_jobs = append_job(args, commands, None, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_plink2_info_commands(args), make_regenie_commands(args, logistic, step=2)]
        num_jobs = append_job(args, commands, args.chr2use, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_regenie_merge_commands(args, logistic)]
        num_jobs = append_job(args, commands, None, num_jobs+1, cmd_file, submit_jobs)

    if 'saige' in args.analysis:
        command, _ = make_saige_commands(args, logistic, step=1)
        num_jobs = append_job(args, [command], None, num_jobs+1, cmd_file, submit_jobs)

        cpus_per_task = args.config_object['slurm']['cpus_per_task']
        args.config_object['slurm']['cpus_per_task'] = args.config_object['saige']['cpus_per_task_stage2']
        command, array_spec = make_saige_commands(args, logistic, step=2)
        num_jobs = append_job(args, [command], array_spec, num_jobs+1, cmd_file, submit_jobs)
        args.config_object['slurm']['cpus_per_task'] = cpus_per_task

        commands = [make_plink2_info_commands(args)]
        num_jobs = append_job(args, commands, args.chr2use, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_saige_merge_commands(args, logistic, array_spec)]
        num_jobs = append_job(args, commands, None, num_jobs+1, cmd_file, submit_jobs)

    commands = []
    if 'figures' in args.analysis: commands.append(make_figures_commands(args))
    if commands:
        num_jobs = append_job(args, commands, None, num_jobs+1, cmd_file, submit_jobs)

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
        if np.any(info['SNP'].duplicated()): raise(ValueError("SNP column has duplicated values in --info-file file"))
        log.log('done, {} rows, {} cols'.format(len(info), info.shape[1]))

        log.log("merging --sumstats (n={} rows) and --info-file...".format(len(df)))
        df = pd.merge(df, info, how='inner', on='SNP')
        log.log("n={} SNPs remain after merging, n={} with missing INFO score".format(len(df), np.sum(df['INFO'].isnull())))

        n = len(df); df = df[~(df['INFO'] < args.info)].copy()
        log.log("n={} SNPs remain after filtering INFO>={}, n={} removed".format(len(df), args.info, n-len(df)))
        info_col = ['INFO']

    if args.maf is not None:
        maf=pd.concat([pd.read_csv(args.basename.replace('@', chri) + '.afreq', delim_whitespace=True)[['ID', 'ALT_FREQS']] for chri in args.chr2use])
        if np.any(maf['ID'].duplicated()): raise(ValueError("ID column has duplicated values in {}.afreq file - have your .bim file had duplicated SNPs?".format(args.basename)))
        maf.rename(columns={'ID':'SNP'}, inplace=True)
        df = pd.merge(df, maf, how='left', on='SNP')
        n=len(df); df = df[(df['ALT_FREQS'] >= args.maf) & (df['ALT_FREQS'] <= (1-args.maf))].copy()
        log.log("n={} SNPs remain after filtering allele frequency on {}<=FRQ<={}, n={} removed".format(len(df), args.maf, 1-args.maf, n-len(df)))

    if args.hwe is not None:
        hwe=pd.concat([pd.read_csv(args.basename.replace('@', chri) + '.hardy', delim_whitespace=True)[['ID', 'P']] for chri in args.chr2use])
        if np.any(hwe['ID'].duplicated()): raise(ValueError("ID column has duplicated values in {}.hardy file - have your .bim file had duplicated SNPs?".format(args.basename)))
        hwe.rename(columns={'ID':'SNP', 'P':'P_HWE'}, inplace=True)
        df = pd.merge(df, hwe, how='left', on='SNP')
        n=len(df); df = df[df['P_HWE'] >= args.hwe].copy()
        log.log("n={} SNPs remain after filtering Hardy Weinberg equilibrium P>={}, n={} removed".format(len(df), args.hwe, n-len(df)))
        del df['P_HWE']

    if args.geno is not None:
        vmiss=pd.concat([pd.read_csv(args.basename.replace('@', chri) + '.vmiss', delim_whitespace=True)[['ID', 'F_MISS']] for chri in args.chr2use])
        if np.any(vmiss['ID'].duplicated()): raise(ValueError("ID column has duplicated values in {}.vmiss file - have your .bim file had duplicated SNPs?".format(args.basename)))
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
    check_input_file(pattern, args.chr2use)
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
    check_input_file(pattern, args.chr2use)
    df=pd.concat([pd.read_csv(pattern.replace('@', chri), delim_whitespace=True)[['ID', 'CHROM', 'BETA', 'SE', 'GENPOS', 'ALLELE0', 'ALLELE1', 'A1FREQ', 'N', 'LOG10P']] for chri in args.chr2use])
    df['P']=np.power(10, -df['LOG10P'])
    df['Z'] = -stats.norm.ppf(df['P'].values*0.5)*np.sign(df['BETA']).astype(np.float64)
    df.dropna(inplace=True)
    df.rename(columns={'ID':'SNP', 'CHROM':'CHR', 'GENPOS':'BP', 'ALLELE0':'A2', 'ALLELE1':'A1', 'A1FREQ':'FRQ'}, inplace=True)
    df, info_col = apply_filters(args, df)
    df[['SNP', 'CHR', 'BP', 'A1', 'A2', 'N'] + info_col + ['FRQ', 'Z', 'BETA', 'SE', 'P']].to_csv(args.out,index=False, sep='\t')
    os.system('gzip -f ' + args.out)
    write_readme_file(args)

def merge_saige(args, log):
    # quantitative GWAS columns: CHR POS SNPID Allele1 Allele2 AC_Allele2 AF_Allele2 imputationInfo N BETA SE Tstat p.value varT varTstar
    # binary GWAS columns:       CHR POS SNPID Allele1 Allele2 AC_Allele2 AF_Allele2 imputationInfo N BETA SE Tstat p.value p.value.NA Is.SPA.converge varT varTstar AF.Cases AF.Controls N.Cases N.Controls

    fix_and_validate_chr2use(args, log)
    pattern = args.sumstats
    chr_or_chunk_labels = list(range(1, args.chunks + 1)) if args.chunks else args.chr2use
    check_input_file(pattern, chr_or_chunk_labels)
    df=pd.concat([pd.read_csv(pattern.replace('@', str(label)), delim_whitespace=True) for label in chr_or_chunk_labels])
    cols = [('SNPID', 'SNP'), ('CHR', 'CHR'), ('POS', 'BP'),
            ('Allele1', 'A2'), ('Allele2', 'A1'),
            ('N', 'N'), ('BETA', 'BETA'), ('SE', 'SE'), 
            ('Tstat', 'Z'), ('p.value', 'P'), ('AF_Allele2', 'FRQ')]

    logistic = ('N.Cases' in df.columns) and ('N.Controls' in df.columns)
    if logistic: cols += [('N.Cases', 'CaseN'), ('N.Controls', 'ControlN')]

    df.dropna(inplace=True)
    df.rename(columns=dict(cols), inplace=True)
    df, info_col = apply_filters(args, df)
    df[['SNP', 'CHR', 'BP', 'A1', 'A2', 'N'] + (['CaseN', 'ControlN'] if logistic else []) + info_col + ['FRQ', 'Z', 'BETA', 'SE', 'P']].to_csv(args.out,index=False, sep='\t')
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

def read_bim(args, bim_file):
    log.log('reading {}...'.format(bim_file))
    bim = pd.read_csv(bim_file, delim_whitespace=True, header=None, names='CHR SNP GP BP A1 A2'.split())
    log.log('done, {} rows, {} cols'.format(len(bim), bim.shape[1]))
    return bim

def read_iid_from_keep_or_remove_file(args, fname):
    log.log('reading {}...'.format(fname))
    df = pd.read_csv(fname, delim_whitespace=True, header=None, comment='#', dtype=str)
    col_idx = 0 if (len(df.columns) == 1) else 1
    iid = set(df[col_idx].values)
    log.log('done, {} rows, {} cols, {} unique IIDs taken from {} column'.format(len(df), df.shape[1], len(iid), col_idx + 1))
    if len(iid) == 0:
        raise(ValueError(f'no IIDs found in {fname} file'))
    return iid

def read_fam(args, fam_file):
    log.log('reading {}...'.format(fam_file))
    fam = pd.read_csv(fam_file, delim_whitespace=True, header=None, names='FID IID FatherID MotherID SEX PHENO'.split(), dtype=str)
    log.log('done, {} rows, {} cols'.format(len(fam), fam.shape[1]))
    if args.log_sensitive: log.log(fam.head())
    if np.any(fam['IID'].duplicated()): raise(ValueError("IID column has duplicated values in --fam file"))
    return fam

# Intput:
#   args - command line arguments (as usual)
#   commands - array of commands to put in a SLURM job
#   array_spec - list of SLURM_ARRAY_TASK_ID if job array, otherwise None
# Output:
#   slurm_job_file - filename of a .job file to output commands (with SLURM header)
#   cmd_file - file that concatenate all commands (in case user wants to execute everything by a BASH on a local node)
#   submit_job_list - instructions for a user about how to schedule SLURM jobs
def append_job(args, commands, array_spec, slurm_job_index, cmd_file, submit_jobs_list):
    slurm_job_file = args.out + '.{}.job'.format(slurm_job_index)
    with open(slurm_job_file, 'w') as f:
        f.write(make_slurm_header(args, array_spec=array_spec) + '\n'.join(commands) + '\n')
    
    with open(cmd_file, 'a') as f:
        for command in commands:
            if array_spec is not None:
                f.write('for SLURM_ARRAY_TASK_ID in {}; do {}; done\n'.format(' '.join(array_spec), command))
            else:
                f.write('{}\n'.format(command))

    if (slurm_job_index != 1):
        submit_jobs_list.append('RES=$(sbatch --dependency=afterok:${{RES##* }} {})'.format(slurm_job_file))
    else:
        submit_jobs_list.append('RES=$(sbatch {})'.format(slurm_job_file))

    return slurm_job_index

def read_comorment_pheno(args, pheno_file, dict_file):
    log.log('reading {}...'.format(pheno_file))
    pheno = pd.read_csv(pheno_file, sep=args.pheno_sep, dtype=str)
    log.log('done, {} rows, {} cols'.format(len(pheno), pheno.shape[1]))
    if args.log_sensitive: log.log(pheno.head())

    log.log('reading {}...'.format(dict_file))
    pheno_dict = pd.read_csv(dict_file, sep=args.dict_sep)
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

    # filter phenotype file according to --keep and --remove
    keep = set(); remove = set()
    for fname in args.keep:
        keep = keep.union(read_iid_from_keep_or_remove_file(args, fname))
    for fname in args.remove:
        remove = remove.union(read_iid_from_keep_or_remove_file(args, fname))

    if len(keep) > 0:
        pheno = pheno[pheno['IID'].isin(keep)]
        log.log('{} individuals remain after applying --keep file(s)'.format(len(pheno)))
        if len(pheno) == 0:
            raise ValueError('no individuals left after applying --keep file(s)')

    if len(remove) > 0:
        pheno = pheno[~pheno['IID'].isin(remove)]
        log.log('{} individuals remain after applying --remove file(s)'.format(len(pheno)))
        if len(pheno) == 0:
            raise ValueError('no individuals left after applying --keep file(s)')

    return pheno, pheno_dict

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.out is None:
        raise ValueError('--out is required.')

    log = Logger(args.log if args.log else (args.out + '.log'), 'a' if args.log_append else 'w')

    start_time = time.time()

    try:
        header = MASTHEAD
        header += "Call: \n"
        header += ' '.join(sys.argv).replace(' --', ' \\\n\t--')
        log.log(header)

        if 'config' in args:
            args.config_object = yaml.safe_load(open(args.config, "r"))
            log.log("Config: \n{}".format(args.config_object))

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
