
#!/usr/bin/env python3

# README:
# gwas.py converts pheno+dict files into format compatible with plink or regenie analysis. Other association analyses can be added later.
# gwas.py automatically decides whether to run logistic or linear regression by looking at the data dictionary for requested phenotypes
# gwas.py generates all scripts needed to run the analysis, and to convert the results back to a standard summary statistics format

import argparse
import logging, time, sys, traceback, socket, getpass, six, os
import json
import pandas as pd
import numpy as np
from scipy import stats
import tarfile, subprocess, collections, shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as mpe

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
    pheno_parser.add_argument("--fam", type=str, default=None, help="an argument pointing to a plink's .fam file, use by gwas.py script to pre-filter phenotype information (--pheno) with the set of individuals available in the genetic file (--geno-file / --geno-fit-file). Optional when either --geno-file (or --geno-fit-file) is in plink's format, otherwise required - but IID in this file must be consistent with identifiers of the genetic file.")
    pheno_parser.add_argument("--pheno", type=str, default=[], nargs='+', help="target phenotypes to run GWAS (must be columns of the --pheno-file")
    pheno_parser.add_argument("--covar", type=str, default=[], nargs='+', help="covariates to control for (must be columns of the --pheno-file); individuals with missing values for any covariates will be excluded not just from <out>.covar, but also from <out>.pheno file")
    pheno_parser.add_argument("--variance-standardize", type=str, default=None, nargs='*', help="the list of continuous phenotypes to standardize variance; accept the list of columns from the --pheno file (if empty, applied to all); doesn't apply to dummy variables derived from NOMINAL or BINARY covariates.")

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

    parser_gwas_add_arguments(args=args, func=execute_gwas, parser=subparsers.add_parser("gwas", parents=[parent_parser, pheno_parser, slurm_parser, filter_parser], help='perform GWAS (genome-wide association) analysis'))
    parser_pgrs_add_arguments(args=args, func=execute_pgrs, parser=subparsers.add_parser("pgrs", parents=[parent_parser, pheno_parser, slurm_parser], help='compute polygenic risk score'))
    
    parser_merge_plink2_add_arguments(args=args, func=merge_plink2, parser=subparsers.add_parser("merge-plink2", parents=[parent_parser, filter_parser], help='merge plink2 sumstats files'))
    parser_merge_regenie_add_arguments(args=args, func=merge_regenie, parser=subparsers.add_parser("merge-regenie", parents=[parent_parser, filter_parser], help='merge regenie sumstats files'))
    parser_merge_saige_add_arguments(args=args, func=merge_saige, parser=subparsers.add_parser("merge-saige", parents=[parent_parser, filter_parser], help='merge saige sumstats files'))

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

    manh_example_text =  """Example:
python gwas.py manh result.mat.csv \\
\t--lead conj.result.clump.lead.csv --indep conj.result.clump.indep.csv \\
\t--p FDR --y-label conjFDR --color-list 1 --legend-label 'Trait1 & Trait2' \\
\t--legend-location 'upper right' --p-thresh 0.05 --out conjfdr_manhattan"""
    parser_manh_add_arguments(args=args, func=make_manh_implementation, parser=subparsers.add_parser("manh", parents=[parent_parser], help="A tool to draw Manhattan plot from sumstat files", description=manh_example_text, formatter_class=argparse.RawDescriptionHelpFormatter))

    qq_example_text =  """Example 1:
python qq.py PGC_BIP_2016_qc.csv.gz\n
Example 2:
python qq.py PGC_SCZ_2014_EUR_qc.csv.gz --strata PGC_MDD_2018_no23andMe.csv.gz \\
\t--strata-num PVAL --top-as-dot 100 --weights weights.prune.txt.gz \\
\t--out qq.scz_mdd.top100.prune.png --y-lim 15\n
Example 3:
python qq.py PGC_MDD_2018_no23andMe.csv.gz --strata PGC_MDD_2018_no23andMe.csv.gz \\
\t--strata-cat CHR --strata-cat-ids 'chr1_7=1:2:3:4:5:6:7,chr18_21=18:19:20:21' \\
\t--weights weights.tld.txt.gz --y-lim 7.301029995663981 --out qq.mdd.chr.png"""
    parser_qq_add_arguments(args=args, func=make_qq_implementation, parser=subparsers.add_parser("qq", parents=[parent_parser], help="A tool to draw Quantile-Quantile (QQ) plots from sumstat files", description=qq_example_text, formatter_class=argparse.RawDescriptionHelpFormatter))

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

    parser.add_argument('--analysis', type=str, default=['plink2', 'regenie', 'saige', 'figures'],
        nargs='+', choices=['plink2', 'regenie', 'saige', 'loci', 'manh', 'qq', 'figures'],
        help='list of analyses to perform. plink2 and regenie can not be combined '
        '(i.e. require two separate runs). loci, manh and qq can be added to etiher '
        'plink2 or regenie analysis, but then can also be executed separately '
        '("--analysis loci manh qq" without plink2 or regenie). '
        'This scenario indented as a follow-up to visualize the results produced by '
        'running only plink2 or regenie analysis. If you want to apply loci analyses to '
        'summary statistics generated not via gwas.py, use a more flexible "gwas.py loci" option '
        'instead of trying to use "gwas.py gwas --analysis loci"; same applyes for manh and qq.')

    parser.add_argument('--vcf-field', type=str, default=['DS'], choices=['DS', 'GT'], help='field to read for vcf files')

    # deprecated options for genetic files
    parser.add_argument("--bed-fit", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-fit-file instead (but remember to add .bed to your argument)] plink bed/bim/fam file to use in a first step of mixed effect models")
    parser.add_argument("--bed-test", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-file instead (but remember to add .bed to your argument)] plink bed/bim/fam file to use in association testing; supports '@' as a place holder for chromosome labels (see --chr2use argument)")
    parser.add_argument("--bgen-fit", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-fit-file instead] .bgen file to use in a first step of mixed effect models")
    parser.add_argument("--bgen-test", type=str, default=None, action=ActionStoreDeprecated, help="[DEPRECATED, use --geno-file instead] .bgen file to use in association testing; supports '@' as a place holder for chromosome labels")

    parser.add_argument("--bfile-ld", type=str, default=None, help="plink file to use for LD structure estimation (forwarded to 'gwas.py loci --bfile' argument")
    parser.add_argument("--clump-p1", type=float, default=5e-8, help="p-value threshold for independent significant SNPs. Applys to 'loci' analysis.")
    
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
        "if the filename prefix contains the symbol @, it will be replaced with chromosome numbers. ")

    parser.add_argument("--ld-window-kb", type=float, default=10000, help="Window size in KB to search for clumped SNPs. ")
    parser.add_argument("--loci-merge-kb", type=float, default=250, help="Maximum distance in KB of LD blocks to merge. ")
    parser.add_argument("--merge-ranges", type=str, nargs='+',
        help='Merge loci if they fall within --merge-ranges, so that no more than 1 loci is reported for each range. '
        'This is useful to handle complex LD regions such as MHC or chr8 inversion. The syntax is chr:from-to, and multiple regions can be excluded. '
        'Example: --merge-ranges 6:25000000-35000000 8:7000000-12000000.')
    parser.add_argument("--plink", type=str, default='plink', help="Path to plink executable.")
    parser.set_defaults(func=func)

