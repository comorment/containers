require(devtools)
url <- "https://packagemanager.posit.co/cran/__linux__/jammy/2024-10-01"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'

options(repos = c(CRAN = url))

# CRAN packages w. version
packages <- list(
    argparser,
    arsenal,
    bigreadr,
    bigsnpr,
    BiocManager,
    brant,
    brms,
    carat,
    caret,
    circlize,
    correlation,
    corrplot,
    CPBayes,
    DescTools,
    'data.table',
    dendextend,
    dplyr,
    EFAtools,
    fastICA,
    fcfdr,
    flextable,
    fmsb,
    foreign,
    GCPBayes,
    geepack,
    genio,
    ggalluvial,
    ggcorrplot,
    ggplot2,
    ggseg,
    ggseg3d,
    ggstar,
    ggthemes,
    ggpubr,
    glmnet,
    glue,
    gplots,
    gtsummary,
    Haplin,
    homologene,
    imputeMissings,
    jtools,
    lavaan,
    lightgbm,
    lmerTest,
    magrittr,
    MatrixEQTL,
    mgcv,  # has gamm function
    miniCRAN,
    moments,
    MplusAutomation,
    MultiABEL,
    MVN,
    mvtnorm,
    optparse,
    parameters,
    patchwork,
    PooledCohort,
    pracma,
    PredictABEL,
    pROC,
    qqman,
    reghelper,
    remotes,
    RiskScorescvd,
    rjags,
    ROCR,
    rmarkdown,
    rstan,
    runonce,
    scales,
    semptools,
    seqminer,
    semTools,
    simplecolors,
    sp,
    splines2,
    stringr,
    survey,
    survival,
    survminer,
    tibble,
    tidyr,
    tree,
    vctrs,
    xgboost)
 
# install package from CRAN and quit with error if installation fails
# for (package in names(packages)) {
for (package in packages) {
    # version <- packages[[package]]

    tryCatch(
    {
        devtools::install_cran(package, dependencies=dependencies, upgrade=upgrade)
        # devtools::install_version(package, version=version, repos=url, dependencies=dependencies, upgrade=upgrade)
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
