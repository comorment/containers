library(data.table)
library(argparser, quietly=T)

par <- arg_parser('write generate headerless .eigenvec file')
par <- add_argument(par, "--pheno-file", help=".csv input file")
par <- add_argument(par, "--eigenvec-file", help=".eigenvec output file")
par <- add_argument(par, "--pca", type="integer", default=20, 
                    help="Integer number of Principal Components (PCs)")
parsed <- parse_args(par)

csv <- fread(parsed$pheno_file)
cols <- c("FID","IID", paste0("PC", 1:parsed$pca))
eigen <- csv[, ..cols]
fwrite(eigen, parsed$eigenvec_file, sep="\t", col.names=F)