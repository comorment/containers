# Calculate counts of missingness in the genotype matrix, i.e., in the columns of the matrix.
#' @param genoMat A FBM.code256 bigSNP genotype matrix (eg, <bigSNP>$genotypes)
#' @return A list of counts of missingness per genotype across all individuals
countMissingGenotypes <-  function(genoMat, cores=nb_cores()) {
  require(bigsnpr)
  big_apply(genoMat, a.FUN=function (x, ind) colSums(is.na(x[,ind])), a.combine='c', ncores = cores)
}

# Replace missing genotypes with zero
#' @param genoMat A FBM.code256 bigSNP genotype matrix (eg, <bigSNP>$genotypes)
#' @return A FBM.code256 bigSNP genotype matrix
zeroMissingGenotypes <- function(genoMat) {
  if (class(genoMat) != "FBM.code256") stop('Argument must be a FBM.code256 object. Received ', class(genoMat))
  genoMat$copy(code=c(0,1,2, rep(0, 253)))
}

# Get the indices of a vector for elements that are numeric
# Haven't found a better way to deal with warnings without doing text based filtering.
#' @param x A vector
getNumericIndices <- function(x) {
  suppressWarnings(which(!is.na(as.numeric(x))))
}

# Complement sumstats with missing information
#' @param sumstats A data.frame with sumstats
#' @param reference A data.frame with reference data to complement sumstats
#' @param colRsidSumstats Name of column with RSID/SNP ID in sumstats
#' @param colRsidRef Name of column with RSID/SNP ID in reference data
#' @param colsKeepReference Vector of columns to merge with sumstats
#' @return A data.frame with merged data of sumstats and reference
complementSumstats <- function(sumstats, reference, colRsidSumstats='SNP', colRsidRef='ID', colsKeepReference=c('CHR','POS')) {
  colsRef <- c(colRsidRef, colsKeepReference)
  merge(sumstats, reference[,colsRef], by.x=colRsidSumstats, by.y=colRsidRef, all.x=T)
}