# test script checking that all installed libraries are present

# Load the testthat package
library(testthat)

# List of libraries to check
libraries_to_check <- c(
    "AER",
    "argparser", 
    "bigreadr", 
    "bigsnpr",
    "BiocGenerics",
    "BiocManager",
    "caret",
    "DescTools",
    "devtools",
    "data.table",
    "dplyr",
    "EFAtools",
    "flextable",
    "fmsb",
    "foreign",
    "genio",
    "GenomicSEM",
    "ggplot2",
    "gsmr",
    "gtsummary",
    "GWASTools",
    "lightgbm",
    "magrittr",
    "mvtnorm",
    "optparse",
    "parameters",
    "PooledCohort",
    "pROC",
    "qqman",
    "rareGWAMA",
    "reghelper",
    "remotes",
    "RiskScorescvd",
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
    "zlibbioc",
    "AnnotationDbi",
    "arsenal",
    "ASSET",
    "biomaRt",
    "biomartr",
    "brant",
    "brms",
    "broom",
    "carat",
    "car",
    "CCGWAS",
    "cfdr",
    "cfdrCommonControls",
    "cfdr.pleio",
    "circlize",
    "clusterProfiler",
    "correlation",
    "corrplot",
    "CPBayes",
    "DBI",
    "dendextend",
    "e1071",
    "fastICA",
    "fcfdr",
    "foreign",
    "GCPBayes",
    "geepack",
    "ggalluvial",
    "ggcorrplot",
    "ggpubr",
    "ggseg",
    "ggseg3d",
    "ggstar",
    "ggthemes",
    "gitcreds",
    "glmExtras",
    "glmmTMB",
    "glmnet",
    "gplots",
    "gridExtra",
    "gwasglue",
    "gwasglue2",
    "gwasurvivr",
    "gwasvcf",
    "haven",
    "Haplin",
    "hazrd",
    "homologene",
    "hyprcoloc",
    "ieugwasr",
    "imputeMissings",
    "jtools",
    "lavaan",
    "limma",
    "lme4",
    "lmerTest",
    "lubridate",
    "MASS",
    "MatrixEQTL",
    "MendelianRandomization",
    "mgcv",
    "miniCRAN",
    "MRBEE",
    "MVMR",
    "modelr",
    "moments",
    "MplusAutomation",
    "MultiABEL",
    "MVN",
    "nlme",
    "normentR",
    "officer",
    "org.Hs.eg.db",
    "parallel",
    "patchwork",
    "phenotools",
    "pracma",
    "PredictABEL",
    "psych",
    "RColorBrewer",
    "Rcpp",
    "readxl",
    "readr",
    "rjags",
    "ROCR",
    "RSQLite",
    "rstan",
    "rtracklayer",
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
    "TMixClust",
    "tree",
    "viridis")

# Define a test
test_that("Required libraries are installed", {
  missing_libraries <- setdiff(libraries_to_check, installed.packages()[, "Package"])
  expect_true(length(missing_libraries) == 0, 
              sprintf("Missing libraries: %s", paste(missing_libraries, collapse = ", ")))
})