def parser_manh_add_arguments(args, func, parser):
    parser.add_argument("--sumstats", nargs="+", help="A list of sumstat files")
    parser.add_argument("--sep", nargs="+", default=['\t'],
        help="A list of column separators in sumstat files")
    parser.add_argument("--snp", nargs="+", default=["SNP"],
        help="A list of columns with SNP ids in sumstat files")
    parser.add_argument("--chr", nargs="+", default=["CHR"],
        help="A list of columns with SNP chromosomes in sumstat files")
    parser.add_argument("--bp", nargs="+", default=["BP"],
        help="A list of columns with SNP positions in sumstat files")
    parser.add_argument("--p", nargs="+", default=["P"],
        help="A list of columns with SNP p-values in sumstat files")

    parser.add_argument("--outlined", nargs="+", default=["NA"],
        help=("A list of files with ids of SNPs to mark with outlined bold dots, 'NA' if absent. "
            "These files should contain a single column with SNP ids without header"))
    parser.add_argument("--bold", nargs="+", default=["NA"],
        help=("A list of files with ids of SNPs to mark with bold dots, 'NA' if absent. "
            "These files should contain a single column with SNP ids without header"))
    parser.add_argument("--annot", nargs="+", default=["NA"],
        help=("A list of files with ids (1st column) and labels (2nd column) of SNPs to annotate, 'NA' if absent. "
            "These files should contain two tab-delimited columns (1st: SNP ids, 2nd: SNP labels) without header"))
    # the next two options are shortcuts for --outlined and --bold to work
    # directly with the output of "gwas.py loci". These options probably
    # should be removed in future for clarity
    parser.add_argument("--lead", nargs="+", default=["NA"],
        help=("A list of files with ids of lead SNPs, 'NA' if absent. "
            "These files should be the output of 'gwas.py loci'"))
    parser.add_argument("--indep", nargs="+", default=["NA"],
        help=("A list of files with ids of independent significant SNPs, 'NA' if absent. "
        "These files should be the output of 'gwas.py loci'"))

    parser.add_argument("--p-thresh", type=float, default=5.E-8,
        help="Significance threshold for p-values")
    parser.add_argument("--transparency", type=float, nargs="+", default=[1],
        help="Transparency level of points")
    parser.add_argument("--between-chr-gap", type=float, default=0.1,
        help="Size of the gap between chromosomes in the figure")
    parser.add_argument("--snps-to-keep", nargs="+", default=["NA"],
        help="A list of files with ids of SNPs to take for plotting, 'NA' if absent. "
        "These files should contain a single column with SNP ids without header")
    parser.add_argument("--snps-visual-bins", type=int, default=1000,
        help= "We filter points if they are too close on a screen to make the figure more lightweight (especially .svg and other vector graphics). This is done by binning vertical and horizonal range into this many bins, and keeping one point of a bin. Points that are annotated, bold or outlined are always plotted.")
    parser.add_argument("--chr2use", type=str, default="1-22",
        help=("Chromosome ids to plot (e.g. 1,2,3 or 1-4,12,16-20 or 19-22,X,Y). "
            "The order in the figure will correspond to the order in this argument. "
            "Chromosomes with non-integer ids should be indicated separately"))
    parser.add_argument("--striped-background", action="store_true",
        help="Draw grey background for every second chromosome")
    parser.add_argument("--color-list", nargs="+", default=[],
        help="Use specified color list, e.g. 1 3 5 7 9 11 13 15 17 19; 2 4 6 8 10 12 14 16 18 20; orange sky_blue bluish_green yellow blue vermillion reddish_purple black, or any colors listed on https://python-graph-gallery.com/100-calling-a-color-with-seaborn")
    parser.add_argument("--cb-colors", action="store_true",
        help="Use colors designed for color-blind people")
    parser.add_argument("--seed", type=int, default=1, help="Random seed")
    parser.add_argument("--separate-sumstats", action="store_true",
        help="Plot each sumstat in a separate subplot.")

    parser.add_argument("--y-label", default="P",
        help="Label of y axis. Label in the figure will be: -log10(y_label).")
    parser.add_argument("--y-max", type=float, default=-1, help="Upper limit of y axis. Default: autodetect.")
    parser.add_argument("--legend-location", default="best",
        help="Legend location: 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'")
    parser.add_argument("--no-legend", action="store_true",
        help="Don't add legend to the figure.")
    parser.add_argument("--legend-labels", nargs="+", default=["NA"],
        help="A list of labels for sumstats to use in the legend in the corresponding order. "
        "If '--no-legend' is specified, this argument is ignored. If both this and "
        "'--no-legend' arguments are absent, corresponding file names are used in "
        "the legend.")
    parser.set_defaults(func=func)

def parser_qq_add_arguments(args, func, parser):
    parser.add_argument("--sumstats", help="Sumstats file")
    parser.add_argument("--sep", default='\t',
        help="Column separator in sumstat file")
    parser.add_argument("--p", default="P",
        help="A column with SNP p-values in sumstats file")
    parser.add_argument("--snp", default="SNP",
        help="A column with SNP ids in sumstats file")
    parser.add_argument("--strata", default="NA",
        help="A file with at least 2 columns: SNP id and SNP stratum")
    parser.add_argument("--strata-sep", default='\t',
        help="Column separator in strata file")
    parser.add_argument("--strata-snp", default="SNP",
        help="A column with SNP ids in strata file")
    parser.add_argument("--strata-cat", default="NA",
        help="A column with SNP categories. Each category represents a separate stratum in qq plot")
    parser.add_argument("--strata-cat-ids", default="NA",
        help=("Comma-separated list of categories from --strata-cat column to plot "
            "and corresponding names, e.g. 'chr1_2_6=1:2:6' (defines strata chr1_2_6 "
            "containinfg all variants with value in --strata-cat column = 1,2 or 6). "
            "By default all categories are plotted with original names"))
    parser.add_argument("--strata-num", default="NA",
        help="A column with SNP numerical value (e.g. p-value)")
    parser.add_argument("--strata-num-intervals", type=str,
        default="p<10^-1=:0.1,p<10^-2=:0.01,p<10^-3=:0.001", help=("Comma-separated "
            "intervals defining SNP strata based on values from --strata-num column "
            "and corresponding names, e.g.: 'A=:-1,B=0:6' (defines stratum A "
            "corresponding to the interval (-inf, -1] and stratum B = (0,6].  "
            "If there is a '-' charecter in any of values, the whole argument value should be quoted"))
    parser.add_argument("--strata-bin", nargs='+', default="NA",
        help=("A list of columns (each column representing one stratum) with binary data "
            "0/1 or False/True for each variant indicatig whether the variant belongs to "
            "the corresponding strata"))
    parser.add_argument("--weights", default="NA",
        help=("Tab-separated file without header and with 2 columns: SNP id and SNP weight. "
            "Don't need to be normalized"))
    parser.add_argument("--top-as-dot", default=0, type=int,
        help="Number of top associations (lowest p-values) to mark as a separate dot")
    parser.add_argument("--x-lim", default=None, type=float,
        help="X-axis maximum limit on -log10 scale")
    parser.add_argument("--y-lim", default=None, type=float,
        help="Y-axis maximum limit on -log10 scale (e.g. gws threshold = 7.3)")
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

    # validate that some of genetic data is provided as input
    if not args.geno_file:
        raise ValueError('--geno-file must be specified')

    if args.fam is None:
        if is_bed_file(args.geno_file):
            args.fam = replace_suffix(args.geno_file, '.bed', '.fam')
        elif ('geno_fit_file' in vars(args)) and args.geno_fit_file and is_bed_file(args.geno_fit_file):
            args.fam = replace_suffix(args.geno_fit_file, '.bed', '.fam')
        else:
            raise ValueError('please specify --fam argument in plink format, containing the same set of individuals as your --geno-file / --geno-fit-file')
        if '@' in args.fam: args.fam = args.fam.replace('@', args.chr2use[0])
    check_input_file(args.fam)

    check_input_file(args.pheno_file)
    if not args.dict_file: args.dict_file = args.pheno_file + '.dict'
    check_input_file(args.dict_file)

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

    if ('@' in geno_fit_file): raise(ValueError('--geno-fit-file contains "@", hense it is incompatible with SAIGE step1 which require a single file'))
    if (is_pgen_file(geno_fit_file) or is_pgen_file(geno_file)): raise(ValueError('--geno-file / --geno-fit-file can not point to plink2 pgen file for SAIGE analysis'))

    cmd_step1 = ''; cmd_step2 = ''

    for pheno in args.pheno:
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
            " --nThreads={} ".format(args.slurm_cpus_per_task) + \
            " --LOCO=TRUE " + \
            " --minMAFforGRM=0.01" + \
            " --tauInit=1,0 "

        cmd_step2 += '\n$SAIGE step2_SPAtests.R ' + \
            (" --plinkFile={} ".format(remove_suffix(geno_file, '.bed')) if is_bed_file(geno_file) else "") + \
            (" --vcfFile={f} --vcfFileIndex={f}.tbi --vcfField={vf} ".format(f=geno_file, vf=args.vcf_field) if is_vcf_file(geno_file) else "") + \
            (" --bgenFile={f} --bgenFileIndex={f}.bgi ".format(f=geno_file) if is_bgen_file(geno_file) else "") + \
            " --chr ${SLURM_ARRAY_TASK_ID}" + \
            (" --minMAF={}".format(args.maf) if (args.maf is not None) else '') + \
            " --minMAC=1" + \
            " --sampleFile={}.sample".format(args.out) + \
            " --GMMATmodelFile={}_{}.step1.rda".format(args.out, pheno) + \
            " --varianceRatioFile={}_{}.step1.varianceRatio.txt".format(args.out, pheno) + \
            " --SAIGEOutputFile={}_chr${{SLURM_ARRAY_TASK_ID}}_{}.saige".format(args.out, pheno) + \
            " --numLinesOutput=2" + \
            (" --IsOutputAFinCaseCtrl=TRUE" if logistic else '')+ \
            (" --IsOutputNinCaseCtrl=TRUE" if logistic else '') + \
            " --LOCO=TRUE "

    return cmd_step1 if step==1 else cmd_step2

