### Unit tests for functions in scripts/pgs/LDpred2/funMatrix.R
library(testthat)
dirScripts <- Sys.getenv('DIR_SCRIPTS')
dirTests <- Sys.getenv('DIR_TESTS')
dirLDpredRef <- Sys.getenv('DIR_REF_LDPRED')
source(paste0(dirScripts, '/funMatrix.R'))

test_that('Test zeroes', {
  mat <- readRDS(paste0(dirLDpredRef,'/ldref_hm3_plus/LD_with_blocks_chr22.rds'))
  print(nonZeroesCount(mat))
  # Upper or lower off-diagonal non-zeroes + the length of the diagonal
  expect_equal(18012387*2+21233, nonZeroesCount(mat))
})

