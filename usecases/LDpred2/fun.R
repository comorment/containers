# Calculate counts of missingness in the genotype matrix, i.e., in the columns of the matrix.
#' @param genoMat A FBM.code256 bigSNP genotype matrix (eg, <bigSNP>$genotypes)
#' @return A list of counts of missingness per genotype across all individuals
countMissingGenotypes <-  function(genoMat) {
  require(bigsnpr)
  counts <- big_apply(genoMat, a.FUN=function (x, ind) colSums(is.na(x[,ind])), a.combine='c')
  return(counts)
}