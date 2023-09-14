url <- "https://packagemanager.posit.co/cran/__linux__/focal/2023-02-16"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'
devtools::install_github('dajiangliu/rareGWAMA', ref='72e962dae19dc07251244f6c33275ada189c2126', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_github('GenomicSEM/GenomicSEM', ref='bcbbaffff5767acfc5c020409a4dc54fbf07876b', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_github('MRCIEU/TwoSampleMR', ref='c174107cfd9ba47cf2f780849a263f37ac472a0e', repos=url, dependencies=dependencies, upgrade=upgrade)