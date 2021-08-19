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
import os
import time, sys, traceback
import argparse
import six
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
MASTHEAD += "* loci.py: utility to detect loci boundaries in GWAS summary statistics\n"
MASTHEAD += "* This code is forked from python_convert/sumstats.py clump.\n"
MASTHEAD += "* Version {V}\n".format(V=__version__)
MASTHEAD += "* (C) 2016-2021 Oleksandr Frei and Alexey A. Shadrin\n"
MASTHEAD += "* Norwegian Centre for Mental Disorders Research / University of Oslo\n"
MASTHEAD += "* GNU General Public License v3\n"
MASTHEAD += "***********************************************************************\n"

def parse_args(args):
    parser = argparse.ArgumentParser(description="""Perform LD-based clumping of summary stats, using a procedure that is similar to FUMA snp2gene functionality (http://fuma.ctglab.nl/tutorial#snp2gene):
Step 1. Re-save summary stats into one file for each chromosome.
Step 2a Use 'plink --clump' to find independent significant SNPs (default r2=0.6);
Step 2b Use 'plink --clump' to find lead SNPs, by clumping independent significant SNPs (default r2=0.1);
Step 3. Use 'plink --ld' to find genomic loci around each independent significant SNP (default r2=0.6);
Step 4. Merge together genomic loci which are closer than certain threshold (250 KB);
Step 5. Merge together genomic loci that fall into exclusion regions, such as MHC;
Step 6. Output genomic loci report, indicating lead SNPs for each loci;
Step 7. Output candidate SNP report;""")

    parser.add_argument("--sumstats", type=str, help="Input file with summary statistics")
    parser.add_argument("--out", type=str, help="[required] File to output the result.")
    parser.add_argument("--force", action="store_true", default=False, help="Allow sumstats.py to overwrite output file if it exists.")
    parser.add_argument("--chr2use", type=str, default='1-22', help="Chromosome ids to use "
         "(e.g. 1,2,3 or 1-4,12,16-20). Used when '@' is present in --geno-file, and allows to specify for which chromosomes to run the association testing.")

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
    parser.add_argument("--sumstats-chr", type=str, help="Input file with summary statistics, one file per chromosome")
    parser.set_defaults(func=make_clump)

    return parser.parse_args(args)

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

def tar_filter(tarinfo):
    if os.path.basename(tarinfo.name).startswith('sumstats'): return None
    return tarinfo

def clump_cleanup(args, log):
    temp_out = args.out + '.temp'
    log.log('Saving intermediate files to {out}.temp.tar.gz'.format(out=args.out))
    with tarfile.open('{out}.temp.tar.gz'.format(out=args.out), "w:gz") as tar:
        tar.add(temp_out, arcname=os.path.basename(temp_out), filter=tar_filter)
    rmtree(temp_out)

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

def make_clump(args, log):
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

### =================================================================================
###                                Main section
### ================================================================================= 
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.out is None:
        raise ValueError('--out is required.')

    log = Logger(args.out + '.log', 'w')
    start_time = time.time()

    try:
        defaults = vars(parse_args([]))
        opts = vars(args)
        non_defaults = [x for x in opts.keys() if opts[x] != defaults[x]]
        header = MASTHEAD
        header += "Call: \n"
        header += './loci.py \\\n'
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

