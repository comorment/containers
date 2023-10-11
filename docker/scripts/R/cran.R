require(devtools)
url <- "https://packagemanager.posit.co/cran/__linux__/focal/2023-02-16"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'

# CRAN packages w. version
packages <- list(
    argparser = '0.7.1',
    arsenal = '3.6.3',
    bigreadr = '0.2.5',
    bigsnpr = '1.11.6',
    BiocManager = '1.30.19',
    brant = '0.3-0',
    brms = '2.18.0',
    carat = '2.1.0',
    circlize = '0.4.15',
    correlation = '0.8.3',
    corrplot = '0.92',
    CPBayes = '1.1.0',
    DescTools = '0.99.47',
    'data.table' = '1.14.6',
    dendextend = '1.16.0',
    dplyr = '1.1.0',
    flextable = '0.8.5',
    fmsb = '0.7.5',
    GCPBayes = '4.0.0',
    geepack = '1.3.9',
    ggalluvial = '0.12.4',
    ggcorrplot = '0.1.4',
    ggplot2 = '3.4.1',
    ggseg = '1.6.5',
    ggseg3d = '1.6.3',
    ggstar = '1.0.4',
    ggthemes = '4.2.4',
    ggpubr = '0.6.0',
    glue = '1.6.2',
    gplots = '3.1.3',
    gtsummary = '1.7.0',
    fastICA = '1.2-3',
    fcfdr = '1.0.0',
    foreign = '0.8-84',
    homologene = '1.4.68.19.3.27',
    imputeMissings = '0.0.3',
    jtools = '2.2.1',
    lavaan = '0.6-14',
    lmerTest = '3.1-3',
    magrittr = '2.0.3',
    MatrixEQTL = '2.3',
    mgcv = '1.8-41',  # has gamm function
    miniCRAN = '0.2.16',
    moments = '0.14.1',
    MplusAutomation = '1.1.0',
    MultiABEL = '1.1-6',
    MVN = '5.9',
    mvtnorm = '1.1-3',
    optparse = '1.7.3',
    parameters = '0.20.2',
    patchwork = '1.1.2',
    pracma = '2.4.2',
    PredictABEL = '1.2-4',
    pROC = '1.18.0',
    qqman = '0.1.8',
    reghelper = '1.1.1',
    remotes = '2.4.2',
    rjags = '4-13',
    ROCR = '1.0-11',
    rmarkdown = '2.20',
    rstan = '2.21.8',
    runonce = '0.2.3',
    scales = '1.2.1',
    semptools = '0.2.9.6',
    seqminer = '8.6',
    semTools = '0.5-6',
    simplecolors = '0.1.1',
    sp = '1.6-0',
    splines2 = '0.4.7',
    stringr = '1.5.0',
    survey = '4.1-1',
    survminer = '0.4.9',
    tibble = '3.1.8',
    tidyr = '1.3.0',
    tree = '1.0-43',
    vctrs = '0.5.2',
    xgboost = '1.7.3.1')
 
# install package from CRAN and quit with error if installation fails
for (package in names(packages)) {
    version <- packages[[package]]

    tryCatch(
    {
        devtools::install_version(package, version=version, repos=url, dependencies=dependencies, upgrade=upgrade)
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
