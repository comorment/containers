#!/usr/bin/env python3
# Run-script for polygenic (risk) score calculations using containerized applications. 
# For usage, cf. this folder's README
#
#
# https://github.com/comorment/containers/issues/17
# MegaPRS
# LDpred2 (auto, inf, grid)
# Plink
# PRS-CS
# PRSice2
# SBayesR
# SBayesS


import os
import sys
import argparse
import json
import numpy as np
import pandas as pd
import yaml
from scipy import stats


_MAJOR = "0"
_MINOR = "0"
# On main and in a nightly release the patch should be one ahead of the last
# released build.
_PATCH = "1"
# This is mainly for nightly builds which have the suffix ".dev$DATE". See
# https://semver.org/#is-v123-a-semantic-version for the semantics.
_SUFFIX = "dev"

VERSION_SHORT = "{0}.{1}".format(_MAJOR, _MINOR)
VERSION = "{0}.{1}.{2}{3}".format(_MAJOR, _MINOR, _PATCH, _SUFFIX)

__version__ = VERSION


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

# compute polygenic risk scores
def parser_pgrs_add_arguments(args, func, parser):
    '''
    Parameters
    ----------
    args: 
    func:
    parser
    '''
    parser.add_argument("--geno-file", type=str, default=None, help="required argument pointing to a genetic file: (1) plink's .bed file, or (2) .bgen file, or (3) .pgen file, or (4) .vcf file. Note that a full name of .bed (or .bgen, .pgen, .vcf) file is expected here. Corresponding files should have standard names, e.g. for plink's format it is expected that .fam and .bim file can be obtained by replacing .bed extension accordingly. supports '@' as a place holder for chromosome labels")
    parser.add_argument("--geno-ld-file", type=str, default=None, help="plink file to use for LD structure estimation")
    parser.add_argument("--sumstats", type=str, help="Input file with summary statistics")
    parser.add_argument('--analysis', type=str, default=['prsice2'], nargs='+', choices=['prsice2'], help='list of analyses to perform.')
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use, (e.g. 1,2,3 or 1-4,12,16-20).")
    parser.add_argument("--clump-p1", type=float, nargs='+', default=[5e-8, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 0.05, 0.1, 0.5, 1.0], help="p-value threshold for independent significant SNPs.")
    parser.add_argument("--keep-ambig", action="store_true", help='Keep ambiguous SNPs. Only use this option if you are certain that the base and target has the same A1 and A2 alleles')
    parser.set_defaults(func=func)


def parse_args(args):
    parser = argparse.ArgumentParser(description="A pipeline for PGS analysis")

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


class BaseParser(object)

if __name__ == '__main__':
    pass
