#!/usr/bin/env python
'''
(c) 2016-2018 Oleksandr Frei and Alexey A. Shadrin
Various utilities for GWAS summary statistics.
'''

from __future__ import print_function
import pandas as pd
import numpy as np
from scipy import stats
import scipy.io as sio
import scipy.sparse
import os
import time, sys, traceback
import argparse
import six
from sumstats_utils import *
import collections
import re
from shutil import copyfile, rmtree
import zipfile
import glob
import socket
import getpass
import subprocess
import tarfile

__version__ = '1.0.0'
MASTHEAD = "***********************************************************************\n"
MASTHEAD += "* sumstats.py: utilities for GWAS summary statistics\n"
MASTHEAD += "* Version {V}\n".format(V=__version__)
MASTHEAD += "* (C) 2016-2018 Oleksandr Frei and Alexey A. Shadrin\n"
MASTHEAD += "* Norwegian Centre for Mental Disorders Research / University of Oslo\n"
MASTHEAD += "* GNU General Public License v3\n"
MASTHEAD += "***********************************************************************\n"

def parse_args(args):
    parser = argparse.ArgumentParser(description="A collection of various utilities for GWAS summary statistics.")

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--log", type=str, default=None, help="filename for the log file. Default is <out>.log")
    parent_parser.add_argument("--log-append", action="store_true", default=False, help="append to existing log file. Default is to erase previous log file if it exists.")

    subparsers = parser.add_subparsers()

    # 'csv' utility : load raw summary statistics file and convert it into a standardized format
    parser_csv = subparsers.add_parser("csv", parents=[parent_parser],
        help='Load raw summary statistics file and convert it into a standardized format: '
        'tab-separated file with standard column names, standard chromosome labels, NA label for missing data, etc. '
        'The conversion does not change the number of lines in the input files (e.g. no filtering is done on markers). '
        'Unrecognized columns are removed from the summary statistics file. '
        'The remaining utilities in sumstats.py work with summary statistics files in the standardized format.')

    parser_csv.add_argument("--sumstats", type=str, default='-',
        help="Raw input file with summary statistics. "
        "Default is '-', e.i. to read from sys.stdin (input pipe).")
    parser_csv.add_argument("--out", type=str, default='-',
        help="File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_csv.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    # Generate parameters from describe_cname.
    # Keys in describe_cname will be used as standard columns names for the resulting csv file.
    for cname in sorted(cols._asdict()):
        parser_csv.add_argument("--{}".format(cname.lower()), default=None, type=str, help=describe_cname[cname])

    parser_csv.add_argument("--auto", action="store_true", default=False,
        help="Auto-detect column types based on a set of standard column names.")
    parser_csv.add_argument("--ignore", type=str, nargs='+',
        help="List of column names in the original file to ignore during auto-detection")
    parser_csv.add_argument("--chunksize", default=100000, type=int,
        help="Size of chunk to read the file.")
    parser_csv.add_argument("--head", default=0, type=int,
        help="How many header lines of the file to print out for visual inspection (0 to disable)")
    parser_csv.add_argument("--preview", default=0, type=int,
        help="How many chunks to output into the output (debug option to preview large files that take long time to parse)")
    parser_csv.add_argument("--skip-validation", action="store_true", default=False,
        help="Skip validation of the resulting csv file")
    parser_csv.add_argument("--sep", default='\s+', type=str, choices=[',', ';', '\t', ' '],
        help="Delimiter to use (',' ';' $' ' or $'\\t'). By default uses delim_whitespace option in pandas.read_csv.")
    parser_csv.add_argument("--na-values", type=str, nargs='+',
        help="Additional strings to recognize as NA/NaN.")
    parser_csv.add_argument("--all-snp-info-23-and-me", default=None, type=str,
        help="all_snp_info file for summary stats in 23-and-me format")
    parser_csv.add_argument("--qc-23-and-me", action="store_true", default=False,
        help="QC 23andMe summary stats (exclude SNPs with 'N' in 'pass' column")
    parser_csv.add_argument("--n-val", default=None, type=float,
        help="Sample size. If this option is not set, will try to infer the sample "
        "size from the input file. If the input file contains a sample size "
        "column, and this flag is set, the argument to this flag has priority.")
    parser_csv.add_argument("--ncase-val", default=None, type=float,
        help="Number of cases. If this option is not set, will try to infer the number "
        "of cases from the input file. If the input file contains a number of cases "
        "column, and this flag is set, the argument to this flag has priority.")
    parser_csv.add_argument("--ncontrol-val", default=None, type=float,
        help="Number of controls. If this option is not set, will try to infer the number "
        "of controls from the input file. If the input file contains a number of controls "
        "column, and this flag is set, the argument to this flag has priority.")
    parser_csv.add_argument("--header", default=None, type=str,
        help="Whitespace-delimited list of column names. "
        "This could be used for input files without column names.")
    parser_csv.add_argument("--keep-cols", nargs='*', default=[],
        help="List of non-standard column names from --sumstats file to keep in --out file. Columns names will UPPERCASEed.")
    parser_csv.add_argument("--keep-all-cols", action="store_true", default=False,
        help="Keep all non-standard column names from --sumstats file to keep in --out file. Columns names will UPPERCASEed.")
    parser_csv.set_defaults(func=make_csv)

    # 'variantid' utility : load raw summary statistics file and convert it into a standardized format
    parser_variantid = subparsers.add_parser("variantid", parents=[parent_parser],
        help='Add VARIANT_ID column, with CHR:BP:A1:A2, where A1 and A2 codes are taking from the reference ')

    parser_variantid.add_argument("--sumstats", type=str, default='-',
        help="Raw input file with summary statistics. "
        "Default is '-', e.i. to read from sys.stdin (input pipe).")
    parser_variantid.add_argument("--out", type=str, default='-',
        help="File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_variantid.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_variantid.add_argument("--ref", type=str, help="[required] Tab-separated file with list of referense SNPs.")
    parser_variantid.set_defaults(func=make_variantid)

    # 'qc' utility: miscellaneous quality control and filtering procedures
    parser_qc = subparsers.add_parser("qc", parents=[parent_parser],
        help="Miscellaneous quality control and filtering procedures")

    parser_qc.add_argument("--sumstats", type=str, default='-',
        help="Raw input file with summary statistics. "
        "Default is '-', e.i. to read from sys.stdin (input pipe).")
    parser_qc.add_argument("--out", type=str, default='-',
        help="[required] File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_qc.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_qc.add_argument("--exclude-ranges", type=str, nargs='+',
        help='Exclude SNPs in ranges of base pair position, for example MHC. '
        'The syntax is chr:from-to, for example 6:25000000-35000000. Multiple regions can be excluded. Require CHR and BP columns in sumstats file. ')
    parser_qc.add_argument("--dropna-cols", type=str, nargs='+',
        help='List of column names. SNPs with missing values in either of the columns will be excluded.')
    parser_qc.add_argument("--fix-dtype-cols", type=str, nargs='+',
        help='List of column names. Ensure appropriate data type for the columns (CHR, BP - int, PVAL - float, etc)')
    parser_qc.add_argument("--require-cols", type=str, nargs='+',
        help='List of column names to require in the input. '
        'Adding "EFFECT"" to the list will have a special meaning: at least one of BETA, OR, LOGODDS, Z columns must be present in the input.')
    parser_qc.add_argument("--maf", type=float, default=None,
        help='filters out all variants with minor allele frequency below the provided threshold'
        'This parameter is ignored when FRQ column is not present in the sumstats file. ')
    parser_qc.add_argument("--info", type=float, default=None,
        help='filters out all variants with imputation INFO score below the provided threshold'
        'This parameter is ignored when INFO column is not present in the sumstats file. ')
    parser_qc.add_argument("--qc-substudies", default=False, action="store_true",
        help='filters out variants that pass QC and imputation is less than half of all studies in the meta-analysis '
        '(i.e. "?" was seen in more than 1/2*N_studies in the METAL "direction" column)'
        'This parameter is ignored when DIRECTION column is not present in the sumstats file. ')
    parser_qc.add_argument("--max-or", type=float, default=None,
        help='Filter SNPs with OR exceeding threshold. Also applies to OR smaller than the inverse value of the threshold, '
        'e.i. for --max-or 25 this QC procedure will exclude SNPs with OR above 25 and below 1/25. '
        '--max-or values below 1 are also acceptable (they will be inverted). '
        'This parameter is ignored when OR column is not present in the sumstats file. ')
    parser_qc.add_argument("--min-pval", type=float, default=None,
        help='Filter SNPs with p-value below given threshold (for example, to exclude genome-wide significant SNPs from analysis')
    parser_qc.add_argument("--update-z-col-from-beta-and-se",  action="store_true", default=False,
        help='Create or update Z score column from BETA and SE columns. This parameter is ignored when BETA or SE columns are not present in the sumstats file. ')
    parser_qc.add_argument("--snps-only", action="store_true", default=False,
        help="excludes all variants with one or more multi-character allele codes. Require A1 and A2 columns in sumstats file. ")
    parser_qc.add_argument("--just-acgt", action="store_true",
        help="similar to --snps-only, but variants with single-character allele codes outside of {'A', 'C', 'G', 'T' } are also excluded. Require A1 and A2 columns in sumstats file. ")
    parser_qc.add_argument("--drop-strand-ambiguous-snps", action="store_true", default=False,
        help="excludes strand ambiguous SNPs (AT, CG). Require A1 and A2 columns in sumstats file. ")
    parser_qc.add_argument("--just-rs-variants", action="store_true", default=False,
        help="keeps only variants with an RS number. Require SNP column in sumstats file. ")
    parser_qc.set_defaults(func=make_qc)

    # 'zscore' utility: calculate z-score from p-value column and effect size column
    parser_zscore = subparsers.add_parser("zscore", parents=[parent_parser],
        help="Calculate z-score from p-value column and effect size column")

    parser_zscore.add_argument("--sumstats", type=str, help="[REQUIRED] Raw input file with summary statistics. ")
    parser_zscore.add_argument("--out", type=str, default='-',
        help="[required] File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_zscore.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_zscore.add_argument("--effect", default=None, type=str, choices=['BETA', 'OR', 'Z', 'LOGODDS'],
        help="Effect column. Default is to auto-detect. In case if multiple effect columns are present in the input file"
        " a warning will be shown and the first column is taken according to the priority list: "
        "Z (highest priority), BETA, OR, LOGODDS (lowest priority).")
    parser_zscore.add_argument("--a1-inc", action="store_true", default=False,
        help='A1 is the increasing risk (effect) allele.')
    parser_zscore.add_argument("--chunksize", default=100000, type=int,
        help="Size of chunk to read the file.")
    parser_zscore.set_defaults(func=make_zscore)

    # 'pvalue' utility: calculate p-value column from 'z'' or 'beta'/'se' columns
    parser_pvalue = subparsers.add_parser("pvalue", parents=[parent_parser],
        help="Calculate p-value column from 'z'' or 'beta'/'se' columns")
    parser_pvalue.add_argument("--sumstats", type=str, help="[REQUIRED] Raw input file with summary statistics. ")
    parser_pvalue.add_argument("--out", type=str, default='-',
        help="[required] File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_pvalue.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_pvalue.add_argument("--chunksize", default=100000, type=int,
        help="Size of chunk to read the file.")
    parser_pvalue.set_defaults(func=make_pvalue)

    # 'beta' utility: calculate BETA column from OR and LOGODDS columns
    parser_beta = subparsers.add_parser("beta", parents=[parent_parser],
        help="Calculate BETA column from OR and LOGODDS columns")
    parser_beta.add_argument("--sumstats", type=str, help="[REQUIRED] Raw input file with summary statistics. ")
    parser_beta.add_argument("--out", type=str, default='-',
        help="[required] File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_beta.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_beta.set_defaults(func=make_beta)

    # 'mat' utility: load summary statistics into matlab format
    parser_mat = subparsers.add_parser("mat", parents=[parent_parser], help="Create mat files that can "
        "be used as an input for cond/conj FDR and for CM3 model. "
        "Takes csv files (created with the csv task of this script). "
        "Require columns: SNP, P, and one of the signed summary statistics columns (BETA, OR, Z, LOGODDS). "
        "Creates corresponding mat files which can be used as an input for the conditional fdr model. "
        "Only SNPs from the reference file are considered. Zscores of strand ambiguous SNPs are set to NA. "
        "To use CHR:POS for merging summary statistics with reference file consider 'rs' utility "
        "which auguments summary statistics with SNP column (first run 'sumstats.py rs ...', "
        "then feed the resulting file into sumstats.py mat ...)")

    parser_mat.add_argument("--sumstats", type=str, default='-',
        help="Raw input file with summary statistics. "
        "Default is '-', e.i. to read from sys.stdin (input pipe).")
    parser_mat.add_argument("--ref", type=str, help="[required] Tab-separated file with list of referense SNPs.")
    parser_mat.add_argument("--out", type=str, help="[required] File to output the result. File should end with .mat extension.")
    parser_mat.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_mat.add_argument("--keep-cols", nargs='*', choices=cols._fields,
        default=[], type=lambda col: col.upper(), metavar='COLUMN_NAME',
        help="Columns from csv file to keep in mat file")
    parser_mat.add_argument("--keep-all-cols", action="store_true",
        default=False, help="Keep all columns from cvs file in mat file, except SNP, CHR, BP, A1 and A2")

    parser_mat.add_argument("--trait", type=str, default='',
        help="Trait name that will be used in mat file. Can be kept empty, in this case the variables will be named 'logpvec', 'zvec' and 'nvec'")
    parser_mat.add_argument("--ignore-alleles", action="store_true", default=False,
        help="Load summary stats file ignoring alleles (only 'logpvec' is created in this case, entire 'zvec' is set to nan).")
    parser_mat.add_argument("--without-n", action="store_true", default=False,
        help="Proceed without sample size (N or NCASE/NCONTROL)")
    parser_mat.add_argument("--chunksize", default=100000, type=int,
        help="Size of chunk to read the file.")
    parser_mat.set_defaults(func=make_mat)

    # 'lift' utility: lift RS numbers to a newer version of SNPdb, and/or liftover chr:pos to another genomic build using UCSC chain files
    parser_lift = subparsers.add_parser("lift", parents=[parent_parser],
        help="Lift RS numbers to a newer version of SNPdb, "
        "and/or liftover chr:pos to another genomic build using UCSC chain files. "
        "WARNING: this utility may use excessive amount of memory (up and beyong 32 GB of RAM).")
    parser_lift.add_argument("--sumstats", type=str, default='-',
        help="Raw input file with summary statistics. "
        "Default is '-', e.i. to read from sys.stdin (input pipe).")
    parser_lift.add_argument("--out", type=str, default='-',
        help="File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")

    parser_lift.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_lift.add_argument("--chain-file", default=None, type=str,
        help="Chain file to use for CHR:BP conversion between genomic builds")
    parser_lift.add_argument("--snp-chrpos", default=None, type=str,
        help="NCBI SNPChrPosOnRef file.")
    parser_lift.add_argument("--snp-history", default=None, type=str,
        help="NCBI SNPHistory file.")
    parser_lift.add_argument("--rs-merge-arch", default=None, type=str,
        help="NCBI RsMergeArch file.")
    parser_lift.add_argument("--keep-bad-snps", action="store_true", default=False,
        help="Keep SNPs with undefined rs# number or CHR:POS location in the output file.")
    parser_lift.add_argument("--na-rep", default='NA', type=str, choices=['NA', ''],
        help="Missing data representation.")
    parser_lift.add_argument("--gzip", action="store_true", default=False,
        help="A flag indicating whether to compress the resulting file with gzip.")
    parser_lift.set_defaults(func=make_lift)

    # 'clump' utility: clump summary stats, produce lead SNP report, produce candidate SNP report
    parser_clump = subparsers.add_parser("clump", parents=[parent_parser],
        help="""Perform LD-based clumping of summary stats. This works similar to FUMA snp2gene functionality (http://fuma.ctglab.nl/tutorial#snp2gene).
    Step 1. Re-save summary stats into one file for each chromosome.
    Step 2a Use 'plink --clump' to find independent significant SNPs (default r2=0.6)
    Step 2b Use 'plink --clump' to find lead SNPs, by clumping independent significant SNPs (default r2=0.1)
    Step 3. Use 'plink --ld' to find genomic loci around each independent significant SNP (default r2=0.6)
    Step 4. Merge together genomic loci which are closer than certain threshold (250 KB)
    Step 5. Merge together genomic loci that fall into exclusion regions, such as MHC
    Step 6. Output genomic loci report, indicating lead SNPs for each loci
    Step 7. Output candidate SNP report""")
    parser_clump.add_argument("--sumstats", type=str, help="Input file with summary statistics")
    parser_clump.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_clump.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_clump.add_argument("--chr-labels", type=str, nargs='+',
        help="List of chromosome labels to substitute for @, default to 1..22")

    parser_clump.add_argument("--clump-field", type=str, default='PVAL', help="Column to clump on.")
    parser_clump.add_argument("--clump-snp-field", type=str, default='SNP', help="Column with marker name.")
    parser_clump.add_argument("--chr", type=str, default='CHR', help="Column name with chromosome labels. ")

    parser_clump.add_argument("--indep-r2", type=float, default=0.6, help="LD r2 threshold for clumping independent significant SNPs.")
    parser_clump.add_argument("--lead-r2", type=float, default=0.1, help="LD r2 threshold for clumping lead SNPs.")
    parser_clump.add_argument("--clump-p1", type=float, default=5e-8, help="p-value threshold for independent significant SNPs.")
    parser_clump.add_argument("--bfile-chr", type=str,
        help="prefix for plink .bed/.bim/.fam file. Will automatically concatenate .bed/.bim/.fam files split across 22 chromosomes. "
        "If the filename prefix contains the symbol @, sumstats.py will replace the @ symbol with chromosome numbers. "
        "Otherwise, sumstats.py will append chromosome numbers to the end of the filename prefix. ")
    parser_clump.add_argument("--ld-window-kb", type=float, default=10000, help="Window size in KB to search for clumped SNPs. ")
    parser_clump.add_argument("--loci-merge-kb", type=float, default=250, help="Maximum distance in KB of LD blocks to merge. ")
    parser_clump.add_argument("--exclude-ranges", type=str, nargs='+',
        help='Exclude SNPs in ranges of base pair position, for example MHC. '
        'The syntax is chr:from-to, for example 6:25000000-35000000. Multiple regions can be excluded.')
    parser_clump.add_argument("--plink", type=str, default='plink', help="Path to plink executable.")
    parser_clump.add_argument("--sumstats-chr", type=str, help="Input file with summary statistics, one file per chromosome")
    parser_clump.set_defaults(func=make_clump)

    # 'rs' utility: augument summary statistic file with SNP RS number from reference file
    parser_rs = subparsers.add_parser("rs", parents=[parent_parser],
        help="Augument summary statistic file with SNP RS number from reference file. "
        "Merging is done on chromosome and position. If SNP column already exists in --sumstats file, it will be overwritten.")

    parser_rs.add_argument("--sumstats", type=str, help="[required] Input file with summary statistics in standardized format")
    parser_rs.add_argument("--ref", type=str, help="[required] Tab-separated file with list of referense SNPs.")
    parser_rs.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_rs.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_rs.add_argument("--a1a2", action="store_true", default=False, 
        help="Add A1 and A2 columns from the reference file. "
        "Existing A1 and/or A2 columns in --sumstats file will be overwritten.")

    parser_rs.add_argument("--chunksize", default=100000, type=int,
        help="Size of chunk to read the file.")
    parser_rs.set_defaults(func=make_rs)

    # 'ls' utility: display information about columns of a standardized summary statistics file
    parser_ls = subparsers.add_parser("ls", parents=[parent_parser],
        help="Report information about standard sumstat files, "
        "including the set of columns available, number of SNPs, etc.")

    parser_ls.add_argument("--path", type=str, help="[required] File or regular expresion of the files to include in the report.")
    parser_ls.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_ls.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_ls.set_defaults(func=make_ls)

    # 'mat-to-csv' utility: convert matlab .mat file with logpvec and zvec into CSV files
    parser_mattocsv = subparsers.add_parser("mat-to-csv", parents=[parent_parser],
        help="Convert matlab .mat file with logpvec, zvec and (optionally) nvec into CSV files.")

    parser_mattocsv.add_argument("--mat", type=str, help="[required] Input mat file.")
    parser_mattocsv.add_argument("--ref", type=str, help="[required] Tab-separated file with list of referense SNPs.")
    parser_mattocsv.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_mattocsv.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_mattocsv.add_argument("--na-rep", default='NA', type=str, choices=['NA', ''],
        help="Missing data representation.")
    parser_mattocsv.add_argument("--gzip", action="store_true", default=False,
        help="A flag indicating whether to compress the resulting file with gzip.")
    parser_mattocsv.set_defaults(func=mat_to_csv)

    # 'ldsc-to-mat' utility: convert data from LD score regression formats to .mat files
    parser_ldsctomat = subparsers.add_parser("ldsc-to-mat", parents=[parent_parser],
        help="Convert .sumstats, .ldscore, .M, .M_5_50 and "
        "binary .annot files from LD score regression to .mat files.")

    parser_ldsctomat.add_argument("--ref", type=str, help="[required] Tab-separated file with list of referense SNPs.")
    parser_ldsctomat.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_ldsctomat.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_ldsctomat.add_argument("--sumstats", type=str, default=None,
        help="Name of .sumstats.gz file")
    parser_ldsctomat.add_argument("--ldscore", type=str, default=None,
        help="Name of .ldscore.gz files, where symbol @ indicates chromosome index. Example: baseline.@.l2.ldscore.gz")
    parser_ldsctomat.add_argument("--annot", type=str, default=None,
        help="Name of .annot.gz files, where symbol @ indicates chromosome index. Example: baseline.@.annot.gz")
    parser_ldsctomat.add_argument("--M", type=str, default=None,
        help="Name of .M files, where symbol @ indicates chromosome index. Example: baseline.@.l2.M")
    parser_ldsctomat.add_argument("--M-5-50", type=str, default=None,
        help="Name of .M_5_50 files, where symbol @ indicates chromosome index. Example: baseline.@.l2.M_5_50")
    parser_ldsctomat.add_argument("--chr-labels", type=str, nargs='+',
        help="List of chromosome labels to substitute for @, default to 1..22")
    parser_ldsctomat.set_defaults(func=ldsc_to_mat)

    # 'frq-to-mat' utility: convert allele frequency from FRQ plink format to .mat files
    parser_frqtomat = subparsers.add_parser("frq-to-mat", parents=[parent_parser],
        help="Convert .frq files plink from .mat files.")

    parser_frqtomat.add_argument("--ref", type=str, help="Tab-separated file with list of referense SNPs.")
    parser_frqtomat.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_frqtomat.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_frqtomat.add_argument("--frq", type=str, default=None,
        help="Name of .frq files, where symbol @ indicates chromosome index. Example: 1000G.EUR.QC.@.frq")
    parser_frqtomat.add_argument("--afreq", type=str, default=None,
        help="Name of .afreq files, where symbol @ indicates chromosome index. Example: 1000G.EUR.QC.@.afreq")
    parser_frqtomat.add_argument("--chr-labels", type=str, nargs='+',
        help="List of chromosome labels to substitute for @, default to 1..22")
    parser_frqtomat.set_defaults(func=frq_to_mat)

    # 'ref-to-mat' utility: convert reference files  to .mat files
    parser_reftomat = subparsers.add_parser("ref-to-mat", parents=[parent_parser],
        help="Convert reference files to .mat files.")

    parser_reftomat.add_argument("--ref", type=str, help="Tab-separated file with list of referense SNPs.")
    parser_reftomat.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_reftomat.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_reftomat.add_argument("--numeric-only", action="store_true", default=False, help="Save only numeric data (CHR, BP, GP), skip all other column (A1, A2, SNP).")
    parser_reftomat.set_defaults(func=ref_to_mat)

    # 'ldsum' utility: convert plink .ld.gz files (pairwise ld r2) to ld scores
    parser_ldsum = subparsers.add_parser("ldsum", parents=[parent_parser],
        help="convert plink .ld.gz files (pairwise ld r2) to ld scores")

    parser_ldsum.add_argument("--bim", type=str, help="[required] plink bim file")
    parser_ldsum.add_argument("--ld", type=str, help="[required] plink .ld file")
    parser_ldsum.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_ldsum.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_ldsum.add_argument('--r2-min', default=None, type=float, nargs='+',
        help='Lower bound (exclusive) of r2 to consider in ld score estimation. '
        'Should be used in conjunction with --r2-max. ' 
        'Intended usage of this parameter is to create a binned histogram of l2 or l4 values, for example: '
        '"--r2-min 0.00 0.25 0.50 0.75 --r2-max 0.25 0.50 0.75 1.00". '
        'Normally --r2-min and --r2-max should cover the range from 0 to 1. '
        'In case of --per-allele flag, --r2-min and --r2-max thresholds apply to the product of allelic correlation and heterozigosity, '
        'e.i. to r2_{jk} * 2*p_k*(1-p_k), where p_k denotes the MAF of SNP k. '
        'To produce a complete histogram in case of --per-allele flag one must use --r2-min and --r2-max that cover the range from 0 to 0.5. ')
    parser_ldsum.add_argument('--r2-max', default=None, type=float, nargs='+',
        help='Upper bound (inclusive) of r2 to consider in ld score estimation. '
        'See description of --r2-min option for additional details. ')
    parser_ldsum.add_argument('--per-allele', default=False, action='store_true',
        help='Setting this flag causes sumstats.py to compute per-allele LD Scores, '
        'i.e., '
        '\ell2_j := \sum_k  2*p_k(1-p_k)    r^2_{jk}, and '
        '\ell4_j := \sum_k (2*p_k(1-p_k))^2 r^4_{jk}, '
        'where p_k denotes the MAF of SNP k. '
        'Require --frq parameter to be specified. ')
    parser_ldsum.add_argument("--frq", type=str, default=None, help="Name of the .frq file.")
    parser_ldsum.add_argument('--not-diag', default=False, action='store_true',
        help='sumstats.py assume that plink-generated --ld file does not have diagonal elements, '
        'e.i. does not contain LD r2 entries of 1.0 for variant r2 with itself. '
        'By default sumstats.py adds such diagonal entries to the LD score. '
        'Setting --not-diag flag causes sumstats.py to NOT to add the diagonal elements. ')
    parser_ldsum.add_argument("--chunksize", default=10000000, type=int,
        help="Size of chunk to read the --ld file.")
    parser_ldsum.set_defaults(func=ldsum)

    # 'diff-mat' utility: compare two .mat files with logpvec, zvec and nvec, and report the differences
    parser_diffmat = subparsers.add_parser("diff-mat", parents=[parent_parser],
        help="Compare two .mat files with logpvec, zvec and nvec, "
        "and report the differences.")

    parser_diffmat.add_argument("--mat1", type=str, default=None, help="[required] Name of the first .mat file")
    parser_diffmat.add_argument("--mat2", type=str, default=None, help="[required] Name of the second .mat file")
    parser_diffmat.add_argument("--ref", type=str, help="[required] Tab-separated file with list of referense SNPs.")
    parser_diffmat.add_argument("--out", type=str, help="[required] File to output the result.")
    parser_diffmat.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")

    parser_diffmat.add_argument("--sumstats", type=str, default=None,
        help="Optionally, the name of the source summary statistics file in standardized .csv format. "
        "Assuming that both .mat files originate from this file diff-mat will produce output file "
        "to help investigate where the differences came from.")
    parser_diffmat.set_defaults(func=diff_mat)

    # 'neff' utility: generate N column from NCASE and NCONTROL
    parser_neff = subparsers.add_parser("neff", parents=[parent_parser],
        help="generate N column from NCASE and NCONTROL, as 4 / (1 / NCASE + 1 / NCONTROL)")
    parser_neff.add_argument("--sumstats", type=str, default='-',
        help="Raw input file with summary statistics. "
        "Default is '-', e.i. to read from sys.stdin (input pipe).")
    parser_neff.add_argument("--out", type=str, default='-',
        help="[required] File to output the result. "
        "Default is '-', e.i. to write to sys.stdout (output pipe).")
    parser_neff.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser_neff.add_argument("--drop", action="store_true", default=False, help="Drop NCASE and NCONTROL columns.")
    parser_neff.add_argument("--factor", default=4, type=float,
        help="Factor in the numerator of the NEFF formula. Default to 4. Sometimes you may want FACTOR=2. Set FACTOR=0 if you want NEFF = NCASE + NCONTROL.")
    parser_neff.set_defaults(func=make_neff)

    return parser.parse_args(args)

### =================================================================================
###                          Implementation for parser_csv
### ================================================================================= 
def set_clean_args_cnames(args):
    """
    Inspect column names in user args, and clean them according to sumstats_utils.clean_header()
    Raises an exception if either before or after cleaning some column names are duplicated.
    """
    cnames = [x.lower() for x in cols._asdict()]
    args_cnames = [args[x] for x in cnames if args[x] is not None]
    if len(args_cnames) != len(set(args_cnames)):
        raise(ValueError('Duplicated argument: {}'.format(find_duplicates(args_cnames))))

    for cname in cnames:
        if args[cname] is not None:
            args[cname] = clean_header(args[cname])
    args_clean_cnames = [args[x] for x in cnames if args[x] is not None]
    if len(args_clean_cnames) != len(set(args_clean_cnames)):
        raise(ValueError('Cleaning rules yield duplicated argument: {}'.format(find_duplicates(args_clean_cnames))))

def set_clean_file_cnames(df):
    """
    Inspect column names in pd.DataFrame, and clean them according to sumstats_utils.clean_header()
    Raises an exception if either before or after cleaning some column names are duplicated.
    """
    file_cnames = df.columns
    if len(file_cnames) != len(set(file_cnames)):
        raise(ValueError('Unable to process input file due to duplicated column names'))
    
    clean_file_cnames = [clean_header(x) for x in file_cnames]
    if len(clean_file_cnames) != len(set(clean_file_cnames)):
        raise(ValueError('Cleaning column names resulted in duplicated column names: {}'.format(clean_file_cnames)))

    df.columns = clean_file_cnames

def find_duplicates(values):
    return [item for item, count in collections.Counter(values).items() if count > 1]

def find_auto_cnames(args, clean_file_cnames):
    """
    Auto-detect column using a set of default columns names 
    """
    
    cnames = [x.lower() for x in cols._asdict()]
    user_args = [args[x] for x in cnames if args[x] is not None]

    for default_cname, cname in default_cnames.items():
        # Ignore default cname if it is explicitly provided by the user
        if (cname.lower() not in args) or args[cname.lower()]:
            continue

        # Ignore default cname if it is not present among file columns
        if clean_header(default_cname) not in clean_file_cnames:
            continue
        
        # Ignore default cname if user took the column for something else
        if clean_header(default_cname) in user_args:
            continue

        # Ignore default cname if user explicitly asked to ignore it
        if args['ignore'] and (clean_header(default_cname) in [clean_header(x) for x in args['ignore']]):
            continue

        args[cname.lower()] = clean_header(default_cname)

def check_input_file(file):
    if file == '-':
        raise ValueError("sys.stdin is not supported as input file")
    if (file != sys.stdin) and not os.path.isfile(file):
        raise ValueError("Input file does not exist: {f}".format(f=file))

def check_output_file(file, force=False):
    # Delete target file if user specifies --force option
    if file == '-':
        raise ValueError("sys.stdout is not supported as output file")

    if file == sys.stdout:
        return

    if force:
        try:
            os.remove(file)
        except OSError:
            pass

    # Otherwise raise an error if target file already exists
    if os.path.isfile(file) and not force:
        raise ValueError("Output file already exists: {f}".format(f=file))

    # Create target folder if it doesn't exist
    output_dir = os.path.dirname(file)
    if output_dir and not os.path.isdir(output_dir): os.makedirs(output_dir)  # ensure that output folder exists

def make_csv(args, log):
    """
    Based on file with summary statistics creates a tab-delimited csv file with standard columns.
    """
    if args.sumstats == '-': args.sumstats = sys.stdin
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    if args.all_snp_info_23_and_me: check_input_file(args.all_snp_info_23_and_me)
    set_clean_args_cnames(vars(args))
    check_output_file(args.out, args.force)

    if args.keep_all_cols and args.keep_cols:
        err_msg = ("Misleading input arguments! Use either '--keep-cols' or "
            "'--keep-all-cols' option, but not both at a time.")
        raise(ValueError(err_msg))

    if args.keep_cols is None: args.keep_cols = []

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    if (args.head > 0) and (args.sumstats != sys.stdin):
        log.log('File header:')
        header = get_header(args.sumstats, lines=args.head)
        for line in header: log.log(line)

    if args.header is None:
        reader = pd.read_csv(args.sumstats, dtype=str, sep=args.sep, chunksize=args.chunksize, na_values=args.na_values)
    else:
        reader = pd.read_csv(args.sumstats, dtype=str, sep=args.sep, chunksize=args.chunksize, na_values=args.na_values, header=None, names=args.header.split())
    reader_23_and_me = pd.read_csv(args.all_snp_info_23_and_me, dtype=str, sep=args.sep, chunksize=args.chunksize) if args.all_snp_info_23_and_me else None
    n_snps = 0
    max_n_val = np.nan; max_ncase_val = np.nan; max_ncontrol_val = np.nan
    with (open(args.out, 'a') if args.out != sys.stdout else sys.stdout) as out_f:
        for chunk_index, chunk in enumerate(reader):
            if reader_23_and_me:
                chunk = pd.concat([chunk, next(reader_23_and_me)], axis=1)
                chunk = chunk.loc[:, ~chunk.columns.duplicated()]
                if args.qc_23_and_me:
                    chunk = chunk[chunk['pass'] != 'N'].copy()

            original_file_cname = chunk.columns
            set_clean_file_cnames(chunk)

            if chunk_index == 0:  # First chunk => analyze column names
                if args.auto: find_auto_cnames(vars(args), chunk.columns)
            
                # Find the map from (cleaned) column name to a standard cname (as it will appear in the resulting file)
                cnames = [x.lower() for x in cols._asdict()]
                cname_map = {vars(args)[cname] : cname.upper() for cname in cnames if vars(args)[cname] is not None}

                # Report any missing columns that user requested to put in the resulting file
                cname_missing = [x for x in cname_map if x not in chunk.columns]
                if cname_missing: raise(ValueError('Columns {} are missing in the input file'.format(cname_missing)))

                # Describe the mapping between old and new column names that we are going to perform
                log.log('Interpret column names as follows:')
                for original in original_file_cname:
                    cname = cname_map.get(clean_header(original))
                    if (args.ncase_val is not None) and (cname==cols.NCASE): cname=None
                    if (args.ncontrol_val is not None) and (cname==cols.NCONTROL): cname=None
                    if (args.n_val is not None) and (cname==cols.N): cname=None
                    if cname: column_status = describe_cname[cname]
                    elif args.keep_all_cols or (original.upper() in args.keep_cols): column_status = "Will be kept as unrecognized column"
                    else: column_status = "Will be deleted"
                    log.log("\t{o} : {d} ({e})".format(o=original, d=cname, e=column_status))
                if not cname_map: raise(ValueError('Arguments imply to delete all columns from the input file. Did you forget --auto flag?'))

                final_cols = set(cname_map.values())  # final list of columns in the resulting file
                if (cols.CHRPOS not in final_cols) and (cols.CHRPOSA1A2 not in final_cols) and (cols.CHR not in final_cols): log.log('Warning: CHR column ({}) is not found'.format(describe_cname[cols.CHR]))
                if (cols.CHRPOS not in final_cols) and (cols.CHRPOSA1A2 not in final_cols) and (cols.BP not in final_cols): log.log('Warning: BP column ({}) is not found'.format(describe_cname[cols.BP]))
                if cols.SNP not in final_cols: log.log('Warning: SNP column ({}) is not found'.format(describe_cname[cols.SNP]))
                if cols.PVAL not in final_cols: log.log('Warning: PVAL column ({}) is not found'.format(describe_cname[cols.PVAL]))
                if (cols.A1 not in final_cols) and (cols.A1A2 not in final_cols) and (cols.CHRPOSA1A2 not in final_cols): log.log('Warning: A1 column ({}) is not found'.format(describe_cname[cols.A1]))
                if (cols.A2 not in final_cols) and (cols.A1A2 not in final_cols) and (cols.CHRPOSA1A2 not in final_cols): log.log('Warning: A2 column ({}) is not found'.format(describe_cname[cols.A2]))
                effect_size_column_count = int(cols.Z in final_cols) + int(cols.OR in final_cols) + int(cols.BETA in final_cols) + int(cols.LOGODDS in final_cols)
                if effect_size_column_count == 0: log.log('Warning: None of the columns indicate effect direction: typically either BETA, OR, LOGODDS or Z column is expected')
                if effect_size_column_count > 1: log.log('Warning: Multiple columns indicate effect direction: typically only one of BETA, OR, LOGODDS and Z columns is expected')

            if not args.keep_all_cols:
                chunk.drop([x for x in chunk.columns if ((x not in cname_map) and (x not in args.keep_cols))], axis=1, inplace=True)
            chunk.rename(columns=cname_map, inplace=True)

            # Split CHR:POS column into two
            if cols.CHRPOS in chunk.columns:
                chunk[cols.CHR], chunk[cols.BP] = chunk[cols.CHRPOS].str.replace('_', ':').str.split(':', 1).str
                chunk.drop(cols.CHRPOS, axis=1, inplace=True)

            # Split A1/A2 column into two
            if cols.A1A2 in chunk.columns:
                chunk[cols.A1], chunk[cols.A2] = chunk[cols.A1A2].str.split('/', 1).str
                chunk.drop(cols.A1A2, axis=1, inplace=True)

            # Split CHR:POS:A1:A2 column into four
            if cols.CHRPOSA1A2 in chunk.columns:
                chunk[cols.CHR], chunk[cols.BP], chunk[cols.A1], chunk[cols.A2] = chunk[cols.CHRPOSA1A2].str.replace('_', ':').str.split(':', 3).str
                chunk.drop(cols.CHRPOSA1A2, axis=1, inplace=True)

            # Validate that EA has the same values as A1, and drop EA:
            if cols.EA in chunk.columns:
                if np.any(chunk[cols.EA] != chunk[cols.A1]):
                    raise('EA column does not match A1 column, unable to read summary stats')
                chunk.drop(cols.EA, axis=1, inplace=True)

            # Ensure standard labels in CHR column
            if cols.CHR in chunk.columns:
                chunk[cols.CHR].fillna(-9, inplace=True)
                chunk[cols.CHR] = format_chr(chunk[cols.CHR])

            # Ensure that alleles are coded as capital letters
            if cols.A1 in chunk.columns: chunk[cols.A1] = chunk[cols.A1].str.upper().str.strip()
            if cols.A2 in chunk.columns: chunk[cols.A2] = chunk[cols.A2].str.upper().str.strip()

            # Populate sample size columns (NCASE, NCONTROL, N)
            if args.ncase_val is not None: chunk[cols.NCASE] = args.ncase_val
            if args.ncontrol_val is not None: chunk[cols.NCONTROL] = args.ncontrol_val
            if args.n_val is not None: chunk[cols.N] = args.n_val

            # Keep track of the largest NCASE, NCONTROL and N values
            if cols.NCASE in chunk: max_ncase_val = np.nanmax([max_ncase_val, chunk[cols.NCASE].astype(float).max()])
            if cols.NCONTROL in chunk: max_ncontrol_val = np.nanmax([max_ncontrol_val, chunk[cols.NCONTROL].astype(float).max()])
            if cols.N in chunk: max_n_val = np.nanmax([max_n_val, chunk[cols.N].astype(float).max()])

            # Swap A1 and A2 for 23andMe, because in 23andMe summary stats effect size is about A2
            if args.all_snp_info_23_and_me:
                chunk.columns = [(cols.A1 if x==cols.A2 else cols.A2 if x==cols.A1 else x) for x in chunk.columns]

            chunk = chunk.sort_index(axis=1)
            fix_columns_order(chunk).to_csv(out_f, index=False, header=(chunk_index==0), sep='\t', na_rep='NA')
            n_snps += len(chunk)
            eprint("{f}: {n} lines processed".format(f=args.sumstats, n=(chunk_index+1)*args.chunksize))
            if args.preview and (chunk_index+1) >= args.preview:
                log.log('Abort reading input file due to --preview flag.')
                break

        if n_snps == 0: raise(ValueError('Input summary stats file appears to be empty.'))
        log.log("Done. {n} SNPs saved to {f}".format(n=n_snps, f=args.out))
        log.log('Sample size: N={} NCASE={} NCONTROL={}'.format(max_n_val, max_ncase_val, max_ncontrol_val))

    if (not args.skip_validation) and (args.out != sys.stdout):
        log.log('Validate the resulting file...')
        reader = pd.read_csv(args.out, sep='\t', chunksize=args.chunksize)
        n_snps = 0
        for chunk_index, chunk in enumerate(reader):
            if chunk_index==0:
                log.log('Column types: ' + ', '.join([column + ':' + str(dtype) for (column, dtype) in zip(chunk.columns, chunk.dtypes)]))
            n_snps += len(chunk)
        log.log("Done. {n} SNPs read from {f}".format(n=n_snps, f=args.out))

### =================================================================================
###                          Implementation for parser_qc
### =================================================================================
def describe_sample_size(sumstats, log):
    log.log('Sample size N={} NCASE={} NCONTROL={}'.format(
        sumstats[cols.N].max() if cols.N in sumstats else np.nan,
        sumstats[cols.NCASE].max() if cols.NCASE in sumstats else np.nan,
        sumstats[cols.NCONTROL].max() if cols.NCONTROL in sumstats else np.nan))

def drop_sumstats(sumstats, log, reason, drop_labels=None, dropna_subset=None):
    '''Drop labels from sumstats, and log the number of excluded rows.'''
    sumstats_len = len(sumstats)

    if drop_labels is not None:
        sumstats.drop(drop_labels, inplace=True)

    if dropna_subset is not None:
        sumstats.dropna(subset=dropna_subset, inplace=True)

    log.log('Drop {} markers ({})'.format(sumstats_len - len(sumstats), reason))

def make_qc(args, log):
    if args.sumstats == '-': args.sumstats = sys.stdin
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    if (args.max_or is not None) and (args.max_or <= 0): raise(ValueError('--max-or value must not be negative'))
    if (args.maf is not None) and ((args.maf < 0) or (args.maf > 1)): raise(ValueError('--maf value must be between 0 and 1'))
    if (args.info is not None) and (args.info < 0): raise(ValueError('--info value must not be negative'))
    if (args.min_pval is not None) and ((args.min_pval < 0) or (args.min_pval > 1)): raise(ValueError('--min-pval value be between 0 and 1'))

    if (args.max_or is not None) and (args.max_or < 1):
        log.log('--max-or was changed from {} to {}'.format(args.max_or, 1/args.max_or))
        args.max_or = 1 / args.max_or

    if args.dropna_cols is None: args.dropna_cols = []
    if args.fix_dtype_cols is None: args.fix_dtype_cols = []
    if args.require_cols is None: args.require_cols = []

    # Read summary sumstats file...
    log.log('Reading sumstats file {}...'.format(args.sumstats))
    sumstats = pd.read_csv(args.sumstats, sep='\t', dtype=str)
    exclude_ranges = make_ranges(args.exclude_ranges, log)
    log.log("Sumstats file contains {d} markers.".format(d=len(sumstats)))

    if (args.exclude_ranges is not None) and (('BP' not in sumstats) or ('CHR' not in sumstats)):
        log.log('Warning: skip --exclude-ranges ("BP" and/or "CHR" columns not found in {})'.format(args.sumstats))
        args.exclude_ranges = None
    missing_dropna_cols = [x for x in args.dropna_cols if x not in sumstats]
    missing_fix_dtype_cols = [x for x in args.fix_dtype_cols if x not in sumstats]
    if missing_dropna_cols:
        log.log('Warning: can not apply --dropna-cols to {}; columns are missing'.format(', '.join(missing_dropna_cols)))
        args.dropna_cols = [x for x in args.dropna_cols if x not in missing_dropna_cols]
    if missing_fix_dtype_cols:
        log.log('Warning: can not apply --fix-dtype-cols to {}; columns are missing'.format(', '.join(missing_fix_dtype_cols)))
        args.fix_dtype_cols = [x for x in args.fix_dtype_cols if x not in missing_fix_dtype_cols]

    if args.exclude_ranges is not None:
        args.dropna_cols.extend(['CHR', 'BP'])
        args.fix_dtype_cols.extend(['CHR', 'BP'])
    if args.fix_dtype_cols is not None:
         for col in args.fix_dtype_cols:
            if cols_type_map[col] == int:
                args.dropna_cols.append(col)

    # Check all required columns
    args.require_cols = [col.upper() for col in args.require_cols]
    missing_cols = []
    for col in args.require_cols:
        if col == 'EFFECT':
            if not any(col in sumstats for col in ['BETA', 'OR', 'LOGODDS', 'Z']):
                missing_cols.append('"EFFECT" (e.i. BETA, OR, LOGODDS or Z)')
        elif col not in sumstats:
            missing_cols.append('"{}"'.format(col))
    if missing_cols:
        raise(ValueError('--require-cols detected that columns {} are not available in the sumstats file'.format(', '.join(missing_cols))))

    # Adjust optional parameters (those that can be ignored if certain columns are missing)
    if (args.max_or is not None) and ('OR' not in sumstats):
        log.log('Warning: skip --max-or ("OR" column not found in {})'.format(args.sumstats))
        args.max_or = None

    if (args.maf is not None) and ('FRQ' not in sumstats):
        log.log('Warning: skip --maf ("FRQ" column not found in {})'.format(args.sumstats))
        args.maf = None

    if (args.info is not None) and ('INFO' not in sumstats):
        log.log('Warning: skip --info ("INFO" column not found in {})'.format(args.sumstats))
        args.info = None

    if (args.min_pval is not None) and ('PVAL' not in sumstats):
        log.log('Warning: skip --min-pval ("PVAL" column not found in {})'.format(args.sumstats))
        args.min_pval = None

    if args.update_z_col_from_beta_and_se and (('BETA' not in sumstats) or ('SE' not in sumstats)):
        log.log('Warning: can not apply --update-z-col-from-beta-and-se ("OR" column not found in {})'.format(args.sumstats))
        args.update_z_col_from_beta_and_se = False

    if args.qc_substudies and ('DIRECTION' not in sumstats):
        log.log('Warning: can not apply --qc-substudies ("DIRECTION" column not found in {})'.format(args.sumstats))
        args.qc_substudies = False

    nstudies = None
    if args.qc_substudies:
        nstudies = np.min(sumstats['DIRECTION'].str.len())
        max_nstudies = np.max(sumstats['DIRECTION'].str.len())
        if max_nstudies != nstudies:
            raise(ValueError('Problem with DIRECTION column: number of studies vary between {} and {}'.format(nstudies, max_nstudies)))
        log.log('DIRECTION column indicates a meta-analysis of {} sub-studies. --qc-substudies will exclude variants with ? in {} or more substudies.'.format(nstudies, 1+int(nstudies/2)))

    if args.max_or is not None: args.fix_dtype_cols.append('OR')
    if args.maf is not None: args.fix_dtype_cols.append('FRQ')
    if args.info is not None: args.fix_dtype_cols.append('INFO')
    if args.update_z_col_from_beta_and_se: args.fix_dtype_cols.extend(['BETA', 'SE'])
    if args.min_pval is not None: args.fix_dtype_cols.append('PVAL')

    # Validate that all required columns are present
    if (args.just_acgt or args.snps_only or args.drop_strand_ambiguous_snps) and (('A1' not in sumstats) or ('A2' not in sumstats)):
        raise(ValueError('A1 and A2 columns are required for --just-acgt, --snps-only, --drop-strand-ambiguous-snps'))
    if (args.just_rs_variants) and ('SNP' not in sumstats):
        raise(ValueError('SNP column is required --just-rs-variants'))

    # Perform QC procedures
    if len(args.dropna_cols) > 0:
        drop_sumstats(sumstats, log, "missing values in either of '{}' columns".format(args.dropna_cols), dropna_subset=args.dropna_cols)

    for col in args.fix_dtype_cols:
        if col in sumstats:
            log.log('Set column {} dtype to {}'.format(col, cols_type_map[col]))
            if cols_type_map[col] in [float, np.float64, int]:
                sumstats[col] = pd.to_numeric(sumstats[col], errors='coerce')
                if col in args.dropna_cols:
                    drop_sumstats(sumstats, log, "dtype conversion in {} column".format(col), dropna_subset=[col])
                if cols_type_map[col] == int:
                    sumstats[col] = sumstats[col].astype(int)
            else:
                sumstats[col] = sumstats[col].astype(cols_type_map[col])

    for range in exclude_ranges:
        idx = sumstats.index[(sumstats[cols.CHR] == range.chr) & (sumstats[cols.BP] >= range.from_bp) & (sumstats[cols.BP] < range.to_bp)]
        drop_sumstats(sumstats, log, 'exclude range {}:{}-{}'.format(range.chr, range.from_bp, range.to_bp), drop_labels=idx)

    if args.max_or is not None:
        drop_sumstats(sumstats, log, 'OR exceeded threshold {}'.format(args.max_or),
            drop_labels=sumstats.index[(sumstats.OR > args.max_or) | (sumstats.OR < (1/args.max_or))])

    if args.maf is not None:
        drop_sumstats(sumstats, log, 'MAF below threshold {}'.format(args.maf),
            drop_labels=sumstats.index[(sumstats.FRQ < args.maf) | (sumstats.FRQ>(1-args.maf))])

    if args.info is not None:
        drop_sumstats(sumstats, log, 'INFO below threshold {}'.format(args.info),
            drop_labels=sumstats.index[sumstats.INFO < args.info])

    if args.min_pval is not None:
        drop_sumstats(sumstats, log, 'PVAL below threshold {} or above 1.0'.format(args.min_pval),
            drop_labels=sumstats.index[(sumstats.PVAL < args.min_pval) | (sumstats.PVAL > 1.0)])

    if args.update_z_col_from_beta_and_se:
        sumstats['Z'] = np.divide(sumstats.BETA.values, sumstats.SE.values)

    if args.snps_only:
        drop_sumstats(sumstats, log, '--snps-only',
            drop_labels=sumstats.index[(sumstats['A1'].str.len() != 1) | (sumstats['A2'].str.len() != 1)])

    if args.just_acgt:
        drop_sumstats(sumstats, log, '--just-acgt',
            drop_labels=sumstats.index[np.logical_not(sumstats['A1'].isin(BASES)) | np.logical_not(sumstats['A2'].isin(BASES))])

    if args.drop_strand_ambiguous_snps:
        drop_sumstats(sumstats, log, '--drop-strand-ambiguous-snps',
            drop_labels=sumstats.index[(sumstats['A1'].map(str) + sumstats['A2']).isin(['AT', 'TA', 'CG', 'GC']) & (sumstats['A1'].str.len() == 1)])

    if args.just_rs_variants:
        drop_sumstats(sumstats, log, '--just-rs-variants',
            drop_labels=sumstats.index[np.logical_not(sumstats['SNP'].str.match('^rs\d+$'))])

    if nstudies is not None:
        drop_sumstats(sumstats, log, '--qc-substudies',
            drop_labels=sumstats.index[sumstats['DIRECTION'].str.count('\?') > int(nstudies/2)])

    fix_columns_order(sumstats).to_csv(args.out, index=False, header=True, sep='\t', na_rep='NA')
    log.log("{n} SNPs saved to {f}".format(n=len(sumstats), f=args.out))
    describe_sample_size(sumstats, log)

### =================================================================================
###                          Implementation for parser_zscore
### =================================================================================
def get_str_list_sign(str_list):
    return np.array([-1 if e[0]=='-' else 1 for e in list(str_list)], dtype=np.int)
 
def make_zscore(args, log):
    """
    Calculate z-score from p-value column and effect size column
    """
    """
    Takes csv files (created with the csv task of this script).
    Require columns: SNP, P, and one of the signed summary statistics columns (BETA, OR, Z, LOGODDS).
    Creates corresponding mat files which can be used as an input for the conditional fdr model.
    Only SNPs from the reference file are considered. Zscores of strand ambiguous SNPs are set to NA.
    """
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    columns = list(pd.read_csv(args.sumstats, sep='\t', nrows=0).columns)
    log.log('Columns in {}: {}'.format(args.sumstats, columns))

    if (args.effect is None) and (not args.a1_inc):
        if cols.Z in columns: args.effect = cols.Z
        elif cols.BETA in columns: args.effect = cols.BETA
        elif cols.OR in columns: args.effect = cols.OR
        elif cols.LOGODDS in columns: args.effect = cols.LOGODDS
        else: raise(ValueError('Warning: signed effect column is not detected in {}. Enable --a1-inc'.format(args.sumstats)))
        effect_size_column_count = np.sum([int(c in columns) for c in [cols.Z, cols.BETA, cols.OR, cols.LOGODDS]])
        if effect_size_column_count > 1: log.log('Warning: Multiple columns indicate effect direction')
        if effect_size_column_count == 1: log.log('Use {} column as effect direction.'.format(args.effect))

    missing_columns = [c for c in [cols.PVAL, args.effect] if (c != None) and (c not in columns)]
    if missing_columns: raise(ValueError('{} columns are missing'.format(missing_columns)))

    if args.a1_inc:
        signed_effect = None
        effect_col_dtype_map = {}
    else:
        # if signed_effect is true, take effect column as string to handle correctly
        # case of truncated numbers, e.g.: 0.00 and -0.00 should have different sign
        signed_effect = False if args.effect == cols.OR else True
        effect_col_dtype_map = {args.effect: (str if signed_effect else np.float)}

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    reader = pd.read_csv(args.sumstats, sep='\t', chunksize=args.chunksize,
        dtype=effect_col_dtype_map, float_precision='high')
    n_snps = 0
    with (open(args.out, 'a') if args.out != sys.stdout else sys.stdout) as out_f:
        for chunk_index, chunk in enumerate(reader):
            if chunk_index==0: log.log('Column types: ' + ', '.join([column + ':' + str(dtype) for (column, dtype) in zip(chunk.columns, chunk.dtypes)]))
            if args.a1_inc:
                effect_sign = np.ones(len(chunk))
            elif signed_effect:
                # effect column has str type
                # -1 if effect starts with '-' else 1
                effect_sign = get_str_list_sign(chunk[args.effect].astype(str))
            else:
                # effect column has np.float type
                # 1 if effect >=1 else -1
                if (chunk[args.effect] < 0).any():
                    raise ValueError("OR column contains negative values")
                effect_sign = np.sign(chunk[args.effect].values - 1)
                effect_sign[effect_sign == 0] = 1
            chunk[cols.PVAL] = pd.to_numeric(chunk[cols.PVAL], errors='coerce')
            chunk[cols.Z] = -stats.norm.ppf(chunk[cols.PVAL].values*0.5)*effect_sign.astype(np.float64)
            chunk.to_csv(out_f, index=False, header=(chunk_index==0), sep='\t', na_rep='NA')
            n_snps += len(chunk)
            eprint("{f}: {n} lines processed".format(f=args.sumstats, n=(chunk_index+1)*args.chunksize))
    log.log("{n} SNPs saved to {f}".format(n=n_snps, f=args.out))


### =================================================================================
###                          Implementation for parser_pvalue
### =================================================================================
def make_pvalue(args, log):
    """
    Calculate p-value column from 'z'' or 'beta'/'se' columns
    """
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    columns = list(pd.read_csv(args.sumstats, sep='\t', nrows=0).columns)
    log.log('Columns in {}: {}'.format(args.sumstats, columns))

    if 'PVAL' in columns:
        log.log('PVAL already exists, nothing to be done.')
        return
    if ('Z' not in columns) and (('BETA' not in columns) or ('SE' not in column)):
        raise(ValueError("Neither Z nor BETA/SE are available in the input summary stats file"))

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    reader = pd.read_csv(args.sumstats, sep='\t', chunksize=args.chunksize)
    n_snps = 0
    with (open(args.out, 'a') if args.out != sys.stdout else sys.stdout) as out_f:
        for chunk_index, chunk in enumerate(reader):
            if chunk_index==0: log.log('Column types: ' + ', '.join([column + ':' + str(dtype) for (column, dtype) in zip(chunk.columns, chunk.dtypes)]))
            if 'Z' in columns:
                chunk[cols.PVAL] = scipy.stats.norm.sf(abs(chunk['Z'].values))*2
            elif ('BETA'in columns) and ('SE' in columns):
                chunk[cols.PVAL] = scipy.stats.norm.sf(abs(np.divide(chunk['BETA'].values, chunk['SE'].values)))*2
            chunk.to_csv(out_f, index=False, header=(chunk_index==0), sep='\t', na_rep='NA')
            n_snps += len(chunk)
            eprint("{f}: {n} lines processed".format(f=args.sumstats, n=(chunk_index+1)*args.chunksize))
    log.log("{n} SNPs saved to {f}".format(n=n_snps, f=args.out))

### =================================================================================
###                          Implementation for parser_beta
### =================================================================================
def make_beta(args, log):
    """
    Calculate beta column from OR or LOGODDS
    """
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    df = pd.read_csv(args.sumstats, sep='\t')
    log.log('Done, {} markers found'.format(len(df)))

    if 'BETA' in df:
        log.log('WARNING: nothing to be done, BETA column is already present')
    elif 'LOGODDS' in df:
        df.rename(columns={'LOGODDS':'BETA'}, inplace=True)
        log.log('Rename LOGODDS column to BETA')
    elif 'OR' in df:
        df['BETA'] = np.log(df['OR'].values)
        df.drop(labels=['OR'], axis=1, inplace=True)
        log.log('Calculate BETA=log(OR), and drop the OR column')

    fix_columns_order(df).to_csv(args.out, index=False, header=True, sep='\t', na_rep='NA')
    log.log("{n} SNPs saved to {f}".format(n=len(df), f=args.out))

### =================================================================================
###                          Implementation for parser_mat
### ================================================================================= 
_base_complement = {"A":"T", "C":"G", "G":"C", "T":"A"}
def _complement(seq):
    return "".join([_base_complement[b] for b in seq])

def _reverse_complement_variant(variant):
    # variant should be a 2-elemet sequence with upper case string elements
    return ("".join([_base_complement[b] for b in variant[0][::-1]]),
            "".join([_base_complement[b] for b in variant[1][::-1]]))

def _is_alleles_match(variant_x, variant_y):
    if variant_x == variant_y: return True
    if variant_x == variant_y[::-1]: return True
    if variant_x == _reverse_complement_variant(variant_y): return True
    if variant_x == _reverse_complement_variant(variant_y)[::-1]: return True
    return False

def make_mat(args, log):
    """
    Takes csv files (created with the csv task of this script).
    Require columns: SNP, P, and one of the signed summary statistics columns (BETA, OR, Z, LOGODDS).
    Creates corresponding mat files which can be used as an input for the conditional fdr model.
    Only SNPs from the reference file are considered. Zscores of strand ambiguous SNPs are set to NA.
    """
    if args.sumstats == '-': args.sumstats = sys.stdin
    check_input_file(args.ref)
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    # very special handling of cases where input file has no alleles information
    if args.ignore_alleles:
        log.log('Ignore A1/A2 alleles from the input files')
        log.log('Reading reference file {}...'.format(args.ref))
        df_ref = pd.read_csv(args.ref, sep='\t', usecols=[cols.SNP])
        log.log('Reading summary statistics file {}...'.format(args.sumstats))
        df_sumstats = pd.read_csv(args.sumstats, sep='\t', float_precision='high', usecols=[cols.SNP, cols.PVAL])
        log.log('Merging with reference file...')
        df_sumstats.drop_duplicates(subset=[cols.SNP], keep='first', inplace=True)
        df_result = pd.merge(df_ref, df_sumstats, how='left', on='SNP')
        num_matches = df_result[cols.PVAL].notnull().sum()
        if num_matches == 0: raise(ValueError("No SNPs match after joining with reference data"))
        log.log("{f}: {n} SNPs matched with reference file".format(f=args.sumstats, n=num_matches))
        sio.savemat(args.out, {'logpvec'+args.trait: -np.log10(df_result[cols.PVAL].values)}, format='5', do_compression=False, oned_as='column', appendmat=False)
        log.log("%s created" % args.out)
        return

    reader = pd.read_csv(args.sumstats, sep='\t', chunksize=args.chunksize, float_precision='high')
    df_out = None
    for chunk_index, ss_chunk in enumerate(reader):
        # (BEGIN) special handling of the first chunk
        if chunk_index==0:
            columns = list(ss_chunk.columns)

            # check whether arguments are correct
            if args.keep_all_cols and args.keep_cols:
                err_msg = ("Misleading input arguments! Use either '--keep-cols' or "
                    "'--keep-all-cols' option, but not both at a time.")
                raise(ValueError(err_msg))
            not_in_csv_keep_cols = set(args.keep_cols) - set(columns)
            if not_in_csv_keep_cols:
                log.log("Warning: '--keep-cols' contains names which are absent in csv "
                    "file: %s. They will be ignored." % ', '.join(not_in_csv_keep_cols))

            if cols.Z not in columns:
                raise(RuntimeError('Z column is not present in the input file. Use ``sumstats.py zscore`` to enrich summary stats with z-score column.'))

            # cols2ignore: columns from sumstats file which are dropped anyway
            cols2ignore = ["SNP", "CHR", "BP", "A1", "A2", "Z"]
            if (set(cols2ignore) - set(columns)):
                # If this happens, probably standard format of csv file has changed.
                absent_cols = set(cols2ignore) - set(columns)
                err_msg = ("Columns required in standard csv file: {} are missing in "
                    "input csv file {}.").format(', '.join(absent_cols), args.sumstats)
                raise(RuntimeError(err_msg))
            if "DIRECTION" in columns: cols2ignore.append("DIRECTION")
            # cols2keep: columns from sumstats file which are kept in mat file
            cols2keep = cols._fields if args.keep_all_cols else args.keep_cols
            # cols2keep: columns from sumstats file which are not saved to mat file
            cols2drop = (set(columns) - set(cols2keep)) | set(cols2ignore)

            n_col = cols.N if cols.N in columns else None
            ncase_col = cols.NCASE if cols.NCASE in columns else None
            ncontrol_col = cols.NCONTROL if cols.NCONTROL in columns else None
            if (not args.without_n) and ((n_col is None) and ((ncase_col is None) or (ncontrol_col is None))):
                raise(ValueError('Sample size column is not detected in {}. Expact either N or NCASE, NCONTROL column.'.format(args.sumstats)))
            missing_columns = [c for c in [cols.A1, cols.A2, cols.SNP, cols.PVAL] if (c != None) and (c not in columns)]
            if missing_columns: raise(ValueError('{} columns are missing'.format(missing_columns)))

            log.log('Reading reference file {}...'.format(args.ref))
            usecols = [cols.SNP, cols.A1, cols.A2]
            ref_reader = pd.read_csv(args.ref, sep='\t', usecols=usecols,
                chunksize=args.chunksize)
            ref_dict = {}
            for ref_chunk in ref_reader:
                ref_chunk.drop(ref_chunk.index[np.logical_not(ref_chunk['A1'].str.upper().str.match('^[ACTG]*$')) | np.logical_not(ref_chunk['A2'].str.upper().str.match('^[ACTG]*$'))], inplace=True)
                if ref_chunk.empty: continue
                gtypes = zip(ref_chunk[cols.A1].apply(str.upper),ref_chunk[cols.A2].apply(str.upper))
                #TODO?: add check whether some id is already in ref_dict
                ref_dict.update(dict(zip(ref_chunk[cols.SNP], gtypes)))
            ref_dict = {i: (variant, _reverse_complement_variant(variant),
                            variant[::-1], _reverse_complement_variant(variant[::-1]))
                        for i, variant in ref_dict.items()}
            ref_snps = pd.read_csv(args.ref, sep='\t', usecols=[cols.SNP], squeeze=True)
            #TODO?: add check whether ref_snps contains duplicates
            log.log("Reference dict contains {d} snps.".format(d=len(ref_dict)))

            log.log('Reading summary statistics file {}...'.format(args.sumstats))
            log.log('Column types: ' + ', '.join([column + ':' + str(dtype) for (column, dtype) in zip(ss_chunk.columns, ss_chunk.dtypes)]))

        # (END) special handling of the first chunk

        ss_chunk = ss_chunk.loc[ss_chunk[cols.SNP].isin(ref_dict),:]
        if ss_chunk.empty: continue
        gtypes = list(zip(ss_chunk[cols.A1].apply(str.upper),ss_chunk[cols.A2].apply(str.upper)))
        # index of SNPs that have the same alleles as indicated in reference
        ind = [gt in ref_dict[sid] for sid, gt in zip(ss_chunk[cols.SNP], gtypes)]
        ss_chunk = ss_chunk.loc[ind,:]
        gtypes = [gt for gt, j in zip(gtypes, ind) if j]
        log10pv = -np.log10(ss_chunk[cols.PVAL].values)
        # not_ref_effect = [
        #   1 if effect allele in data == other allele in reference
        #   -1 if effect allele in data == effect allele in reference ]
        # So zscores with positive effects will be positive and zscores with
        # negative effects will stay negative, since
        # stats.norm.ppf(ss_chunk[cols.PVAL]*0.5) is always negetive (see zvect
        # calculation below).
        not_ref_effect = np.array([1 if gt in ref_dict[sid][:2] else -1
            for sid, gt in zip(ss_chunk[cols.SNP], gtypes)])
        #TODO: check proportion of positive and negative effects
        zvect = ss_chunk[cols.Z].values*not_ref_effect
        ind_ambiguous = [j for j,gt in enumerate(gtypes) if gt == _reverse_complement_variant(gt)[::-1]]
        # set zscore of ambiguous SNPs to nan
        zvect[ind_ambiguous] = np.nan
        #TODO: check whether output df contains duplicated rs-ids (warn)

        # reindex by SNP, add required columns and drop unnecessary columns
        ss_chunk.index = ss_chunk[cols.SNP]
        # add required columns
        ss_chunk["logpvec"] = log10pv
        ss_chunk["zvec"] = zvect
        if not args.without_n:
            if n_col is None:
                nvec = 4./(1./ss_chunk[ncase_col] + 1./ss_chunk[ncontrol_col])
            else:
                nvec = ss_chunk[n_col].values
            ss_chunk["nvec"] = nvec
        ss_chunk.drop(cols2drop, axis=1, inplace=True)

        if df_out is None:
            df_out = ss_chunk.copy()
        else:
            df_out = df_out.append(ss_chunk)

        eprint("{f}: {n} lines processed, {m} SNPs matched with reference file".format(f=args.sumstats, n=(chunk_index+1)*args.chunksize, m=len(df_out)))

    if df_out.empty: raise(ValueError("No SNPs match after joining with reference data"))
    dup_index = df_out.index.duplicated(keep=False)
    if dup_index.any():
        log.log("Duplicated SNP ids detected:")
        log.log(df_out[dup_index])
        log.log("Keeping only the first occurance.")
    df_out = df_out[~df_out.index.duplicated(keep='first')]
    # allign index accordind order of SNPs in ref, insert NaN rows for SNPs that
    # present in ref but absent in sumstats file
    df_out = df_out.reindex(ref_snps)

    log.log('Writing .mat file...')

    #TODO: check column type, transform into matrix if not numeric
    save_dict = {c+args.trait: df_out[c].astype(np.float64).values for c in df_out.columns}

    sio.savemat(args.out, save_dict, format='5', do_compression=False,
        oned_as='column', appendmat=False)
    log.log("%s created" % args.out)

### =================================================================================
###                          Implementation for parser_variantid
### =================================================================================
def make_variantid(args, log):
    if args.sumstats == '-': args.sumstats = sys.stdin
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_input_file(args.ref)
    check_output_file(args.out, args.force)

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    df = pd.read_csv(args.sumstats, sep='\t', dtype={"CHR":str})
    log.log('Done, {} markers found'.format(len(df)))

    log.log('Reading reference file {}...'.format(args.ref))
    ref = pd.read_csv(args.ref, sep='\t', usecols=[cols.CHR, cols.BP, cols.A1, cols.A2], dtype={cols.CHR:str})
    ref.rename(columns={'A1': 'A1_ref', 'A2': 'A2_ref'}, inplace=True)
    log.log("Reference dict contains {d} snps.".format(d=len(ref)))

    log.log('Merging summary statistics file with the reference...')
    ref['DUP']=ref.duplicated(subset=['CHR', 'BP'], keep=False)
    df['index'] = df.index

    df_nodups = pd.merge(df[['index', 'CHR', 'BP']], ref[['CHR', 'BP', 'A1_ref', 'A2_ref']][~ref['DUP']], on=['CHR', 'BP'], how='inner')
    df_variant_id = df_nodups
    if ('A1' in df) and ('A2' in df):
        df_dups = pd.merge(df[['index', 'CHR', 'BP', 'A1', 'A2']], ref[['CHR', 'BP', 'A1_ref', 'A2_ref']][ref['DUP']], on=['CHR', 'BP'], how='inner')
        if not df_dups.empty: df_dups = df_dups[[_is_alleles_match((row.A1, row.A2), (row.A1_ref, row.A2_ref)) for _, row in df_dups.iterrows()]].copy()
        if not df_dups.empty: df_dups.drop(labels=['A1', 'A2'], axis=1, inplace=True)
        if not df_dups.empty: df_variant_id = pd.concat([df_nodups, df_dups]).copy()
    else:
        log.log("WARNING: sumstats file has no allele codes")

    df_variant_id['VARIANT_ID']=df_variant_id['CHR'].astype(str)+':'+df_variant_id['BP'].astype(str)+':'+df_variant_id['A1_ref']+':'+df_variant_id['A2_ref']
    df_variant_id.drop_duplicates(subset=['VARIANT_ID'], keep=False, inplace=True)
    df_variant_id.drop_duplicates(subset=['index'], keep=False, inplace=True)

    df = pd.merge(df, df_variant_id[['index', 'VARIANT_ID']], how='left', on='index')
    df.drop(labels=['index'], axis=1, inplace=True)
    df['VARIANT_ID'].fillna('.', inplace=True)

    log.log("Merging complete, {n} out of {m} SNPs receive VARIANT_ID".format(n=(df['VARIANT_ID'] != '.').sum(), m=len(df)))

    fix_columns_order(df).to_csv(args.out, index=False, header=True, sep='\t', na_rep='NA')
    log.log("{n} SNPs saved to {f}".format(n=len(df), f=args.out))

### =================================================================================
###                          Implementation for parser_lift
### =================================================================================
def make_lift(args, log):
    """
    Lift RS numbers to a newer version of SNPdb, and/or
    liftover chr:pos to another genomic build using NCBI chain files.
    """
    from pyliftover import LiftOver
    from lift_rs_numbers import LiftRsNumbers

    if args.sumstats == '-': args.sumstats = sys.stdin
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    if args.chain_file is not None: check_input_file(args.chain_file)
    if args.snp_chrpos is not None: check_input_file(args.snp_chrpos)
    if args.snp_history is not None: check_input_file(args.snp_history)
    if args.rs_merge_arch is not None: check_input_file(args.rs_merge_arch)

    if (args.snp_history is not None) != (args.rs_merge_arch is not None):
        raise(ValueError('--snp-history and --rs-merge-arch must be used together'))

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    df = pd.read_csv(args.sumstats, sep='\t')
    log.log('Done, {} markers found'.format(len(df)))

    lift_bp = None; lift_rs = None; snp_chrpos = None

    if (args.chain_file is not None) and (cols.CHR in df) and (cols.BP in df):
        log.log('Reading {}...'.format(args.chain_file))
        lift_bp = LiftOver(args.chain_file)

    if (args.snp_history is not None) and (cols.SNP in df):
        lift_rs = LiftRsNumbers(hist_file=args.snp_history, merge_file=args.rs_merge_arch)

    if args.snp_chrpos is not None:
        log.log('Reading {}...'.format(args.snp_chrpos))
        snp_chrpos = pd.read_csv(args.snp_chrpos, sep='\t', header=None, usecols=[0,1,2])
        snp_chrpos.columns=['snp_id','chr','pos'] #,'orien','neighbor_snp_list','isPAR']
        snp_chrpos.dropna(subset=['pos'],inplace=True)           # drop NA positions
        snp_chrpos['pos']=snp_chrpos['pos'].astype(np.int) + 1   # convert to integer unity-based positions
        snp_chrpos['chr'].replace({'X':23, 'Y':24, 'PAR': 25, 'MT': 26}, inplace=True)   # standarize chr labels
        snp_chrpos['chr']=snp_chrpos['chr'].astype(np.int)
        log.log('Done, found {} entries'.format(len(snp_chrpos)))
        # if snp_chrpos.duplicated(subset=['snp_id'], keep=False).sum() != 0:
        #   raise('Duplicated snp_id found in SNPChrPosOnRef file')

    indices_with_old_chrpos = range(len(df))  # indices with original chr:pos
    fixes = []
    if (cols.SNP in df) and (lift_rs is not None):
        # Fix1 brings forward SNP rs# numbers and set SNP rs# to None for SNPs found in SNPHistory table
        df[cols.SNP], stats = lift_rs.lift(df[cols.SNP])
        fixes.append('{} rs# numbers has changed based on RsMergeArch table'.format(stats['lifted']))
        log.log(stats)

    if (cols.SNP in df) and (snp_chrpos is not None):
        # Fix2 set chr:pos based on SNPChrPosOnRef table (only applies to SNPs with rs# number, not to other markers)
        df['SNP_LIFTED'] = [(int(x[2:]) if (x and x.startswith('rs') and x[2:].isdigit()) else -1) for x in df[cols.SNP]]
        df = pd.merge(df, snp_chrpos, how='left', left_on='SNP_LIFTED', right_on='snp_id')
        log.log('Warning: there are {} SNPs with a valid RS number, but not found in SNPChrPosOnRef'.format(((df['SNP_LIFTED'] != -1) & df['snp_id'].isnull()).sum()))

        if cols.CHR in df and cols.BP in df:
            idx = ((df['pos'] != df[cols.BP]) | (df['chr'] != df[cols.CHR])) & ~df['pos'].isnull() & ~df['chr'].isnull()
            df.loc[idx, cols.BP] = df.loc[idx, 'pos'].astype(int)
            df.loc[idx, cols.CHR] = df.loc[idx, 'chr'].astype(int)
            fixes.append('{} markers receive new CHR:POS based on SNPChrPosOnRef table'.format(idx.sum()))
        else:
            idx = ~df['pos'].isnull() & ~df['chr'].isnull()
            df[cols.BP] = np.nan; df[cols.CHR] = np.nan
            df.loc[idx, cols.BP] = df.loc[idx, 'pos'].astype(int)
            df.loc[idx, cols.CHR] = df.loc[idx, 'chr'].astype(int)
            fixes.append('{} markers receive CHR:POS based on SNPChrPosOnRef table'.format(idx.sum()))

        indices_with_old_chrpos = [i for (i, b) in enumerate(df['pos'].isnull() | df['chr'].isnull()) if b]
        df.drop(['SNP_LIFTED', 'snp_id', 'chr', 'pos'], axis=1, inplace=True)

    if (cols.CHR in df) and (cols.BP in df) and (cols.SNP not in df) and (snp_chrpos is not None):
        # Fix3 set SNP rs# based on SNPChrPosOnRef table based on CHR:POS
        # It is a fairly rough guess about SNP rs#, because we do not take allele codes into account.
        # Therefore it is important that this step applies only when SNP column is missing.
        df = pd.merge(df, snp_chrpos, how='left', left_on=[cols.CHR, cols.BP], right_on=['chr', 'pos'])
        df['snp_id'][df['snp_id'].isnull()] = -1
        df['snp_id'] = 'rs' + df['snp_id'].astype(int).astype(str)
        df['snp_id'][df['snp_id'] == 'rs-1'] = None
        df['SNP'] = df['snp_id']
        fixes.append('{} markers receive SNP rs# based on SNPChrPosOnRef table'.format((~df[cols.SNP].isnull()).sum()))
        df.drop(['snp_id', 'chr', 'pos'], axis=1, inplace=True)

    if lift_bp is not None:
        # Fix4 lifts chr:pos to another genomic build. This step is OFF by default, only applies if user provided chain file.
        # Note that lifting with pyliftover is rather slow, so we apply this step only to markers that are not in SNPChrPosOnRef table.
        log.log('Lift CHR:POS for {} SNPs to another genomic build...'.format(len(indices_with_old_chrpos)))
        unique = 0; multi = 0; failed = 0
        for i, index in enumerate(indices_with_old_chrpos):
            if (i+1) % 100 == 0: eprint('Finish {} SNPs'.format(i+1))
            chri = int(df.loc[index, cols.CHR]); bp = int(df.loc[index, cols.BP]); snp = df.loc[index, cols.SNP]
            lifted = lift_bp.convert_coordinate('chr{}'.format(chri), bp)
            if (lifted is None) or (len(lifted) == 0):
                #log.log('Unable to lift SNP {} at chr{}:{}, delete'.format(snp, chri, bp))
                df.loc[index, cols.CHR] = None
                df.loc[index, cols.BP] = None
                failed += 1
                continue
            if len(lifted) > 1:
                log.log('Warning: SNP {} at chr{}:{} lifts to multiple position, use first.'.format(snp, chri, bp))
                multi += 1
            if len(lifted) == 1:
                unique += 1

            df.loc[index, cols.CHR] = int(lifted[0][0][3:])
            df.loc[index, cols.BP] = lifted[0][1]
        log.log('Done, {} failed, {} unique, {} multi'.format(failed, unique, multi))
        fixes.append('{} markers receive new CHR:POS based on liftover chain files'.format(unique + multi))

    if cols.SNP in df:
        df[cols.SNP].fillna('.', inplace=True)
        num_variants_without_rs_number = (df[cols.SNP]=='.').sum()
        if num_variants_without_rs_number > 0:
            log.log('{} variants have missing SNP rs#'.format(num_variants_without_rs_number))

    if not args.keep_bad_snps:
        if (cols.CHR in df) and (cols.BP in df):
            df_len = len(df)
            df.dropna(subset=[cols.CHR, cols.BP], inplace=True)     # Fix6, due to failed liftover across genomic builds
            if len(df) < df_len:
                fixes.append("{n} markers were dropped due to missing CHR:POS information or due to failed CHR:POS lift".format(n = df_len - len(df)))
            df[cols.CHR] = df[cols.CHR].astype(int)
            df[cols.BP] = df[cols.BP].astype(int)

    fix_columns_order(df).to_csv(args.out + ('.gz' if args.gzip else ''),
        index=False, header=True, sep='\t', na_rep=args.na_rep,
        compression='gzip' if args.gzip else None)

    log.log("{n} SNPs saved to {f}".format(n=len(df), f=args.out))
    describe_sample_size(df, log)
    log.log('Summary: \n\t{}'.format("\n\t".join(fixes)))

### =================================================================================
###                          Implementation for parser_clump
### =================================================================================
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def tar_filter(tarinfo):
    if os.path.basename(tarinfo.name).startswith('sumstats'): return None
    return tarinfo

def clump_cleanup(args, log):
    temp_out = args.out + '.temp'
    log.log('Saving intermediate files to {out}.temp.tar.gz'.format(out=args.out))
    with tarfile.open('{out}.temp.tar.gz'.format(out=args.out), "w:gz") as tar:
        tar.add(temp_out, arcname=os.path.basename(temp_out), filter=tar_filter)
    rmtree(temp_out)

def make_clump(args, log):
    """
    Clump summary stats, produce lead SNP report, produce candidate SNP report
    TBD: refine output tables
    TBD: in snps table, do an outer merge - e.i, include SNPs that pass p-value threshold (some without locus number), and SNPs without p-value (e.i. from reference genotypes)
    """
    #check_output_file(args.out, args.force)
    #for chri in range(1, 23):
    #    check_input_file(sub_chr(args.bfile_chr, chri) + '.bed')
    exclude_ranges = make_ranges(args.exclude_ranges, log)

    temp_out = args.out + '.temp'
    if not os.path.exists(temp_out):
        os.makedirs(temp_out)

    if (not args.sumstats) and (not args.sumstats_chr):
        raise ValueError('At least one of --sumstats or --sumstats-chr must be specified')

    if args.chr_labels is None:
        args.chr_labels = list(range(1, 23))

    if args.sumstats_chr:
        args.sumstats_chr = [sub_chr(args.sumstats_chr, chri) for chri in args.chr_labels]
    else:
        args.sumstats_chr = ['{}/sumstats.chr{}.csv'.format(temp_out, chri) for chri in args.chr_labels]

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
        for chri, df_chr_file in zip(args.chr_labels, args.sumstats_chr):
            df_sumstats[df_sumstats[args.chr] == int(chri)].to_csv(df_chr_file, sep='\t',index=False)
    else:
        for df_chr_file in args.sumstats_chr:
            check_input_file(df_chr_file)
        log.log('Reading {}...'.format(args.sumstats_chr))
        df_sumstats = pd.concat([pd.read_csv(df_chr_file, delim_whitespace=True) for df_chr_file in args.sumstats_chr])
        log.log('Read {} SNPs'.format(len(df_sumstats)))

    for chri, df_chr_file in zip(reversed(args.chr_labels), reversed(args.sumstats_chr)):
        # Step1 - find independent significant SNPs
        execute_command(
            "{} ".format(args.plink) +
            "--bfile {} ".format(sub_chr(args.bfile_chr, chri)) +
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
            "--bfile {} ".format(sub_chr(args.bfile_chr, chri)) +
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
            "--bfile {} ".format(sub_chr(args.bfile_chr, chri)) +
            "--r2 --ld-window {} --ld-window-r2 {} ".format(args.ld_window_kb, args.indep_r2) +
            "--ld-snp-list {out}/indep.chr{chri}.clumped.snps ".format(out=temp_out, chri=chri) +
            "--out  {out}/indep.chr{chri} ".format(out=temp_out, chri=chri),
            log)

    # find indep to lead SNP mapping (a data frame with columns 'LEAD' and 'INDEP')
    files = ["{}/lead.chr{}.clumped".format(temp_out, chri) for chri in args.chr_labels]
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
    files = ["{out}/indep.chr{chri}.ld".format(out=temp_out, chri=chri) for chri in args.chr_labels]
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
                df_lead['locusnum'][i] = df_lead['locusnum'][i-1]
                df_lead['MaxBP_locus'][i] = np.max([df_lead['MaxBP_locus'][i-1], df_lead['MaxBP_locus'][i]])
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

### =================================================================================
###                          Implementation for parser_rs
### =================================================================================
def make_rs(args, log):
    """
    Augument summary statistic file with SNP RS number from reference file.
    Merging is done on chromosome and position.
    """
    check_input_file(args.ref)
    check_input_file(args.sumstats)
    check_output_file(args.out, force=args.force)

    log.log('Reading reference file {}...'.format(args.ref))
    usecols = [cols.SNP, cols.CHR, cols.BP]
    if args.a1a2: usecols = usecols + ['A1', 'A2']
    ref_file = pd.read_csv(args.ref, sep='\t', usecols=usecols)
    log.log("Reference dict contains {d} snps.".format(d=len(ref_file)))

    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    reader = pd.read_csv(args.sumstats, dtype=str, sep='\t', chunksize=args.chunksize)
    n_snps = 0
    with open(args.out, 'a') as out_f:
        for chunk_index, chunk in enumerate(reader):
            if cols.SNP in chunk: chunk.drop(cols.SNP, axis=1, inplace=True)
            if args.a1a2:
                if (cols.A1 in chunk): chunk.drop(cols.A1, axis=1, inplace=True)
                if (cols.A2 in chunk): chunk.drop(cols.A2, axis=1, inplace=True)
            chunk.BP = chunk.BP.astype(int)
            chunk.CHR = chunk.CHR.astype(int)
            chunk = pd.merge(chunk, ref_file, how='left', on=[cols.CHR, cols.BP])
            chunk = chunk.sort_index(axis=1)
            chunk.to_csv(out_f, index=False, header=(chunk_index==0), sep='\t', na_rep='NA')
            n_snps += len(chunk)
            eprint("{f}: {n} lines processed".format(f=args.sumstats, n=(chunk_index+1)*args.chunksize))
    log.log("{n} SNPs saved to {f}".format(n=n_snps, f=args.out))

### =================================================================================
###                          Implementation for make_ls
### =================================================================================
def make_ls(args, log):
    ml = max([len(os.path.basename(file).replace('.csv.gz', '')) for file in glob.glob(args.path)])
    cols_list = [x for x in cols._asdict() if x not in ['A1A2', 'CHRPOS', 'CHRPOSA1A2', 'SNP', 'CHR', 'BP', 'PVAL', 'A1', 'A2']]
    log.log('{f}\t{n}\t{c}'.format(f='file'.ljust(ml),n='#snp'.ljust(9),c='\t'.join([x.replace('NCONTROL', 'NCONT.') for x in cols_list])))
    for file in glob.glob(args.path):
        if not os.path.isfile(file): continue
        if '_noMHC' in file: continue
        num_snps = np.nan; n = np.nan; ncase = np.nan; ncontrol = np.nan 
        try:
            file_log = os.path.splitext(file)[0] + '.log'
            if os.path.isfile(file_log):
                lines = open(file_log, 'r').readlines()
                num_snps = [int(x.group(1)) for x in [re.search('([0-9]+) SNPs saved to', line.strip()) for line in lines] if x][0]
                n = [float(x.group(1)) for x in [re.search(r'Sample size.* N=([^ ]+) ', line.strip()) for line in lines] if x][0]
                ncase = [float(x.group(1)) for x in [re.search(r'Sample size.* NCASE=([^ ]+) ', line.strip()) for line in lines] if x][0]
                ncontrol = [float(x.group(1)) for x in [re.search(r'Sample size.* NCONTROL=([^ ]+)', line.strip()) for line in lines] if x][0]
        except:
            pass

        num_snps = 'n/a' if np.isnan(num_snps) else str(num_snps)
        n = 'n/a' if np.isnan(n) else str(int(n))
        ncase = 'n/a' if np.isnan(ncase) else str(int(ncase))
        ncontrol = 'n/a' if np.isnan(ncontrol) else str(int(ncontrol))

        for chunk in pd.read_csv(file, sep='\t', chunksize=1):
            yes_no_or_sample_size = [(  n if (x == 'N') else
                                        ncase if (x == 'NCASE') else
                                        ncontrol if (x == 'NCONTROL') else
                                        'YES' if x in chunk
                                        else '-') for x in cols_list]
            log.log('{f}\t{n}\t{c}'.format(f=os.path.basename(file).replace('.csv.gz', '').ljust(ml), c='\t'.join(yes_no_or_sample_size),n=str(num_snps).ljust(9)))
            break
    log.log('Columns description:')
    for cname in sorted(cols._asdict()):
        log.log('{c}\t{d}'.format(c=cname, d=describe_cname[cname]))

### =================================================================================
###                          Implementation for mat_to_csv
### =================================================================================
def mat_to_csv(args, log):
    check_input_file(args.ref)
    check_input_file(args.mat)
    check_output_file(args.out, args.force)

    log.log('Reading reference file {}...'.format(args.ref))
    ref_file = pd.read_csv(args.ref, sep='\t', usecols=[cols.SNP, cols.A1, cols.A2])
    log.log("Reference dict contains {d} snps.".format(d=len(ref_file)))

    log.log('Reading .mat file {}...'.format(args.mat))
    df = ref_file.copy()
    sumstats = sio.loadmat(args.mat)
    for key in sumstats.keys():
        if key.lower().startswith('zvec'):
            df['Z'] = sumstats[key]
            log.log('Found zvec, {} non-nan values.'.format(np.sum(~np.isnan(sumstats[key]))))
        if key.lower().startswith('logpvec'):
            df['PVAL'] = np.power(10, -sumstats[key])
            log.log('Found logpvec, {} non-nan values.'.format(np.sum(~np.isnan(sumstats[key]))))
        if key.lower().startswith('nvec'):
            df['N'] = sumstats[key]
            log.log('Found nvec, {} non-nan values.'.format(np.sum(~np.isnan(sumstats[key]))))

    df.to_csv(args.out,
        index=False, header=True, sep='\t', na_rep=args.na_rep,
        compression='gzip' if args.gzip else None)
    log.log('Result is written into {}'.format(args.out))

### =================================================================================
###                          Implementation for ldsc_to_mat
### =================================================================================
def ldsc_to_mat(args, log):
    check_input_file(args.ref)
    if args.sumstats: check_input_file(args.sumstats)
    if args.chr_labels is None:
        args.chr_labels = list(range(1, 23))
    for chri in args.chr_labels:
        if args.ldscore: check_input_file(args.ldscore.replace('@', str(chri)))
        if args.annot: check_input_file(args.annot.replace('@', str(chri)))
        if args.M: check_input_file(args.M.replace('@', str(chri)))
        if args.M_5_50: check_input_file(args.M_5_50.replace('@', str(chri)))
    check_output_file(args.out, args.force)

    log.log('Reading reference file {}...'.format(args.ref))
    ref_file = pd.read_csv(args.ref, sep='\t', usecols=[cols.SNP, cols.A1, cols.A2])
    log.log("Reference dict contains {d} snps.".format(d=len(ref_file)))

    save_dict = {}
    if args.sumstats:
        df_sumstats = pd.read_csv(args.sumstats, sep='\t')
        df_len = len(df_sumstats)
        log.log('Read {} SNPs from --sumstats file'.format(df_len))

        df_sumstats = pd.merge(ref_file, df_sumstats, how='left', on=cols.SNP)
        df_sumstats = df_sumstats.dropna(how='any')
        log.log('Removed {} SNPs not in --ref file'.format(df_len - len(df_sumstats)))
        df_len = len(df_sumstats)

        df_sumstats['ALLELES'] = df_sumstats.A1_x + df_sumstats.A2_x + df_sumstats.A1_y + df_sumstats.A2_y
        df_sumstats = df_sumstats[filter_alleles(df_sumstats['ALLELES'])].copy()
        log.log('Removed {} SNPs with alleles not matching --ref file'.format(df_len - len(df_sumstats)))
        log.log('{} SNPs remain'.format(len(df_sumstats)))

        df_z = df_sumstats.Z.copy()
        df_sumstats.Z = align_alleles(df_sumstats.Z, df_sumstats['ALLELES'])
        log.log('Flip z score for {} SNPs'.format((df_sumstats.Z != df_z).sum()))

        df_sumstats.drop(['A1_x', 'A2_x', 'A1_y', 'A2_y','ALLELES'], axis=1, inplace=True)
        df_sumstats = pd.merge(ref_file, df_sumstats, how='left', on=cols.SNP)
        save_dict['zvec'] = df_sumstats["Z"].values
        save_dict['nvec'] = df_sumstats["N"].values

    if args.ldscore:
        df_ldscore = pd.concat([pd.read_csv(args.ldscore.replace('@', str(chri)), delim_whitespace=True)  for chri in args.chr_labels])
        df_ldscore.drop([x for x in ['CHR', 'BP', 'CM', 'MAF'] if x in df_ldscore], inplace=True, axis=1)
        log.log('Shape of ldscore file: {shape}'.format(shape=df_ldscore.shape))
        df_ldscore = pd.merge(ref_file[['SNP']], df_ldscore, how='left', on='SNP')
        del df_ldscore['SNP']
        log.log('Shape of ldscore file after merge: {shape}'.format(shape=df_ldscore.shape))
        save_dict['annonames'] = list(df_ldscore.columns)
        save_dict['annomat'] = df_ldscore.values

    if args.annot:
        df_annot = pd.concat([pd.read_csv(args.annot.replace('@', str(chri)), delim_whitespace=True)  for chri in args.chr_labels])
        df_annot.drop([x for x in ['CHR', 'BP', 'CM', 'MAF'] if x in df_annot], inplace=True, axis=1)
        log.log('Shape of annots file: {shape}'.format(shape=df_annot.shape))
        df_annot = pd.merge(ref_file[['SNP']], df_annot, how='left', on='SNP')
        del df_annot['SNP']
        log.log('Shape of annots file after merge: {shape}'.format(shape=df_annot.shape))
        save_dict['annonames_bin'] = list(df_annot.columns)
        save_dict['annomat_bin'] = df_annot.values

    if args.M_5_50:
        m_5_50 = pd.concat([pd.read_csv(args.M_5_50.replace('@', str(chri)), delim_whitespace=True, header=None) for chri in args.chr_labels])
        m_5_50 = np.atleast_2d(m_5_50.sum().values)
        log.log('M_5_50={}'.format(m_5_50))
        save_dict['M_5_50']=m_5_50

    if args.M:
        m = pd.concat([pd.read_csv(args.M.replace('@', str(chri)), delim_whitespace=True, header=None) for chri in args.chr_labels])
        m = np.atleast_2d(m.sum().values)
        log.log('M={}'.format(m))
        save_dict['M']=m

    sio.savemat(args.out, save_dict, format='5', do_compression=False, oned_as='column', appendmat=False)
    log.log('Result written to {f}'.format(f=args.out))

### =================================================================================
###                          Implementation for frq_to_mat
### =================================================================================
def frq_to_mat(args, log):
    if args.ref:
        check_input_file(args.ref)
    if args.chr_labels is None:
        args.chr_labels = list(range(1, 23))
    if args.frq and args.afreq:
        raise ValueError('--frq and --afreq must not be used together')
    frq = args.frq if args.frq else args.afreq
    snp_col = 'SNP' if args.frq else 'ID'
    maf_col = 'MAF' if args.frq else 'ALT_FREQS'
    for chri in args.chr_labels:
        check_input_file(frq.replace('@', str(chri)))
    check_output_file(args.out, args.force)

    if args.ref:
        log.log('Reading reference file {}...'.format(args.ref))
        ref_file = pd.read_csv(args.ref, sep='\t', usecols=[cols.SNP, cols.A1, cols.A2])
        log.log("Reference dict contains {d} snps.".format(d=len(ref_file)))

    save_dict = {}
    df_frq = pd.concat([pd.read_csv(frq.replace('@', str(chri)), delim_whitespace=True)  for chri in args.chr_labels])
    log.log('Input file contains {d} snps'.format(d=len(df_frq)))
    if args.ref:
        df_frq.drop_duplicates(subset='SNP', inplace=True)
        log.log('After drop duplicates, file contains {d} snps'.format(d=len(df_frq)))
        df_frq = pd.merge(ref_file[['SNP']], df_frq, how='left', left_on='SNP', right_on=snp_col)
        log.log('{d} non-null values after merging with ref file'.format(d=df_frq[maf_col].notnull().sum()))

    save_dict['mafvec'] = df_frq[maf_col].values

    sio.savemat(args.out, save_dict, format='5', do_compression=False, oned_as='column', appendmat=False)
    log.log('Result written to {f}'.format(f=args.out))
### =================================================================================
###                          Implementation for ref_to_mat
### =================================================================================
def ref_to_mat(args, log):
    check_input_file(args.ref)
    check_output_file(args.out, args.force)

    log.log('Reading reference file {}...'.format(args.ref))
    ref_file = pd.read_csv(args.ref, sep='\t')
    log.log("Reference dict contains {d} snps.".format(d=len(ref_file)))

    save_dict = {}
    for col in ref_file.columns:
        # skip fields SNP, A1, A2 because they are saved as cell array
        if args.numeric_only and ref_file[col].dtype == object:
            continue
        save_dict[col] = ref_file[col].values

    sio.savemat(args.out, save_dict, format='5', do_compression=False, oned_as='column', appendmat=False)
    log.log('Result written to {f}'.format(f=args.out))

### =================================================================================
###                          Implementation for ldsum
### =================================================================================
def ldsum(args, log):
    # Adjust r2_min and  r2_max thresholds.
    # They must be vectors (e.g. [None] instead of None).
    # Values of 0.0 and 1.0 must be replaced with None to avoid filtering.
    # Mathematicaly all r2 values are within [0, 1], but due to float-point precision
    # some values may exceed 1 my small amount, and we don't want them to be filtered.
    if args.r2_min is None: args.r2_min = [0.0]
    if args.r2_max is None: args.r2_max = [1.0]
    args.r2_min = [None if __isclose__(x, 0.0) else x for x in args.r2_min]
    args.r2_max = [None if __isclose__(x, 1.0) else x for x in args.r2_max]

    if len(args.r2_min) != len(args.r2_max):
        raise(ValueError('--r2-min and --r2-max arguments must have equal length'))
    if args.per_allele and not args.frq:
        raise(ValueError('--frq argument is required for --per-allele'))

    check_input_file(args.bim)
    check_input_file(args.ld)
    if args.frq and args.per_allele: check_input_file(args.frq)
    check_output_file(args.out + ".l2.ldscore.gz", args.force)
    check_output_file(args.out + ".l4.ldscore.gz", args.force)

    log.log('Reading {}...'.format(args.bim))
    ref = pd.read_csv(args.bim, delim_whitespace=True, header=None, names=['CHR', 'SNP', 'GP', 'BP', 'A1', 'A2'])
    ref['INDEX_A'] = ref.index
    ref['INDEX_B'] = ref.index
    ref['SNP_A'] = ref['SNP']
    ref['SNP_B'] = ref['SNP']
    if len(ref.drop_duplicates(subset=['SNP'], keep='first', inplace=False)) != len(ref):
        raise(ValueError('--bim file contains duplicated markers, which is not allowed'))
    log.log('Done, {} markers found'.format(len(ref)))

    if args.frq and args.per_allele:
        log.log('Reading {}...'.format(args.frq))
        frq = pd.read_csv(args.frq, delim_whitespace=True)
        if len(frq) != len(ref):
            raise(ValueError('--frq file is not consistent with --ref file'))
        log.log('Done, {} markers found'.format(len(frq)))
        ref['HVEC'] = 2 * np.multiply(frq['MAF'].values, 1.0 - frq['MAF'].values)
    else:
        ref['HVEC'] = 1

    l2 = ref[['CHR', 'SNP', 'BP']].copy()
    l4 = ref[['CHR', 'SNP', 'BP']].copy()
    for r2_bin, (r2_min, r2_max) in enumerate(zip(args.r2_min, args.r2_max)):
        suffix = '.{}'.format(r2_bin) if len(args.r2_min) > 0 else ''
        l2['L2' + suffix] = 0.0
        l4['L4' + suffix] = 0.0

    log.log('Reading {} in chunks of {} lines at a time...'.format(args.ld, args.chunksize))
    n_snps = 0
    for chunk_index, ld in enumerate(pd.read_csv(args.ld, delim_whitespace=True, chunksize=args.chunksize, usecols=['SNP_A', 'SNP_B', 'R2'])):
        n_snps += len(ld)

        ld_t = ld.copy()
        ld_t['SNP_A'] = ld['SNP_B']
        ld_t['SNP_B'] = ld['SNP_A']
        ld = pd.concat([ld, ld_t])

        incl_diag = ''
        if (not args.not_diag) and (chunk_index==0):
            ld_diag = ref[['SNP', 'SNP']].copy()
            ld_diag.columns = ['SNP_A', 'SNP_B']
            ld_diag['R2'] = 1.0
            ld = pd.concat([ld, ld_diag])
            incl_diag = ' (including diagonal)'

        ld = pd.merge(ld, ref[['SNP_A','INDEX_A']], how='left', on='SNP_A')
        ld = pd.merge(ld, ref[['SNP_B','INDEX_B', 'HVEC']], how='left', on='SNP_B')

        # Set r2 to the product of H2 and HVEC (the later could be 1.0, when one runs without --per-allele)
        ld['R2'] = np.multiply(ld['R2'].values, ld['HVEC'].values)

        r2_per_bin = np.zeros(len(args.r2_min))
        for r2_bin, (r2_min, r2_max) in enumerate(zip(args.r2_min, args.r2_max)):
            suffix = '.{}'.format(r2_bin) if len(args.r2_min) > 0 else ''
            ld['idx'] = True
            if (r2_min is not None): ld['idx'] = ld['idx'] & (ld['R2'] > r2_min)
            if (r2_max is not None): ld['idx'] = ld['idx'] & (ld['R2'] <= r2_max)
            idx = ld['idx'].values

            vals = ld['R2'][idx].values
            rows = ld['INDEX_A'][idx].values
            cols = ld['INDEX_B'][idx].values

            csr     = scipy.sparse.coo_matrix((vals,              (rows, cols)), shape=(len(ref), len(ref))).tocsr()
            csr_sqr = scipy.sparse.coo_matrix((np.power(vals, 2), (rows, cols)), shape=(len(ref), len(ref))).tocsr()
            r2_per_bin[r2_bin] = csr.nnz

            l2['L2' + suffix] += csr.dot(np.ones((len(ref), 1))).reshape(len(ref))
            l4['L4' + suffix] += csr_sqr.dot(np.ones((len(ref), 1))).reshape(len(ref))

        eprint("{f}: {n} lines finished, number of r2 in the last --l2 chunk: {r}{d}".format(f=args.ld, n=n_snps,r=', '.join([str(int(x)) for x in r2_per_bin]), d=incl_diag))

    log.log('Writting {}...'.format(args.out + ".l2.ldscore.gz"))
    l2.to_csv(args.out + ".l2.ldscore.gz", sep='\t', index=False, compression='gzip')
    log.log('Writting {}...'.format(args.out + ".l4.ldscore.gz"))
    l4.to_csv(args.out + ".l4.ldscore.gz", sep='\t', index=False, compression='gzip')
    log.log('Done.')

### =================================================================================
###                          Implementation for diff_mat
### =================================================================================
def diff_mat(args, log):
    check_input_file(args.mat1)
    check_input_file(args.mat2)
    check_input_file(args.ref)
    if args.sumstats: check_input_file(args.sumstats)
    check_output_file(args.out, args.force)

    def read_mat_file(filename, log):
        log.log('Reading .mat file {}...'.format(filename))
        mat = sio.loadmat(filename)
        log.log('Found variables: {}'.format([x for x in mat.keys() if x not in ['__version__', '__header__', '__globals__']]))
        nvec = None; zvec = None; logpvec = None
        for key in mat.keys():
            if key.lower().startswith('zvec'): zvec = mat[key]
            if key.lower().startswith('logpvec'): logpvec = mat[key]
            if key.lower().startswith('nvec'): nvec = mat[key]
        return (zvec, logpvec, nvec)

    def compare_vectors(v1, v2,  log):
        s1 = v1 is not None
        s2 = v2 is not None
        log.log('\tIs present in the first  file? {}'.format('YES' if s1 else 'NO'))
        log.log('\tIs present in the second file? {}'.format('YES' if s2 else 'NO'))
        if not s1 or not s2: return (None, None)

        s1 = len(v1); s2 = len(v2)
        log.log('\tHave equal length in both files? {}'.format('YES, {}'.format(s1) if s1==s2 else 'NO, {} vs {}'.format(s1, s2)))
        if s1 != s2: return (None, None)

        s = all(np.isnan(v1) == np.isnan(v2))
        log.log('\tHave equal pattern of defined values? {}'.format('YES' if s else 'NO'))

        if not s:
            s1 = np.sum(np.isnan(v1)); s2 = np.sum(np.isnan(v2))
            log.log('\t\tHave equal number of undefined values? {}'.format('YES, {}'.format(s1) if s1==s2 else 'NO, {} vs {} - difference is {}'.format(s1, s2, abs(s1-s2))))

            s1 = np.sum(~np.isnan(v1) & np.isnan(v2))
            s2 = np.sum(np.isnan(v1) & ~np.isnan(v2))
            log.log('\t\tHow many values are defined in the first file but not in the second file? {}'.format(s1))
            log.log('\t\tHow many values are defined in the second file but not in the first file? {}'.format(s2))

        # Select values defined in both vectors
        idx_def = ~np.isnan(v1) & ~np.isnan(v2)
        def_v1 = v1[idx_def]
        def_v2 = v2[idx_def]
        idx_diff_sign = ((def_v1 <= 0) & (def_v2 > 0)) | ((def_v1 > 0) & (def_v2 <= 0))
        idx_diff_value = np.greater(abs(def_v1 - def_v2), 1e-5)
        log.log('\tAll defined values are equal in both files? {}'.format('YES' if all(def_v1 == def_v2) else 'NO, {} values are different'.format(np.sum(def_v1 != def_v2))))
        if not all(def_v1 == def_v2):
            s = np.sum(idx_diff_sign)
            log.log('\t\tMean(Std) for the first  file? {} ({})'.format(np.mean(def_v1), np.std(def_v1)))
            log.log('\t\tMean(Std) for the second file? {} ({})'.format(np.mean(def_v2), np.std(def_v2)))
            log.log('\t\tAll values have equal sign? {}'.format('YES' if s == 0 else 'NO, {} values have different sign'.format(s)))
            log.log('\t\tMaximum difference of absolute values? {}'.format(max(abs(abs(def_v1) - abs(def_v2)))))
            log.log('\t\tNumber of values with absolute difference above 1e-5? {}'.format(sum(idx_diff_value)))

        # Return index of SNPs that we consider to be different
        # First vector, idx_diff_nan_or_sign, indicate where nan pattern is different or sign is different
        # Second vector, idx_diff_nan_or_sign_or_value, indicates where nan pattern is different or sign is different or value is different
        idx_diff_nan_or_sign = (np.isnan(v1) != np.isnan(v2))
        idx_diff_nan_or_sign[idx_def] = idx_diff_sign
        idx_diff_nan_or_sign_or_value = (np.isnan(v1) != np.isnan(v2))
        idx_diff_nan_or_sign_or_value[idx_def] = idx_diff_value | idx_diff_sign
        return (idx_diff_nan_or_sign, idx_diff_nan_or_sign_or_value)

    [zvec1, logpvec1, nvec1] = read_mat_file(args.mat1, log)
    [zvec2, logpvec2, nvec2] = read_mat_file(args.mat2, log)

    log.log('{}:'.format('zvec'))
    (zvec_diff, _) = compare_vectors(zvec1, zvec2, log)

    log.log('{}:'.format('logpvec'))
    (_, logpvec_diff) = compare_vectors(logpvec1, logpvec2, log)

    log.log('{}:'.format('nvec'))
    (_, nvec_diff) = compare_vectors(nvec1, nvec2, log)

    diff = np.logical_or.reduce([diff for diff in [zvec_diff, logpvec_diff, nvec_diff] if diff is not None])
    log.log('Overall, {} markers appears to be different.'.format(np.sum(diff)))

    if np.sum(diff) == 0:
        open(args.out, 'a').close()
        return

    log.log('Reading reference file {}...'.format(args.ref))
    ref = pd.read_csv(args.ref, sep='\t', usecols=[cols.SNP, cols.CHR, cols.BP])
    log.log("Reference dict contains {d} snps.".format(d=len(ref)))

    # Insert not-null vectors into the data frame
    vectors = {'zvec1':zvec1, 'zvec2':zvec2, 'logpvec1':logpvec1, 'logpvec2':logpvec2, 'nvec1':nvec1, 'nvec2':nvec2}
    for k in vectors:
        if (vectors[k] is not None) and (len(vectors[k]) == len(ref)):
            ref[k] = vectors[k]
    ref = ref.loc[[i for i, x in enumerate(diff) if x]]

    if args.sumstats:
        log.log('Reading sumstats file {}...'.format(args.sumstats))
        sumstats = pd.read_csv(args.sumstats, sep='\t')
        log.log("Sumstats file contains {d} markers.".format(d=len(sumstats)))

        sumstats_cols = sumstats.columns
        if cols.SNP in sumstats_cols:
            sumstats.columns = [(x + '_onSNP' if x != 'SNP' else x) for x in sumstats_cols]
            ref = pd.merge(ref, sumstats, how='left', on='SNP')
        if cols.CHR in sumstats_cols and cols.BP in sumstats_cols:
            sumstats.columns = [(x + '_onCHRPOS' if x not in ['CHR', 'BP'] else x) for x in sumstats_cols]
            ref = pd.merge(ref, sumstats, how='left', on=['CHR', 'BP'])

    ref.to_csv(args.out, sep='\t', index=False, na_rep='NA')
    log.log('Result is written into {}'.format(args.out))

### =================================================================================
###                          Implementation for parser_neff
### ================================================================================= 
def make_neff(args, log):
    """
    Generate N column from NCASE and NCONTROL
    """
    if args.sumstats == '-': args.sumstats = sys.stdin
    if args.out == '-': args.out = sys.stdout
    check_input_file(args.sumstats)
    check_output_file(args.out, args.force)
    
    log.log('Reading summary statistics file {}...'.format(args.sumstats))
    df = pd.read_csv(args.sumstats, delim_whitespace=True)

    if 'N' in df.columns:
        if (('NCASE' not in df.columns) or ('NCONTROL' not in df.columns)):
            log.log('WARNING: N column is alredy present, NCASE/NCONTROL columns are not available. Nothing to be done.')
            df.to_csv(args.out, sep='\t', index=False, na_rep='NA')
            log.log("{n} SNPs saved to {f}".format(n=len(df), f=args.out))
            return
        log.log('WARNING: N column is already present and will be overwritten.')

    if args.factor > 0:
        df['N'] = np.divide(args.factor, 1./df['NCASE'] + 1./df['NCONTROL'])
    else:
        df['N'] = df['NCASE'] + df['NCONTROL']
    if args.drop: df.drop(['NCASE', 'NCONTROL'], axis=1, inplace=True)
    df.to_csv(args.out, sep='\t', index=False, na_rep='NA')
    log.log("{n} SNPs saved to {f}".format(n=len(df), f=args.out))

### =================================================================================
###                                Misc stuff and helpers
### =================================================================================
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

def wait_for_system_memory(log):
    # safety guard to ensure that at least 25% of system memory is available
    try:
        import psutil
        if psutil.virtual_memory().percent < 80:
            return
        log.log('Waiting for at least 20% of system memory to be available...')
        while psutil.virtual_memory().percent > 80:
            time.sleep(5)
    except ImportError:
        pass

def sub_chr(s, chr):
    '''Substitute chr for @, else append chr to the end of str.'''
    if '@' not in s:
        s += '@'

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

def __isclose__(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def fix_columns_order(sumstats):
    # Ensure that all standard columns go first (in the order define dby namedtuple 'Cols'), following by non-standard columns
    cols_std   = [c for c in Cols._fields if c in sumstats.columns]
    cols_other = [c for c in sumstats.columns if c not in Cols._fields]
    return sumstats[cols_std + cols_other]

### =================================================================================
###                                Main section
### ================================================================================= 
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.out is None:
        raise ValueError('--out is required.')

    log = Logger(args.log if args.log else (args.out + '.log' if (args.out != '-') else None), 'a' if args.log_append else 'w')
    start_time = time.time()

    try:
        defaults = vars(parse_args([sys.argv[1]]))
        opts = vars(args)
        non_defaults = [x for x in opts.keys() if opts[x] != defaults[x]]
        header = MASTHEAD
        header += "Call: \n"
        header += './sumstats.py {} \\\n'.format(sys.argv[1])
        options = ['\t--'+x.replace('_','-')+' '+str(opts[x]).replace('\t', '\\t')+' \\' for x in non_defaults]
        header += '\n'.join(options).replace('True','').replace('False','')
        header = header[0:-1]+'\n'
        log.log(header)
        wait_for_system_memory(log)
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
