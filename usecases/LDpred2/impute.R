library(bigsnpr)
library(argparser, quietly=T)
par <- arg_parser('Impute usign bigsnpr')
par <- add_argument(par, "file-bed", help="BED file to impute")
par <- add_argument(par, "file-output", help="BED output file")
parsed <- parse_args(par)
tmpFile <- tempfile()
fileRDS <- snp_readBed(parsed$file_bed, backingfile=tmpFile)
obj.bigSNP <- snp_attach(fileRDS)
# Use method random, seems to be a lot of missingness wich if I understand it correctly, causes problems
# for the later predictions (to many snps that are missing for all individuals). Maybe better to remove
# such SNPS but when testing. I guess such decisions should be left to the end-user
obj.bigSNP$genotypes <- snp_fastImputeSimple(obj.bigSNP$genotypes, method="random", ncores = nb_cores() - 1)
snp_writeBed(obj.bigSNP, bedfile = parsed$file_output)
file.remove(paste0(tmpFile, '.rds'))
file.remove(paste0(tmpFile, '.bk'))