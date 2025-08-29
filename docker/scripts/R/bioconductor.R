# set up
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'

url = "https://packagemanager.posit.co/bioconductor/__linux__/noble/2025-08-01"
# Configure BioCManager to use Posit Package Manager:
options(BioC_mirror = "https://packagemanager.posit.co/bioconductor/2025-08-01")
options(BIOCONDUCTOR_CONFIG_FILE = "https://packagemanager.posit.co/bioconductor/2025-08-01/config.yaml")

# Configure a CRAN snapshot compatible with Bioconductor 3.19:
options(repos = c(CRAN = "https://packagemanager.posit.co/cran/__linux__/noble/2025-08-01"))

# Bioconductor packages
packages <- c(
    'AnnotationDbi',
    'ASSET',
    'BiocGenerics',
    'biomaRt',
    'biomartr',
    'clusterProfiler',
    'GenomeInfoDb',
    'gwasurvivr',
    'GWASTools',
    'limma',
    'org.Hs.eg.db',
    'rtracklayer',
    'snpStats', 
    'TMixClust',
    'VariantAnnotation')

# install package from Bioconductor and quit with error if installation fails
library(devtools)
BiocManager::install(version='3.22', ask=FALSE)

for (package in packages) {
    tryCatch(
    {
        BiocManager::install(package, version='3.22')
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

