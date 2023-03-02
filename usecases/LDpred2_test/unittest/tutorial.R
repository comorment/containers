library(testthat)
library(bigsnpr, quietly=T)
dirTests <- Sys.getenv('DIR_TESTS')
context('Test results from tutorial replication')

# Prerequisites
obj.bigSNP <- snp_attach(Sys.getenv('fileOutputSNPR'))
G <- obj.bigSNP$genotypes
y <- obj.bigSNP$fam$affection
# Sampling of individuals according to tutorial
set.seed(1)
samp <- sample(nrow(G), 350) # They call this the model validation sample
samp <- setdiff(rows_along(G), samp) # Evaluatio/test sample

test_that("Infinitessimal score output", {
  res <- read.table(paste0(dirTests, '/output/public-data.score.inf'), header=T)
  # The number of individuals should equal the number of rows in the score file (+1 for headers)
  expect_equal(nrow(obj.bigSNP$fam), nrow(res))
  cr <- pcor(y[samp], res$score[samp], NULL)
  cr <- substr(cr*100, 1, 2)
  # Our results differ slightly, but equality up to the third decimal should be sufficient.
  expect_equal(cr, c("31", "16", "45"))
  })

test_that("Auto score output", {
  res <- read.table(paste0(dirTests, '/output/public-data.score.auto'), header=T)
  # The number of individuals should equal the number of rows in the score file (+1 for headers)
  expect_equal(nrow(obj.bigSNP$fam), nrow(res))
  cr <- pcor(y[samp], res$score[samp], NULL)
  cr <- substr(cr*100, 1, 2)
  expect_equal(cr, c("49", "36", "60"))
})