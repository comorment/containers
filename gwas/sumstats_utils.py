# Misc utils to deal with summary stat files.
# Some parts of the code in this file originates from https://github.com/bulik/ldsc/,
# which is licensed under GNU General Public License v3.0
# See https://github.com/bulik/ldsc/blob/master/LICENSE for complete license.

import sys, os, re, logging, datetime
import numpy as np
import pandas as pd
import gzip
import six
import itertools as it
from collections import namedtuple

COMPLEMENT_ALLELE = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
# bases
BASES = COMPLEMENT_ALLELE.keys()
# true iff strand ambiguous
STRAND_AMBIGUOUS = {''.join(x): x[0] == COMPLEMENT_ALLELE[x[1]]
                    for x in it.product(BASES, BASES)
                    if x[0] != x[1]}
# SNPS we want to keep (pairs of alleles)
VALID_SNPS = {x for x in map(lambda y: ''.join(y), it.product(BASES, BASES))
              if x[0] != x[1] and not STRAND_AMBIGUOUS[x]}
# T iff SNP 1 has the same alleles as SNP 2 (allowing for strand or ref allele flip).
MATCH_ALLELES = {x for x in map(lambda y: ''.join(y), it.product(VALID_SNPS, VALID_SNPS))
                 # strand and ref match
                 if ((x[0] == x[2]) and (x[1] == x[3])) or
                 # ref match, strand flip
                 ((x[0] == COMPLEMENT_ALLELE[x[2]]) and (x[1] == COMPLEMENT_ALLELE[x[3]])) or
                 # ref flip, strand match
                 ((x[0] == x[3]) and (x[1] == x[2])) or
                 ((x[0] == COMPLEMENT_ALLELE[x[3]]) and (x[1] == COMPLEMENT_ALLELE[x[2]]))}  # strand and ref flip
# T iff SNP 1 has the same alleles as SNP 2 w/ ref allele flip.
FLIP_ALLELES = {''.join(x):
                ((x[0] == x[3]) and (x[1] == x[2])) or  # strand match
                # strand flip
                ((x[0] == COMPLEMENT_ALLELE[x[3]]) and (x[1] == COMPLEMENT_ALLELE[x[2]]))
                for x in MATCH_ALLELES}

def filter_alleles(alleles):
    '''Remove bad variants (mismatched alleles, non-SNPs, strand ambiguous).'''
    ii = alleles.apply(lambda y: y in MATCH_ALLELES)
    return ii


def align_alleles(z, alleles):
    '''Align Z1 and Z2 to same choice of ref allele (allowing for strand flip).'''
    try:
        z *= (-1) ** alleles.apply(lambda y: FLIP_ALLELES[y])
    except KeyError as e:
        raise KeyError('Incompatible alleles. ')
    return z

Cols = namedtuple('Cols', ['SNP', 'CHR', 'BP', 'PVAL', 'A1', 'A2', 'EA', 'N', 'NCASE', 'NCONTROL', 'Z', 'OR', 'BETA', 'LOGODDS', 'SE', 'INFO', 'FRQ', 'NSTUDY', 'CHRPOS', 'A1A2', 'CHRPOSA1A2', 'DIRECTION'])
cols = Cols._make(        ['SNP', 'CHR', 'BP', 'PVAL', 'A1', 'A2', 'EA', 'N', 'NCASE', 'NCONTROL', 'Z', 'OR', 'BETA', 'LOGODDS', 'SE', 'INFO', 'FRQ', 'NSTUDY', 'CHRPOS', 'A1A2', 'CHRPOSA1A2', 'DIRECTION'])
cols_type_map =           {'SNP':str, 'CHR':int, 'BP':int, 'PVAL':np.float64, 'A1':str, 'A2':str, 'EA':str, 'N':float, 'NCASE':float, 'NCONTROL':float, 'Z':float, 'OR':float, 'BETA':float,
                           'LOGODDS':float, 'SE':float, 'INFO':float, 'FRQ':float, 'NSTUDY':int, 'CHRPOS':str, 'A1A2':str, 'CHRPOSA1A2':str, 'DIRECTION':str }
null_values = {
    cols.LOGODDS: 0,
    cols.BETA: 0,
    cols.OR: 1,
    cols.Z: 0
}

