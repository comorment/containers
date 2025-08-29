url <- "https://packagemanager.posit.co/cran/__linux__/noble/2025-08-01"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
# upgrade <- 'default'
upgrade <- 'never'
auth_token <- Sys.getenv("github_pat")
cat("GitHub PAT length: ", nchar(auth_token), "\n")

# GitHub packages w. Git SHA
packages <- list(
    'alexploner/cfdr.pleio' = '76d5085e6d3f3ca9576d5d7564d2acf11bcfd021',
    'dajiangliu/rareGWAMA' = '72e962dae19dc07251244f6c33275ada189c2126',
    'deepchocolate/glm-extras' = 'ecba68c0378fc953edf8fe594ce914aff8ada6fa',
    'GenomicSEM/GenomicSEM' = '8e0ef594e95885b1f734f1dfcfe668b16ada2880',
    'jamesliley/cfdr' = 'ec5fddbd27c746a470eb827dc249a80194b231e8',
    'jamesliley/cFDR-common-controls' = '9b923fea283e2373ee8effa2909620a1930004bd',
    # gwasvcf deps:
    'MRCIEU/genetics.binaRies' = 'b0324f180476d80c43bba2ab026b72c5be426a92',
    'MRCIEU/gwasglue2' = 'c93b3a1fca7d2eae5d40bd62117091b1ad57f0fa',
    'MRCIEU/gwasvcf' = '477b365da8522e9a47f3bce51993d5f36df49ceb',
    # gwasglue/TwoSampleMR deps:
    'rondolab/MR-PRESSO' = '3e3c92d7eda6dce0d1d66077373ec0f7ff4f7e87',
    'gqi/MRMix'='56afdb2bc96760842405396f5d3f02e60e305039',
    'WSpiller/RadialMR' = '0ed91f83aebf265a09482561c128c830e58ed697',
    'qingyuanzhao/mr.raps' = '27b96f31e26ae97a395422bd757f514a7f96cc85',
    'MRCIEU/TwoSampleMR' = '578c68fa754c57d764553812bf85d69ecf43b011',
    'MRCIEU/gwasglue' = 'c2d5660eed389e1a9b3e04406b88731d642243f1',
    'noahlorinczcomi/MRBEE' = '6295549a1f5a158c6701eb793646d60c8aef11ca',
    'norment/normentR' = 'dfa1fbae9587db6c3613b0405df4f9cfa98ee0e1',
    'psychgen/phenotools' = '9eefa4ee0e8ea00bcbdb0e579dcdd7912cfe0597',
    'wouterpeyrot/CCGWAS' = 'ce9764da946189623a0164f156ad119773bc32f5',
    'WSpiller/MVMR' = '65705da9421b6235c7458dba6f01cddfebfe96f5',
    'xiashen/MultiABEL' = '7067fe6753c74f6580029abc82bce914472b4b16',
    'amorris28/hazrd' = 'f2748a815a094f2e12a5de89c707aa808de5fe25'
)

# install package from GitHub and quit with error if installation fails
for (package in names(packages)) {
    ref <- packages[[package]]
    cat("Installing package ", package, " from GitHub with ref ", ref, "\n")
    tryCatch(
    {
        devtools::install_github(package, ref=ref, repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
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


# misc. packages
library(remotes)
remotes::install_version('RcppEigen', version = '0.3.3.9.3')
remotes::install_github('jrs95/hyprcoloc', build_opts = c('--resave-data', '--no-manual'), upgrade = 'never')