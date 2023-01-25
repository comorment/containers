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


def post_run_plink(
        Output_dir,
        Data_prefix,
        best_fit_file='best_fit_prs.csv',
        score_file='test.score'):
    '''
    Read best-fit predictions and export standardized ``test.score`` file
    to Output_dir from class PGS_Plink output

    Parameters
    ----------
    Output_dir: path
        path to output directory
    Data_prefix: str
        standard file name prefix (for .bed, .bim, .fam, etc.)
    best_fit_file: str
        .csv file in ``Output_dir`` with best fit Threshold value.
        Default: 'best_fit_prs.csv'
    score_file: str
        test score file in ``Output_dir``. Default: 'test.score'
    '''
    best_fit = pd.read_csv(
        os.path.join(
            Output_dir,
            best_fit_file))

    f = f"{Data_prefix}.{best_fit['Threshold'].values[0]}.profile"
    scores = pd.read_csv(
        os.path.join(Output_dir, f),
        delim_whitespace=True,
        usecols=['IID', 'FID', 'SCORE'])
    scores.rename(columns={'SCORE': 'score'}, inplace=True)
    scores.to_csv(os.path.join(Output_dir, score_file),
                  sep=' ', index=False)


def post_run_prsice2(Output_dir, Data_prefix, score_file='test.score'):
    '''
    Read best-fit predictions and export standardized ``test.score`` file
    to Output_dir from class PGS_PRSice2 output

    Parameters
    ----------
    Output_dir: path
        path to output directory
    Data_prefix: str
        standard file name prefix (for .bed, .bim, .fam, etc.)
    score_file: str
        test score file in ``Output_dir``. Default: 'test.score'
    '''
    scores = pd.read_csv(
        os.path.join(Output_dir, Data_prefix + '.best'),
        delim_whitespace=True,
        usecols=['IID', 'FID', 'PRS'])
    scores.rename(columns={'PRS': 'score'}, inplace=True)
    scores.to_csv(os.path.join(Output_dir, 'test.score'),
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


class BasePGS(abc.ABC):
    """Base PGRS object declaration with some
    shared properties for subclassing
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 Sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 Pheno_file='/REF/examples/prsice2/EUR.height',
                 Phenotype='Height',
                 Geno_file='/REF/examples/prsice2/EUR',
                 Output_dir='qc-output',
                 **kwargs):
        """
        Parameters
        ----------
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Phenotype: str
            phenotype name (must be a column header in ``Pheno_file``)
        Geno_file: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        Data_prefix: str
            file prefix for QC'd .bed, .bim, .fam files
        Output_dir: str
            path for output files (<path>)
        **kwargs

        Attributes
        ----------
        Data_prefix: str
            file name prefix of .bed, .bim, etc. files
        """
        # set attributes
        self.Sumstats_file = Sumstats_file
        self.Pheno_file = Pheno_file
        self.Phenotype = Phenotype
        self.Geno_file = Geno_file
        self.Output_dir = Output_dir

        self.kwargs = kwargs

        # inferred
        self.Data_prefix = os.path.split(self.Geno_file)[-1]

        # check if Output_dir exist. Create if missing.
        if os.path.isdir(self.Output_dir):
            pass
        else:
            os.mkdir(self.Output_dir)

    @abc.abstractmethod
    def get_str(self):
        '''
        Required public method
        '''
        raise NotImplementedError


class PGS_Plink(BasePGS):
    """
    Helper class for setting up Plink PRS analysis.
    Inherited from class ``BasePGS``
    """

    def __init__(self,
                 Sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 Pheno_file='/REF/examples/prsice2/EUR.height',
                 Phenotype='Height',
                 Geno_file='QC_data/EUR',
                 Output_dir='PGS_plink',
                 Cov_file='/REF/examples/prsice2/EUR.cov',
                 Eigenvec_file='/REF/examples/prsice2/EUR.eigenvec',
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
        Phenotype: str
            phenotype name (must be a column header in ``Pheno_file``)
        Geno_file: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        Output_dir: str
            path for output files (<path>)
        Cov_file: str
            path to covariance file (.cov)
        Eigenvec_file: str or None
            None, or path to eigenvec file (.eigenvec)
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

        Attributes
        ----------
        Data_prefix: str
            file name prefix of .bed, .bim, etc. files

        '''
        super().__init__(Sumstats_file=Sumstats_file,
                         Pheno_file=Pheno_file,
                         Phenotype=Phenotype,
                         Geno_file=Geno_file,
                         Output_dir=Output_dir,
                         **kwargs)
        # set attributes
        if Cov_file is None or Eigenvec_file is None:
            self.Cov_file = os.path.join(
                self.Output_dir,
                self.Data_prefix + '.')
            self.Eigenvec_file = os.path.join(
                self.Output_dir,
                self.Data_prefix + '.eigenvec')
        else:
            for fpath in [Cov_file, Eigenvec_file]:
                try:
                    assert os.path.isfile(fpath)
                except AssertionError:
                    print(f'file {fpath} may not exist\n')

            self.Cov_file = Cov_file
            self.Eigenvec_file = Eigenvec_file

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
        self._range_list_file = os.path.join(self.Output_dir, 'range_list')

    def _preprocessing_update_effect_size(self):
        '''
        Return string which can be included in job script
        for generating file with updated effect size
        '''
        command = ' '.join([
            os.environ['RSCRIPT'],
            'update_effect_size.R',
            self.Sumstats_file,
            self._transformed_file])

        return command

    def _preprocessing_clumping(self, update_effect_size):
        '''
        Generate string which can be included in job script
        for clumping (generating .clumped file)

        Parameters
        ----------
        update_effect_size: bool
            if False, use Sumstats_file for --clump param
        Returns
        -------
        str
        '''
        command = ' '.join([
            os.environ['PLINK'],
            '--bfile',
            self.Geno_file,
            '--clump-p1', str(self.clump_p1),
            '--clump-r2', str(self.clump_r2),
            '--clump-kb', str(self.clump_kb),
            '--clump',
            (self._transformed_file
                if update_effect_size else self.Sumstats_file),
            '--clump-snp-field', 'SNP',
            '--clump-field', 'P',
            '--out', os.path.join(self.Output_dir, self.Data_prefix)
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
            os.environ['AWK_EXEC'],
            "'NR!=1{print $3}'",
            os.path.join(self.Output_dir, self.Data_prefix + '.clumped'),
            '>',
            os.path.join(self.Output_dir, self.Data_prefix + '.valid.snp'),
        ])

        return command

    def _preprocessing_extract_p_values(self, update_effect_size):
        '''
        Extract P-values (generating SNP.pvalue file)

        Parameters
        ----------
        update_effect_size: bool
            if False, use Sumstats_file as input

        Returns
        -------
        str
        '''
        command = ''
        if not update_effect_size:
            # unzip Sumstats file to Output_dir allowing parsing
            # it to Plink using --score
            command += ' '.join([
                os.environ['PYTHON'],
                '-c',
                f"""'from pgs import pgs; pgs.df_colums_to_file("{self.Sumstats_file}", "{self._transformed_file}")'"""  # noqa: 501
                '\n'
            ])
        command += ' '.join([
            os.environ['PYTHON'],
            '-c',
            f"""'from pgs import pgs; pgs.df_colums_to_file("{self._transformed_file}", "{os.path.join(self.Output_dir, "SNP.pvalue")}", ["SNP", "P"])'"""  # noqa: 501
        ])
        return command

    def _write_range_list_file(self):
        '''
        Write range_list file in output directory
        '''
        with open(self._range_list_file, 'wt') as f:
            for v in self.range_list:
                f.write(f'{v} 0 {v}\n')

    def _run_plink_basic(self):
        '''
        Generate string for basic plink run

        Returns
        -------
        str
        '''
        command = ' '.join([
            os.environ['PLINK'],
            '--bfile',
            self.Geno_file,
            '--score',
            self._transformed_file,
            ' '.join([str(x) for x in self.score_args]),
            '--q-score-range',
            self._range_list_file,
            os.path.join(self.Output_dir, 'SNP.pvalue'),
            '--extract',
            os.path.join(self.Output_dir, self.Data_prefix + '.valid.snp'),
            '--out',
            os.path.join(self.Output_dir, self.Data_prefix)
        ])

        return command

    def _run_plink_w_stratification(self):
        '''
        Account for (population) stratification using PCs,
        creating .eigenvec file.
        If class parameter Eigenvec_file is set and file exist,
        this function will not return commands to compute
        a new eigenvec file.

        Returns
        -------
        list of str
        '''
        # skip this step if Eigenvec_file argument is specified and file exist.
        if os.path.isfile(self.Eigenvec_file):
            print(f'Eigenvec_file {self.Eigenvec_file} exists. ' +
                  'To get instructions to compute, set Eigenvec_file=None')
            # check that number of PCs match with class input
            eigenvec_df = pd.read_csv(
                self.Eigenvec_file,
                delim_whitespace=True, header=None, nrows=1)
            nPCs = eigenvec_df.columns.size - 2
            if nPCs != self.nPCs:
                mssg = (
                    f'The number of PCs in {self.Eigenvec_file} nPCs={nPCs} ' +
                    f'while <pgs.PGS_Plink instance>.nPCs={self.nPCs}. ' +
                    f'Inst. class pgs.PGS_Plink w. nPCs={self.Eigenvec_file}' +
                    ' (confer config.yaml file with settings).')
                raise ValueError(mssg)
            return ''
        else:
            # First, perform pruning
            tmp_str_0 = ' '.join([
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--indep-pairwise',
                ' '.join([str(x) for x in self.strat_indep_pairwise]),
                '--out', os.path.join(self.Output_dir, self.Data_prefix)
            ])

            # Then we calculate the first N PCs
            tmp_str_1 = ' '.join([
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--extract',
                os.path.join(self.Output_dir, self.Data_prefix) + '.prune.in',
                '--pca', str(self.nPCs),
                '--out', os.path.join(self.Output_dir, self.Data_prefix)
            ])

            return '\n'.join([tmp_str_0, tmp_str_1])

    def _find_best_fit_pgs(self):
        '''
        Generate command for running find_best_fit_pgs.R script,
        producing

        Returns
        -------
        str
        '''
        command = ' '.join([
            os.environ['RSCRIPT'], 'find_best_fit_pgs.R',
            self.Pheno_file,
            self.Eigenvec_file,
            self.Cov_file,
            self.Phenotype,
            os.path.join(self.Output_dir, self.Data_prefix),
            ','.join([str(x) for x in self.range_list]),
            str(self.nPCs),
            os.path.join(self.Output_dir, 'best_fit_prs.csv')
        ])

        return command

    def _generate_post_run_str(self):
        arg = ','.join([f'"{self.Output_dir}"', f'"{self.Data_prefix}"'])
        cmd = ' '.join([
            os.environ['PYTHON'], '-c',
            f"""'from pgs.pgs import post_run_plink; post_run_plink({arg})'"""
        ])
        return cmd

    def _evaluate_model_str(self):
        '''
        Return callable string for fitting a simple
        linear model between PGS score and phenotype data
        using R stats::lm, printing stats::lm.fit.summary output
        to file
        '''
        cmd = ' '.join([
            os.environ['RSCRIPT'],
            'eval_model.R',
            '--pheno-file', self.Pheno_file,
            '--phenotype', self.Phenotype,
            '--score-file', os.path.join(self.Output_dir, 'test.score'),
            '--out', os.path.join(self.Output_dir, 'test_summary')
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
                    self._generate_post_run_str(),
                    self._evaluate_model_str()]
            elif mode == 'stratification':
                commands += [self._run_plink_w_stratification(),
                             self._find_best_fit_pgs(),
                             self._generate_post_run_str(),
                             self._evaluate_model_str()
                             ]
            return commands
        else:
            raise NotImplementedError


class PGS_PRSice2(BasePGS):
    """
    Helper class for setting up PRSice-2 PRS analysis.
    Inherited from class ``BasePGS``
    """

    def __init__(self,
                 Sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 Pheno_file='/REF/examples/prsice2/EUR.height',
                 Phenotype='Height',
                 Geno_file='/REF/examples/prsice2/EUR',
                 Output_dir='PGS_prsice2',
                 Cov_file='/REF/examples/prsice2/EUR.cov',
                 Eigenvec_file='/REF/examples/prsice2/EUR.eigenvec',
                 nPCs=6,
                 MAF=0.01,
                 INFO=0.8,
                 stat='OR',
                 **kwargs):
        '''
        Parameters
        ----------
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Phenotype: str
            phenotype name (must be a column header in ``Pheno_file``)
        Geno_file: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        Output_dir: str
            path for output files (<path>)
        Cov_file: str
            path to covariance file (.cov)
        Eigenvec_file: str
            path to eigenvec file (.eig)
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

        Attributes
        ----------
        Data_prefix: str
            file name prefix of .bed, .bim, etc. files
        '''
        super().__init__(Sumstats_file=Sumstats_file,
                         Pheno_file=Pheno_file,
                         Phenotype=Phenotype,
                         Geno_file=Geno_file,
                         Output_dir=Output_dir,
                         **kwargs)
        # set attributes
        self.Cov_file = Cov_file
        self.Eigenvec_file = Eigenvec_file
        self.nPCs = nPCs
        self.MAF = MAF
        self.INFO = INFO
        self.stat = stat

        # inferred
        self.Covariance_file = os.path.join(
            self.Output_dir,
            self.Data_prefix + '.covariate')

    def _generate_covariance_str(self):
        '''
        Generate string which will be included in job script
        for generating .covariate file combining .cov and .eigenvec
        input files.

        Returns
        -------
        str
        '''
        command = ' '.join([
            os.environ['RSCRIPT'],
            'generate_covariate.R',
            self.Cov_file,
            self.Eigenvec_file,
            self.Covariance_file,
            str(self.nPCs)])

        return command

    def _generate_run_str(self):
        '''
        Generate string which will be included in job script
        for running the PRSice2 analysis script

        Returns
        -------
        str
        '''
        target = self.Geno_file
        command = ' '.join([
            os.environ['RSCRIPT'], 'PRSice.R',
            '--prsice /usr/bin/PRSice_linux',
            f'--base {self.Sumstats_file}',
            f'--target {target}',
            '--binary-target F',
            f'--pheno {self.Pheno_file}',
            f'--cov {self.Covariance_file}',
            f'--base-maf MAF:{self.MAF}',
            f'--base-info INFO:{self.INFO}',
            f'--stat {self.stat}',
            f'--out {os.path.join(self.Output_dir, self.Data_prefix)}'
        ])

        # deal with kwargs
        if len(self.kwargs) > 0:
            for key, value in self.kwargs.items():
                command = ' '.join(
                    [command, f'--{key} {value or ""}'])

        return command

    def _generate_post_run_str(self):
        arg = ','.join([f'"{self.Output_dir}"', f'"{self.Data_prefix}"'])
        cmd = ' '.join([
            os.environ['PYTHON'], '-c',
            f"""'from pgs.pgs import post_run_prsice2; post_run_prsice2({arg})'"""  # noqa: E501
        ])
        return cmd

    def _evaluate_model_str(self):
        '''
        Return callable string for fitting a simple
        linear model between PGS score and phenotype data
        using R stats::lm, printing stats::lm.fit.summary output
        to file
        '''
        cmd = ' '.join([
            os.environ['RSCRIPT'],
            'eval_model.R',
            '--pheno-file', self.Pheno_file,
            '--phenotype', self.Phenotype,
            '--score-file', os.path.join(self.Output_dir, 'test.score'),
            '--out', os.path.join(self.Output_dir, 'test_summary')
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
        return [self._generate_covariance_str(),
                self._generate_run_str(),
                self._generate_post_run_str(),
                self._evaluate_model_str()]


class PGS_LDpred2(BasePGS):
    """
    Helper class for setting up LDpred2 PRS analysis.
    Inherited from class ``BasePGS``
    """

    def __init__(self,
                 Sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 Pheno_file='/REF/examples/prsice2/EUR.height',
                 Phenotype='Height',
                 Geno_file='/REF/examples/prsice2/EUR',
                 Output_dir='PGS_ldpred2_inf',
                 method='inf',
                 fileGenoRDS='EUR.rds',
                 col_stat='OR',
                 col_stat_se='SE',
                 stat_type='OR',
                 file_keep_snps='/REF/hapmap3/w_hm3.justrs',
                 **kwargs):
        '''
        Parameters
        ----------
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Phenotype: str
            phenotype name (must be a column header in ``Pheno_file``)
        Geno_file: str
            path to QC'd .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        Output_dir: str
            path for output files (<path>)
        method: str
            LDpred2 method, either "inf" (default) or "auto"
        fileGenoRDS: str
            base name for .rds file output
        col_stat: str
            Effect estimate column. Default: 'OR'
        col_stat_se: str
            Effect estimate standard error column. Default: 'SE'
        stat_type: str
            Effect estimate type (BETA for linear, OR for odds-ratio.
            Default: 'OR'
        file_keep_snps: str

        **kwargs
            dict of additional keyword/arguments pairs parsed to
            the LDpred2.R script (see file for full set of options).
            If the option is only a flag without value, set value
            as None-type or empty string.
        '''
        super().__init__(Sumstats_file=Sumstats_file,
                         Pheno_file=Pheno_file,
                         Phenotype=Phenotype,
                         Geno_file=Geno_file,
                         Output_dir=Output_dir,
                         **kwargs)

        # set attributes
        self.method = method
        self.fileGenoRDS = fileGenoRDS
        self.col_stat = col_stat
        self.col_stat_se = col_stat_se
        self.stat_type = stat_type
        self.file_keep_snps = file_keep_snps

        # inferred
        self._fileGeno = self.Geno_file + '.bed'
        self._file_out = os.path.join(self.Output_dir, 'test.score')

    def _run_createBackingFile(self):
        # Convert plink files to bigSNPR backingfile(s) (.rds/.bk)
        command = ' '.join([
            os.environ['RSCRIPT'],
            'createBackingFile.R',
            self._fileGeno,
            self.fileGenoRDS
        ])
        return command

    def _evaluate_model_str(self):
        '''
        Return callable string for fitting a simple
        linear model between PGS score and phenotype data
        using R stats::lm, printing stats::lm.fit.summary output
        to file
        '''
        cmd = ' '.join([
            os.environ['RSCRIPT'],
            'eval_model.R',
            '--pheno-file', self.Pheno_file,
            '--phenotype', self.Phenotype,
            '--score-file', os.path.join(self.Output_dir, 'test.score'),
            '--out', os.path.join(self.Output_dir, 'test_summary')
        ])
        return cmd

    def get_str(self, create_backing_file=True):
        '''
        Public method to create commands

        Parameters
        ----------
        create_backing_file: bool
            if True (default), prepend statements for running the
            ``createBackingFile.R`` script, generating fileGenoRDS

        Returns
        -------
        list of str
            list of command line statements for analysis run
        '''
        tmp_cmd1 = ' '.join([
            os.environ['RSCRIPT'], 'ldpred2.R',
            '--ldpred-mode', self.method,
            '--file-pheno', self.Pheno_file,
            '--col-stat', self.col_stat,
            '--col-stat-se', self.col_stat_se,
            '--stat-type', self.stat_type,
            '--geno-file', self.fileGenoRDS,
            '--sumstats', self.Sumstats_file,
            '--file-keep-snps', self.file_keep_snps,
            '--out', self._file_out,
        ])

        # deal with kwargs
        if len(self.kwargs) > 0:
            tmp_cmd1 = ' '.join([tmp_cmd1, convert_dict_to_str(self.kwargs)])

        # return calls
        if create_backing_file:
            tmp_cmd0 = self._run_createBackingFile()
            return [tmp_cmd0, tmp_cmd1, self._evaluate_model_str()]
        else:
            return [tmp_cmd1, self._evaluate_model_str()]


class Standard_GWAS_QC(BasePGS):
    '''
    Helper class for common GWAS QC.
    Inherited from class ``BasePGS``

    Based on the tutorial
    https://choishingwan.github.io/PRS-Tutorial/target/#qc-of-target-data
    '''

    def __init__(self,
                 Sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
                 Pheno_file='/REF/examples/prsice2/EUR.height',
                 Geno_file='/REF/examples/prsice2/EUR',
                 Output_dir='QC_data',
                 Phenotype='Height',
                 Data_postfix='.QC',
                 QC_target_kwargs={'maf': 0.01, 'hwe': 1e-6,
                                   'geno': 0.01, 'mind': 0.01},
                 QC_prune_kwargs={'indep-pairwise': [200, 50, 0.25]},
                 QC_relatedness_prune_kwargs={'rel-cutoff': 0.125},
                 **kwargs):
        '''
        Parameters
        ----------
        Sumstats_file: str
            summary statistics file (.gz)
        Pheno_file: str
            phenotype file (for instance, .height)
        Geno_file: str
            path to (raw) .bed, .bim, .fam files (w.o. file ending)
            (</ENV/path/to/data/file>)
        Output_dir: str
            path for output files (<path>)
        Phenotype: str
            default: 'Height'
        Data_postfix: str
            default: '.QC'
        QC_target_kwargs: dict
            key, values
        QC_prune_kwargs: dict
            keys, values
        QC_relatedness_prune_kwargs: dict
            keys, values
        **kwargs
        '''
        super().__init__(Sumstats_file=Sumstats_file,
                         Pheno_file=Pheno_file,
                         Geno_file=Geno_file,
                         Output_dir=Output_dir,
                         **kwargs)
        self.Phenotype = Phenotype
        self.Data_postfix = Data_postfix
        self.QC_target_kwargs = QC_target_kwargs
        self.QC_prune_kwargs = QC_prune_kwargs
        self.QC_relatedness_prune_kwargs = QC_relatedness_prune_kwargs

        # check if Output_dir exist. Create if missing.
        if os.path.isdir(self.Output_dir):
            pass
        else:
            os.mkdir(self.Output_dir)

    def get_str(self):
        '''
        Standard GWAS QC
        '''
        command = []
        # Filter summary statistics file, zip output.
        cmd = ' '.join([os.environ['GUNZIP_EXEC'],
                        '-c',
                        self.Sumstats_file,
                        '|\\\n',
                        os.environ['AWK_EXEC'],
                        "'NR==1 || ($11 > 0.01) && ($10 > 0.8) {print}'",
                        '|\\\n',
                        os.environ['GZIP_EXEC'],
                        '->',
                        os.path.join(self.Output_dir,
                                     self.Phenotype + '.gz')])
        command += [cmd]

        # Remove duplicates
        cmd = ' '.join([os.environ['GUNZIP_EXEC'],
                        '-c',
                        os.path.join(self.Output_dir,
                                     self.Phenotype + '.gz'),
                        '|\\\n',
                        os.environ['AWK_EXEC'],
                        "'{seen[$3]++; if(seen[$3]==1){ print}}'",
                        '|\\\n',
                        os.environ['GZIP_EXEC'],
                        '->',
                        os.path.join(self.Output_dir,
                                     self.Phenotype + '.nodup.gz')])
        command += [cmd]

        # Retain nonambiguous SNPs:
        cmd = ' '.join(
            [
                os.environ['GUNZIP_EXEC'],
                '-c',
                os.path.join(
                    self.Output_dir,
                    self.Phenotype +
                    '.nodup.gz'),
                '|\\\n',
                os.environ['AWK_EXEC'],
                """'!( ($4=="A" && $5=="T") ||  ($4=="T" && $5=="A") || ($4=="G" && $5=="C") || ($4=="C" && $5=="G")) {print}'""",  # noqa: E501
                '|\\\n',
                os.environ['GZIP_EXEC'],
                '->',
                os.path.join(
                    self.Output_dir,
                    self.Phenotype +
                    self.Data_postfix + '.gz')])
        command += [cmd]

        # QC target data
        # Modified from
        # https://choishingwan.github.io/PRS-Tutorial/target/#qc-of-target-data
        cmd = ' '.join([
            os.environ['PLINK'],
            '--bfile',
            self.Geno_file,
            '--write-snplist',
            '--make-just-fam',
            '--out',
            os.path.join(
                self.Output_dir,
                self.Data_prefix) + self.Data_postfix
        ])
        cmd = ' '.join([cmd, convert_dict_to_str(self.QC_target_kwargs)])
        command += [cmd]

        # Prune to remove highly correlated SNPs
        cmd = ' '.join(
            [
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--keep',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.fam'),
                '--extract',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.snplist'),
                '--out',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix),
            ])
        cmd = ' '.join([cmd, convert_dict_to_str(self.QC_prune_kwargs)])
        command += [cmd]

        # Compute heterozygosity rates, generating the EUR.QC.het file:
        cmd = ' '.join(
            [
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--extract',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.prune.in'),
                '--keep',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.fam'),
                '--het',
                '--out',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix)])
        command += [cmd]

        # remove individuals with F coefficients that are more than 3 standard
        # deviation (SD) units from the mean in ``R``:
        cmd = ' '.join([
            os.environ['RSCRIPT'], 'create_valid_sample.R',
            os.path.join(
                self.Output_dir,
                self.Data_prefix + self.Data_postfix + '.het'),
            os.path.join(
                self.Output_dir,
                self.Data_prefix + '.valid.sample'),
        ])
        command += [cmd]

        # strand-flipping the alleles to their complementary alleles
        cmd = ' '.join([
            os.environ['RSCRIPT'], 'strand_flipping.R',
            self.Geno_file + '.bim',
            os.path.join(self.Output_dir,
                         self.Phenotype + self.Data_postfix + '.gz'),
            os.path.join(self.Output_dir,
                         self.Data_prefix + self.Data_postfix + '.snplist'),
            os.path.join(self.Output_dir, self.Data_prefix + '.a1'),
            os.path.join(self.Output_dir, self.Data_prefix + '.mismatch')
        ])
        command += [cmd]

        # Sex-check pre-pruning, generating EUR.QC.sexcheck:
        cmd = ' '.join(
            [
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--extract',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.prune.in'),
                '--keep',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    '.valid.sample'),
                '--check-sex',
                '--out',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix)])
        command += [cmd]

        # Assign individuals as biologically male if F-statistic is > 0.8;
        # biologically female if F < 0.2:
        cmd = ' '.join([
            os.environ['RSCRIPT'], 'create_QC_valid.R',
            os.path.join(
                self.Output_dir,
                self.Data_prefix + '.valid.sample'),
            os.path.join(
                self.Output_dir,
                self.Data_prefix + self.Data_postfix + '.sexcheck'),
            os.path.join(
                self.Output_dir,
                self.Data_prefix + self.Data_postfix + '.valid')
        ])
        command += [cmd]

        # Relatedness pruning of individuals that have a first or second degree
        # relative
        cmd = ' '.join(
            [
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--extract',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.prune.in'),
                '--keep',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix + '.valid'),
                '--out',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix)])
        cmd = ' '.join([cmd, convert_dict_to_str(
            self.QC_relatedness_prune_kwargs)])
        command += [cmd]

        # Generate a QC'ed data set, creating .ai and .mismatch files:
        cmd = ' '.join(
            [
                os.environ['PLINK'],
                '--bfile',
                self.Geno_file,
                '--make-bed',
                '--keep',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix +
                    '.rel.id'),
                '--out',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix),
                '--extract',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    self.Data_postfix +
                    '.snplist'),
                '--a1-allele',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    '.a1'),
                '--exclude',
                os.path.join(
                    self.Output_dir,
                    self.Data_prefix +
                    '.mismatch')])
        command += [cmd]

        return command


if __name__ == '__main__':
    pass
