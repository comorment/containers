# Split LD into blocks
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(argparser, quietly = T)
library(stringr)
# Load some functions
coms <- commandArgs()
coms <- coms[substr(coms, 1, 7) == '--file=']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))
source(paste0(dirScript, '/funMatrix.R'))

par <- arg_parser('Split LD matrices into blocks using bigSNPr')
## Mandatory arguments
par <- add_argument(par, "--file-ld-chr", nargs=1, default="LD_with_blocks_chr@.rds", help="Template name of LD files using @ to indicate chromosome nr")
par <- add_argument(par, "--file-ld-map", nargs=1, default="map.rds", help="Name of LD map file")
par <- add_argument(par, '--file-output-ld-blocks', help='Template name of output files using @ to indicate chromosome nr')

## Optional arguments
par <- add_argument(par, "--chr2use", nargs=Inf, help="List of chromosomes to use (by default it uses chromosomes 1 to 22)")
# Parameters to bigsnpr::ldsplit
par <- add_argument(par, '--min-size', nargs=1, default=50, help='Minimum number of variants in each block. See bigsnpr::ldsplit.')
par <- add_argument(par, '--max-size-weights', nargs=2, help='Weights for providing an upper range of block sizes to try. See bigsnpr::ldsplit.
                    The number of columns in each matrix is divided by the first (weight 1) and second (weight 2) argument and a logarithmic sequence created, 
                    implying Thus [weight 1] > [weight 2]. Defaults to [30 5].')
par <- add_argument(par, '--max-r2', nargs=1, default=0.3, help='Maximum squared correlation between variants in different blocks. See bigsnpr::snp_ldsplit')
par <- add_argument(par, '--thr-r2', nargs=1, default=0.02, help='Threshold under which squared correlations are ignored. See bigsnpr::snp_ldsplit')

parsed <- parse_args(par)
# Chromosomes to use
chr2use <- parsed$chr2use
if (any(is.na(chr2use))) chr2use <- 1:22

fileLDChr <- parsed$file_ld_chr
fileOutputLDBlocks <- parsed$file_output_ld_blocks
if (!dir.exists(dirname(fileOutputLDBlocks))) dir.create(dirname(fileOutputLDBlocks))
fileLDMap <- parsed$file_ld_map
argMaxR2 <- parsed$max_r2
argMinSize <- parsed$min_size
argThrR2 <- parsed$thr_r2
argWeights <- parsed$max_size_weights
if (isVarNA(argWeights)) {
  argWeights <- c(30, 5)
} else {
  argWeights <- as.integer(argWeights)
}

if (argWeights[2] >= argWeights[1]) stop('First weight to --max-size-weights should be greater than the second, received: ', argWeights)

cat('Processing chromosome\n')
for (chr in chr2use) {
  fileName <- str_replace(fileLDChr, "@", toString(chr))
  if (!file.exists(fileName)) {
    cat('\tSkipping chromosome', chr, 'File not found\n')
    next
  }
  outputFileName <- str_replace(fileOutputLDBlocks, '@', toString(chr))
  cat('\t', chr, ': Loading LD from ', basename(fileName), '\n\t\t', sep='')
  mat <- readRDS(fileName)
  mat <- LDSplitMatrix(mat, thrR2=argThrR2, minSize=argMinSize, maxSizeWeightLower=argWeights[1], maxSizeWeightUpper=argWeights[2], maxR2=argMaxR2)
  cat('\t\tWriting LD to', basename(outputFileName), '\n')
  saveRDS(mat, file=outputFileName)
}