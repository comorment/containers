# Calculate polygenic scores using ldpred2
# this script is an adaptation of the demo script available at the bigsnpr homepage
library(bigsnpr, quietly = T)
library(tools)
library(argparser, quietly=T)
par <- arg_parser('Create bigSNPR rds/bk (backing) files from plink bed files')
par <- add_argument(par, 'file-input', help='The bed input file')
par <- add_argument(par, 'file-output', help='The output basename of files')
parsed <- parse_args(par)
if (!file.exists(parsed$file_input)) stop(parsed$file_input, ' does not exist!')
# If the user passes a file.rds, the output will not be file.rds.rds
# This is so that the same file specification can be used at several locations in a script.
baseName <- parsed$file_output
if (file_ext(tolower(parsed$file_output)) == 'rds') baseName <- file_path_sans_ext(parsed$file_output)
outputFileRDS <- paste0(baseName, '.rds')
if (file.exists(outputFileRDS)) {
  cat('File', outputFileRDS, 'already exists. Exiting.\n')
  quit('no') # Exit without saving the workspace
}
cat('Processing', parsed$file_input, '\n')
res <- snp_readBed(parsed$file_input, backingfile = baseName)
cat('Created', baseName, ' (.rds, .bk)\n')