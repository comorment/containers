# set up
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'

url = "https://packagemanager.posit.co/bioconductor/__linux__/jammy/2024-10-01"
# Configure BioCManager to use Posit Package Manager:
options(BioC_mirror = "https://packagemanager.posit.co/bioconductor/2024-10-01")
options(BIOCONDUCTOR_CONFIG_FILE = "https://packagemanager.posit.co/bioconductor/2024-10-01/config.yaml")

# Configure a CRAN snapshot compatible with Bioconductor 3.20:
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/__linux__/jammy/2024-10-01"))

# Bioconductor packages
packages <- c(
    'AnnotationDbi',
    'ASSET',
    'BiocGenerics',
    'biomaRt',
    'biomartr',
    'clusterProfiler',
    'GWASTools',
    'limma',
    'org.Hs.eg.db',
    'rtracklayer',
    'snpStats', 
    'TMixClust',
    'VariantAnnotation',
    'zlibbioc')

# install package from Bioconductor and quit with error if installation fails
library(devtools)
for (package in packages) {
    tryCatch(
    {
        devtools::install_bioc(package, mirror=url, dependencies=dependencies, upgrade=upgrade)
        # BiocManager::install(package, version='3.12')
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

