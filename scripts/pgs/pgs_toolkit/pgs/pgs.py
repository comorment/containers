#!/usr/bin/env python3
# Codes for running polygenic (risk) score calculations using
# containerized applications.
# For usage, cf. this folder's README
#
#
# Related Issue: https://github.com/comorment/containers/issues/17
#
# Supported tools:
# *LDpred2 (auto, inf)
# *Plink
# *PRSice2
#
# Not yet supported tools:
# Lassosum/Lassosum2
# LDpred2 (grid)
# MegaPRS
# PRS-CS
# SBayesR
# SBayesS

import abc
import os
import subprocess
import pandas as pd
import numpy as np


_MAJOR = "1"
_MINOR = "0"
# On main and in a nightly release the patch should be one
# ahead of the last
# released build.
_PATCH = ""
# This is mainly for nightly builds which have the
# suffix ".dev$DATE". See
# https://semver.org/#is-v123-a-semantic-version for the
# semantics.
_SUFFIX = "dev"

VERSION_SHORT = "{0}.{1}".format(_MAJOR, _MINOR)
VERSION = "{0}.{1}.{2}{3}".format(_MAJOR, _MINOR, _PATCH, _SUFFIX)

__version__ = VERSION

MASTHEAD = "*************************************************\n"
MASTHEAD += "* pgs.py: pipeline for PGRS analysis\n"
MASTHEAD += "* Version {V}\n".format(V=__version__)
MASTHEAD += "* (C) 2022 Espen Hagen, Oleksandr Frei, \n"
MASTHEAD += "* Bayram Akdeniz and Alexey A. Shadrin\n"
MASTHEAD += "* Norwegian Centre for Mental Disorders Research\n"
MASTHEAD += "* University of Oslo\n"
MASTHEAD += "* Centre for Bioinformatics / University of Oslo\n"
MASTHEAD += "* GNU General Public License v3\n"
MASTHEAD += "************************************************\n"


def convert_dict_to_str(d, key_prefix='--'):
    '''
    Parameters
    ----------
    d: dict
        key, value pairs
    key_prefix: str
        string prefix for key names. Default: "--"

    Returns
    -------
    str
        string formatted as "--key0 value0 --key1 value1 ...".
        In case values are iterable, it will be formatted
        as "--key0 value0[0] value0[1] ... --key0"
    '''
    cmd = ''
    if len(d) > 0:
        for key, value in d.items():
            if isinstance(value, (tuple, list, np.ndarray)):
                cmd = ' '.join(
                    [cmd,
                     f'{key_prefix}{key} {" ".join([str(v) for v in value])}'
                     ])
            else:
                cmd = ' '.join(
                    [cmd, f'{key_prefix}{key} {str(value) or ""}'])
    return cmd


def extract_variables(df, variables, pheno_dict_map, log):
    cat_vars = [x for x in variables if pheno_dict_map[x] == 'NOMINAL']
    other_vars = ['FID', 'IID'] + \
        [x for x in variables if pheno_dict_map[x] != 'NOMINAL']

    dummies = df[other_vars]
    for var in cat_vars:
        new = pd.get_dummies(df[var], prefix=var)
        dummies = dummies.join(new)

        # drop most frequent variable for ref category
        drop_col = df.groupby([var]).size().idxmax()
        dummies.drop('{}_{}'.format(var, drop_col), axis=1, inplace=True)

        log.log(
            f'Variable {var} will be extracted as dummy, ' +
            f'dropping {drop_col} label (most frequent)')
    return dummies.copy()


def run_call(call):
    '''run subprocess call'''
    print(f'\nevaluating: {call}\n')
    proc = subprocess.run(call, shell=True, check=True)
    assert proc.returncode == 0
    return proc


def post_run_plink(
        output_dir,
        data_prefix,
        best_fit_file='best_fit_prs.csv',
        score_file='test.score'):
    '''
    Read best-fit predictions and export standardized ``test.score`` file
    to output_dir from class PGS_Plink output

    Parameters
    ----------
    output_dir: path
        path to output directory
    data_prefix: str
        standard file name prefix (for .bed, .bim, .fam, etc.)
    best_fit_file: str
        .csv file in ``output_dir`` with best fit Threshold value.
        Default: 'best_fit_prs.csv'
    score_file: str
        test score file in ``output_dir``. Default: 'test.score'
    '''
    best_fit = pd.read_csv(
        os.path.join(
            output_dir,
            best_fit_file))

    f = f"{data_prefix}.{best_fit['Threshold'].values[0]}.profile"
    scores = pd.read_csv(
        os.path.join(output_dir, f),
        delim_whitespace=True,
        usecols=['IID', 'FID', 'SCORE'])
    scores.rename(columns={'SCORE': 'score'}, inplace=True)
    scores.to_csv(os.path.join(output_dir, score_file),
                  sep=' ', index=False)


