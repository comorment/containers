# Analyze LD matrixes produced by calculateLD.R
library(bigsnpr, quietly = T)
library(argparser, quietly = T)
library(stringr)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
# Load some functions
coms <- commandArgs()
coms <- coms[substr(coms, 1, 7) == '--file=']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))
source(paste0(dirScript, '/funMatrix.R'))

par <- arg_parser('Analyze LD matrixes')
# Files
par <- add_argument(par, '--file-ld-blocks', nargs=1, default='LD_with_blocks_chr@.rds', help='Template name of input files using @ to indicate chromosome nr')
par <- add_argument(par, '--file-ld-map', nargs=1, help='Name of LD map file')
par <- add_argument(par, '--file-out', nargs=1, help='Output file. Content and headers depends on provided arguments.')
par <- add_argument(par, '--file-out-sep', nargs=1, default='\t', help='Separator in output file.')
# Plotting
par <- add_argument(par, '--plot', flag=T, help='Plot the LD structure')
par <- add_argument(par, '--plot-threshold', default=0.2, help='Absolute value of correlation threshold to include in plot.')
par <- add_argument(par, '--plot-scale-x', nargs=1, default='relative', help='X-scale in plot. "relative" indicates position in genetic correlation matrix, "basepair" physical positions.')
par <- add_argument(par, '--plot-file-out', nargs=1, help='Name of plot output file.')
# Summary arguments
par <- add_argument(par, '--non-zeroes', nargs=1, help='"Count", "fraction", or "percentage" non-zero elements in the matrixes')
par <- add_argument(par, '--intervals', flag=T, help='% values from -1 to 1 in intervals of 0.02')
# Figures
# Chromosome selection
par <- add_argument(par, '--chr2use', nargs=Inf, help='List of chromosomes to use (by default it uses chromosomes 1 to 22)')

## Parse arguments
parsed <- parse_args(par)
fileLDBlocks <- parsed$file_ld_blocks
fileLDMap <- parsed$file_ld_map

LDMap <- NULL
if (!is.na(fileLDMap)) LDMap <- readRDS(fileLDMap)
argNonZeroes <- parsed$non_zeroes
if (!is.na(argNonZeroes)) {
  func <- paste0('nonZeroes', str_to_title(argNonZeroes), '(mat)')
}
argIntervals <- parsed$intervals
if (argIntervals) func <- 'intervals(mat)'

# Plotting
argPlot <- parsed$plot
argPlotThreshold <- parsed$plot_threshold
argPlotFileOut <- parsed$plot_file_out
argPlotScaleX <- parsed$plot_scale_x
if (argPlotScaleX == 'basepair' & is.null(LDMap)) stop('Plotting on the basepair scale requires --file-ld-map to be specified')

# Output
fileOut <- parsed$file_out
fileOutSep <- parsed$file_out_sep
output <- NULL
if (!is.na(fileOut)) output <- data.frame()

# Chromosomes to use
chr2use <- parsed$chr2use
if (any(is.na(chr2use))) chr2use <- 1:22

cat('Chromosome\n')
plts <- list()
for (chrom in chr2use) {
  fileName <- str_replace(fileLDBlocks, "@", toString(chrom))
  if (!file.exists(fileName)) {
    warning(fileName, ' not found! Skipping..')
    next
  }
  cat('\t', chrom, ': Loading LD from', basename(fileName), '\n')
  mat <- readRDS(fileName)
  if (argPlot) {
    positions <- NULL
    yLab <- 'Distance (columns)'
    if (argPlotScaleX == 'basepair') {
      positions <- subset(LDMap, chr==chrom)$pos
      yLab <- 'Distance (kb)'
    }
    plt <- plotLD(mat, argPlotThreshold, positions) + labs(x=paste0('Chr ', chrom), y=yLab)
    ix <- paste0('c', chrom)
    plts[[ix]] <- plt
  }
  if (!is.na(argNonZeroes) | argIntervals) {
    res <- eval(parse(text=func))
    nms <- names(res)
    cnames <- c('CHR')
    if (argIntervals) {
      cnames <- c(cnames, nms)
    } else {
      cnames <- c(cnames, func)
    }
    output <- rbind(output, c(chrom, res))
    colnames(output) <- cnames
  }
  gc(verbose=F)
}

if (argPlot) {
  cat('Writing plot', argPlotFileOut, '\n')
  plt <- plot_grid(plotlist=plts, ncol=1)
  ggsave(plt, width=14, height=4*length(chr2use), file=argPlotFileOut, bg='white', limitsize=F)
}

if (!is.na(argNonZeroes)) {
  colnames(output) <- c('chromosome', func)
  cat('Chromosome\t', func, '\n')
  for (i in 1:nrow(output)) {
    cat(output[i,1], '\t', output[i,2], '\n', sep='')
  }
}

if (!is.na(fileOut)) {
  cat('Writing restults to', fileOut, '\n')
  write.table(output, file=fileOut, sep=fileOutSep, quote=T, row.names = F)
} 