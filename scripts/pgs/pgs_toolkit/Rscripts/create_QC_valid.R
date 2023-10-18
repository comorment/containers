library(data.table)
library(argparser, quietly=T)

# library(argparser, quietly=T)
par <- arg_parser('Assign individuals as male if F-stat is > 0.8; female if F < 0.2')
par <- add_argument(par, "--file-valid", help=".valid.sample input file")
par <- add_argument(par, "--file-sexcheck", help=".QC.sexcheck input file")
par <- add_argument(par, "--file-output", help=".QC.valid output file")
parsed <- parse_args(par)

# Read in file
valid <- fread(parsed$file_valid)
dat <- fread(parsed$file_sexcheck)[FID%in%valid$FID]
fwrite(dat[STATUS=="OK",c("FID","IID")], parsed$file_output, sep="\t") 