# this function works similarly to ** in python:
# all args from args_list that are not None are passed to the caller
# see make_regenie_merge and make_plink2_merge for a usage example.
def pass_arguments_along(args, args_list):
    opts = vars(args)
    vals = [opts[arg.replace('-', '_')] for arg in args_list]
    return ''.join([(' --{} {} '.format(arg, '' if (val==True) else val) if val else '') for arg, val in zip(args_list, vals)])

def make_loci_commands(args):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py loci ' + \
        ' --sumstats {out}_{pheno}.gz'.format(out=args.out, pheno=pheno) + \
        ' --bfile {}'.format(args.bfile_ld if (args.bfile_ld is not None) else remove_suffix(args.geno_file, '.bed')) + \
        ' --out {out}_{pheno} '.format(out=args.out, pheno=pheno) + \
        ' --log-append ' + \
        pass_arguments_along(args, ['clump-p1']) + \
        ' --chr2use {} '.format(','.join(args.chr2use)) + \
        '\n'
    return cmd

def make_figures_commands(args):
    cmd = ''
    for pheno in args.pheno:
        Rcmd = 'library(data.table);library(qqman);library(ggplot2);'
        Rcmd += 'df=read.table("{out}_{pheno}.gz", header=TRUE);'.format(out=args.out, pheno=pheno)
        Rcmd += 'png("{out}_{pheno}.qq.png", width=600, unit="px", pointsize=12, bg="white");'.format(out=args.out, pheno=pheno)
        Rcmd += 'qq(df$P, main="{pheno}");'.format(pheno=pheno)
        Rcmd += 'dev.off();'
        Rcmd += 'df=df[df$P < 0.05, ];'
        Rcmd += 'png("{out}_{pheno}.manh.png", width=1200, unit="px", pointsize=12, bg="white");'.format(out=args.out, pheno=pheno)
        Rcmd += 'manhattan(df, chr="CHR", bp="BP", snp="SNP", p="P", main="{pheno}");'.format(pheno=pheno)
        Rcmd += 'dev.off();'
        cmd += "$RSCRIPT -e '{}'\n".format(Rcmd)
    return cmd

def make_manh_commands(args):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py manh ' + \
            ' --sumstats {out}_{pheno}.gz'.format(out=args.out, pheno=pheno) + \
            ' --out {out}_{pheno}.manh.png '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use))
        if 'loci' in args.analysis:
            cmd += ' --lead {out}_{pheno}.lead.csv '.format(out=args.out, pheno=pheno)
            cmd += ' --indep {out}_{pheno}.indep.csv '.format(out=args.out, pheno=pheno)
        cmd += '\n'
    return cmd

def make_qq_commands(args):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py qq ' + \
        ' --sumstats {out}_{pheno}.gz'.format(out=args.out, pheno=pheno) + \
        ' --out {out}_{pheno}.qq.png '.format(out=args.out, pheno=pheno) + \
        '\n'
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

def make_saige_merge_commands(args, logistic):
    cmd = ''
    for pheno in args.pheno:
        cmd += '$PYTHON gwas.py merge-saige ' + \
            pass_arguments_along(args, ['info-file', 'info', 'maf', 'hwe', 'geno']) + \
            ' --sumstats {out}_chr@_{pheno}.saige'.format(out=args.out, pheno=pheno) + \
            ' --basename {out}_chr@'.format(out=args.out) + \
            ' --out {out}_{pheno} '.format(out=args.out, pheno=pheno) + \
            ' --chr2use {} '.format(','.join(args.chr2use)) + \
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
export RSCRIPT="singularity exec --home $PWD:/home $SIF/r.sif Rscript"
export PRSICE2="singularity exec --home $PWD:/home $SIF/gwas.sif PRSice_linux"
export SAIGE="singularity exec --home $PWD:/home $SIF/saige.sif"

