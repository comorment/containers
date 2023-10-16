### Unit tests for functions in scripts/pgs/LDpred2/funMatrix.R
library(testthat)
library(bigsnpr)
dirScripts <- Sys.getenv('DIR_SCRIPTS')
dirTests <- Sys.getenv('DIR_TESTS')
dirLDpredRef <- Sys.getenv('DIR_REF_LDPRED')
source(paste0(dirScripts, '/fun.R'))
source(paste0(dirScripts, '/funMatrix.R'))

test_that('Test zeroes', {
  mat <- readRDS(paste0(dirLDpredRef,'/ldref_hm3_plus/LD_with_blocks_chr22.rds'))
  #print(nonZeroesCount(mat))
  # Upper or lower off-diagonal non-zeroes + the length of the diagonal
  expect_equal(18012387*2+21233, nonZeroesCount(mat))
})

test_that('Test block sequence', {
  matCols <- 100
  expected <- c(10, 12, 14, 17, 20, 24, 29, 35, 42, 50)
  expect_equal(expected, getLogBlockSequence(matCols, 10, 2, 10))
  expect_error(getLogBlockSequence(matCols, 10, 0.2, 10))
})