def post_run_prsice2(output_dir, data_prefix, score_file='test.score'):
    '''
    Read best-fit predictions and export standardized ``test.score`` file
    to output_dir from class PGS_PRSice2 output

    Parameters
    ----------
    output_dir: path
        path to output directory
    data_prefix: str
        standard file name prefix (for .bed, .bim, .fam, etc.)
    score_file: str
        test score file in ``output_dir``. Default: 'test.score'
    '''
    scores = pd.read_csv(
        os.path.join(output_dir, data_prefix + '.best'),
        delim_whitespace=True,
        usecols=['IID', 'FID', 'PRS'])
    scores.rename(columns={'PRS': 'score'}, inplace=True)
    scores.to_csv(os.path.join(output_dir, score_file),
                  sep=' ', index=False)


def df_colums_to_file(
        source_file,
        output_file,
        usecols=None,
        delim_whitespace=True,
        delimiter=None,
        **kwargs):
    '''Extract columns from dataframe (.csv) on file to output_file

    Parameters
    ----------
    source_file: file path
        .csv (or similar) input file read by pandas.read_csv.
    output_file: file path
        output file to be written
    usecols: list of str or None
        columns to read and write
    delim_whitespace: bool
        parsed to df.read_csv. Default: True
    delimiter: None or str
        delimiter. Default: None
    **kwargs
        keyword arguments parsed to pd.read_csv()
    '''
    # read
    df = pd.read_csv(
        source_file,
        usecols=usecols,
        delim_whitespace=delim_whitespace,
        delimiter=delimiter,
        **kwargs)
    # reorder
    if usecols is not None:
        df = df[usecols]
    # write
    df.to_csv(
        output_file,
        sep=' ' if delim_whitespace else delimiter,
        index=False)


def set_env(config):
    '''Function to set environment variables from config.yaml

    Parameters
    ----------
    config: dict
        config dictionary from config.yaml (or similar file)
    '''
    # present working dir
    PWD = os.getcwd()

    ROOT_DIR = config['environ']['ROOT_DIR']
    os.environ.update({'ROOT_DIR': ROOT_DIR})

    for key, val in config['environ_inferred'].items():
        if key in os.environ:
            print('os.environ already contains ' +
                  f'{key} with value {os.environ[key]} - redefining...')
        if os.path.isdir(os.path.expandvars(val)):
            os.environ[key] = os.path.expandvars(val)
        else:
            mssg = (f'Path {os.path.expandvars(val)} for variable {key} ' +
                    'does not exist. Revise config.yaml!')
            raise FileNotFoundError(mssg)

    print(
        '\nenvironment variables in use:\n',
        '\n'.join(f'{key}: {val}' for key, val in os.environ.items()
                  if key in dict(**config['environ'],
                                 **config['environ_inferred']).keys()),
        '\n')

    # set SINGULARITY_BIND to mount volumes in containers:
    os.environ['SINGULARITY_BIND'] = ','.join(
        [f'{os.path.expandvars(item)}:/{key}'
            for key, item in config['SINGULARITY_BIND'].items()
         ])
    print('mounted volumes on containers:\n',
          os.environ['SINGULARITY_BIND'], '\n')

    # Executables in different containers
    SIF = os.environ['SIF']
    os.environ.update(
        dict(
            BASH=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif bash",  # noqa: E501
            GUNZIP=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif gunzip",  # noqa: E501
            GZIP=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif gzip",  # noqa: E501
            AWK=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif awk",  # noqa: E501
            RSCRIPT=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/r.sif Rscript",  # noqa: E501
            PLINK=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif plink",  # noqa: E501
            PRSICE=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/gwas.sif PRSice_linux",  # noqa: E501
            PYTHON=f"singularity exec --home={PWD}:/home --cleanenv {SIF}/python3.sif python3",  # noqa: E501
        ))


