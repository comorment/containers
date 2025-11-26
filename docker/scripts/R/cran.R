require(devtools)
url <- "https://packagemanager.posit.co/cran/__linux__/noble/2025-08-01"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'

options(repos = c(CRAN = url))

# CRAN packages w. version
packages <- list(
    'AER',
    'argparser',
    'arsenal',
    'arrow',
    'bigreadr',
    'bigsnpr',
    'BiocManager',
    'bit64',
    'brant',
    'brms',
    'carat',
    'caret',
    'circlize',
    'coloc',
    'colocboost',
    'colocPropTest',
    'compareC',
    'correlation',
    'corrplot',
    'CPBayes',
    'DescTools',
    'data.table',
    'dendextend',
    'dplyr',
    'EFAtools',
    'fastICA',
    'fcfdr',
    'flextable',
    'fmsb',
    'foreign',
    'GCPBayes',
    'geepack',
    'genio',
    'ggalluvial',
    'ggcorrplot',
    'ggplot2',
    'ggseg',
    'ggseg3d',
    'ggstar',
    'ggthemes',
    'ggpubr',
    'gitcreds',
    'glmmTMB',
    'glmnet',
    'glue',
    'gplots',
    'gtsummary',
    'Haplin',
    'here',
    'homologene',
    'ieugwasr',
    'imputeMissings',
    'jtools',
    'lavaan',
    'lightgbm',
    'lmerTest',
    'magrittr',
    'MatrixEQTL',
    'MendelianRandomization',
    'mgcv',  # has gamm function
    'miniCRAN',
    'moments',
    'MplusAutomation',
    'MVN',
    'mvtnorm',
    'optparse',
    'parameters',
    'patchwork',
    'PooledCohort',
    'pracma',
    'PredictABEL',
    'pROC',
    'qqman',
    'QRISK3',
    'r2redux',
    'reghelper',
    'remotes',
    'RiskScorescvd',
    'rjags',
    'ROCR',
    'rmarkdown',
    'rstan',
    'runonce',
    'scales',
    'semptools',
    'seqminer',
    'semTools',
    'simplecolors',
    'sp',
    'splines2',
    'stringr',
    'susieR',
    'survey',
    'survival',
    'survminer',
    'tibble',
    'tidyr',
    'tree',
    'vctrs',
    'xgboost',
    'zlib')
 
# install package from CRAN and quit with error if installation fails
# for (package in names(packages)) {
for (package in packages) {
    # version <- packages[[package]]

    tryCatch(
    {
        devtools::install_cran(package, dependencies=dependencies, upgrade=upgrade)
    },
    error = function(e) {
        cat("Error occurred during package installation:\n")
        print(e)
        quit(status=1, save='no')
    },
    finally = {
    }
    )
}