default_cnames = {

    # RS NUMBER
    'SNP': cols.SNP,
    'MARKERNAME': cols.SNP,
    'SNPID': cols.SNP,
    'SNP_ID': cols.SNP,  
    'RS': cols.SNP,
    'RSID': cols.SNP,
    'RS_NUMBER': cols.SNP,
    'RS_NUMBERS': cols.SNP,
    # CHROMOSOME
    'CHR': cols.CHR,
    'CHROM': cols.CHR,
    'CHROMSOME': cols.CHR,
    'CHROMOSOME' : cols.CHR,
    # POSITION
    'POS': cols.BP,
    'BP': cols.BP,
    'BPOS': cols.BP,
    'POSITION' : cols.BP,
    # NUMBER OF STUDIES
    'NSTUDY': cols.NSTUDY,
    'N_STUDY': cols.NSTUDY,
    'NSTUDIES': cols.NSTUDY,
    'N_STUDIES': cols.NSTUDY,
    # P-VALUE
    'P': cols.PVAL,
    'PVALUE': cols.PVAL,
    'P_VALUE':  cols.PVAL,
    'PVAL': cols.PVAL,
    'P_VAL': cols.PVAL,
    'GC_PVALUE': cols.PVAL,
    'MTAG_PVAL': cols.PVAL,
    # ALLELE 1
    'A1': cols.A1,
    'ALLELE1': cols.A1,
    'ALLELE_1': cols.A1,
    'EFFECT_ALLELE': cols.A1,
    'REFERENCE_ALLELE': cols.A1,
    'INC_ALLELE': cols.A1,
    'EA': cols.A1,
    # ALLELE 2
    'A2': cols.A2,
    'ALLELE2': cols.A2,
    'ALLELE_2': cols.A2,
    'OTHER_ALLELE': cols.A2,
    'NON_EFFECT_ALLELE': cols.A2,
    'NON_EFF_ALLELE': cols.A2,
    'DEC_ALLELE': cols.A2,
    'NEA': cols.A2,
    # N
    'N': cols.N,
    'SAMPLESIZE': cols.N,  
    'NCASE': cols.NCASE,
    'CASES_N': cols.NCASE,
    'N_CASE': cols.NCASE,
    'N_CASES': cols.NCASE,
    'N_CONTROLS': cols.NCONTROL,
    'N_CAS': cols.NCASE,
    'N_CON': cols.NCONTROL,
    'N_CASE': cols.NCASE,
    'NCONTROL': cols.NCONTROL,
    'CONTROLS_N': cols.NCONTROL,
    'N_CONTROL': cols.NCONTROL,
    'WEIGHT': cols.N,  # metal does this. possibly risky.
    # SIGNED STATISTICS
    'ZSCORE': cols.Z,
    'Z-SCORE': cols.Z,
    'GC_ZSCORE': cols.Z,
    'Z': cols.Z,
    'MTAG_Z': cols.Z,
    'OR': cols.OR,
    'B': cols.BETA,
    'BETA': cols.BETA,
    'MTAG_BETA': cols.BETA,
    'LOGODDS': cols.LOGODDS,
    'EFFECTS': cols.BETA,
    'EFFECT': cols.BETA,
    'SIGNED_SUMSTAT': 'SIGNED_SUMSTAT',
    # STANDARD ERROR
    'SE' : cols.SE,
    'STDERR' : cols.SE,
    'MTAG_SE' : cols.SE,
    # INFO
    'INFO': cols.INFO,
    # MAF
    'EAF': cols.FRQ,
    'FRQ': cols.FRQ,
    'MAF': cols.FRQ,
    'FRQ_U': cols.FRQ,
    'F_U': cols.FRQ,
    'FREQ': cols.FRQ,
    # DIRECTION
    'DIRECTION': cols.DIRECTION,
}

