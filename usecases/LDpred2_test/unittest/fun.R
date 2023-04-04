library(testthat)
dirScripts <- Sys.getenv('DIR_SCRIPTS')
dirTests <- Sys.getenv('DIR_TESTS')
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

test_that("Test if variable is NA (isVarNA)", {
  expect_true(isVarNA(NA))
  expect_false(isVarNA(NULL))
  expect_false(isVarNA(c()))
  expect_false(isVarNA(F))
  expect_false(isVarNA('a'))
  expect_false(isVarNA(1:3))
  expect_false(isVarNA(data.frame()))
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

# Using the sumstats file to test this may seem wrong, but it should in principle
# be enough to cover the expected behavior of this function
test_that("Test functions used when merging score to existing files", {
  expect_error(verifyScoreOutputFile(fileSumstats, 'score', COLNAMES_ID_PLINK))
  expect_warning(verifyScoreOutputFile(fileSumstats, 'OR', c('CHR_ORG', 'SNP')))
  expect_no_error(verifyScoreOutputFile(fileSumstats, 'score', c('CHR_ORG', 'SNP')))
})
