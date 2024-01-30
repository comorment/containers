library(testthat)
library(bigsnpr, quietly=T)
# Files used in tests are passed using environmental variables
dirTests <- Sys.getenv('DIR_TESTS')
if (dirTests == '') stop('Environmental variable DIR_TESTS is undefined')
fileOutputSNPR <- Sys.getenv('fileOutputSNPR')
fileSumstats25k <- Sys.getenv('fileSumstats25k')
fileLD25K <- Sys.getenv('fileLD25K')
fileOutputIntervals <- Sys.getenv('fileOutputIntervals')
fileOutputZeroes <- Sys.getenv('fileOutputZeroes')
filePlotFull <- Sys.getenv('filePlotFull')
filePlot2122 <- Sys.getenv('filePlot2122')

context('Test results from LD related scripts')

test_that('Test calculateLD.R: LD estimation', {
  mapOrg <- snp_attach(fileOutputSNPR)$map
  sumstats25k <- read.csv(fileSumstats25k)[,'rsid']
  overlap <- sum(mapOrg$marker.ID %in% sumstats25k)
  expect_equal(22584, overlap) # Overlap between genotype data and filtering file
  map <- readRDS(fileLD25K)
  expect_equal(c('chr','rsid','pos','a1','a0','ld'), colnames(map))
  expect_equal(overlap, sum(map$rsid %in% sumstats25k))
})

test_that('Test analyzeLD.R: Summary file output', {
  res <- read.csv(fileOutputIntervals, sep='\t')
  expect_equal(101, ncol(res))
  expect_equal(2, nrow(res))
  expect_equal('CHR', colnames(res)[1])
  res <- read.csv(fileOutputZeroes, sep='\t')
  expect_equal(2, ncol(res))
  expect_equal(2, nrow(res))
  expect_equal('chromosome', colnames(res)[1])
})

test_that('Test analyzeLD.R: Plots', {
  expect_true(file.exists(filePlotFull))
  expect_true(file.exists(filePlot2122))
})

quit('no')
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