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
    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        **kwargs
        """
        self.kwargs = kwargs
    
    @abc.abstractmethod
    def get_str(self):
        pass


class PGS_Plink(BasePGRS):
    """
    Helper class for setting up Plink PRS analysis.
    Inherited from class ``BasePGRS``
    """
    def __init__(self,
    ):
        super().__init__(**kwargs)


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
        super().__init__(**kwargs)
        self.Cov_file = Cov_file
        self.Eigenvec_file = Eigenvec_file
        self.Sumstats_file = Sumstats_file
        self.Pheno_file = Pheno_file
        self.Input_dir = Input_dir
        self.Data_prefix = Data_prefix
        self.Output_dir = Output_dir
        self.nPCs = nPCs
        self.MAF = MAF
        self.INFO = INFO

        # inferred
        self.Covariance_file = os.path.join(
            self.Output_dir, 
            self.Data_prefix + '.covariate')

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
                self._run_str = ' '.join([self._run_str, f'--{key} {value or ""}'])

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


def 



if __name__ == '__main__':
    pass
