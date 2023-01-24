# simple script to compute and print some model fit metrics  
library(argparser, quietly=T)
library(data.table)
library(stats)

# deal with parsed arguments
par <- arg_parser('evaluate PGS model')
par <- add_argument(par, "--pheno-file", help="phenotype file")
par <- add_argument(par, "--phenotype", help="phenotype name (must be a column header in phenotype file)")
par <- add_argument(par, "--score-file", help="input scores from PGS")
par <- add_argument(par, "--out", help="stats::lm.fit summary")
parsed <- parse_args(par)

# df
pheno <- fread(parsed$pheno_file)
scores <- fread(parsed$score_file)
df <- merge(pheno, scores, by=c("FID", "IID"))
print(df)

# fit lm model and print summary
simple.fit = lm(paste(parsed$phenotype, '~.'), 
    data=df[,-c("FID", "IID")])
print(summary(simple.fit))

# write summary
sink(parsed$out)
print(summary(simple.fit))
sink()