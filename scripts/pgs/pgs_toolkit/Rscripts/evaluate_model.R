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
par <- add_argument(par, "--eigenvec-file", help='eigenvec file')
par <- add_argument(par, "--covariate-file", help='covariate file')
par <- add_argument(par, "--out", help="output stats file prefix (for .txt and .csv)")
parsed <- parse_args(par)

# df
pheno <- fread(parsed$pheno_file, select=c("FID", "IID", parsed$phenotype))
scores <- fread(parsed$score_file, select=c("FID", "IID", "score"))
df <- merge(pheno, scores, by=c("FID", "IID"))

# append columns w. PCs to df
pcs <- fread(parsed$eigenvec_file, 
             col.names=c("FID", "IID", paste("PC", 1:parsed$nPCs, sep="")), 
             select=1:(2 + parsed$nPCs))
covariate <- fread(parsed$covariate_file)

df <- merge(df, pcs, by=c("FID", "IID"))
df <- merge(df, covariate, by=c("FID", "IID"))
cols <- colnames(df)[5:length(df)]


# fit model
if (parsed$phenotype_class == "BINARY") {
    null.formula <- paste(parsed$phenotype, "~", paste(cols, sep="", collapse="+"), sep="", collapse="")  %>% as.formula
    null.fit <- glm(null.formula, data=df[,-c("FID", "IID")], family="binomial")
    reg.formula <- paste(parsed$phenotype, "~score+", paste(cols, sep="", collapse="+"), sep="", collapse="")  %>% as.formula
    linear.fit <- glm(reg.formula, data=df[,-c("FID", "IID")], family="binomial")
    # pseudo R2
    null.eval <- NagelkerkeR2(null.fit)
    linear.eval <- NagelkerkeR2(linear.fit)
} else if (parsed$phenotype_class == "CONTINUOUS") {
    null.formula <- paste(parsed$phenotype, "~", paste(cols, sep="", collapse="+"), sep="", collapse="")  %>% as.formula
    null.fit <- lm(null.formula, data=df[,-c("FID", "IID")])
    reg.formula <- paste(parsed$phenotype, "~score+", paste(cols, sep="", collapse="+"), sep="", collapse="")  %>% as.formula
    linear.fit <- lm(reg.formula, data=df[,-c("FID", "IID")])
    # R2
    null.eval <- summary(null.fit)$r.squared
    linear.eval <- summary(linear.fit)$r.squared
}
print(summary(null.fit))
print(glance(null.fit))
print(summary(linear.fit))
print(glance(linear.fit))

if (parsed$phenotype_class == "BINARY") {
    print(paste('Nagelkerke R2 (null model):', null.eval))
    print(paste('Nagelkerke R2 (full model):', linear.eval))
} else if (parsed$phenotype_class == "CONTINUOUS") {
    print(paste('R2 (null model):', null.eval))
    print(paste('R2 (full model):', linear.eval))
}

# write <out>.txt)
sink(paste(parsed$out, '.txt', sep=""))
print(summary(null.fit))
print(summary(linear.fit))
sink()

# write <out>.csv
write.table(rbind(glance(null.fit), glance(linear.fit)), paste(parsed$out, '.csv', sep=""))
