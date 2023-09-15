# test script checking that all installed libraries are present

# Load the testthat package
library(testthat)

# List of libraries to check
libraries_to_check <- c(
    "brant",
    "brms",
    "broom",
    "carat",
    "car",
    "clusterProfiler",
    "corrplot",
    "DBI",
    "dendextend",
    "glmnet",
    "e1071",
    "fastICA",
    "foreign",
    "geepack",
    "ggthemes",
    "ggpubr",
    "gplots",
    "gridExtra",
    "haven",
    "imputeMissings",
    "lavaan",
    "lme4",
    "lmerTest",
    "lubridate",
    "MASS",
    "MatrixEQTL",
    "mgcv",
    "modelr",
    "moments",
    "MVN",
    "nlme",
    "normentR",
    "officer",
    "parallel",
    "patchwork",
    "pracma",
    "RColorBrewer",
    "Rcpp",
    "readxl",
    "readr",
    "rjags",
    "ROCR",
    "RSQLite",
    "rstan",
    "scales",
    "semptools",
    "semTools",
    "simplecolors",
    "sp",
    "splines",
    "splines2",
    "stats",
    "stats4",
    "survival",
    "survminer",
    "tidyverse",
    "tree",
    "viridis"
)

# Define a test
test_that("Required libraries are installed", {
  missing_libraries <- setdiff(libraries_to_check, installed.packages()[, "Package"])
  expect_true(length(missing_libraries) == 0, 
              sprintf("Missing libraries: %s", paste(missing_libraries, collapse = ", ")))
})