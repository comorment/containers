#!/usr/bin/env python3
# Run-script for polygenic (risk) score calculations using containerized applications.
# For usage, cf. this folder's README
#
#
# https://github.com/comorment/containers/issues/17
# MegaPRS
# LDpred2 (auto, inf, grid)
# *Plink
# PRS-CS
# *PRSice2
# SBayesR
# SBayesS

import abc
import argparse
import logging
import time
import sys
import traceback
import socket
import getpass
import six
import os
import json
import yaml
#import pandas as pd
import numpy as np
#from scipy import stats

_MAJOR = "1"
_MINOR = "0"
# On main and in a nightly release the patch should be one ahead of the last
# released build.
_PATCH = ""
# This is mainly for nightly builds which have the suffix ".dev$DATE". See
# https://semver.org/#is-v123-a-semantic-version for the semantics.
_SUFFIX = "dev"

VERSION_SHORT = "{0}.{1}".format(_MAJOR, _MINOR)
VERSION = "{0}.{1}.{2}{3}".format(_MAJOR, _MINOR, _PATCH, _SUFFIX)

__version__ = VERSION

MASTHEAD = "***********************************************************************\n"
MASTHEAD += "* pgrs.py: pipeline for PGRS analysis\n"
MASTHEAD += "* Version {V}\n".format(V=__version__)
MASTHEAD += "* (C) 2022 Espen Hagen, Oleksandr Frei, Bayram Akdeniz and Alexey A. Shadrin\n"
MASTHEAD += "* Norwegian Centre for Mental Disorders Research / University of Oslo\n"
MASTHEAD += "* Centre for Bioinformatics / University of Oslo\n"
MASTHEAD += "* GNU General Public License v3\n"
MASTHEAD += "***********************************************************************\n"


