url <- "https://packagemanager.posit.co/cran/__linux__/focal/2023-02-16"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'
auth_token <- Sys.getenv("GITHUB_TOKEN")
devtools::install_github('alexploner/cfdr.pleio', ref='76d5085e6d3f3ca9576d5d7564d2acf11bcfd021', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('dajiangliu/rareGWAMA', ref='72e962dae19dc07251244f6c33275ada189c2126', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('deepchocolate/glm-extras', ref='91f8d53c886b27b7c9941df6c3233f99981323a8', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('GenomicSEM/GenomicSEM', ref='bcbbaffff5767acfc5c020409a4dc54fbf07876b', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('jamesliley/cfdr', ref='ec5fddbd27c746a470eb827dc249a80194b231e8', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('jamesliley/cFDR-common-controls', ref='9b923fea283e2373ee8effa2909620a1930004bd', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
# devtools::install_github('MRCIEU/gwasvcf', ref='v0.1.2', repos=url, dependencies=dependencies, upgrade=upgrade)  # inst. before gwasglue
devtools::install_github('MRCIEU/gwasvcf', ref='477b365da8522e9a47f3bce51993d5f36df49ceb', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)  # inst. before gwasglue
devtools::install_github('MRCIEU/gwasglue', ref='c2d5660eed389e1a9b3e04406b88731d642243f1', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('MRCIEU/gwasglue2', ref='5d4e35bad211299e95e25151972382a1d7b84092', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('MRCIEU/TwoSampleMR', ref='c174107cfd9ba47cf2f780849a263f37ac472a0e', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('norment/normentR', ref='dfa1fbae9587db6c3613b0405df4f9cfa98ee0e1', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
devtools::install_github('psychgen/phenotools', ref='b744d927a1302d85152917f3802a2212093d588a', repos=url, dependencies=dependencies, upgrade=upgrade, auth_token=auth_token)
