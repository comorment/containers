library(testthat)
library(bigreadr, quietly=T)
dirScripts <- Sys.getenv('DIR_SCRIPTS')
source(paste0(dirScripts, '/fun.R'))
# These environmental variables are provided by scripts/extended.sh
fileExisting <- Sys.getenv('fileExisting')
scoreNameExisting <- Sys.getenv('scoreNameExisting')
scoreNameNew <- Sys.getenv('scoreNameNew')

context('Test results from scripts/extended.sh')

test_that("Appended score output", {
  tmp <- bigreadr::fread2(fileExisting, nrows=2)
  cnames <- colnames(tmp)
  cnamesExp <- c(COLNAMES_ID_PLINK, scoreNameExisting, scoreNameNew)
  expect_true(hasAllColumns(tmp, cnamesExp), 
	paste('Expected columns', paste0(cnamesExp, collapse=','), 'but', paste0(colnames(tmp), collapse=','), 'were found in', fileExisting))
})
