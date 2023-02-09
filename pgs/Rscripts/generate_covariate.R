library(data.table)
library(argparser, quietly=T)

par <- arg_parser('write generate .covariate file')
par <- add_argument(par, "file_cov", help=".cov input file")
par <- add_argument(par, "file_eigenvec", help=".eigenvec input file")
par <- add_argument(par, "file_covariate", help=".covariate output file")
par <- add_argument(par, "nPCs", type="integer", default=6, 
                    help="Integer number of Principal Components (PCs)")
parsed <- parse_args(par)

covariate <- fread(parsed$file_cov)
pcs <- fread(parsed$file_eigenvec, header=F)
# colnames(pcs) <- c("FID","IID", paste0("PC", 1:6))
colnames(pcs) <- c("FID","IID", paste0("PC", 1:parsed$nPCs))
cov <- merge(covariate, pcs)
print(paste('writing', parsed$file_covariate, 'with covariate and PCs'))
fwrite(cov, parsed$file_covariate, sep="\t")