library(argparser, quietly=T)
library(data.table)

# capture command-line input
par <- arg_parser('')
par <- add_argument(par, "qcfile", help=".gz input file")
par <- add_argument(par, "transformed", help=".transformed output file")
parsed <- parse_args(par)

dat <- fread(parsed$qcfile)
fwrite(dat[,BETA:=log(OR)], parsed$transformed, sep="\t")
