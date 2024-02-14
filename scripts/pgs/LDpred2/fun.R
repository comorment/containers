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

# Same as isVarNA above but extended to NULL
isVarNAorNULL <- function (x) {
  isVarNA(x) | is.null(x)
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

# Get effective sample size from various sources in user input
# Note that arguments effectiveSampleSize or cases and controls will override
# effective sample size if provided as a column in sumstats.
#' @param sumstats A data.frame with sumstats
#' @param effectiveSampleSize Precalculated effective sample size
#' @param cases No of cases for a binary trait
#' @param controls No of controls for a binary trait
#' @param colES Column containing effective sample size in sumstats
#' @return Either integer or a vector of integers
getEffectiveSampleSize <- function (sumstats, effectiveSampleSize=NULL, cases=NULL, controls=NULL, colES=NULL) {
  argsCcNA <- isVarNAorNULL(cases) + isVarNAorNULL(controls)
  cases <- as.numeric(cases)
  controls <- as.numeric(controls)
  esInSumstats <- ifelse(isVarNAorNULL(colES), F, colES %in% colnames(sumstats))
  if (argsCcNA == 2 && isVarNAorNULL(effectiveSampleSize) && !esInSumstats) 
    stop("Effective sample size has not been provided as an argument and no such column was found in the sumstats (column ", colES, ")")
  if (esInSumstats) esOut <- sumstats[, colES]
  if (!isVarNAorNULL(effectiveSampleSize)) {
    if (argsCcNA < 2) stop('Do not provide both --effective sample size and --n-cases/--n-controls')
    esOut <- as.numeric(effectiveSampleSize)
    if (!is.numeric(esOut)) stop('Effective sample size needs to be numeric, received: ', effectiveSampleSize)
  }
  # User cannot supply only one of --n-cases and --n-controls
  if (argsCcNA == 1) stop('Provide both --n-cases and --n-controls')
  if (argsCcNA == 0) esOut <- 1/((1/cases) + (1/controls))
  esOut
}

# Rename columns in data.frame
#' @param df A data.frame
#' @param old_names A vector of old column names
#' @param new_names A vector of new column names
#' @return A data.frame with renamed columns
rename_columns <- function(df, old_names, new_names) {
  if (length(old_names) != length(new_names)) {
    stop("The length of the old_names and new_names lists must be the same.")
  }
  colnames(df)[match(old_names, colnames(df))] <- new_names
  return(df)
}

# Filter a data frame or a vector using values in a file
# Mainly used to filter snps
#' @param dta Either a data frame or vector
#' @param fileFilter A file with RSIDs
#' @param colFilter Column name in dta to filter on
#' @param col The column name in fileSNPs if different than the first
#' @param verbose Print progress
#' @return Same object type as dta, filtered for entries in fileFilter
filterFromFile <- function(dta, fileFilter, colFilter=NULL, col=NULL, verbose=T) {
  if (is.data.frame(dta) && !(colFilter %in% colnames(dta))) stop('Missing column in data to filter: ', colFilter)
  if (!file.exists(fileFilter)) stop('Could not find file: ', fileFilter)
  rowsBefore <- length(dta)
  dtaFilter <- data.table::fread(fileFilter, sep='auto', data.table=F)
  if (is.character(col) && !(col %in% colnames(dtaFilter))) stop('Could not find column ', col, ' in file ', fileFilter)
  if (is.integer(col) && !(col %in% 1:ncol(dtaFilter))) stop('Only columns indexed 1-', ncol(dtaFilter),' available in file ', fileFilter)
  if (is.character(col) || is.integer(col)) dtaFilter <- dtaFilter[,col]
  else dtaFilter <- dtaFilter[,1]
  if (verbose) cat('Read', length(dtaFilter), 'rows from', fileFilter, '\n')
  if (is.data.frame(dta)) {
    dta <- dta[dta[,colFilter] %in% dtaFilter,]
    nKept <- nrow(dta)
  } else {
    dta <- dta[dta %in% dtaFilter]
    nKept <- length(dta)
  }
  if (verbose) cat('Retained', nrow(dta), 'out of', nKept, 'rows\n')
  dta
}

# Get the betas from snp_ldpred2_auto
#' @param fitAuto The return value form snp_ldpred2_auto
#' @param quantile Range of estimates to keep
getBetasAuto <- function (fitAuto, quantile=0.95, verbose=T) {
  corrRange <- sapply(fitAuto, function (auto) diff(range(auto$corr_est)))
  # Keep chains that pass the filtering below
  keep <- (corrRange > (0.95 * quantile(corrRange, 0.95, na.rm=T)))
  nas <- sum(is.na(keep))
  if (nas > 0 && verbose) cat('Omitting', nas, 'chains out of', length(keep), ' due to missing values in correlation range\n')
  keep[is.na(keep)] <- F
  beta <- rowMeans(sapply(fitAuto[keep], function (auto) auto$beta_est))
  beta
}
