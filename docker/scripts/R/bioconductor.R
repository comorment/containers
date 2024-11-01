# set up
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'

url = "https://packagemanager.posit.co/bioconductor/__linux__/jammy/2024-09-02"
# Configure BioCManager to use Posit Package Manager:
options(BioC_mirror = "https://packagemanager.posit.co/bioconductor/2024-09-02")
options(BIOCONDUCTOR_CONFIG_FILE = "https://packagemanager.posit.co/bioconductor/2024-09-02/config.yaml")

# Configure a CRAN snapshot compatible with Bioconductor 3.19:
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/__linux__/jammy/2024-09-01"))

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
    'SNPRelate',
    'snpStats', 
    'SummarizedExperiment',
    'TMixClust',
    'VariantAnnotation',
    'zlibbioc')

# install package from Bioconductor and quit with error if installation fails
library(devtools)
for (package in packages) {
    tryCatch(
    {
        BiocManager::install(package, version='3.19')
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

