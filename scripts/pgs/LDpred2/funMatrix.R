### Function applicable to matrixes of type dsCMatrix (maybe other types aswell)
### Main purpose is to summarize LD matrixes
# Count zeroes in a symmetric matrix. For the dsCMatrix this is just the length of the @slot
#' @param mat A symmetric/square matrix
nonZeroesCount <- function (mat) {
  require(Matrix)
  length(mat@x)*2 + ncol(mat)
}

# Fraction zeroes
nonZeroesFraction <- function (mat) {
  o <- nonZeroesCount(mat)
  o/length(mat)
}

# Percentage zeroes
nonZeroesPercentage <- function (mat) {
  100*nonZeroesFraction(mat)
}

# Percentage entries with correlations between -1 to 1 in steps of 0.02
intervals <- function (mat) {
  steps <- seq(-1, 1, by=.02)
  tb <- table(cut(mat@x, breaks=steps, include.lowest=T))
  tb <- 100*tb/length(mat@x)
  tb
}

roundToThousands <- function (x) round(x/1000)

getLogBlockSequence <- function (nMatCols, lower=30, upper=5, length=20) {
  if (lower <= 0 | upper <= 0) stop('lower/upper weights need to be positive numbers')
  blockSizes <- seq_log(nMatCols/lower, nMatCols/upper, length)
  if (sum(nMatCols < blockSizes)) stop('Requested block size is greater than matrix columns (', nMatCols,')')
  round(blockSizes)
}
# LD splitting of a correlation matrix
# Arguments are passed to bigsnpr::ldsplit
LDSplitMatrix <- function (mat, thrR2, minSize, maxSizeWeightLower, maxSizeWeightUpper, maxR2) {
  nc <- ncol(mat)
  # Maximum variants in each block
  sequence <- round(seq_log(nc/maxSizeWeightLower, nc/maxSizeWeightUpper, length.out=20))
  splits <- snp_ldsplit(mat, thr_r2 = thrR2, min_size=minSize, max_size = sequence, max_r2 = maxR2)
  
  # Select the best split
  costs <- with(splits, cost2 * (5 + cost))
  best <- splits[order(costs),]
  best <- best[1,]
  allSize <- best$all_size[[1]]
  bestGroup <- rep(seq_along(allSize), allSize)
  mat <- as(as(mat, 'generalMatrix'), 'TsparseMatrix')
  # Replace elements outside splits with 0
  mat@x <- ifelse(bestGroup[mat@i + 1L] == bestGroup[mat@j + 1L], mat@x, 0)
  # Drop zeroes
  Matrix::drop0(mat)
}

# Plotting
#' @param mat A correlation matrix
#' @param positions Positions of each matrix column
plotLD <- function (mat,threshold, positions=NULL) {
  require(ggplot2, quietly = T)
  suppressMessages(require(tidyverse, quietly = T, warn.conflicts = F)) # Tidyverse throws some maskings of methods in dplyr
  #require(colorRamps, quietly=T)
  mat <- as(as(mat, 'generalMatrix'), 'TsparseMatrix')
  upper <- (mat@i <= mat@j)
  df <- data.frame(i=mat@i[upper], j=mat@j[upper], r2=mat@x[upper])
  if (!is.null(positions)) {
    df$i <- positions[df$i+1]
    df$j <- positions[df$j+1]
  }
  df$y <- with(df, (j-i)/2)
  plt <- ggplot(subset(df, abs(r2) > threshold)) +
    geom_point(aes(i + y, y, color=r2, alpha=r2), size=rel(0.01)) +
    coord_fixed(ratio=3) + scale_colour_gradientn(colours = rev(heat.colors(100))) +
    scale_y_continuous(labels=roundToThousands) +
    scale_x_continuous(labels=roundToThousands) +
    labs(x='Position', y='Distance') +
    scale_alpha(guide='none')
  plt
}
