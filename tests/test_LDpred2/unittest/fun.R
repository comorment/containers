library(testthat)
dirScripts <- Sys.getenv('DIR_SCRIPTS')
dirTests <- Sys.getenv('DIR_TESTS')
dirTemp <- Sys.getenv('DIR_TEMP')
fileTutorialSumstats <- Sys.getenv('fileInputSumStats')
source(paste0(dirScripts, '/fun.R'))

context("Test functions")
dta <- data.frame(a=1:3, b=c(1, 'X', 2))
test_that("Test numeric counts", {
  # isNumeric()
  expect_true(isNumeric('1'))
  expect_false(isNumeric('a'))
  expect_true(isNumeric(0))
  expect_equal(c(TRUE, FALSE), isNumeric(c(1, 'a')))
  # isOnlyNumeric()
  expect_true(isOnlyNumeric(1))
  expect_false(isOnlyNumeric('a'))
  expect_true(isOnlyNumeric(1:2))
  expect_false(isOnlyNumeric(c(1, 'a')))
  # getNumericIndices()
  expect_equal(c(1, 3), getNumericIndices(dta$b))
  })

test_that("Test various functions", {
  expect_true(hasAllColumns(dta, c('a','b')))
  expect_true(hasAllColumns(dta, c('a')))
  expect_false(hasAllColumns(dta, c('a','b', 'c')))
  expect_false(hasAllColumns(dta, c('no')))
})

test_that("Test if variable is NA/NULL (isVarNA)", {
  expect_true(isVarNA(NA))
  expect_false(isVarNA(NULL))
  expect_false(isVarNA(c()))
  expect_false(isVarNA(F))
  expect_false(isVarNA('a'))
  expect_false(isVarNA(1:3))
  expect_false(isVarNA(data.frame()))
  # isVarNAorNULL()
  expect_false(isVarNAorNULL(1))
  expect_false(isVarNAorNULL('a'))
  expect_false(isVarNAorNULL(F))
  expect_false(isVarNAorNULL(1:3))
  expect_true(isVarNAorNULL(c()))
  expect_true(isVarNAorNULL(NA))
  expect_true(isVarNAorNULL(NULL))
})

# Test data to use for complementSumstats
# Joining reference to sumstats should result in 3 successful matches on RSID
fileSumstats <- paste0(dirTests, '/unittest/data/sumstats.txt')
sumstats <- bigreadr::fread2(fileSumstats)
reference <- bigreadr::fread2(paste0(dirTests, '/unittest/data/hrc37.txt'))
test_that("Test appending columns to sumstats", {
  # Error due to that one of the default columns (CHR) is not available in the reference data
  expect_error(complementSumstats(sumstats, reference, colRsidSumstats='SNP', colRsidRef='ID'))
  expect_error(complementSumstats(sumstats, reference, colRsidSumstats='BAD COL', colRsidRef='ID'))
  expect_error(complementSumstats(sumstats, reference, colRsidSumstats='SNP', colRsidRef='BAD COL'))
  merged <- complementSumstats(sumstats, reference, colRsidSumstats='SNP', colRsidRef='ID', colsKeepReference=c('#CHROM', 'POS'))
  expect_s3_class(merged, "data.frame")
  expect_equal(nrow(merged), 9)
  expect_equal(sum(!is.na(merged$`#CHROM`)), 3)
  expect_equal(sum(!is.na(merged$POS)), 3)
})

