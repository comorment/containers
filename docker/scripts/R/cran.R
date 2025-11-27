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
    'bdsmatrix',
    'bigreadr',
    'bigsnpr',
    'BiocManager',
    'bit',
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
    'coxme',
    'CPBayes',
    'DescTools',
    'data.table',
    'dendextend',
    'dplyr',
    'EFAtools',
    'egg',
    'fastICA',
    'fcfdr',
    'feather',
    'flextable',
    'fmsb',
    'foreign',
    'GCPBayes',
    'geepack',
    'genio',
    'ggalluvial',
    'ggcorrplot',
    'ggplot2',
    'ggpubr',
    'ggrepel',
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
    'kinship2',
    'lavaan',
    'lightgbm',
    'lmerTest',
    'magrittr',
    'MatrixEQTL',
    'matrixStats',
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
    'pgenlibr',
    'PooledCohort',
    'pracma',
    'PredictABEL',
    'pROC',
    'psych',
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
    'simsalapar',
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