class BasePGS(abc.ABC):
    """Base PGRS object declaration with some
    shared properties for subclassing
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 pheno_file='/REF/examples/prsice2/EUR.height',
                 phenotype='Height',
                 phenotype_class='CONTINUOUS',
                 geno_file_prefix='/REF/examples/prsice2/EUR',
                 output_dir='qc-output',
                 **kwargs):
        """
        Parameters
        ----------
        sumstats_file: str
            summary statistics file (.gz)
        pheno_file: str
            phenotype file (for instance, .height)
        phenotype: str or None
            if not ``None``, phenotype name (must be a column
            header in ``pheno_file``)
        phenotype_class: str
            phenotype class, either 'CONTINUOUS' or 'BINARY'
        geno_file_prefix: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        output_dir: str
            path for output files (<path>)
        **kwargs

        Attributes
        ----------
        data_prefix: str
            file name prefix of .bed, .bim, etc. files
        """
        # set attributes
        self.sumstats_file = sumstats_file
        self.pheno_file = pheno_file
        self.phenotype = phenotype
        self.phenotype_class = phenotype_class
        self.geno_file_prefix = geno_file_prefix
        self.output_dir = output_dir

        self.kwargs = kwargs

        # inferred
        self.data_prefix = os.path.split(self.geno_file_prefix)[-1]

        # create output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @abc.abstractmethod
    def get_str(self):
        '''
        Required public method
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def get_model_evaluation_str(self,
                                 eigenvec_file=None,
                                 nPCs=None,
                                 covariate_file=None):
        '''
        Required public method
        '''
        raise NotImplementedError

    def _generate_eigenvec_eigenval_files(self, nPCs=6):
        '''
        Return string which can be included in job script for 
        generating .eigenvec and .eigenval files in the output directory
        using PLINK
        
        Parameters
        ----------
        nPCs: int
            number of PCs to account for
        '''
        command = ' '.join([
            '$PLINK',
            '--bfile', self.geno_file_prefix,
            '--pca', str(nPCs),
            '--out', os.path.join(self.output_dir, self.data_prefix)
        ])
        return command


class PGS_Plink(BasePGS):
    """
    Helper class for setting up Plink PRS analysis.
    Inherited from class ``BasePGS``
    """

    def __init__(self,
                 sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 pheno_file='/REF/examples/prsice2/EUR.height',
                 phenotype='Height',
                 phenotype_class='CONTINUOUS',
                 geno_file_prefix='QC_data/EUR',
                 output_dir='PGS_plink',
                 covariate_file='/REF/examples/prsice2/EUR.cov',
                 eigenvec_file='/REF/examples/prsice2/EUR.eigenvec',
                 clump_p1=1,
                 clump_r2=0.1,
                 clump_kb=250,
                 clump_snp_field='SNP',
                 clump_field='P',
                 range_list=None,
                 strat_indep_pairwise=None,
                 nPCs=6,
                 score_args=None,
                 **kwargs):
        '''
        Parameters
        ----------
        sumstats_file: str
            summary statistics file (.gz)
        pheno_file: str
            phenotype file (for instance, .height)
        phenotype: str or None
            if not ``None``, phenotype name (must be a column
            header in ``pheno_file``)
        phenotype_class: str
            phenotype class, either 'CONTINUOUS' or 'BINARY'
        geno_file_prefix: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        output_dir: str
            path for output files (<path>)
        covariate_file: str
            path to covariance file (.cov)
        eigenvec_file: str or None
            None, or path to eigenvec file (.eigenvec)
        clump_p1: float
            plink --clump-p1 parameter value (default: 1)
        clump_r2: float
            plink --clump-r2 parameter value (default: 0.1)
        clump_kb: float
            plink --clump-r2 parameter value (default: 250)
        clump_snp_field: str
            plink --clump-snp-field parameter value (default: 'SNP')
        clump_field: str
            plink --clump-field parameter value (default: 'P')
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

        Attributes
        ----------
        data_prefix: str
            file name prefix of .bed, .bim, etc. files

        '''
        super().__init__(sumstats_file=sumstats_file,
                         pheno_file=pheno_file,
                         phenotype=phenotype,
                         phenotype_class=phenotype_class,
                         geno_file_prefix=geno_file_prefix,
                         output_dir=output_dir,
                         **kwargs)
        # set attributes
        if covariate_file is None or eigenvec_file is None:
            self.covariate_file = os.path.join(
                self.output_dir,
                self.data_prefix + '.')
            self.eigenvec_file = os.path.join(
                self.output_dir,
                self.data_prefix + '.eigenvec')
        else:
            for fpath in [covariate_file, eigenvec_file]:
                try:
                    assert os.path.isfile(fpath)
                except AssertionError:
                    print(f'file {fpath} may not exist\n')

            self.covariate_file = covariate_file
            self.eigenvec_file = eigenvec_file

        if range_list is None:
            range_list = [0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
        if strat_indep_pairwise is None:
            strat_indep_pairwise = [250, 50, 0.25]
        if score_args is None:
            score_args = [3, 4, 12, 'header']

        # clumping params
        self.clump_p1 = clump_p1
        self.clump_r2 = clump_r2
        self.clump_kb = clump_kb
        self.clump_snp_field = clump_snp_field
        self.clump_field = clump_field

        # range of p-values on interval (0, p-value)
        self.range_list = range_list

        # stratification param
        self.strat_indep_pairwise = strat_indep_pairwise

        # number of principal componentes
        self.nPCs = nPCs

        self.score_args = score_args

        # inferred
        self._transformed_file = os.path.join(
            output_dir,
            '.'.join(os.path.split(
                self.sumstats_file)[-1].split('.')[:-1]
                + ['transformed']))
        self._range_list_file = os.path.join(self.output_dir, 'range_list')

    def _preprocessing_update_effect_size(self):
        '''
        Return string which can be included in job script
        for generating file with updated effect size
        '''
        command = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'update_effect_size.R'),
            self.sumstats_file,
            self._transformed_file])

        return command

    def _preprocessing_clumping(self, update_effect_size):
        '''
        Generate string which can be included in job script
        for clumping (generating .clumped file)

        Parameters
        ----------
        update_effect_size: bool
            if False, use sumstats_file for --clump param
        Returns
        -------
        str
        '''
        command = ' '.join([
            '$PLINK',
            '--bfile',
            self.geno_file_prefix,
            '--clump-p1', str(self.clump_p1),
            '--clump-r2', str(self.clump_r2),
            '--clump-kb', str(self.clump_kb),
            '--clump',
            (self._transformed_file
                if update_effect_size else self.sumstats_file),
            '--clump-snp-field', self.clump_snp_field,  #
            '--clump-field', self.clump_field,
            '--threads', str(self.kwargs['threads']),
            '--out', os.path.join(self.output_dir, self.data_prefix)
        ])

        return command

    def _preprocessing_extract_index_SNP_ID(self):
        '''
        Extract index SNP ID to (generating .valid.snp file)

        Returns
        -------
        str
        '''
        command = ' '.join([
            '$AWK',
            "'NR!=1{print $3}'",
            os.path.join(self.output_dir, self.data_prefix + '.clumped'),
            '>',
            os.path.join(self.output_dir, self.data_prefix + '.valid.snp'),
        ])

        return command

    def _preprocessing_extract_p_values(self, update_effect_size):
        '''
        Extract P-values (generating SNP.pvalue file)

        Parameters
        ----------
        update_effect_size: bool
            if False, use sumstats_file as input

        Returns
        -------
        str
        '''
        command = ''
        if not update_effect_size:
            # unzip Sumstats file to output_dir allowing parsing
            # it to Plink using --score
            command += ' '.join([
                '$PYTHON',
                '-c',
                f"""'from pgs import pgs; pgs.df_colums_to_file("{self.sumstats_file}", "{self._transformed_file}")'"""  # noqa: 501
                '\n'
            ])
        command += ' '.join([
            '$PYTHON',
            '-c',
            f"""'from pgs import pgs; pgs.df_colums_to_file("{self._transformed_file}", "{os.path.join(self.output_dir, self.clump_snp_field + ".pvalue")}", ["{self.clump_snp_field}", "{self.clump_field}"])'"""  # noqa: 501
        ])
        return command

    def _write_range_list_file(self):
        '''
        Write range_list file in output directory
        '''
        with open(self._range_list_file, 'wt', encoding='utf-8') as f:
            for val in self.range_list:
                f.write(f'{val} 0 {val}\n')

    def _run_plink_basic(self):
        '''
        Generate string for basic plink run

        Returns
        -------
        str
        '''
        command = ' '.join([
            '$PLINK',
            '--bfile',
            self.geno_file_prefix,
            '--score',
            self._transformed_file,
            ' '.join([str(x) for x in self.score_args]),
            '--q-score-range',
            self._range_list_file,
            os.path.join(self.output_dir, self.clump_snp_field + '.pvalue'),
            '--extract',
            os.path.join(self.output_dir, self.data_prefix + '.valid.snp'),
            '--threads', str(self.kwargs['threads']),
            '--out',
            os.path.join(self.output_dir, self.data_prefix)
        ])

        return command

    def _run_plink_w_stratification(self):
        '''
        Account for (population) stratification using PCs,
        creating .eigenvec file.
        If class parameter eigenvec_file is set and file exist,
        this function will not return commands to compute
        a new eigenvec file.

        Returns
        -------
        list of str
        '''
        # skip this step if eigenvec_file argument is specified and file exist.
        if os.path.isfile(self.eigenvec_file):
            print(f'eigenvec_file {self.eigenvec_file} exists. ' +
                  'To get instructions to compute, set eigenvec_file=None')
            # check that number of PCs match with class input
            eigenvec_df = pd.read_csv(
                self.eigenvec_file,
                delim_whitespace=True, header=None, nrows=1)
            nPCs = eigenvec_df.columns.size - 2
            if nPCs != self.nPCs:
                mssg = (
                    f'The number of PCs in {self.eigenvec_file} nPCs={nPCs} ' +
                    f'while <pgs.PGS_Plink instance>.nPCs={self.nPCs}. ' +
                    f'Inst. class pgs.PGS_Plink w. nPCs={self.eigenvec_file}' +
                    ' (confer config.yaml file with settings).')
                raise ValueError(mssg)
            return ''
        else:
            # First, perform pruning
            tmp_str_0 = ' '.join([
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--indep-pairwise',
                ' '.join([str(x) for x in self.strat_indep_pairwise]),
                '--out', os.path.join(self.output_dir, self.data_prefix)
            ])

            # Then we calculate the first N PCs
            tmp_str_1 = ' '.join([
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--extract',
                os.path.join(self.output_dir, self.data_prefix) + '.prune.in',
                '--pca', str(self.nPCs),
                '--out', os.path.join(self.output_dir, self.data_prefix)
            ])

            return '\n'.join([tmp_str_0, tmp_str_1])

    def _find_best_fit_pgs(self):
        '''
        Generate command for running ``Rscripts/find_best_fit_pgs.R`` script,
        producing

        Returns
        -------
        str
        '''
        command = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'find_best_fit_pgs.R'),
            '--phenotype-file', self.pheno_file,
            '--eigenvec-file', self.eigenvec_file,
            '--cov-file', self.covariate_file,
            '--phenotype', self.phenotype,
            '--data-prefix', os.path.join(self.output_dir, self.data_prefix),
            '--thresholds', ','.join([str(x) for x in self.range_list]),
            '--nPCs', str(self.nPCs),
            '--results-file', os.path.join(self.output_dir, 'best_fit_prs.csv')
        ])

        return command

    def _generate_post_run_str(self):
        arg = ','.join([f'"{self.output_dir}"', f'"{self.data_prefix}"'])
        cmd = ' '.join([
            '$PYTHON', '-c',
            f"""'from pgs.pgs import post_run_plink; post_run_plink({arg})'"""
        ])
        return cmd

    def get_model_evaluation_str(self):
        '''
        Return callable string for fitting a simple
        linear model between PGS score and phenotype data
        using R stats::lm, printing stats::lm.fit.summary output
        to file

        Returns
        -------
        str
        '''
        cmd = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'evaluate_model.R'),
            '--pheno-file', self.pheno_file,
            '--phenotype', self.phenotype,
            '--phenotype-class', self.phenotype_class,
            '--score-file', os.path.join(self.output_dir, 'test.score'),
            '--nPCs', f'{self.nPCs}',
            '--eigenvec-file', self.eigenvec_file,
            '--covariate-file', self.covariate_file,
            '--out', os.path.join(self.output_dir, 'test_summary')
        ])
        return cmd

    def get_str(self, mode='basic', update_effect_size=False):
        '''
        Parameters
        ----------
        mode: str
            'basic' or 'stratification'
        update_effect_size: bool
            if True, compute PGRS using OR

        Returns:
        --------
        list of str
            line by line statements for analysis
        '''
        mssg = 'mode must be "preprocessing", "basic", or "stratification"'
        assert mode in ['preprocessing', 'basic', 'stratification'], mssg
        commands = []

        if not os.path.isfile(self.eigenvec_file):
            commands += [self._generate_eigenvec_eigenval_files(nPCs=self.nPCs)]

        if mode == 'preprocessing':
            commands += [
                (self._preprocessing_update_effect_size()
                    if update_effect_size else None),
                self._preprocessing_clumping(update_effect_size),
                self._preprocessing_extract_index_SNP_ID(),
                self._preprocessing_extract_p_values(update_effect_size)]
            return list(filter(lambda item: item is not None, commands))
        elif mode in ['basic', 'stratification']:
            self._write_range_list_file()
            commands += [self._run_plink_basic()]
            if mode == 'basic':
                commands += [
                    self._find_best_fit_pgs(),
                    self._generate_post_run_str()]
            elif mode == 'stratification':
                commands += [self._run_plink_w_stratification(),
                             self._find_best_fit_pgs(),
                             self._generate_post_run_str()]
            return commands
        else:
            raise NotImplementedError


class PGS_PRSice2(BasePGS):
    """
    Helper class for setting up PRSice-2 PRS analysis.
    Inherited from class ``BasePGS``
    """

    def __init__(self,
                 sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 pheno_file='/REF/examples/prsice2/EUR.height',
                 phenotype='Height',
                 phenotype_class='CONTINUOUS',
                 geno_file_prefix='/REF/examples/prsice2/EUR',
                 output_dir='PGS_prsice2',
                 covariate_file='/REF/examples/prsice2/EUR.cov',
                 eigenvec_file='/REF/examples/prsice2/EUR.eigenvec',
                 nPCs=6,
                 MAF=0.01,
                 INFO=0.8,
                 **kwargs):
        '''
        Parameters
        ----------
        sumstats_file: str
            summary statistics file (.gz)
        pheno_file: str
            phenotype file (for instance, .height)
        phenotype: str or None
            if not ``None``, phenotype name (must be a column
            header in ``pheno_file``)
        phenotype_class: str
            phenotype class, either 'CONTINUOUS' or 'BINARY'
        geno_file_prefix: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        output_dir: str
            path for output files (<path>)
        covariate_file: str or None
            path to covariate file (.cov)
        eigenvec_file: str or None
            path to eigenvec file (.eig) with PCs
        nPCs: int
            number of Principal Components (PCs) to include
            in covariate generation
        MAF: float
            base-MAF upper threshold value (0.01)
        INFO: float
            base-INFO upper threshold value (0.8)
        **kwargs
            dict of additional keyword/arguments pairs parsed to
            the Rscripts/PRSice.R script (see file for full set of options).
            If the option is only a flag without value, set value
            as None-type or empty string.

        Attributes
        ----------
        data_prefix: str
            file name prefix of .bed, .bim, etc. files
        '''
        super().__init__(sumstats_file=sumstats_file,
                         pheno_file=pheno_file,
                         phenotype=phenotype,
                         phenotype_class=phenotype_class,
                         geno_file_prefix=geno_file_prefix,
                         output_dir=output_dir,
                         **kwargs)
        # set attributes
        self.covariate_file = covariate_file
        self.eigenvec_file = eigenvec_file
        self.nPCs = nPCs
        self.MAF = MAF
        self.INFO = INFO

        # deal with covariate file, generate from covariate_file and eigenvec_file if
        # needed
        if 'cov' in self.kwargs.keys():
            self._Covariate_file = self.kwargs.pop('cov')
            print(f'cov={self._Covariate_file} argument found in kwargs.',
                  'eigenvec_file and covariate_file args will be ignored.')
        else:
            if self.covariate_file is not None and self.eigenvec_file is not None:
                self._Covariate_file = os.path.join(
                    self.output_dir,
                    self.data_prefix + '.covariate')
            else:
                self._Covariate_file = None

    def _generate_covariate_str(self):
        '''
        Generate string which will be included in job script
        for generating .covariate file combining .cov and .eigenvec
        input files.

        Returns
        -------
        str
        '''
        command = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'generate_covariate.R'),
            '--cov-file', self.covariate_file,
            '--eigenvec-file', self.eigenvec_file,
            '--covariate-file', self._Covariate_file,
            '--nPCs', str(self.nPCs)])

        return command

    def _generate_run_str(self):
        '''
        Generate string which will be included in job script
        for running the PRSice2 analysis script

        Returns
        -------
        str
        '''
        target = self.geno_file_prefix
        binary_target = "T" if self.phenotype_class == "BINARY" else "F"
        command = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'PRSice.R'),
            '--prsice /usr/bin/PRSice_linux',
            f'--base {self.sumstats_file}',
            f'--target {target}',
            f'--binary-target {binary_target}',
            f'--pheno {self.pheno_file}',
            f'--pheno-col {self.phenotype}',
            f'--out {os.path.join(self.output_dir, self.data_prefix)}'
        ])
        if self._Covariate_file is not None:
            cmd0 = self._generate_covariate_str()
        else:
            cmd0 = ''
        command = '\n'.join([
            cmd0, command
        ])

        # deal with kwargs
        if len(self.kwargs) > 0:
            for key, value in self.kwargs.items():
                command = ' '.join(
                    [command, f'--{key} {value or ""}'])

        return command

    def _generate_post_run_str(self):
        arg = ','.join([f'"{self.output_dir}"', f'"{self.data_prefix}"'])
        cmd = ' '.join([
            '$PYTHON', '-c',
            f"""'from pgs.pgs import post_run_prsice2; post_run_prsice2({arg})'"""  # noqa: E501
        ])
        return cmd

    def get_model_evaluation_str(self):
        '''
        Return callable string for fitting a simple
        linear model between PGS score and phenotype data
        using R stats::lm, printing stats::lm.fit.summary output
        to file

        Returns
        -------
        str

        '''
        cmd = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'evaluate_model.R'),
            '--pheno-file', self.pheno_file,
            '--phenotype', self.phenotype,
            '--phenotype-class', self.phenotype_class,
            '--score-file', os.path.join(self.output_dir, 'test.score'),
            '--nPCs', f'{self.nPCs}',
            '--eigenvec-file', self.eigenvec_file,
            '--covariate-file', self.covariate_file,
            '--out', os.path.join(self.output_dir, 'test_summary')
        ])
        return cmd
    
    def get_str(self):
        '''
        Public method to create commands

        Returns
        -------
        list of str
            list of command line statements for analysis run
        '''
        commands = []
        if not os.path.isfile(self.eigenvec_file):
            commands += [self._generate_eigenvec_eigenval_files(nPCs=self.nPCs)]

        if self._Covariate_file is not None:
            commands += [self._generate_covariate_str()]

        return commands + [self._generate_run_str(), self._generate_post_run_str()]


class PGS_LDpred2(BasePGS):
    """
    Helper class for setting up LDpred2 PRS analysis.
    Inherited from class ``BasePGS``
    """

    def __init__(self,
                 sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 pheno_file='/REF/examples/prsice2/EUR.height',
                 phenotype='Height',
                 phenotype_class='CONTINUOUS',
                 geno_file_prefix='/REF/examples/prsice2/EUR',
                 output_dir='PGS_ldpred2_inf',
                 method='auto',
                 fileGenoRDS='EUR.rds',
                 **kwargs):
        '''
        Parameters
        ----------
        sumstats_file: str
            summary statistics file (.gz)
        pheno_file: str
            phenotype file (for instance, .height)
        phenotype: str or None
            if not ``None``, phenotype name (must be a column
            header in ``pheno_file``)
        phenotype_class: str
            phenotype class, either 'CONTINUOUS' or 'BINARY'
        geno_file_prefix: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        output_dir: str
            path for output files (<path>)
        method: str
            LDpred2 method, either "auto" (default) or 
            "inf" for infinitesimal
        fileGenoRDS: str
            base name for .rds file output

        **kwargs
            dict of additional keyword/arguments pairs parsed to
            the ``$LDPRED2_SCRIPTS/ldpred2.R`` script
            (see file for full set of options).
            If the option is only a flag without value, set value
            as None-type or empty string.
        '''
        super().__init__(sumstats_file=sumstats_file,
                         pheno_file=pheno_file,
                         phenotype=phenotype,
                         phenotype_class=phenotype_class,
                         geno_file_prefix=geno_file_prefix,
                         output_dir=output_dir,
                         **kwargs)

        # set attributes
        self.method = method
        self.fileGenoRDS = fileGenoRDS
        # self.file_keep_snps = file_keep_snps

        # inferred
        self._fileGeno = self.geno_file_prefix + '.bed'
        self._file_out = os.path.join(self.output_dir, 'test.score')

    def _run_createBackingFile(self):
        # Convert plink files to bigSNPR backingfile(s) (.rds/.bk)
        command = ' '.join([
            '$RSCRIPT',
            os.path.join('/ldpred2_scripts', 'createBackingFile.R'),
            '--file-input', self._fileGeno,
            '--file-output', self.fileGenoRDS
        ])
        return command

    def generate_eigenvec_eigenval_files(self, nPCs=6):
        '''
        Return string which can be included in job script for 
        generating .eigenvec and .eigenval files in the output directory
        using PLINK

        Parameters
        ----------
        nPCs: int
            number of PCs to account for
        '''
        return super()._generate_eigenvec_eigenval_files(nPCs)

    def get_model_evaluation_str(self, 
                                 eigenvec_file=None, 
                                 nPCs=None, 
                                 covariate_file=None):
        '''
        Return callable string for fitting a simple
        linear model between PGS score and phenotype data
        using R stats::lm, printing stats::lm.fit.summary output
        to file

        Parameters
        ----------
        eigenvec_file: path
            path to file with PCs (no header, columns FID, IID, PC1, PC2, ...)
        nPCs: int
            number of PCs to account for
        covariate_file: path
            path to file with covariates
            (header, columns FID, IID, <covariate>)

        Returns
        -------
        str
        '''
        cmd = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'evaluate_model.R'),
            '--pheno-file', self.pheno_file,
            '--phenotype', self.phenotype,
            '--phenotype-class', self.phenotype_class,
            '--score-file', os.path.join(self.output_dir, 'test.score'),
            '--nPCs', f'{nPCs}',
            '--eigenvec-file', eigenvec_file,
            '--covariate-file', covariate_file,
            '--out', os.path.join(self.output_dir, 'test_summary')
        ])
        return cmd

    def get_str(self, create_backing_file=True):
        '''
        Public method to create commands

        Parameters
        ----------
        create_backing_file: bool
            if True (default), prepend statements for running the
            ``$LDPRED2_SCRIPTS/createBackingFile.R`` script,
            generating ``fileGenoRDS``

        Returns
        -------
        list of str
            list of command line statements for analysis run
        '''
        tmp_cmd1 = ' '.join([
            '$RSCRIPT',
            os.path.join('/ldpred2_scripts', 'ldpred2.R'),
            '--ldpred-mode', self.method,
            '--geno-file-rds', self.fileGenoRDS,
            '--sumstats', self.sumstats_file,
            '--out', self._file_out,
        ])
        # if self.file_keep_snps is not None:
        #     tmp_cmd1 = ' '.join(
        #         [tmp_cmd1, '--file-keep-snps', self.file_keep_snps])

        # deal with kwargs
        if len(self.kwargs) > 0:
            tmp_cmd1 = ' '.join([tmp_cmd1, convert_dict_to_str(self.kwargs)])

        # return calls
        if create_backing_file:
            tmp_cmd0 = self._run_createBackingFile()
            return [tmp_cmd0, tmp_cmd1]
        else:
            return [tmp_cmd1]


class Standard_GWAS_QC(BasePGS):
    '''
    Helper class for common GWAS QC.
    Inherited from class ``BasePGS``

    Based on the tutorial
    https://choishingwan.github.io/PRS-Tutorial/target/#qc-of-target-data
    '''

    def __init__(self,
                 sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 pheno_file='/REF/examples/prsice2/EUR.height',
                 geno_file_prefix='/REF/examples/prsice2/EUR',
                 output_dir='QC_data',
                 phenotype='Height',
                 data_postfix='.QC',
                 QC_target_kwargs={'maf': 0.01, 'hwe': 1e-6,
                                   'geno': 0.01, 'mind': 0.01},
                 QC_prune_kwargs={'indep-pairwise': [200, 50, 0.25]},
                 QC_relatedness_prune_kwargs={'rel-cutoff': 0.125},
                 **kwargs):
        '''
        Parameters
        ----------
        sumstats_file: str
            summary statistics file (.gz)
        pheno_file: str
            phenotype file (for instance, .height)
        geno_file_prefix: str
            path to (raw) .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        output_dir: str
            path for output files (<path>)
        phenotype: str
            default: 'Height'
        data_postfix: str
            default: '.QC'
        QC_target_kwargs: dict
            key, values
        QC_prune_kwargs: dict
            keys, values
        QC_relatedness_prune_kwargs: dict
            keys, values
        **kwargs
        '''
        super().__init__(sumstats_file=sumstats_file,
                         pheno_file=pheno_file,
                         geno_file_prefix=geno_file_prefix,
                         output_dir=output_dir,
                         **kwargs)
        self.phenotype = phenotype
        self.data_postfix = data_postfix
        self.QC_target_kwargs = QC_target_kwargs
        self.QC_prune_kwargs = QC_prune_kwargs
        self.QC_relatedness_prune_kwargs = QC_relatedness_prune_kwargs

        # create output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_str(self):
        '''
        Standard GWAS QC
        '''
        command = []
        # Filter summary statistics file, zip output.
        cmd = ' '.join(['$GUNZIP',
                        '-c',
                        self.sumstats_file,
                        '|\\\n',
                        '$AWK',
                        "'NR==1 || ($11 > 0.01) && ($10 > 0.8) {print}'",
                        '|\\\n',
                        '$GZIP',
                        '->',
                        os.path.join(self.output_dir,
                                     self.phenotype + '.gz')])
        command += [cmd]

        # Remove duplicates
        cmd = ' '.join(['$GUNZIP',
                        '-c',
                        os.path.join(self.output_dir,
                                     self.phenotype + '.gz'),
                        '|\\\n',
                        '$AWK',
                        "'{seen[$3]++; if(seen[$3]==1){ print}}'",
                        '|\\\n',
                        '$GZIP',
                        '->',
                        os.path.join(self.output_dir,
                                     self.phenotype + '.nodup.gz')])
        command += [cmd]

        # Retain nonambiguous SNPs:
        cmd = ' '.join(
            [
                '$GUNZIP',
                '-c',
                os.path.join(
                    self.output_dir,
                    self.phenotype +
                    '.nodup.gz'),
                '|\\\n',
                '$AWK',
                """'!( ($4=="A" && $5=="T") ||  ($4=="T" && $5=="A") || ($4=="G" && $5=="C") || ($4=="C" && $5=="G")) {print}'""",  # noqa: E501
                '|\\\n',
                '$GZIP',
                '->',
                os.path.join(
                    self.output_dir,
                    self.phenotype +
                    self.data_postfix + '.gz')])
        command += [cmd]

        # QC target data
        # Modified from
        # https://choishingwan.github.io/PRS-Tutorial/target/#qc-of-target-data
        cmd = ' '.join([
            '$PLINK',
            '--bfile',
            self.geno_file_prefix,
            '--write-snplist',
            '--make-just-fam',
            '--out',
            os.path.join(
                self.output_dir,
                self.data_prefix) + self.data_postfix
        ])
        cmd = ' '.join([cmd, convert_dict_to_str(self.QC_target_kwargs)])
        command += [cmd]

        # Prune to remove highly correlated SNPs
        cmd = ' '.join(
            [
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--keep',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.fam'),
                '--extract',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.snplist'),
                '--out',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix),
            ])
        cmd = ' '.join([cmd, convert_dict_to_str(self.QC_prune_kwargs)])
        command += [cmd]

        # Compute heterozygosity rates, generating the EUR.QC.het file:
        cmd = ' '.join(
            [
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--extract',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.prune.in'),
                '--keep',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.fam'),
                '--het',
                '--out',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix)])
        command += [cmd]

        # remove individuals with F coefficients that are more than 3 standard
        # deviation (SD) units from the mean in ``R``:
        cmd = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'create_valid_sample.R'),
            '--file-input',
            os.path.join(
                self.output_dir,
                self.data_prefix + self.data_postfix + '.het'),
            '--file-output',
            os.path.join(
                self.output_dir,
                self.data_prefix + '.valid.sample'),
        ])
        command += [cmd]

        # strand-flipping the alleles to their complementary alleles
        cmd = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'strand_flipping.R'),
            '--bim-file', self.geno_file_prefix + '.bim',
            '--QC-file',
            os.path.join(self.output_dir,
                         self.phenotype + self.data_postfix + '.gz'),
            '--QC-snplist-file',
            os.path.join(self.output_dir,
                         self.data_prefix + self.data_postfix + '.snplist'),
            '--ai-file',
            os.path.join(self.output_dir, self.data_prefix + '.a1'),
            '--mismatch-file',
            os.path.join(self.output_dir, self.data_prefix + '.mismatch')
        ])
        command += [cmd]

        # Sex-check pre-pruning, generating EUR.QC.sexcheck:
        cmd = ' '.join(
            [
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--extract',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.prune.in'),
                '--keep',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    '.valid.sample'),
                '--check-sex',
                '--out',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix)])
        command += [cmd]

        # Assign individuals as biologically male if F-statistic is > 0.8;
        # biologically female if F < 0.2:
        cmd = ' '.join([
            '$RSCRIPT',
            os.path.join('Rscripts', 'create_QC_valid.R'),
            '--file-valid',
            os.path.join(
                self.output_dir,
                self.data_prefix + '.valid.sample'),
            '--file-sexcheck',
            os.path.join(
                self.output_dir,
                self.data_prefix + self.data_postfix + '.sexcheck'),
            '--file-output',
            os.path.join(
                self.output_dir,
                self.data_prefix + self.data_postfix + '.valid')
        ])
        command += [cmd]

        # Relatedness pruning of individuals that have a first or second degree
        # relative
        cmd = ' '.join(
            [
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--extract',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.prune.in'),
                '--keep',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix + '.valid'),
                '--out',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix)])
        cmd = ' '.join([cmd, convert_dict_to_str(
            self.QC_relatedness_prune_kwargs)])
        command += [cmd]

        # Generate a QC'ed data set, creating .ai and .mismatch files:
        cmd = ' '.join(
            [
                '$PLINK',
                '--bfile',
                self.geno_file_prefix,
                '--make-bed',
                '--keep',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix +
                    '.rel.id'),
                '--out',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix),
                '--extract',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    self.data_postfix +
                    '.snplist'),
                '--a1-allele',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    '.a1'),
                '--exclude',
                os.path.join(
                    self.output_dir,
                    self.data_prefix +
                    '.mismatch')])
        command += [cmd]

        return command


if __name__ == '__main__':
    pass
