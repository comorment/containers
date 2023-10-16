### Unit tests for functions in scripts/pgs/LDpred2/funMatrix.R
library(testthat)
library(bigsnpr, quietly=T)
dirScripts <- Sys.getenv('DIR_SCRIPTS')
dirTests <- Sys.getenv('DIR_TESTS')
dirLDpredRef <- Sys.getenv('DIR_REF_LDPRED')
source(paste0(dirScripts, '/fun.R'))
source(paste0(dirScripts, '/funMatrix.R'))

test_that('Test matrix non-zero elements', {
  mat <- readRDS(paste0(dirLDpredRef,'/ldref_hm3_plus/LD_with_blocks_chr22.rds'))
  # Count the number of zeroes as a file verification
  o <- nonZeroesCount(mat)
  expect_equal(36003541, o)
  o <- nonZeroesFraction(mat)
  expect_equal(0.08, o, 0.001)
  o <- nonZeroesPercentage(mat)
  expect_equal(7.99, o, 0.001)
})

test_that('Test getLogBlockSequence', {
  matCols <- 100
  expected <- c(10, 12, 14, 17, 20, 24, 29, 35, 42, 50)
  expect_equal(expected, getLogBlockSequence(matCols, 10, 2, 10))
  expect_error(getLogBlockSequence(matCols, 10, 0.2, 10))
})

test_that('Test LDSplitMatrix error handling', {
  require(Matrix)
  mat <- readRDS(paste0(dirLDpredRef,'/ldref_hm3_plus/LD_with_blocks_chr22.rds'))
  expect_error(LDSplitMatrix(mat, thrR2=0.02, minSize=350, maxSizeWeightLower=70, maxSizeWeightUpper=65, maxR2=0.3))
})
