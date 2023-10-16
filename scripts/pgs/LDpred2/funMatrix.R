### Function applicable to matrixes of type dsCMatrix (maybe other types aswell)
### Main purpose is to summarize LD matrixes
# Count zeroes in a symmetric matrix. For the dsCMatrix this is just the length of the @slot
nonZeroesCount <- function (mat) {
  length(mat@x)*2 + ncol(mat)
}

nonZeroesFraction <- function (mat) {
  o <- nonZeroesCount(mat)
  o/length(mat)
}

nonZeroesPercentage <- function (mat) {
  100*nonZeroesFraction(mat)
}

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
