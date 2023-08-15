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

par <- arg_parser('Split LD matrices into blocks using bigSNPr')
# Mandatory arguments
par <- add_argument(par, "--file-ld-blocks", nargs=1, default="LD_with_blocks_chr@.rds", help="Template name of LD files using @ to indicate chromosome nr")
par <- add_argument(par, "--file-ld-map", nargs=1, default="map.rds", help="Name of LD map file")
par <- add_argument(par, '--file-output-ld-blocks', help='Template name of output files using @ to indicate chromosome nr')

# Optional arguments
par <- add_argument(par, "--chr2use", nargs=Inf, help="List of chromosomes to use (by default it uses chromosomes 1 to 22)")

parsed <- parse_args(par)
# Chromosomes to use
chr2use <- parsed$chr2use
if (any(is.na(chr2use))) chr2use <- 1:22

fileLDBlocks <- parsed$file_ld_blocks
fileOutputLDBlocks <- parsed$file_output_ld_blocks
if (!dir.exists(dirname(fileLDBlocks))) dir.create(dirname(fileLDBlocks))
fileLDMap <- parsed$file_ld_map

for (chr in chr2use) {
  fileName <- str_replace(fileLDBlocks, "@", toString(chr))
  outputFileName <- str_replace(fileOutputLDBlocks, '@', toString(chr))
  print(fileName)
  mat <- readRDS(fileName)
  nc <- ncol(mat)
  sequence <- round(seq_log(nc/30, nc/5, length.out=20))
  splits <- snp_ldsplit(mat, thr_r2 = 0.02, min_size=50, max_size = sequence, max_r2 = 0.1)
  #best_split <- splits %>%
  #  arrange(cost2 * (5 + cost)) %>% slice(1) 
  #str(best_split)
  costs <- with(splits, cost2 * (5 + cost))
  #str(splits)
  best <- splits[order(costs),]
  best <- best[1,]
  #str(best)
  allSize <- best$all_size[[1]]
  str(allSize)
  bestGroup <- rep(seq_along(allSize), allSize)
  mat <- as(as(mat, 'generalMatrix'), 'TsparseMatrix')
  #str(bestGroup)
  mat@x <- ifelse(bestGroup[mat@i + 1L] == bestGroup[mat@j + 1L], mat@x, 0)
  mat <- Matrix::drop0(mat)
  #mat <- as(mat, 'symmetrixMatrix')
  saveRDS(mat, file=outputFileName)
}