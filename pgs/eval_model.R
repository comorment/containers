# post PGS script to compute and print some linear model fit 
# metrics to file between phenotype and PGS score
library(argparser, quietly=T)
library(data.table)
library(stats)
library(broom)

# deal with parsed arguments
par <- arg_parser('evaluate PGS model')
par <- add_argument(par, "--pheno-file", help="phenotype file")
par <- add_argument(par, "--phenotype", help="phenotype name (must be a column header in phenotype file)")
par <- add_argument(par, "--score-file", help="input scores from PGS")
par <- add_argument(par, "--out", help="output stats file prefix (for .txt and .csv)")
parsed <- parse_args(par)

# df
pheno <- fread(parsed$pheno_file, select=c("FID", "IID", parsed$phenotype))
scores <- fread(parsed$score_file, select=c("FID", "IID", "score"))
df <- merge(pheno, scores, by=c("FID", "IID"))
print(df)

# fit lm model and print summary
simple.fit = lm(paste(parsed$phenotype, '~.'), 
    data=df[,-c("FID", "IID")])
print(summary(simple.fit))

print(glance(simple.fit))

# write <out>.txt)
sink(paste(parsed$out, '.txt'))
print(summary(simple.fit))
sink()

# write <out>.csv
write.table(glance(simple.fit), paste(parsed$out, '.csv', sep=""))