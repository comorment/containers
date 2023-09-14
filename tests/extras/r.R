# test script checking that all installed libraries are present

# Load the testthat package
library(testthat)

# List of libraries to check
libraries_to_check <- c(
    "argparser", 
    "bigreadr", 
    "bigsnpr",
    "BiocGenerics",
    "BiocManager",
    "DescTools",
    "devtools",
    "data.table",
    "dplyr",
    "flextable",
    "fmsb",
    "foreign",
    "GenomicSEM",
    "ggplot2",
    "gsmr",
    "gtsummary",
    "GWASTools",
    "magrittr",
    "mvtnorm",
    "optparse",
    "parameters",
    "pROC",
    "qqman",
    "rareGWAMA",
    "reghelper",
    "remotes",
    "rmarkdown",
    "runonce",
    "snpStats",
    "survey",
    "seqminer",
    "stringr",
    "tibble",
    "tidyr",
    "tidyverse",
    "tools",
    "TwoSampleMR",
    "xgboost",
    "zlibbioc"
    )

# Define a test
test_that("Required libraries are installed", {
  missing_libraries <- setdiff(libraries_to_check, installed.packages()[, "Package"])
  expect_true(length(missing_libraries) == 0, 
              sprintf("Missing libraries: %s", paste(missing_libraries, collapse = ", ")))
})