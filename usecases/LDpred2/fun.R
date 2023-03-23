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

# Test if x is NA
# R's built in function is.na is annoying due to that it causes troubles when
# used in conditioning where a variable can be either NA or anything else. For instance
# if the variable tested is a vector this will yield a warning as is.na will return a list
# of booleans when applied to a vector. This function will simply test if the variable itself
# is NA
isVarNA <- function (x) {
  tp <- typeof(x)
  if (tp == 'logical') {
    o <- ifelse(is.null(x), F, is.na(x))
  } else return(F)
}

# Test if x is numeric
# Haven't found a better way to deal with warnings without doing text based filtering.
isNumeric <- function(x) {
  suppressWarnings(!is.na(as.numeric(x)))
}

# Get the indices of a vector for elements that are numeric
#' @param x A vector
getNumericIndices <- function(x) {
  which(isNumeric(x))
}

# Complement sumstats with missing information.
#' @param sumstats A data.frame with sumstats
#' @param reference A data.frame with reference data to complement sumstats
#' @param colRsidSumstats Name of column with RSID/SNP ID in sumstats
#' @param colRsidRef Name of column with RSID/SNP ID in reference data
#' @param colsKeepReference Vector of columns to merge with sumstats
#' @return A handsome data.frame with merged data of sumstats and reference
complementSumstats <- function(sumstats, reference, colRsidSumstats='SNP', colRsidRef='ID', colsKeepReference=c('CHR','POS')) {
  require(data.table, quietly=T) # merge in this package is supposedly faster than base::merge and works the same
  if (!colRsidSumstats %in% colnames(sumstats)) stop('SNP ID column in sumstats (', colRsidSumstats, ') not found')
  if (!colRsidRef %in% colnames(reference)) stop('SNP ID column in reference data (', colRsidRef, ') not found')
  nrRows <- nrow(sumstats)
  colsRef <- c(colRsidRef, colsKeepReference)
  colsRefIntersect <- intersect(colsRef, colnames(reference)) 
  colsRefMissing <- setdiff(colsRef, colsRefIntersect)
  if (length(colsRefMissing) > 0) stop(paste0('Column(s) ', paste0(colsRefMissing, collapse=','), ' was not found in reference data'))
  res <- data.table::merge.data.table(sumstats, reference[,colsRef], by.x=colRsidSumstats, by.y=colRsidRef, all.x=T)
  if (nrow(res) != nrRows) stop('The merge resulted in ', nrow(res), ' but input contained ', nrow(res))
  res
}