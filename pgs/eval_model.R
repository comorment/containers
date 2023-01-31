# post PGS script to compute and print some linear model fit 
# metrics to file between phenotype and PGS score
library(argparser, quietly=T)
library(data.table)
library(stats)
library(broom)
library(dplyr)

# deal with parsed arguments
par <- arg_parser('evaluate PGS model')
par <- add_argument(par, "--pheno-file", help="phenotype file")
par <- add_argument(par, "--phenotype", help="phenotype name (must be a column header in phenotype file)")
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

# # fit lm model and print summary (not accounting for PCs/covariates)
# simple.fit = lm(paste(parsed$phenotype, '~.'), 
#     data=df[,-c("FID", "IID")])

# print(summary(simple.fit))
# print(glance(simple.fit))

# append columns w. PCs to df
pcs <- fread(parsed$eigenvec_file, 
             col.names=c("FID", "IID", paste("PC", 1:parsed$nPCs, sep="")), 
             select=1:(2 + parsed$nPCs))
covariate <- fread(parsed$covariate_file)

df <- merge(df, pcs, by=c("FID", "IID"))
df <- merge(df, covariate, by=c("FID", "IID"))
cols <- colnames(df)[5:length(df)]
reg.formula <- paste(parsed$phenotype, "~score+", paste(cols, sep="", collapse="+"), sep="", collapse="")  %>% as.formula

# fit model
linear.fit <- lm(reg.formula, data=df[,-c("FID", "IID")])
print(summary(linear.fit))
print(glance(linear.fit))

# write <out>.txt)
sink(paste(parsed$out, '.txt'))
print(summary(linear.fit))
sink()

# write <out>.csv
write.table(glance(linear.fit), paste(parsed$out, '.csv', sep=""))