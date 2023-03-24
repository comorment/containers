# Family ID and individual ID
COLNAMES_ID_PLINK <- c('FID', 'IID')
COLNAMES_ID_BIGSNPR <- c('family.ID', 'sample.ID')

# Tests whether a set of columns exist in a data.frame
#' @param dta A data.frame
#' @param cols A vector of columns to look for
#' @return TRUE if all dta has cols, FALSE otherwise
hasAllColumns <- function (dta, cols) {
  sum(cols %in% colnames(dta)) == length(cols)
}

# Verify that an existing file to append scores to meet the requirements
#' @param fileName A file to verify
#' @param scoreName The name of the score to place in the file
verifyScoreOutputFile <- function (fileName, scoreName) {
  if (!file.exists(fileName)) stop('File', fileName, 'does not exist.\n')
  # Inspect that the necessary columns to merge are available in this file (IID and FID)
  tmp <- bigstatsr::fread2(fileName, nrows=2)
  if (!hasAllColumns(tmp, COLNAMES_ID_PLINK)) {
    stop('Necessary ID columns (', paste0(COLNAMES_ID_PLINK, collapse=', '),'). Found: ', paste0(colnames(tmp), collapse=', '))
  }
}

# Write the score to a file
#' @param scoreData A data.frame with at least 'family.ID', 'sample.ID' (bigSNPR name for FID/IID) and the score
#' @param outputFile The name of the file to write output to
#' @param scoreName The name of the score in scoreData
#' @param merge Wheter to merge output data to an existing file
writeScore <- function (scoreData, outputFile, scoreName, merge=F) {
  colsKeep <- c(COLNAMES_ID_BIGSNPR, scoreName)
  if (!hasAllColumns(scoreData, colsKeep)) stop('Necessary columns not present in output data. Found: ', colnames(scoreData))
  outputData <- scoreData[,colsKeep]
  # Rename to stick with plink naming
  colsKeep[1:2] <- COLNAMES_ID_PLINK
  colnames(outputData) <- colsKeep
  if (merge) {
    require(bigstatsr)
    fileData <- bigstatsr::fread2(fileOutput) 
    outputData <- merge(fileData, scoreData, by=COLNAMES_ID_PLINK, all.x=T)
  }
  write.table(outputData, file=fileOutput, row.names = F, quote=F)
}

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
