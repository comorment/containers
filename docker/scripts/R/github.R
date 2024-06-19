url <- "https://packagemanager.posit.co/cran/__linux__/focal/2023-02-16"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'
# auth_token <- Sys.getenv("GITHUB_TOKEN")

# GitHub packages w. Git SHA
packages <- list(
    'alexploner/cfdr.pleio' = '76d5085e6d3f3ca9576d5d7564d2acf11bcfd021',
    'dajiangliu/rareGWAMA' = '72e962dae19dc07251244f6c33275ada189c2126',
    'deepchocolate/glm-extras' = '91f8d53c886b27b7c9941df6c3233f99981323a8',
    'GenomicSEM/GenomicSEM' = 'bcbbaffff5767acfc5c020409a4dc54fbf07876b',
    'jamesliley/cfdr' = 'ec5fddbd27c746a470eb827dc249a80194b231e8',
    'jamesliley/cFDR-common-controls' = '9b923fea283e2373ee8effa2909620a1930004bd',
    'MRCIEU/gwasvcf' = '477b365da8522e9a47f3bce51993d5f36df49ceb',
    'MRCIEU/gwasglue' = 'c2d5660eed389e1a9b3e04406b88731d642243f1',
    'MRCIEU/gwasglue2' = '5d4e35bad211299e95e25151972382a1d7b84092',
    'MRCIEU/TwoSampleMR' = 'c174107cfd9ba47cf2f780849a263f37ac472a0e',
    'norment/normentR' = 'dfa1fbae9587db6c3613b0405df4f9cfa98ee0e1',
    'psychgen/phenotools' = 'b744d927a1302d85152917f3802a2212093d588a',
    'wouterpeyrot/CCGWAS' = 'ce9764da946189623a0164f156ad119773bc32f5'
)

# install package from GitHub and quit with error if installation fails
for (package in names(packages)) {
    ref <- packages[[package]]
    cat("Installing package ", package, " from GitHub with ref ", ref, "\n")
    tryCatch(
    {
        # devtools::install_github(package, ref=ref, repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
        devtools::install_github(package, ref=ref, repos=url, dependencies=dependencies, upgrade=upgrade)
    },
    error = function(e) {
        cat("Error occurred during package installation:\n")
        print(e)
        quit(status=1, save='no')
    },
    finally = {
    }
    )
    Sys.sleep(2)  # avoid rate limiting
}
