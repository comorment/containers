require(devtools)
url <- "https://packagemanager.posit.co/cran/__linux__/focal/2023-02-16"
dependencies <- c('Depends', 'Imports', 'LinkingTo')
upgrade <- 'default'
devtools::install_version('brant', version='0.3-0', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('brms', version='2.18.0', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('CARAT', version='2.1.0', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('corrplot', version='0.92', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('dendextend', version='1.16.0', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('fastICA', version='1.2-3', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('geepack', version='1.3.9', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('ggthemes', version='4.2.4', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('ggpubr', version='0.6.0', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('gplots', version='3.1.3', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('imputeMissings', version='0.0.3', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('Lavaan', version='0.6-14', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('lmerTest', version='3.1-3', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('MatrixEQTL', version='2.3', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('mgcv', version='1.8-41', repos=url, dependencies=dependencies, upgrade=upgrade)  # has gamm function
devtools::install_version('moments', version='0.14.1', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('MVN', version='5.9', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('patchwork', version='1.1.2', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('pracma', version='2.4.2', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('RJags', version='4-13', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('ROCR', version='1.0-11', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('rstan', version='2.21.8', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('semptools', version='0.2.9.6', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('semTools', version='0.5-6', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('simplecolors', version='0.1.1', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('sp', version='1.6-0', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('splines2', version='0.4.7', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('survminer', version='0.4.9', repos=url, dependencies=dependencies, upgrade=upgrade)
devtools::install_version('tree', version='1.0-43', repos=url, dependencies=dependencies, upgrade=upgrade)


BiocManager::install(c('clusterProfiler'), version='3.12')

devtools::install_github('norment/normentR', ref='dfa1fbae9587db6c3613b0405df4f9cfa98ee0e1', repos=url, dependencies=dependencies, upgrade=upgrade)


# not on CRAN
# normentR (https://github.com/norment/normentR)
# clusterProfiler (bioconductor) https://bioconductor.org/packages/release/bioc/html/clusterProfiler.html, https://www.rdocumentation.org/packages/clusterProfiler/versions/3.0.4
# ambiguous
# gamm: is that mgcv? (https://www.rdocumentation.org/packages/mgcv/versions/1.9-0)
# mvn: is this MVN? (https://packagemanager.posit.co/client/#/repos/cran/packages/MVN/450145/overview?search=mvn#package-details)
# RStan: is this rstan? (https://www.rdocumentation.org/packages/rstan/versions/2.26.23
