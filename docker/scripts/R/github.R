url <- "https://packagemanager.posit.co/cran/__linux__/noble/2025-08-01"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
# upgrade <- 'default'
upgrade <- 'never'
auth_token <- Sys.getenv("github_pat")
cat("GitHub PAT length: ", nchar(auth_token), "\n")

# GitHub packages w. Git SHA
packages <- list(
    'alexploner/cfdr.pleio' = '76d5085e6d3f3ca9576d5d7564d2acf11bcfd021',
    'amslala/regtools' = 'v0.2.0',
    'dajiangliu/rareGWAMA' = '72e962dae19dc07251244f6c33275ada189c2126',
    'deepchocolate/glm-extras' = 'ecba68c0378fc953edf8fe594ce914aff8ada6fa',
    'jamesliley/cfdr' = 'ec5fddbd27c746a470eb827dc249a80194b231e8',
    'jamesliley/cFDR-common-controls' = '9b923fea283e2373ee8effa2909620a1930004bd',
    'norment/normentR' = 'dfa1fbae9587db6c3613b0405df4f9cfa98ee0e1',
    'psychgen/phenotools' = '62dd11e111d8d952837c9f207557e9b297ba56bc',
    'wouterpeyrot/CCGWAS' = 'ce9764da946189623a0164f156ad119773bc32f5',
    'xiashen/MultiABEL' = '7067fe6753c74f6580029abc82bce914472b4b16',
    'amorris28/hazrd' = 'ff9f1690e930792f29e1fd87e25c0dc8632339d5',
    'cnfoley/hyprcoloc' = '26ea5953a46b3e204dfa8eadd202f746244afa13',
    'zhenin/HDL/HDL' = '551a8864c5ed3389a6892743ff059357735dc195',
    'JBPG/Gsens' = '6cac02ba1ccaf38870e2526076f0306c0cf0dc0a'
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