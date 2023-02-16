# Impute genotypes in bignpr .rds/.bk files
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(tools)
library(argparser, quietly=T)
par <- arg_parser('Impute genotype in bigSNPR files')
par <- add_argument(par, '--geno-file-rds', nargs=1, help='Genotype .rds file to impute')

par <- add_argument(par, '--impute-simple', nargs=1, help='Impute missing genotypes using one of mode, mean0, mean2, random (See bigsnpr::fastImputeSimple) or zero')
par <- add_argument(par, '--impute-alpha', nargs=1, default=1e-4, help='Imputation type-I error threhold, only relevant for --impute')
par <- add_argument(par, '--impute-size', nargs=1, default=200, help='Imputation number of neighbour SNPs, only relevant for --impute')
par <- add_argument(par, '--impute-ptrain', nargs=1, default=0.8, help='Proportion missing genotypes used for training, only relevant for --impute')
par <- add_argument(par, '--impute-seed', nargs=1, help='Provide a seed to bigsnpr::snp_fastImpute for reproducible imputation.')
par <- add_argument(par, '--cores', nargs=1, default=nb_cores(), help='Number of cores to use.')
parsed <- parse_args(par)
fileGeno <- parsed$geno_file_rds
fileGenoOutput <- parsed$geno_output_file_rds
imputeSimple <- parsed$impute_simple
NCORES <- parsed$cores
argImputeAlpha <- parsed$impute_alpha
argImputeSize <- parsed$impute_size
argImputePtrain <- parsed$impute_ptrain
argImputeSeed <- parsed$impute_seed
### Maybe there's some environment variable availble to determine the location of the script instead
coms <- commandArgs()
coms <- coms[substr(coms, 1, 8) == '--file=/']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))


if (!file.exists(fileGeno)) stop(fileGeno, ' does not exist!')

cat('Loading genotype data from file:', fileGeno ,'\n')
obj.bigSNP <- snp_attach(fileGeno)
G <- obj.bigSNP$genotypes
# Count missingness over individuals for each SNP
nMissingGenotypes <- countMissingGenotypes(G)
nWithMissing <- sum(nMissingGenotypes > 0)
if (nWithMissing == 0) {
  cat('No missing genotypes found. Exiting...\n')
  quit('no')
}
cat('Genotypes missing for at least 1 individual: N=', nWithMissing, ' out of ', length(nMissingGenotypes), ').\n', sep='')
if (!is.na(imputeSimple)) {
  cat('Imputing genotypes by using', imputeSimple, '(see bigsnpr::snp_fastImputeSimple).\n')
  G <- snp_fastImputeSimple(G, method=imputeSimple, ncores = NCORES)
} else {
  library(xgboost)
  cat('Imputing genotypes by using XGBoost models (see bigsnpr::snp_fastImpute).\n')
  infos <- snp_fastImpute(G, 
                          infos.chr=obj.bigSNP$map$chromosome,
                          alpha=argImputeAlpha, size=argImputeSize, p.train=argImputePtrain, ncores=NCORES,
                          seed=argImputeSeed)
  # ggplot2
  library(ggplot2)
  ## Here there is no SNP with more than 1% error (estimated)
  pvals <- c(0.01, 0.005, 0.002, 0.001); colvals <- 2:5
  df <- data.frame(pNA = infos[1, ], pError = infos[2, ])
  
  Reduce(function(p, i) {
    p + stat_function(fun = function(x) pvals[i] / x, color = colvals[i])
  }, x = seq_along(pvals), init = ggplot(df, aes(pNA, pError))) +
    geom_point() +
    coord_cartesian(ylim = range(df$pError, na.rm = TRUE)) +
    theme_bigstatsr()
}
nMissingGenotypes <- countMissingGenotypes(G)
nWithMissing <- sum(nMissingGenotypes > 0)
if (nWithMissing > 0) stop('Imputation has failed: Still missing genotypes')
cat('Storing imputed genotypes in', fileGeno, '\n')
obj.bigSNP$genotypes <- G
snp_save(obj.bigSNP)