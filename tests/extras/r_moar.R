# test script checking that all installed libraries are present

# Load the testthat package
library(testthat)

# List of libraries to check
libraries_to_check <- c(
    "brant",
    "brms",
    "broom",
    "CARAT",
    "car",
    "clusterProfiler",
    "corrplot",
    "DBI",
    "dendextend",
    "glmnet",
    "e1071",
    "fastICA",
    "foreign",
    "gamm",
    "geepack",
    "ggthemes",
    "ggpubr",
    "gplots",
    "gridExtra",
    "haven",
    "imputeMissings",
    "Lavaan",
    "lme4",
    "lmerTest",
    "lubridate",
    "MASS",
    "MatrixEQTL",
    "mgcv",
    "modelr",
    "moments",
    "mvn",
    "nlme",
    "normentR",
    "officer",
    "parallel",
    "patchwork",
    "pracma",
    "RColorBrewer",
    "Rcpp",
    "readxl",
    "RJags",
    "ROCR",
    "RSQLite",
    "RStan",
    "scales",
    "semptools ",
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