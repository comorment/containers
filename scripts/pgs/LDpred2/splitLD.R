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
par <- add_argument(par, "--file-ld-blocks", nargs=1, default="LD_with_blocks_chr@.rds", help="Template name of LD files using @ to indicate chromosome nr")
par <- add_argument(par, "--file-ld-map", nargs=1, default="map.rds", help="Name of LD map file")
par <- add_argument(par, '--file-output-ld-blocks', help='Template name of output files using @ to indicate chromosome nr')

## Optional arguments
par <- add_argument(par, "--chr2use", nargs=Inf, help="List of chromosomes to use (by default it uses chromosomes 1 to 22)")
# Arguments to bigsnpr::snp_ldsplit
par <- add_argument(par, '--max-k', default=500, help='Maximum number of blocks to consider.')
par <- add_argument(par, '--max-r2', default=0.3, help='Maximum squared correlation allowed for variants in different blocks.')
par <- add_argument(par, '--threshold-r2', default=0.02, help='Ignore squared correlations below this value.')
par <- add_argument(par, '--min-block-size', default=50, help='Minimum number of variants in each block.')
# Only one of --max-block-size can be used
par <- add_argument(par, '--max-block-size', nargs=Inf, help='Maxium numboer of variants. Either integer or vector. If vector, the "best" value will be used.')
par <- add_argument(par, '--max-block-size-weights', nargs=3, help='[DEFAULT] Pass [LOWER] [UPPER] [LENGTH]. As --max-block-size, but gives a sequence from smallest to largest block, 
                    evenly spaced logartitmically. [LOWER] and [UPPER] are used to divide column length in each matrix, thus the higher value, the lower number of blocks.
                    Thus [LOWER] should be a bigger weight than [UPPER].')

parsed <- parse_args(par)
# Chromosomes to use
chr2use <- parsed$chr2use
if (any(is.na(chr2use))) chr2use <- 1:22

fileLDBlocks <- parsed$file_ld_blocks
fileOutputLDBlocks <- parsed$file_output_ld_blocks
if (!dir.exists(dirname(fileLDBlocks))) dir.create(dirname(fileLDBlocks))
fileLDMap <- parsed$file_ld_map

argMaxK <- parsed$max_k
argMaxR2 <- parsed$max_r2
argThresholdR2 <- parsed$threshold_r2
argMinBlockSize <- parsed$min_block_size
argMaxBlockSize <- parsed$max_block_size
argMaxBlockSizeWeights <- parsed$max_block_size_weights

for (chr in chr2use) {
  fileName <- str_replace(fileLDBlocks, "@", toString(chr))
  outputFileName <- str_replace(fileOutputLDBlocks, '@', toString(chr))
  cat('\t', chr, ': Loading LD from', basename(fileName), '\n')
  mat <- readRDS(fileName)
  nc <- ncol(mat)
  #sequence <- round(seq_log(nc/30, nc/5, length.out=20))
  blocksMax <- getLogBlockSequence(nc)
  if (!isVarNA(argMaxBlockSize)) blocksMax <- argMaxBlockSize
  if (!isVarNA(argMaxBlockSizeWeights)) blocksMax <- getLogBlockSequence(nc, argMaxBlockSizeWeights[1], argMaxBlockSizeWeights[2], argMaxBlockSizeWeights[3])
  splits <- snp_ldsplit(mat, thr_r2 = argThresholdR2, min_size=argMinBlockSize, max_size = blocksMax, max_r2 = argMaxR2, max_K=argMaxK)
  #best_split <- splits %>%
  #  arrange(cost2 * (5 + cost)) %>% slice(1) 
  #str(best_split)
  costs <- with(splits, cost2 * (5 + cost))
  #str(splits)
  best <- splits[order(costs),]
  best <- best[1,]
  #str(best)
  allSize <- best$all_size[[1]]
  #str(allSize)
  bestGroup <- rep(seq_along(allSize), allSize)
  mat <- as(as(mat, 'generalMatrix'), 'TsparseMatrix')
  mat@x <- ifelse(bestGroup[mat@i + 1L] == bestGroup[mat@j + 1L], mat@x, 0)
  mat <- Matrix::drop0(mat)
  cat('\tWriting LD to', basename(outputFileName), '\n')
  saveRDS(mat, file=outputFileName)
}