describe_cname = {
    cols.SNP: 'Variant ID (e.g., rs number)',
    cols.CHR: 'Chromosome number',
    cols.BP: 'Base-pair position',
    cols.PVAL: 'p-Value',
    cols.A1: 'Allele 1, interpreted as ref allele for signed sumstat.',
    cols.A2: 'Allele 2, interpreted as non-ref allele for signed sumstat.',
    cols.EA: 'Effect Allele, interpreted as ref allele for signed sumstat (specific to MVP data to validate that A1 is the same as EA).',
    cols.N: 'Sample size',
    cols.NCASE: 'Number of cases',
    cols.NCONTROL: 'Number of controls',
    cols.Z: 'Z-score (0 --> no effect; above 0 --> A1 is trait/risk increasing)',
    cols.OR: 'Odds ratio (1 --> no effect; above 1 --> A1 is risk increasing)',
    cols.BETA: '[linear/logistic] regression coefficient (0 --> no effect; above 0 --> A1 is trait/risk increasing)',
    cols.LOGODDS: 'Log odds ratio (0 --> no effect; above 0 --> A1 is risk increasing)',
    cols.SE: 'standard error of the effect size',
    cols.INFO: 'INFO score (imputation quality; higher --> better imputation)',
    cols.FRQ: 'Allele frequency',
    'SIGNED_SUMSTAT': 'Directional summary statistic as specified by --signed-sumstats.',
    cols.NSTUDY: 'Number of studies in which the SNP was genotyped.',
    'UNKNOWN': 'Unknown column type (will be skipped).',
    cols.CHRPOS: 'chr:pos column with colon-separated information about Chromosome and Base-pair position',
    cols.A1A2: 'A1/A2 column with slash-separated information about marker allles',
    cols.CHRPOSA1A2: 'chr:pos:ref:alt column with colon-separated information about Chromosome, Base-pair position, Reference allele, Alternative allele',
    cols.DIRECTION: 'METAL "direction" column, one char per substudy (+ or - indicate effect direction; ? indicate failed imputation or QC)'
}

def clean_header(header):
    '''
    For cleaning file headers.
    - convert to uppercase
    - replace dashes '-' with underscores '_'
    - replace dots '.' (as in R) with underscores '_'
    - remove newlines ('\n')
    '''
    return header.upper().replace('-', '_').replace('.', '_').replace('\n', '')

def format_chr(chrvec):
    '''
    Reformat chromosome names.

    Input:
    ------
    Vector of chromosome IDs

    Output:
    -------
    Vector of cleaned chromosome IDs

    Note:
    * Remove "chr/Chr/CHR/MT/mt" strings in the name
    * Change chrX to 23, ChrY to 24, PAR to 25, MT to 26
    * (as in plink, https://www.cog-genomics.org/plink/1.9/input#allow_extra_chr)
    '''
    try:
        tmpchrvec = chrvec.astype('str')
        tmpchrvec = tmpchrvec.str.lower()
        tmpchrvec = tmpchrvec.str.replace('chr', '')
        tmpchrvec[tmpchrvec=='x'] = '23'
        tmpchrvec[tmpchrvec=='y'] = '24'
        tmpchrvec[tmpchrvec=='par'] = '25'
        tmpchrvec[tmpchrvec=='m'] = '26'
        tmpchrvec[tmpchrvec=='mt'] = '26'
        tmpchrvec[tmpchrvec=='x_par1'] = '25'
        tmpchrvec[tmpchrvec=='x_par2'] = '25'
        tmpchrvec[tmpchrvec=='x_nonpar'] = '23'
        # TO-DO: Bellow is anoying
        tmpchrvec[tmpchrvec=='na'] = '-9'
        tmpchrvec[tmpchrvec.isnull()] = '-9'
        tmpchrvec[tmpchrvec=='nan'] = '-9'
        tmpchrvec[tmpchrvec==' '] = '-9'
        tmpchrvec = tmpchrvec.astype('float').astype('int')
        return tmpchrvec
    except:
        raise

def get_header(fh, lines=5):
    (openfunc, _) = get_compression(fh)
    header = []
    with openfunc(fh) as f:
        for line in it.islice(f, lines):
            line = line if isinstance(line, six.string_types) else line.decode('utf-8')
            header.append(line.rstrip('\n'))
    return header

def get_compression_and_open(fh):
    (openfunc, _) = get_compression(fh)
    return openfunc(fh)

def get_compression(fh):
    '''
    Read filename suffixes and figure out whether it is gzipped,bzip2'ed or not compressed
    '''
    if fh.endswith('gz'):
        compression = 'gzip'
        openfunc = gzip.open
    elif fh.endswith('bz2'):
        compression = 'bz2'
        openfunc = bz2.BZ2File
    else:
        openfunc = open
        compression = None

    return openfunc, compression