class BasePGRS(abc.ABC):
    """Base PGRS object declaration with some
    shared properties for subclassing
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, 
                 Sumstats_file='',
                 Pheno_file='',
                 Input_dir='',
                 Data_prefix='',
                 Output_dir='',                
                **kwargs):
        """
        Parameters
        ----------
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Input_dir: str
            path containing QC'd .bed, .bim, .fam files
            (</ENV/path/to/data/>)
        Data_prefix: str
            file prefix for QC'd .bed, .bim, .fam files
        Output_dir: str
            path for output files (<path>)
        **kwargs
        """
        self.Sumstats_file = Sumstats_file
        self.Pheno_file = Pheno_file
        self.Input_dir = Input_dir
        self.Data_prefix = Data_prefix
        self.Output_dir = Output_dir

        self.kwargs = kwargs

    @abc.abstractmethod
    def get_str(self):
        '''
        Required public method
        '''
        raise NotImplementedError


class PGS_Plink(BasePGRS):
    """
    Helper class for setting up Plink PRS analysis.
    Inherited from class ``BasePGRS``
    """

    def __init__(self, 
                 Sumstats_file='',
                 Pheno_file='',
                 Input_dir='',
                 Data_prefix='',
                 Output_dir='',
                 clump_p1=1,
                 clump_r2=0.1,
                 clump_kb=250,
                 range_list=[0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
                 strat_indep_pairwise=[250, 50, 0.25],
                 nPCs=6,
                 score_args=[3, 4, 12, 'header'],
                 **kwargs):
        '''
        Parameters
        ----------
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Input_dir: str
            path containing QC'd .bed, .bim, .fam files
            (</ENV/path/to/data/>)
        Data_prefix: str
            file prefix for QC'd .bed, .bim, .fam files
        Output_dir: str
            path for output files (<path>)
        clump_p1: float
            plink --clump-p1 parameter value (default: 1)
        clump_r2: float
            plink --clump-r2 parameter value (default: 0.1)
        clump_kb: float
            plink --clump-r2 parameter value (default: 250)
        range_list: list of floats
            list of p-value ranges for plink --q-score-range arg. 
            (default: [0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5])
        strat_indep_pairwise: list of scalars
            plink --indep-pairwise parameters for stratification describing
            window size (kb),  step size (variant ct), r^2 threshold
            (default: [250, 50, 0.25])
        nPCs: int
            plink --pca parameter value (default: 6)
        score_args: list
            plink --score arguments (default: [3, 4, 12, 'header'])
        **kwargs
        '''
        super().__init__(Sumstats_file=Sumstats_file,
                         Pheno_file=Pheno_file,
                         Input_dir=Input_dir,
                         Data_prefix=Data_prefix,
                         Output_dir=Output_dir,
                         **kwargs)
        # set attributes
        # clumping params
        self.clump_p1 = clump_p1
        self.clump_r2 = clump_r2
        self.clump_kb = clump_kb

        # range of p-values on interval (0, p-value)
        self.range_list = range_list

        # stratification param
        self.strat_indep_pairwise = strat_indep_pairwise

        # number of principal componentes
        self.nPCs = nPCs

        self.score_args = score_args

        # inferred
        self._transformed_file = os.path.join(
                Output_dir, 
                '.'.join(os.path.split(
                    self.Sumstats_file)[-1].split('.')[:-1] 
                    + ['transformed']))

        # check if Output_dir exist. Create if missing.
        if os.path.isdir(self.Output_dir):
            pass
        else:
            os.mkdir(self.Output_dir)
        
    def _preprocessing_update_effect_size(self):
        '''
        Generate string which will be included in job script
        for generating file with updated effect size
        '''
        self._preprocessing_update_effect_size_str = ' '.join([
            os.environ['RSCRIPT'],
            'update_effect_size.R',
            self.Sumstats_file,
            self._transformed_file])
    
    def _preprocessing_clumping(self):
        '''
        Generate string which will be included in job script
        for clumping (generating .clumped file)
        '''
        self._preprocessing_clumping_str = ' '.join([
            os.environ['PLINK'], 
            '--bfile', os.path.join(self.Input_dir, self.Data_prefix + '.QC'),
            '--clump-p1', str(self.clump_p1),
            '--clump-r2', str(self.clump_r2),
            '--clump-kb', str(self.clump_kb),
            '--clump', self._transformed_file,
            '--clump-snp-field', 'SNP',
            '--clump-field', 'P',
            '--out', os.path.join(self.Output_dir, self.Data_prefix)
            ])
    
    def _preprocessing_extract_index_SNP_ID(self):
        '''
        Extract index SNP ID to (generating .valid.snp file)
        '''
        self._preprocessing_extract_index_SNP_ID_str = ' '.join([
            os.environ['AWK_EXEC'],
            "'NR!=1{print $3}'",
            os.path.join(self.Output_dir, self.Data_prefix + '.clumped'),
            '>',
            os.path.join(self.Output_dir, self.Data_prefix + '.valid.snp'),
            ])
    
    def _preprocessing_extract_p_values(self):
        '''
        Extract P-values (generating SNP.pvalue file)
        '''
        self._preprocessing_extract_p_values_str = ' '.join([
            os.environ['AWK_EXEC'], 
            "'{print $3,$8}'",
            self._transformed_file,
            '>', 
            os.path.join(self.Output_dir, 'SNP.pvalue'),
        ])
    
    def _write_range_list_file(self):
        '''
        Write range_list file in output directory
        '''
        with open(os.path.join(self.Output_dir, 'range_list'), 'wt') as f:
            for v in self.range_list:
                f.write(f'{v} 0 {v}\n')

    def _run_plink_basic(self):
        '''
        Generate string for basic plink run
        '''
        self._run_plink_basic_str = ' '.join([
            os.environ['PLINK'],
            '--bfile', os.path.join(self.Input_dir, self.Data_prefix + '.QC'),
            '--score', self._transformed_file, ' '.join([str(x) for x in self.score_args]),
            '--q-score-range', os.path.join(self.Output_dir, 'range_list'), os.path.join(self.Output_dir, 'SNP.pvalue'),
            '--extract', os.path.join(self.Output_dir, self.Data_prefix + '.valid.snp'),
            '--out', os.path.join(self.Output_dir, self.Data_prefix)
        ])
    
    def _run_plink_w_stratification(self):
        tmp_str_0 = ' '.join([
            os.environ['PLINK'], 
            '--bfile', os.path.join(self.Input_dir, self.Data_prefix + '.QC'), 
            '--indep-pairwise', ' '.join([str(x) for x in self.strat_indep_pairwise]),
            '--out', os.path.join(self.Output_dir, self.Data_prefix)
        ])
        
        # Then we calculate the first N PCs
        tmp_str_1 = ' '.join([
            os.environ['PLINK'],
            '--bfile', os.path.join(self.Input_dir, self.Data_prefix + '.QC'), 
            '--extract', os.path.join(self.Output_dir, self.Data_prefix) + '.prune.in',
            '--pca', str(self.nPCs),
            '--out', os.path.join(self.Output_dir, self.Data_prefix)
        ])

        self._run_plink_w_stratification_str = '\n'.join([tmp_str_0, tmp_str_1])

    def get_str(self, mode='basic'):
        '''
        Parameters
        ----------
        mode: str
            'basic' or 'stratification'

        Returns: list of str
            line by line statements for analysis
        '''
        mssg = 'mode must be "preprocessing", "basic", or "stratification"'
        assert mode in ['preprocessing', 'basic', 'stratification'], mssg

        if mode == 'preprocessing':
            self._preprocessing_update_effect_size()
            self._preprocessing_clumping()
            self._preprocessing_extract_index_SNP_ID()
            self._preprocessing_extract_p_values()
            statements = [
                self._preprocessing_update_effect_size_str,
                self._preprocessing_clumping_str,
                self._preprocessing_extract_index_SNP_ID_str,
                self._preprocessing_extract_p_values_str,
            ]
            return statements
        elif mode == 'basic':
            self._write_range_list_file()
            self._run_plink_basic()
            return [self._run_plink_basic_str]
        elif mode == 'stratification':
            self._run_plink_w_stratification()
            return [self._run_plink_w_stratification_str]


class PGS_PRSice2(BasePGRS):
    """
    Helper class for setting up PRSice-2 PRS analysis.
    Inherited from class ``BasePGRS``
    """

    def __init__(self,
                 Cov_file='',
                 Eigenvec_file='',
                 Sumstats_file='',
                 Pheno_file='',
                 Input_dir='',
                 Data_prefix='',
                 Output_dir='',
                 nPCs=6,
                 MAF=0.01,
                 INFO=0.8,
                 **kwargs):
        '''
        Parameters
        ----------
        Cov_file: str
            path to covariance file (.cov)
        Eigenvec_file: str
            path to eigenvec file (.eig)
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Input_dir: str
            path containing QC'd .bed, .bim, .fam files
            (</ENV/path/to/data/>)
        Data_prefix: str
            file prefix for QC'd .bed, .bim, .fam files
        Output_dir: str
            path for output files (<path>)
        nPCs: int
            number of Principal Components (PCs) to include
            in covariate generation
        MAF: float
            base-MAF upper threshold value (0.01)
        INFO: float
            base-INFO upper threshold value (0.8)
        **kwargs
            dict of additional keyword/arguments pairs parsed to
            the PRSice.R script (see file for full set of options).
            If the option is only a flag without value, set value
            as None-type or empty string.
        '''
        super().__init__(Sumstats_file=Sumstats_file,
                         Pheno_file=Pheno_file,
                         Input_dir=Input_dir,
                         Data_prefix=Data_prefix,
                         Output_dir=Output_dir,
                         **kwargs)
        # set attributes
        self.Cov_file = Cov_file
        self.Eigenvec_file = Eigenvec_file
        self.nPCs = nPCs
        self.MAF = MAF
        self.INFO = INFO

        # inferred
        self.Covariance_file = os.path.join(
            self.Output_dir,
            self.Data_prefix + '.covariate')

        # check if Output_dir exist. Create if missing.
        if os.path.isdir(self.Output_dir):
            pass
        else:
            os.mkdir(self.Output_dir)

    def _generate_covariance_str(self):
        '''
        Generate string which will be included in job script
        for generating .covariate file combining .cov and .eigenvec
        input files.
        '''
        self._covariance_str = ' '.join([
            os.environ['RSCRIPT'],
            'generate_covariate.R',
            self.Cov_file,
            self.Eigenvec_file,
            self.Covariance_file,
            str(self.nPCs)])

    def _generate_run_str(self):
        '''
        Generate string which will be included in job script
        for running the PRSice2 analasis script
        '''

        self._run_str = ' '.join([
            os.environ['RSCRIPT'], 'PRSice.R',
            '--prsice /usr/bin/PRSice_linux',
            f'--base {self.Sumstats_file}',
            f'--target {os.path.join(self.Input_dir, self.Data_prefix + ".QC")}',
            f'--binary-target F',
            f'--pheno {self.Pheno_file}',
            f'--cov {self.Covariance_file}',
            f'--base-maf MAF:{self.MAF}',
            f'--base-info INFO:{self.INFO}',
            f'--stat OR',
            f'--or',
            f'--out {os.path.join(self.Output_dir, self.Data_prefix)}'
        ])

        # deal with kwargs
        if len(self.kwargs) > 0:
            for key, value in self.kwargs.items():
                self._run_str = ' '.join(
                    [self._run_str, f'--{key} {value or ""}'])

    def get_str(self):
        '''
        Public method to create commands

        Returns
        -------
        list of str
            list of command line statements for analysis run
        '''
        self._generate_covariance_str()
        self._generate_run_str()

        return [self._covariance_str, self._run_str]


if __name__ == '__main__':
    pass
