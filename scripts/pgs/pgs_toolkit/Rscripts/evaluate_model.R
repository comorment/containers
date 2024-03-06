# post PGS script to compute and print some linear model fit 
# metrics to file between phenotype and PGS score
library(argparser, quietly=T)
library(data.table)
library(stats)
library(broom)
library(dplyr)
library(fmsb)

# deal with parsed arguments
par <- arg_parser('evaluate PGS model')
par <- add_argument(par, "--pheno-file", help="phenotype file")
par <- add_argument(par, "--phenotype", help="phenotype name (must be a column header in phenotype file)")
par <- add_argument(par, "--phenotype-class", help="phenotype class (must be either 'BINARY' or 'CONTINUOUS')")
par <- add_argument(par, "--score-file", help="input scores from PGS")
par <- add_argument(par, "--nPCs", help="number of principal components", default=6)
par <- add_argument(par, "--continuous-covariates", help="additional column names to include as continuous covariates", nargs='+')
par <- add_argument(par, "--categorical-covariates", help="additional column names to include as categorical covariates", nargs='+')
par <- add_argument(par, "--out", help="output stats file prefix (for .txt and .csv)")
parsed <- parse_args(par)

# list of columns to read from pheno_file
continuous_cols <- c(paste("PC", 1:parsed$nPCs, sep=""))
categorical_cols <- c()
if (!is.na(parsed$continuous_covariates)) {
    continuous_cols <- unlist(c(continuous_cols, strsplit(parsed$continuous_covariates, ',')))
}
if (!is.na(parsed$categorical_covariates)) {
    categorical_cols <- unlist(c(categorical_cols, strsplit(parsed$categorical_covariates, ',')))
}
data_columns <- unlist(c("FID", "IID", parsed$phenotype, continuous_cols, categorical_cols))
pheno <- fread(parsed$pheno_file, select=data_columns)

# combine all data in one dataframe
scores <- fread(parsed$score_file, select=c("FID", "IID", "score"))
pheno <- merge(pheno, scores, by=c("FID", "IID"))

# fit model
model_covariates <- paste(paste(continuous_cols, sep="", collapse="+"), 
                          '+', paste("as.factor(", categorical_cols, ")", sep="", collapse="+"), 
                          sep="", collapse="+")
if (parsed$phenotype_class == "BINARY") {
    null.formula <- paste(parsed$phenotype, "~", model_covariates, sep="", collapse="")  %>% as.formula
    null.fit <- glm(null.formula, data=pheno[,-c("FID", "IID")], family="binomial")
    reg.formula <- paste(parsed$phenotype, "~score+",model_covariates, sep="", collapse="")  %>% as.formula
    linear.fit <- glm(reg.formula, data=pheno[,-c("FID", "IID")], family="binomial")
    nocov.formula <- paste(parsed$phenotype, "~score", sep="", collapse="")  %>% as.formula
    nocov.fit <- glm(nocov.formula, data=pheno[,-c("FID", "IID")], family="binomial")
    # pseudo R2
    null.eval <- NagelkerkeR2(null.fit)
    linear.eval <- NagelkerkeR2(linear.fit)
    nocov.eval <- NagelkerkeR2(nocov.fit)
    # odds ratios with confidence 95% confidence intervals
    null.or <- exp(cbind(OR_null=coef(null.fit), confint(null.fit)))
    linear.or <- exp(cbind(OR=coef(linear.fit), confint(linear.fit)))
    nocov.or <- exp(cbind(OR_nocov=coef(null.fit), confint(nocov.fit)))
} else if (parsed$phenotype_class == "CONTINUOUS") {
    null.formula <- paste(parsed$phenotype, "~", model_covariates, sep="", collapse="")  %>% as.formula
    null.fit <- lm(null.formula, data=pheno[,-c("FID", "IID")])
    reg.formula <- paste(parsed$phenotype, "~score+", model_covariates, sep="", collapse="")  %>% as.formula
    linear.fit <- lm(reg.formula, data=pheno[,-c("FID", "IID")])
    nocov.formula <- paste(parsed$phenotype, "~score", sep="", collapse="")  %>% as.formula
    nocov.fit <- lm(nocov.formula, data=pheno[,-c("FID", "IID")])
    # R2
    null.eval <- summary(null.fit)$r.squared
    linear.eval <- summary(linear.fit)$r.squared
    nocov.eval <- summary(nocov.fit)$r.squared    
}
# print summaries
print(summary(null.fit))
print(glance(null.fit))
print(summary(linear.fit))
print(glance(linear.fit))
print(summary(nocov.fit))
print(glance(nocov.fit))

if (parsed$phenotype_class == "BINARY") {
    print(paste('Nagelkerke R2 (null model):', null.eval))
    print(summary(null.or))
    print(paste('Nagelkerke R2 (full model):', linear.eval))
    print(summary(linear.or))
    print(paste('Nagelkerke R2 (no covariate model):', nocov.eval))
    print(summary(nocov.or))
} else if (parsed$phenotype_class == "CONTINUOUS") {
    print(paste('R2 (null model):', null.eval))
    print(paste('R2 (full model):', linear.eval))
    print(paste('R2 (no covariate model):', nocov.eval))
}

# write <out>.txt)
sink(paste(parsed$out, '.txt', sep=""))
print(summary(null.fit))
print(summary(linear.fit))
print(summary(nocov.fit))
sink()

# write <out>.csv
write.table(rbind(glance(null.fit), glance(linear.fit), glance(nocov.fit)), paste(parsed$out, '.csv', sep=""))

if (parsed$phenotype_class == "BINARY") {
    # write <out>.or.txt with ORs
    sink(paste(parsed$out, '.or.txt', sep=""))
    print(summary(null.or))
    print(summary(linear.or))
    print(summary(nocov.or))
    sink()

    # write <out>.or.csv with ORs
    write.table(null.or, paste(parsed$out, '.null.or.csv', sep=""))
    write.table(linear.or, paste(parsed$out, '.full.or.csv', sep=""))
    write.table(nocov.or, paste(parsed$out, '.nocov.or.csv', sep=""))
}

