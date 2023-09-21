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
for (package in packages) {
    tryCatch(
    {
        BiocManager::install(package, version='3.12')
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