# Test getting the effective sample size, can be provided in multiple ways
# Sumstats (loaded above) contain a column "N".
test_that("Test getting effective sample size", {
  # Define som hypotetical user input
  nES <- 1 # Effective sample size
  nCases <- 10
  nControls <-100
  colEs <- 'N'
  # Various errors
  expect_error(getEffectiveSampleSize(sumstats))
  expect_error(getEffectiveSampleSize(sumstats, effectiveSampleSize=nES, cases=nCases))
  expect_error(getEffectiveSampleSize(sumstats, effectiveSampleSize=nES, cases=nCases, controls=nControls))
  expect_error(getEffectiveSampleSize(sumstats, cases=nCases, colES=colEs))
  expect_error(getEffectiveSampleSize(sumstats, colES='MissingCol'))
  # OK ways
  expect_vector(getEffectiveSampleSize(sumstats, colES=colEs))
  # Manual calculation
  es <- 1/((1/nCases) + (1/nControls))
  expect_equal(getEffectiveSampleSize(sumstats, cases=nCases, controls=nControls), es)
  expect_equal(getEffectiveSampleSize(sumstats, effectiveSampleSize=nES), nES)
  # Manually provided sample size overrides column in sumstats
  expect_equal(getEffectiveSampleSize(sumstats, cases=nCases, controls=nControls, colES=colEs), es)
  expect_equal(getEffectiveSampleSize(sumstats, effectiveSampleSize=nES, colES=colEs), nES)
  # OK, but input is of wrong type
  expect_equal(getEffectiveSampleSize(sumstats, cases=as.character(nCases), controls=as.character(nControls)), es)
  expect_equal(getEffectiveSampleSize(sumstats, effectiveSampleSize=as.character(nES)), nES)
})

# Using the sumstats file to test this may seem wrong, but it should in principle
# be enough to cover the expected behavior of this function
test_that("Test functions used when merging score to existing files", {
  expect_error(verifyScoreOutputFile(fileSumstats, 'score', COLNAMES_ID_PLINK))
  expect_warning(verifyScoreOutputFile(fileSumstats, 'OR', c('CHR_ORG', 'SNP')))
  expect_no_error(verifyScoreOutputFile(fileSumstats, 'score', c('CHR_ORG', 'SNP')))
})

# Test that rename_columns works as expected
test_that("Test rename_columns", {
  expect_equal(rename_columns(sumstats, c('A1', 'A2'), c('A1', 'A2')), sumstats)
  expect_true(hasAllColumns(rename_columns(sumstats, c('A1', 'A2', 'N'), c('EffectAllele', 'OtherAllele', 'Neff')), c('EffectAllele', 'OtherAllele', 'Neff')))
  expect_error(rename_columns(sumstats, c('A1', 'A2'), c('A1', 'A2', 'N')))
  expect_error(rename_columns(sumstats, c('A1', 'A2', 'N'), c('A1', 'A2')))
})

# Create some test data for filtering SNPs
library(bigsnpr, quietly=T)
map <- snp_attach(Sys.getenv('fileOutputSNPR'))$map
drawSnps <- sample(nrow(map), 5)
map <- map[drawSnps,]
snpsExpectedA <- map
snpsExpectedB <- map[4:5,]
fileSnplist <- paste0(dirTemp, '/snplist')
write.table(snpsExpectedB$marker.ID, file=fileSnplist, row.names = F)

test_that('Test filter SNPS', {
  expect_equal(filterFromFile(map, fileTutorialSumstats, colFilter='marker.ID', col='rsid', verbose=FALSE), snpsExpectedA)
  expect_equal(filterFromFile(map, fileSnplist, colFilter='marker.ID', verbose=FALSE), snpsExpectedB)
  expect_equal(filterFromFile(map, fileSnplist, colFilter='marker.ID', col=NA, verbose=FALSE), snpsExpectedB)
  expect_equal(filterFromFile(map$marker.ID, fileSnplist, verbose=FALSE), snpsExpectedB$marker.ID)
  expect_error(filterFromFile(map, fileTutorialSumstats, colFilter='marker.ID', col='bad', verbose=FALSE))
  expect_error(filterFromFile(map, 'missing-file', colMap='marker.ID', verbose=FALSE))
})

# Create some data with similar structure as what is returned from snp_ldpred2_auto
list1 <- list(list(corr_est=1:10, beta_est=rep(0.1, 10)), list(corr_est=1:10, beta_est=rep(0.2, 10)))
list2 <- list(list(corr_est=1:10, beta_est=rep(0.1, 10)), list(corr_est=c(1:9, NA), beta_est=rep(0.2, 10)),
              list(corr_est=1:10, beta_est=rep(0.2, 10)))
list3 <- list2
list3[[4]] <- list(corr_est=rep(NA,10), beta_est=rep(0.2, 10))
test_that('Test filter chains from snp_ldpred2_auto', {
  expect_equal(getBetasAuto(list1), rep(0.15, 10))
  expect_equal(getBetasAuto(list2, verbose=F), rep(0.15, 10))
  expect_equal(getBetasAuto(list3, verbose=F), rep(0.15, 10))
})
