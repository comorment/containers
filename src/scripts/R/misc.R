# library(BiocManager)
install.packages('http://cnsgenomics.com/software/gsmr/static/gsmr_1.0.9.tar.gz', repos=NULL, type='source')
# version=3.12 refs to the Bioconductor version, installs zlibbioc_1.36.0, BiocGenerics_0.36.1, snpStats_1.40.0:
BiocManager::install(c('zlibbioc', 'BiocGenerics', 'snpStats', 'GWASTools'), version='3.12')
