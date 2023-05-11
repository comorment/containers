# Impute genotypes in bignpr .rds/.bk files
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(tools)
library(argparser, quietly=T)
par <- arg_parser('Impute genotype in bigSNPR files. Note that imputation will be performed in the file provided and not in a copy.')
par <- add_argument(par, '--geno-file-rds', nargs=1, help='Genotype .rds file to impute')
par <- add_argument(par, '--impute-simple', nargs=1, help='Impute missing genotypes using one of mode, mean0, mean2, random (See bigsnpr::fastImputeSimple) or zero')
par <- add_argument(par, '--cores', nargs=1, default=nb_cores(), help='Number of cores to use.')
parsed <- parse_args(par)
fileGeno <- parsed$geno_file_rds
fileGenoOutput <- parsed$geno_output_file_rds
imputeSimple <- parsed$impute_simple
NCORES <- parsed$cores
### Maybe there's some environment variable availble to determine the location of the script instead
coms <- commandArgs()
coms <- coms[substr(coms, 1, 7) == '--file=']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))

if (!file.exists(fileGeno)) stop(fileGeno, ' does not exist!')
cat('Loading genotype data from file:', fileGeno ,'\n')
obj.bigSNP <- snp_attach(fileGeno)
G <- obj.bigSNP$genotypes
# Count missingness over individuals for each SNP
nMissingGenotypes <- countMissingGenotypes(G, cores=NCORES)
nWithMissing <- sum(nMissingGenotypes > 0)
if (nWithMissing == 0) {
  cat('No missing genotypes found. Exiting...\n')
  quit('no')
}
cat('Genotypes missing for at least 1 individual: N=', nWithMissing, ' out of ', length(nMissingGenotypes), ' genotypes).\n', sep='')
cat('Imputing genotypes by using', imputeSimple, '(see bigsnpr::snp_fastImputeSimple).\n')
if (imputeSimple == 'zero') {
  G <- zeroMissingGenotypes(G) 
} else {
  G <- snp_fastImputeSimple(G, method=imputeSimple, ncores = NCORES)
}
nMissingGenotypes <- countMissingGenotypes(G, cores=NCORES)
nWithMissing <- sum(nMissingGenotypes > 0)
if (nWithMissing > 0) stop('Imputation has failed: Still missing genotypes')
cat('Storing imputed genotypes in', fileGeno, '\n')
obj.bigSNP$genotypes <- G
snp_save(obj.bigSNP)