library(data.table)
library(argparser, quietly=T)

par <- arg_parser('write generate .covariate file')
par <- add_argument(par, "--cov-file", help=".cov input file")
par <- add_argument(par, "--eigenvec-file", help=".eigenvec input file")
par <- add_argument(par, "--covariate-file", help=".covariate output file")
par <- add_argument(par, "--nPCs", type="integer", default=6, 
                    help="Integer number of Principal Components (PCs)")
parsed <- parse_args(par)

covariate <- fread(parsed$cov_file)
pcs <- fread(parsed$eigenvec_file, header=F)
# colnames(pcs) <- c("FID","IID", paste0("PC", 1:6))
colnames(pcs) <- c("FID","IID", paste0("PC", 1:parsed$nPCs))
cov <- merge(covariate, pcs)
print(paste('writing', parsed$covariate_file, 'with covariate and PCs'))
fwrite(cov, parsed$covariate_file, sep="\t")