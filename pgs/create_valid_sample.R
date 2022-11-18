library(data.table)
library(argparser, quietly=T)

# library(argparser, quietly=T)
par <- arg_parser('rm individuals with F-coeffs > 3SDs from mean')
par <- add_argument(par, "file_input", help=".QC.het input file")
par <- add_argument(par, "file_output", help=".valid.sample output file")
parsed <- parse_args(par)
# tmpFile <- tempfile()
# fileRDS <- snp_readBed(parsed$file_bed, backingfile=tmpFile)

# Read in file
# dat <- fread("EUR.QC.het")
dat <- fread(parsed$file_input)
# Get samples with F coefficient within 3 SD of the population mean
valid <- dat[F<=mean(F)+3*sd(F) & F>=mean(F)-3*sd(F)] 
# print FID and IID for valid samples
# fwrite(valid[,c("FID","IID")], "EUR.valid.sample", sep="\t") 
fwrite(valid[,c("FID","IID")], parsed$file_output, sep="\t") 
# q() # exit R