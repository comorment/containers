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
#' @param mergeIDs Variables to use when merging score.
verifyScoreOutputFile <- function (fileName, scoreName, mergeIDs) {
  require(bigreadr, quietly = T)
  if (!file.exists(fileName)) stop('File', fileName, 'does not exist.\n')
  # Inspect that the necessary columns to merge are available in this file (IID and FID)
  tmp <- bigreadr::fread2(fileName, nrows=2)
  cnames <- colnames(tmp)
  if (!hasAllColumns(tmp, mergeIDs)) {
    stop('Necessary ID columns (', paste0(mergeIDs, collapse=', '),') for merging not found in ', fileName, '. Found: ', paste0(cnames, collapse=', '))
  }
  if (scoreName %in% cnames) warning('A column with the designated score name (',scoreName,') already exists in output file ', fileName)
}

# Write the score to a file
#' @param scoreData A data.frame with at least 'family.ID', 'sample.ID' (bigSNPR name for FID/IID) and the score
#' @param outputFile The name of the file to write output to
#' @param scoreName The name of the score in scoreData
#' @param fileMerge Whether to merge output data to an existing file
writeScore <- function (scoreData, outputFile, scoreName, fileMerge=F, mergeIDs=NULL) {
  colsKeep <- c(COLNAMES_ID_BIGSNPR, scoreName)
  if (!hasAllColumns(scoreData, colsKeep)) stop('Necessary columns not present in output data. Found: ', colnames(scoreData))
  outputData <- scoreData[,colsKeep]
  # Rename columns
  newIDcols <- COLNAMES_ID_PLINK
  if (fileMerge) newIDcols <- mergeIDs
  colsKeep[1:2] <- newIDcols
  colnames(outputData) <- colsKeep
  if (fileMerge) {
    require(bigreadr)
    fileData <- bigreadr::fread2(fileOutput)
    outputData <- merge(fileData, outputData, by=newIDcols, all.x=T)
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
#' @param x A variable to test.
isNumeric <- function(x) {
  suppressWarnings(!is.na(as.numeric(x)))
}

# Test if there is only numbers in a variable
isOnlyNumeric <-  function (x) {
  sum(isNumeric(x)) == length(x)
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
  if (nrow(res) != nrRows) warning('The merge resulted in ', nrow(res), ' rows but input contained ', nrRows, ' rows')
  res
}