""".format(array="#SBATCH --array={}".format(','.join(args.chr2use)) if array else "",
           modules = '\n'.join(['module load {}'.format(x) for x in args.module_load]),
           job_name = args.slurm_job_name,
           account = args.slurm_account,
           time = args.slurm_time,
           cpus_per_task = args.slurm_cpus_per_task,
           mem_per_cpu = args.slurm_mem_per_cpu,
           comorment_folder = args.comorment_folder,
           singularity_bind = args.singularity_bind)

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
                raise ValueError('Can not apply --variance-standardize to {}, column is missing or its type is other than CONTINUOUS'.fromat(col))

            mean = np.nanmean(pheno[col].values)
            std = np.nanstd(pheno[col].values, ddof=1)
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
        num_jobs = append_job(args, commands, True, num_jobs+1, cmd_file, submit_jobs)

    log.log('To submit all jobs via SLURM, use the following scripts, otherwise execute commands from {}'.format(cmd_file))
    print('\n'.join(submit_jobs))

def execute_gwas(args, log):
    fix_and_validate_chr2use(args, log)
    fix_and_validate_pheno_args(args, log)
    fix_and_validate_gwas_args(args, log)

    if ('loci' in args.analysis) or ('qq' in args.analysis) or ('manh' in args.analysis):
        log.log('loci, qq and manh are deprecated and will soon be removed; use --analysis figures instead')

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
        num_jobs = append_job(args, commands, True, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_plink2_merge_commands(args, logistic)]
        num_jobs = append_job(args, commands, False, num_jobs+1, cmd_file, submit_jobs)

    if 'regenie' in args.analysis:
        commands = [make_regenie_commands(args, logistic, step=1)]
        num_jobs = append_job(args, commands, False, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_plink2_info_commands(args), make_regenie_commands(args, logistic, step=2)]
        num_jobs = append_job(args, commands, True, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_regenie_merge_commands(args, logistic)]
        num_jobs = append_job(args, commands, False, num_jobs+1, cmd_file, submit_jobs)

    if 'saige' in args.analysis:
        commands = [make_saige_commands(args, logistic, step=1)]
        num_jobs = append_job(args, commands, False, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_plink2_info_commands(args), make_saige_commands(args, logistic, step=2)]
        num_jobs = append_job(args, commands, True, num_jobs+1, cmd_file, submit_jobs)

        commands = [make_saige_merge_commands(args, logistic)]
        num_jobs = append_job(args, commands, False, num_jobs+1, cmd_file, submit_jobs)

    commands = []
    if 'loci' in args.analysis: commands.append(make_loci_commands(args))
    if 'manh' in args.analysis: commands.append(make_manh_commands(args))
    if 'qq' in args.analysis: commands.append(make_qq_commands(args))
    if 'figures' in args.analysis: commands.append(make_figures_commands(args))
    if commands:
        num_jobs = append_job(args, commands, False, num_jobs+1, cmd_file, submit_jobs)

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

def merge_saige(args, log):
    # quantitative GWAS columns: CHR POS SNPID Allele1 Allele2 AC_Allele2 AF_Allele2 imputationInfo N BETA SE Tstat p.value varT varTstar
    # binary GWAS columns:       CHR POS SNPID Allele1 Allele2 AC_Allele2 AF_Allele2 imputationInfo N BETA SE Tstat p.value p.value.NA Is.SPA.converge varT varTstar AF.Cases AF.Controls N.Cases N.Controls

    fix_and_validate_chr2use(args, log)
    pattern = args.sumstats
    df=pd.concat([pd.read_csv(pattern.replace('@', chri), delim_whitespace=True) for chri in args.chr2use])
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
#   as_array - whether the job is an array of 22 jobs, or not
# Output:
#   slurm_job_file - filename of a .job file to output commands (with SLURM header)
#   cmd_file - file that concatenate all commands (in case user wants to execute everything by a BASH on a local node)
#   submit_job_list - instructions for a user about how to schedule SLURM jobs
def append_job(args, commands, as_array, slurm_job_index, cmd_file, submit_jobs_list):
    slurm_job_file = args.out + '.{}.job'.format(slurm_job_index)
    with open(slurm_job_file, 'w') as f:
        f.write(make_slurm_header(args, array=as_array) + '\n'.join(commands) + '\n')
    
    with open(cmd_file, 'a') as f:
        for command in commands:
            if as_array:
                f.write('for SLURM_ARRAY_TASK_ID in {}; do {}; done\n'.format(' '.join(args.chr2use), command))
            else:
                f.write('{}\n'.format(command))

    if (slurm_job_index != 1):
        submit_jobs_list.append('RES=$(sbatch --dependency=afterany:${{RES##* }} {})'.format(slurm_job_file))
    else:
        submit_jobs_list.append('RES=$(sbatch {})'.format(slurm_job_file))

    return slurm_job_index

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
    log.log('Saving intermediate files to {out}.loc.tar.gz'.format(out=args.out))
    with tarfile.open('{out}.loci.tar.gz'.format(out=args.out), "w:gz") as tar:
        tar.add(temp_out, arcname=os.path.basename(temp_out), filter=tar_filter)
    shutil.rmtree(temp_out)

def sub_chr(s, chr):
    return s.replace('@', str(chr))

def execute_command(command, log):
    log.log("Execute command: {}".format(command))
    exit_code = subprocess.call(command.split())
    log.log('Done. Exit code: {}'.format(exit_code))
    return exit_code

def make_ranges(args_merge_ranges, log):
    # Interpret --merge-ranges input
    ChromosomeRange = collections.namedtuple('ChromosomeRange', ['chr', 'from_bp', 'to_bp'])
    merge_ranges = []
    if args_merge_ranges is not None:
        for merge_range in args_merge_ranges:
            try:
                range = ChromosomeRange._make([int(x) for x in merge_range.replace(':', ' ').replace('-', ' ').split()[:3]])
            except Exception as e:
                raise(ValueError('Unable to interpret merge range "{}", chr:from-to format is expected.'.format(merge_range)))
            merge_ranges.append(range)
            log.log('Merge range: chromosome {} from BP {} to {}'.format(range.chr, range.from_bp, range.to_bp))
    return merge_ranges

def make_loci_implementation(args, log):
    """
    Clump summary stats, produce lead SNP report, produce candidate SNP report
    TBD: refine output tables
    TBD: in snps table, do an outer merge - e.i, include SNPs that pass p-value threshold (some without locus number), and SNPs without p-value (e.i. from reference genotypes)
    """
    fix_and_validate_chr2use(args, log)    
    merge_ranges = make_ranges(args.merge_ranges, log)

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
        raise ValueError('Some independent significant SNP belongs to two lead SNPs; this is an internal error in "gwas.py loci" logic - please report this bug.')
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
            if (df_lead['MinBP'][i] - df_lead['MaxBP_locus'][i-1]) < (1000 * args.loci_merge_kb):
                merge_to_previous = True
            for exrange in merge_ranges:
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
# implement parser_manhattan
###################################################

# Default colors are similar to matplotlib 2.0 defaults and are taken from:
# https://github.com/vega/vega/wiki/Scales#scale-range-literals
DEFAULT_COLOR_NAMES = [1,3,5,7,9,11,13,15,17,19]
DEFAULT_COLOR_NAMES_ANNOT = [1,3,5,7,9,11,13,15,17,19] # [2,4,6,8,10,12,14,16,18,20]
# colors corresponding to even indices are lighter analogs of colors with odd indices, e.g. DEFAULT_COLORS[2] is a light version of DEFAULT_COLORS[1]
DEFAULT_COLORS = {1:"#1f77b4", 2:"#aec7e8", 3:"#ff7f0e", 4:"#ffbb78",
                  5:"#2ca02c", 6:"#98df8a", 7:"#d62728", 8:"#ff9896",
                  9:"#9467bd", 10:"#c5b0d5", 11:"#8c564b", 12:"#c49c94",
                  13:"#e377c2", 14:"#f7b6d2", 15:"#7f7f7f", 16:"#c7c7c7",
                  17:"#bcbd22", 18:"#dbdb8d", 19:"#17becf", 20:"#9edae5"}

# colors from http://mkweb.bcgsc.ca/colorblind/
CB_COLOR_NAMES = ["orange","sky_blue","bluish_green","yellow","blue",
    "vermillion","reddish_purple","black"]
CB_COLOR_NAMES_ANNOT = ["orange","sky_blue","bluish_green","yellow","blue",
    "vermillion","reddish_purple","black"]
CB_COLORS = {"orange":"#e69f00",
             "sky_blue":"#56b4e9",
             "bluish_green":"#009e73",
             "yellow":"#f0e442",
             "blue":"#0072b2",
             "vermillion":"#d55e00",
             "reddish_purple":"#cc79a7",
             "black":"#000000"}

def process_manhattan_args(args):
    """
    Check whether provided arguments are correct, change list-type arguments
    with single value to have a length = length of sumstats argument and process
    chr2use arument.
    """
    for f in args.sumstats:
        assert os.path.isfile(f), "'%s' file doesn't exist" % f
    for f in args.outlined:
        assert os.path.isfile(f) or f=="NA", "'%s' file doesn't exist" % f
    for f in args.bold:
        assert os.path.isfile(f) or f=="NA", "'%s' file doesn't exist" % f
    for f in args.annot:
        assert os.path.isfile(f) or f=="NA", "'%s' file doesn't exist" % f

    n = len(args.sumstats)
    arg_dict = vars(args)
    for arg_name, arg_val in arg_dict.items():
        if (type(arg_val) is list) and (len(arg_val)<n) and (len(arg_val)==1):
            arg_dict[arg_name] = arg_val*n
    chr2use_arg = arg_dict["chr2use"]
    chr2use = []
    for a in chr2use_arg.split(","):
        if "-" in a:
            start, end = [int(x) for x in a.split("-")]
            chr2use += [str(x) for x in range(start, end+1)]
        else:
            chr2use.append(a.strip())
    arg_dict["chr2use"] = chr2use

    msg = " option should have a value for each sumstat file or a single value"
    assert len(args.sep) == n, "--sep" + msg
    assert len(args.snp) == n, "--snp" + msg
    assert len(args.chr) == n, "--chr" + msg
    assert len(args.bp) == n, "--bp" + msg
    assert len(args.p) == n, "--p " + msg
    assert len(args.snps_to_keep) == n, "--snps-to-keep" + msg
    assert len(args.legend_labels) == n, "--legend-labels" + msg


def manh_get_snp_ids(fname):
    if fname == "NA":
        return np.array([])
    else:
        return pd.read_csv(fname,header=None,squeeze=True).values


def manh_get_lead(fname):
    if fname == "NA":
        return np.array([])
    elif (not os.path.isfile(fname)) or (os.stat(fname).st_size == 0):
        log.log('WARNING: {} (--lead) does not exist, or appears to be empty. Could it be that no variants passed significance threshold?'.format(fname))
        return np.array([])
    else:
        df = pd.read_csv(fname, delim_whitespace=True)
        return df.loc[df.is_locus_lead,"LEAD_SNP"].values


def manh_get_indep_sig(fname):
    if fname == "NA":
        return np.array([])
    elif (not os.path.isfile(fname)) or (os.stat(fname).st_size == 0):
        log.log('WARNING: {} (--indep) does not exist, or appears to be empty. Could it be that no variants passed significance threshold?'.format(fname))
        return np.array([])
    else:
        df = pd.read_csv(fname, delim_whitespace=True)
        return df["INDEP_SNP"].values


def manh_get_annot(fname):
    """
    Read annotation file and return Series: index=SNP ids and values=SNP labels.
    Return empty Series if fname == "NA"
    """
    if fname == "NA":
        return pd.Series([], dtype=object)
    else:
        series = pd.read_csv(fname,header=None,names=["snp", "label"],delim_whitespace=True,
            index_col="snp",squeeze=True)
        return series


def manh_filter_sumstats(log, sumstats_f, sep, snpid_col, pval_col, chr_col, bp_col, chr2use):
    """
    Filter original summary stats file.
    Args:
        sumstats_f: sumstats file name
        sep: column separator in sumstats_f
        snpid_col: a name of column with variant ids
        pval_col: a name of column with variant p-values
        chr_col: a name of column with variant chromosomes
        bp_col: a name of column with variant positions on chromosome
        chr2use: chromosomes to use for plotting (other are dropped)
    Returns:
        df: filtered DataFrame
    """
    log.log("Filtering %s" % sumstats_f)
    cols2use = [snpid_col, pval_col, chr_col, bp_col]
    df = pd.read_csv(sumstats_f, usecols=cols2use, sep=sep,
        dtype={chr_col:str})
    log.log("%d SNPs in %s" % (len(df), sumstats_f))
    df = df.loc[~df[snpid_col].isnull(), :].set_index(snpid_col)
    log.log("%d SNPs with non-null SNP" % len(df))
    # TODO: replace dropna with df = df.loc[df[pval_col]>0,:], should be ~ 1.5x faster
    df.dropna(subset=[pval_col], how="all", inplace = True)
    log.log("%d SNPs with defined p-value" % len(df))
    df = df.loc[df[chr_col].isin(chr2use),:]
    log.log("%d SNPs within specified chromosomes" % len(df))
    # TODO: zero filtering step is very slow, should be optimized
    df = df.loc[df[pval_col]>0,:]
    log.log("%d SNPs with non-zero p-value" % len(df))
    # TODO: drop duplicates as it is done in qq.py
    return df


def manh_get_df2plot(log, df, outlined_snps_f, bold_snps_f, lead_snps_f, indep_snps_f,
    annot_f, snps_to_keep_f):
    """
    Select variants which will be plotted. Mark lead and independent significant
    variants if corresponding information is provided.
    Args:
        df: DataFrame for variant selection
        outlined_snps_f: a name of file with SNP ids to plot with outlined bold dots
        bold_snps_f: a name of file with SNP ids to plot with bold dots
        lead_snps_f: a name of file with lead variants
        indep_snps_f: a name of file with independent significant variants
        snps_to_keep_f: a list of variants to consider for plotting, only these
            variants are considered when downsampling take place 
    Returns:
        df2plot: DataFrame with variants for plotting
    """
    log.log("Preparing SNPs for plotting")
    # define a subset of variants which will be plotted:
    # [outlined + lead] + [bold + indep] + sample
    outlined_snp_ids = manh_get_snp_ids(outlined_snps_f)
    bold_snp_ids = manh_get_snp_ids(bold_snps_f)
    lead_snp_id = manh_get_lead(lead_snps_f)
    indep_snp_id = manh_get_indep_sig(indep_snps_f)
    annot_series = manh_get_annot(annot_f)
    outlined_snp_ids = np.unique(np.concatenate((outlined_snp_ids, lead_snp_id)))
    bold_snp_ids = np.unique(np.concatenate((bold_snp_ids, indep_snp_id)))

    # sample variants
    if snps_to_keep_f != "NA":
        snps2keep = manh_get_snp_ids(snps_to_keep_f)
        ii = df.index.intersection(snps2keep)
        df = df.loc[ii,:]
        log.log("%d SNPs overlap with %s" % (len(df),snps_to_keep_f))
    else:
        snps2keep = df.index

    # NOTE: it could be that there are snp ids in outlined_snp_ids or bold_snp_ids which
    # are not in df.index, therefore we should take an index.intersection first.
    outlined_snp_ids = df.index.intersection(outlined_snp_ids)
    bold_snp_ids = df.index.intersection(bold_snp_ids)
    annot_snp_ids = df.index.intersection(annot_series.index)
    snps2keep = np.unique(np.concatenate((outlined_snp_ids, bold_snp_ids, annot_snp_ids, snps2keep)))

    df2plot = df.loc[snps2keep,:]
    df2plot.loc[:,"outlined"] = False
    df2plot.loc[outlined_snp_ids,"outlined"] = True
    df2plot.loc[:,"bold"] = False
    df2plot.loc[bold_snp_ids,"bold"] = True
    df2plot.loc[:,"annot"] = ""
    df2plot.loc[annot_snp_ids,"annot"] = annot_series[annot_snp_ids]
    log.log("%d SNPs will be used for plotting, including:" % len(df2plot))
    log.log("%d outlined SNPs" % len(outlined_snp_ids))
    log.log("%d bold SNPs" % len(bold_snp_ids))
    log.log("%d annotated SNPs" % len(annot_snp_ids))
    return df2plot


def manh_get_chr_df(log, dfs2plot, bp_cols, chr_cols, between_chr_gap, chr2use):
    """
    Construct DataFrame with index = chromosome names and 5 columns:
    min: minimum coordinate on each chromosome among all dfs in dfs2plot
    max: maximum coordinate on each chromosome among all dfs in dfs2plot
    ind: index of the chromosome = 1:N, where N - nuumber of different chromosomes
    rel_size: size of the chromosome relative to the first chromosome (i.e.
        rel_size of the first chr = 1)
    start: start coordinate of the chromosome on the x axis, where the first
        chromosome starts at x = 0 and ends at x = 1 (if its size = 1), taking
        into account between_chr_gap
    Args:
        dfs2plot: a list of DataFrames that will be plotted
        bp_cols: name of marker position on chromosome columns
        chr_cols: name of marker chromosome columns
        between_chr_gap: gap between end of chr K and start of chr K+1
        chr2use: chromosomes to use for plotting (other are dropped)
    Returns:
        chr_df: a DataFrame with chromosome information as described above
    """
    unique_chr = np.unique(np.concatenate([df[chr_cols[i]].unique() for i,df in enumerate(dfs2plot)]))
    unique_chr = [c for c in chr2use if c in unique_chr]
    chr_df = pd.DataFrame(index=unique_chr, columns=["min","max","ind","start","rel_size"])
    min_df = pd.DataFrame(index=unique_chr)
    max_df = pd.DataFrame(index=unique_chr)
    for i,df in enumerate(dfs2plot):
        chr_min = df.groupby(chr_cols[i])[bp_cols[i]].min()
        chr_max = df.groupby(chr_cols[i])[bp_cols[i]].max()
        min_df[i] = chr_min
        max_df[i] = chr_max
    chr_df["min"] = min_df.min(axis=1)
    chr_df["max"] = max_df.max(axis=1)
    chr_df["ind"] = np.arange(len(unique_chr))
    # use the first chr form unique_chr as a reference unit size
    ref_unit_size = chr_df.loc[chr_df.index[0],"max"] - chr_df.loc[chr_df.index[0],"min"]
    chr_df["rel_size"] = (chr_df["max"] - chr_df["min"])/ref_unit_size
    chr_df["start"] = chr_df["rel_size"].cumsum() - chr_df["rel_size"] + between_chr_gap*chr_df["ind"]
    return chr_df


def manh_add_coords(log, df2plot, chr_col, bp_col, pval_col, chr_df, snps_visual_bins):
    """
    Modify provided DataFrame df2plot by adding columns with x-y coordinates for
    plotting to it.
    Args:
        df2plot: DataFrame with variants for plotting (produced by get_df2plot)
        chr_col: a column with chromosome of variants in df2plot
        bp_col: a column with position on chromosome of variants in df2plot
        pval_col: a column with variant p-values
        chr_df: a DataFrame with chromosome information (produced by get_chr_df)
    """
    chr_start = chr_df.loc[df2plot[chr_col], "start"].values
    chr_min = chr_df.loc[df2plot[chr_col], "min"].values
    df2plot.loc[:,"x_coord"] = (df2plot[bp_col] - chr_min)/chr_df.loc[chr_df.index[0],"max"] + chr_start
    df2plot.loc[:,"log10p"] = -np.log10(df2plot[pval_col]) # y coord

    # filter points for plotting
    df2plot.loc[:,"x_coord_bin"] = np.digitize(df2plot.loc[:,"x_coord"], np.linspace(df2plot['x_coord'].min(), df2plot['x_coord'].max(), num=snps_visual_bins))
    df2plot.loc[:,"log10p_bin"] = np.digitize(df2plot.loc[:,"log10p"], np.linspace(df2plot['log10p'].min(), df2plot['log10p'].max(), num=snps_visual_bins))
    idx = (~df2plot['outlined'].values & ~df2plot['bold'].values & (df2plot['annot']==""))
    df2plot.loc[:, 'screen_dup'] = False
    df2plot.loc[idx, 'screen_dup'] = df2plot[idx][['x_coord_bin', 'log10p_bin']].duplicated()
    df2plot.drop(df2plot.index[df2plot['screen_dup'].values], inplace=True)

def manh_add_striped_background(log, chr_df, ax, y_up):
    """
    Add grey background rectagle for every second chromosome.
    """
    height = y_up
    background_rect = []
    for c in chr_df.index[1::2]:
        x = chr_df.loc[c,"start"]
        y = 0
        width = chr_df.loc[c,"rel_size"]
        rect = mpatches.Rectangle((x, y), width, height)
        background_rect.append(rect)
    pc = PatchCollection(background_rect, facecolor='#AEA79F', alpha=0.3,
                         edgecolor='None')
    ax.add_collection(pc)

def make_manh_implementation(args, log):
    process_manhattan_args(args)

    np.random.seed(args.seed)

    if args.color_list:
        assert len(args.sumstats) <= len(args.color_list), "%d is maximum number of sumstats to plot simultaneously with specified color scheme" % len(color_list)
        color_names = [int(x) if x.isdigit() else x for x in args.color_list]
        color_names_annot = color_names
        color_dict = {**DEFAULT_COLORS, **CB_COLORS}
        for x in args.color_list:
            if x not in color_dict:
                color_dict[x] = x
    elif args.cb_colors:
        assert len(args.sumstats) <= len(CB_COLOR_NAMES), "%d is maximum number of sumstats to plot simultaneously with color-blind color scheme" % len(CB_COLOR_NAMES)
        color_names = CB_COLOR_NAMES
        color_names_annot = CB_COLOR_NAMES_ANNOT
        color_dict = CB_COLORS
    else:
        # use default colors
        assert len(args.sumstats) <= len(DEFAULT_COLOR_NAMES), "%d is maximum number of sumstats to plot simultaneously with default color scheme" % len(DEFAULT_COLOR_NAMES)
        color_names = DEFAULT_COLOR_NAMES
        color_names_annot = DEFAULT_COLOR_NAMES_ANNOT
        color_dict = DEFAULT_COLORS

    legend_labels = [os.path.splitext(os.path.basename(args.sumstats[i]))[0] if ll == "NA" else ll
        for i,ll in enumerate(args.legend_labels)]
    legends_handles = []

    sumstat_dfs = [
        manh_filter_sumstats(log, s, args.sep[i], args.snp[i], args.p[i], args.chr[i], args.bp[i], args.chr2use)
        for i,s in enumerate(args.sumstats)]

    dfs2plot = [manh_get_df2plot(log, df, args.outlined[i], args.bold[i], args.lead[i], args.indep[i],
                            args.annot[i], args.snps_to_keep[i])
        for i, df in enumerate(sumstat_dfs)]

    chr_df = manh_get_chr_df(log, dfs2plot, args.bp, args.chr, args.between_chr_gap, args.chr2use)

    for i,df in enumerate(dfs2plot):
        manh_add_coords(log, df, args.chr[i], args.bp[i], args.p[i], chr_df, snps_visual_bins=args.snps_visual_bins)

    n_subplots = len(dfs2plot) if args.separate_sumstats else 1

    # make plot
    log.log("Making plot")
    plt.rc('legend',fontsize=15)
    fig, axarr = plt.subplots(n_subplots, squeeze=False, figsize=(14,5*n_subplots), dpi=200)
    axarr = axarr[:,0] # squeeze second dimention since we don't need it here


    # find upper limit for Y axis
    if args.y_max > 0:
        y_up = args.y_max
    else:
        y_up = max([df["log10p"].max() for df in dfs2plot])
        y_up = max(y_up, -np.log10(args.p_thresh))
        y_up *= 1.05

    if args.striped_background:
        for ax in axarr:
            manh_add_striped_background(log, chr_df, ax, y_up)

    for i, df in enumerate(dfs2plot):
        # plot normal points
        ax_i = i if args.separate_sumstats else 0
        ax = axarr[ax_i]
        
        color = color_dict[color_names[i]]
        ax.plot(df["x_coord"], df["log10p"], ls=' ', marker='.', ms=2,
            color=color, alpha=args.transparency[i])
        patch = mpatches.Patch(color=color, label=legend_labels[i])
        legends_handles.append(patch)
    for i, df in enumerate(dfs2plot):
        # plot bold significant and outlined variants "on top" of normal points
        ax_i = i if args.separate_sumstats else 0
        ax = axarr[ax_i]
        
        color = color_dict[color_names[i]]
        df_tmp = df.loc[df["bold"],:]
        ax.plot(df_tmp["x_coord"], df_tmp["log10p"], ls=' ', marker='o', ms=5,
            color=color)
        df_tmp = df.loc[df["outlined"],:]
        ax.plot(df_tmp["x_coord"], df_tmp["log10p"], ls=' ', marker='o', ms=8,
            markeredgewidth=0.6, markeredgecolor='k', color=color)
        df_tmp = df.loc[df["annot"]!="",["annot","x_coord", "log10p"]]
        pe = [mpe.Stroke(linewidth=0.8, foreground='black')]
        for row in df_tmp.itertuples():
            color = color_dict[color_names_annot[i]]
            ax.annotate(row.annot, xy=(row.x_coord, row.log10p), xycoords='data',
                xytext=(2,2), textcoords='offset points', color=color,
                fontsize=12, style='italic', fontweight='heavy',
                # path_effects=pe, # uncomment path_effects to have a black border of the label symbols 
                bbox={"boxstyle":"square, pad=0.02", "facecolor":"white",
                      "edgecolor":"none","alpha":0.6})

    for i,ax in enumerate(axarr):
        ax.hlines([-np.log10(args.p_thresh)], 0, 1, colors='k', linestyles='dotted',
            transform=ax.get_yaxis_transform())

        ax.tick_params(axis='y', which='major', labelsize=15)
        ax.tick_params(axis='x', which='major', labelsize=15)
        x_ticks = chr_df["start"] + 0.5*chr_df["rel_size"]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(map(str, x_ticks.index), fontsize=14)

        xlim = chr_df.loc[chr_df.index[-1], "start"] + chr_df.loc[chr_df.index[-1], "rel_size"]
        ax.set_xlim((-0.1, (xlim if np.isfinite(xlim) else 0) + 0.1))
        y_low = ax.get_ylim()[0]
        ax.set_ylim((0-0.005*y_up, y_up))
        # remove top and right spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        # add offset for left spine
        ax.spines['left'].set_position(('outward',5))
        ax.spines['bottom'].set_position(('outward',5))

        ax.set_xlabel("Chromosome", fontsize=20)
        ax.set_ylabel(r"$\mathrm{-log_{10}(%s)}$" % args.y_label, fontsize=20)

        if args.legend_location:
            handles = legends_handles[i:i+1] if args.separate_sumstats else legends_handles
            ax.legend(handles=handles, loc=args.legend_location)
        elif not args.no_legend:
            handles = legends_handles[i:i+1] if args.separate_sumstats else legends_handles
            ax.legend(handles=handles, loc='best')


    plt.tight_layout()
    plt.savefig(args.out)
    log.log("%s was generated" % args.out)

###################################################
# implement parser_qq
###################################################
def qq_drop_duplicated_ind(log, df):
    i = df.index.duplicated(keep='first')
    if i.any():
        log.log("The table contains %d duplicated ids" % sum(i))
        log.log("Only the first row with duplicated id will be retained")
        df = df.loc[~i,:]
    return df


def qq_process_args(args):
    """
    Check whether provided arguments are correct, change list-type arguments
    with single value to have a length = length of sumstats argument and process
    chr2use arument.
    """
    assert os.path.isfile(args.sumstats), "'%s' file doesn't exist" % args.sumstats
    assert os.path.isfile(args.strata) or args.strata=="NA", "'%s' file doesn't exist" % args.strata
    assert os.path.isfile(args.weights) or args.weights=="NA", "'%s' file doesn't exist" % args.weights

    # process special arguments
    arg_dict = vars(args)
    if args.strata_num != "NA":
        intervals = {}
        for name_i in arg_dict["strata_num_intervals"].split(","):
            name, i = name_i.split("=")
            name = name.strip()
            assert name != "", "Stratum name should not be an empty string"
            start,end = i.split(":")
            start = -np.inf if start == "" else float(start)
            end = np.inf if end == "" else float(end)
            assert not name in intervals, "Stratum name must be unique (duplicated name: %s)" % name
            intervals[name] = (start, end)
        arg_dict["strata_num_intervals"] = intervals
    if args.strata_cat != "NA" and args.strata_cat_ids != "NA":
        categories = {}
        for name_c in arg_dict["strata_cat_ids"].split(","):
            name, c = name_c.split("=")
            name = name.strip()
            assert name != "", "Stratum name should not be an empty string"
            c = frozenset(map(str.strip, c.split(":")))
            assert not name in categories, "Strata name must be unique (duplicated name: %s)" % name
            categories[name] = c
        arg_dict["strata_cat_ids"] = categories


def qq_read_sumstats(log, sumstats_f, sep, snpid_col, pval_col):
    """
    Filter original summary stats file.
    Args:
        sumstats_f: sumstats file name
        sep: column separator in sumstats_f
        snpid_col: a name of column with variant ids
        pval_col: a name of column with variant p-values
    Returns:
        df: filtered p-values, pd.DataFrame(index=snp_id, values=pval)
    """
    log.log("Reading %s" % sumstats_f)
    cols2use = [snpid_col, pval_col]
    df = pd.read_csv(sumstats_f, usecols=cols2use, index_col=snpid_col,
        sep=sep)
    log.log("%d SNPs in %s" % (len(df), sumstats_f))
    df = df.loc[np.isfinite(df[pval_col]),:]
    log.log("%d SNPs with defined p-value" % len(df))
    df = df.loc[df[pval_col]>0,:]
    log.log("%d SNPs with non-zero p-value" % len(df))
    df = qq_drop_duplicated_ind(log, df)
    return df


def qq_read_strata_cat(log, strata_f, sep, snpid_col, strata_cat_col, strata_cat_ids):
    log.log("Reading strata file %s" % strata_f)
    cols2use = [snpid_col, strata_cat_col]
    df = pd.read_csv(strata_f, usecols=cols2use, index_col=snpid_col, sep=sep,
        dtype={strata_cat_col:str})
    # make a standard name for variant strata column
    if strata_cat_ids == "NA":
        for s in df[strata_cat_col].unique():
            stratum_i = (df[strata_cat_col] == s)
            df.loc[:,s] = stratum_i
    else:
        for name, ids_set in strata_cat_ids.items():
            stratum_i = df[strata_cat_col].isin(ids_set)
            df.loc[:,name] = stratum_i
    df.drop([strata_cat_col], axis=1, inplace=True)
    # keep only variants which are within any stratum
    df = df.loc[df.any(axis=1)]
    assert len(df) > 0, "All strata are empty"
    df = qq_drop_duplicated_ind(df)
    return df


def qq_read_strata_num(log, strata_f, sep, snpid_col, strata_num_col, strata_num_intervals):
    log.log("Reading strata file %s" % strata_f)
    cols2use = [snpid_col, strata_num_col]
    df = pd.read_csv(strata_f, usecols=cols2use, index_col=snpid_col, sep=sep,
        dtype={strata_num_col:float})
    for name, (start, end) in strata_num_intervals.items():
        stratum_i = (start<df[strata_num_col]) & (df[strata_num_col]<end)
        df.loc[:,name] = stratum_i
    df.drop([strata_num_col], axis=1, inplace=True)
    # keep only variants which are within any stratum
    df = df.loc[df.any(axis=1)]
    assert len(df) > 0, "All strata are empty"
    df = qq_drop_duplicated_ind(log, df)
    return df


def qq_read_strata_bin(log, strata_f, sep, snpid_col, strata_bin):
    log.log("Reading strata file %s" % strata_f)
    cols2use = [snpid_col] + strata_bin
    df = pd.read_csv(strata_f, usecols=cols2use, index_col=snpid_col, sep=sep,
        dtype=dict.fromkeys(strata_bin, bool))
    df = df.loc[df.any(axis=1)]
    assert len(df) > 0, "All strata are empty"    
    df = qq_drop_duplicated_ind(log, df)
    return df


def qq_read_weights(log, weights_f):
    log.log("Reading weights file %s" % weights_f)
    df = pd.read_csv(weights_f, sep='\t', header=None, names=["snp", "w"],
        index_col="snp")
    # drop zero weights
    df = df.loc[df.w>0,:]
    qq_drop_duplicated_ind(log, df)
    return df


def qq_get_xy_from_p(p, top_as_dot, p_weights, nbins=200):
    if p_weights is None:
        p_weights = np.ones(len(p))
    p_weights /= sum(p_weights) # normalize weights

    i = np.argsort(p)
    p = p[i]
    p_weights = p_weights[i]
    p_ecdf = np.concatenate([[0], np.cumsum(p_weights)])

    y = np.logspace(np.log10(p[-1]), np.log10(p[top_as_dot]), nbins)
    i = np.searchsorted(p, y, side='right')
    i[0] = len(p)  # last index in p_ecdf
    i[-1] = top_as_dot+1 # top_as_dot index in p_ecdf
    # estimate standard uniform quantiles corresponding to y observed quantiles
    uniform_quantiles = p_ecdf[i]
    x = -np.log10(uniform_quantiles)
    y = -np.log10(y)
    # if top_as_dot = 0, then x_dot and y_dot are empty arrays
    x_dot = -np.log10(p_ecdf[1:top_as_dot+1])
    y_dot = -np.log10(p[:top_as_dot]).values
    return x, y, x_dot, y_dot


def qq_get_ci(p, p_weights, ci_alpha=0.05, nbins=200):
    # TODO: the first part of this function is identical to the first part of
    # get_xy_from_p(), so probably should be merged??
    if p_weights is None:
        p_weights = np.ones(len(p))
    p_weights *= len(p)/sum(p_weights) # normalize weights and imitate order statistics

    i = np.argsort(p)
    p = p[i]
    p_weights = p_weights[i]
    cum_p_weights = np.cumsum(p_weights)

    y = np.logspace(np.log10(p[-1]), np.log10(p[0]), nbins)
    # the following code is inspired by:
    # https://genome.sph.umich.edu/wiki/Code_Sample:_Generating_QQ_Plots_in_R
    # beta_a is our order statistics. For standard uniform distr (expected under null)
    # it follows beta distr:
    # https://en.wikipedia.org/wiki/Order_statistic#Order_statistics_sampled_from_a_uniform_distribution
    i = np.searchsorted(p, y, side='left')
    i[0] = len(p) - 1
    i[-1] = 0
    beta_a = cum_p_weights[i]
    beta_b = len(p) + 1 - beta_a
    lower_ci = -np.log10(stats.beta.ppf(1-ci_alpha/2, beta_a, beta_b))
    upper_ci = -np.log10(stats.beta.ppf(ci_alpha/2, beta_a, beta_b))
    x_ci = -np.log10(beta_a/len(p))
    return x_ci, lower_ci, upper_ci

def make_qq_implementation(args, log):
    qq_process_args(args)

    df_sumstats = qq_read_sumstats(log, args.sumstats, args.sep, args.snp, args.p)

    df_strata = None
    if args.strata_cat != "NA":
        df_strata = qq_read_strata_cat(log, args.strata, args.strata_sep, args.strata_snp,
            args.strata_cat, args.strata_cat_ids)
    elif args.strata_num != "NA":
        df_strata = qq_read_strata_num(log, args.strata, args.strata_sep, args.strata_snp,
            args.strata_num, args.strata_num_intervals)
    elif args.strata_bin != "NA":
        df_strata = qq_read_strata_bin(log, args.strata, args.strata_sep, args.strata_snp,
            args.strata_bin)

    if args.weights != 'NA':
        df_weights = qq_read_weights(log, args.weights)
        snps_with_weight = df_sumstats.index.intersection(df_weights.index)
        log.log("%d varints from %s have weight" % (len(snps_with_weight), args.sumstats))
        assert len(snps_with_weight) > 0, ("At least one variant from %s must "
            "have weight in %s if weights are provided" % (args.sumstats, args.weights))
        log.log("Only they will be plotted") 
        df_sumstats = df_sumstats.loc[snps_with_weight,:]
        df_sumstats["weights"] = df_weights.loc[snps_with_weight,:]
    else:
        # if weights are not provided set equal weights to all SNPs
        df_sumstats["weights"] = 1.

    if not df_strata is None:
        # drop variants which are not in df_sumstats
        df_strata = df_strata.loc[df_strata.index.isin(df_sumstats.index),:]
    # df_strata is either None or:
    # df_strata = DataFrame(index=snp_ids, columns=boolean_strata)

    x, y, x_dot, y_dot = qq_get_xy_from_p(df_sumstats[args.p], args.top_as_dot,
        df_sumstats["weights"])
    x_ci, lower_ci, upper_ci = qq_get_ci(df_sumstats[args.p], df_sumstats["weights"])

    # estimate axis limits
    max_x_lim = max(x[-1],x_ci[-1], 0 if args.top_as_dot==0 else x_dot[0])
    max_y_lim = max(y[-1],upper_ci[-1], 0 if args.top_as_dot==0 else y_dot[0])

    log.log("Making plot")
    json_data = {}
    fig, ax = plt.subplots(figsize=(6,6), dpi=200)

    # plot null and ci
    ax.fill_between(x_ci, lower_ci, upper_ci, color="0.8"); json_data['x_ci'] = x_ci; json_data['lower_ci'] = lower_ci; json_data['upper_ci'] = upper_ci
    ax.plot([0,x_ci[-1]], [0,x_ci[-1]], ls='--', lw=1, marker=' ', color="k")
    # plot all data
    if df_strata is None:
        ax.plot(x, y, ls='-', lw=1, marker=' ', label="all variants", color='C0'); json_data['x'] = x; json_data['y'] = y
        if args.top_as_dot > 0:
            ax.plot(x_dot, y_dot, ls=' ', marker='.', ms=1, color='C0'); json_data['x_dot'] = x_dot; json_data['y_dot'] = y_dot

    # plot strata
    if not df_strata is None:
        json_data['stratum'] = []
        for j, stratum_id in enumerate(df_strata.columns):
            i = df_strata.index[df_strata[stratum_id]]
            json_stratum = {'stratum_id':stratum_id}
            x, y, x_dot, y_dot = qq_get_xy_from_p(df_sumstats.loc[i,args.p],
                args.top_as_dot, df_sumstats.loc[i,"weights"])
            color = "C%d" % ((j%9)+1); json_stratum['color'] = color
            ax.plot(x, y, ls='-', lw=1, marker=' ', label=stratum_id, color=color); json_stratum['x'] = x; json_stratum['y'] = y
            if args.top_as_dot > 0:
                ax.plot(x_dot, y_dot, ls=' ', marker='.', ms=1, color=color); json_stratum['x_dot'] = x_dot; json_stratum['y_dot'] = y_dot
            # update upper limits if needed
            max_x_lim = max(max_x_lim, x[-1], 0 if args.top_as_dot==0 else x_dot[0])
            max_y_lim = max(max_y_lim, y[-1], 0 if args.top_as_dot==0 else y_dot[0])
            json_data['stratum'].append(json_stratum)

    ax.set_xlabel(r"expected $\mathrm{-log_{10}(P)}$")
    ax.set_ylabel(r"observed $\mathrm{-log_{10}(P)}$")

    if not args.x_lim is None:
        max_x_lim = args.x_lim
    if not args.y_lim is None:
        max_y_lim = args.y_lim
    ax.set_xlim((-0.005*max_x_lim, 1.01*max_x_lim))
    ax.set_ylim((-0.005*max_y_lim, 1.01*max_y_lim))

    # configure and set title
    title = os.path.splitext(os.path.basename(args.sumstats))[0]
    if args.strata != "NA":
        strata = os.path.splitext(os.path.basename(args.strata))[0]
        title = "%s | %s" % (title, strata)
    ax.set_title(title, fontsize='small'); json_data['title'] = title

    ax.legend(loc='upper left', fontsize="small")

    # remove top and right spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # add offset for left spine
    # ax.spines['left'].set_position(('outward',1))
    # ax.spines['bottom'].set_position(('outward',1))

    plt.grid(True)
    # plt.axis('equal')
    plt.tight_layout()
    # plt.show()

    plt.savefig(args.out)
    log.log("%s was generated" % args.out)

    with open(args.out + '.json', 'w') as outfile:  
        json.dump(json_data, outfile, cls=NumpyEncoder)    
    log.log("%s.json was generated" % args.out)

    log.log("Done.")

###################################################

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
