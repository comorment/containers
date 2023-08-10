score <- read.table('containers/usecases/LDpred2_example/output/public-data.score.inf', header=T)
score2 <- read.table('containers/usecases/LDpred2_example/output/public-data.score2.inf', header=T)
score3 <- read.table('containers/usecases/LDpred2_example/output/public-data.score2.inf', header=T)
library(bigsnpr)
bigsnp <- snp_attach('containers/usecases/LDpred2_example/data/public-data3.rds')

set.sed(1)
ind.val <- sample(nrow(bigsnp$genotypes), 350)
y <- bigsnp$fam$affection
pcor(score$score, y, NULL)
pcor(score2$score, y, NULL)
pcor(score3$score, y, NULL)
pcor(score$score[ind.val], y[ind.val], NULL)
pcor(score2$score[ind.val], y[ind.val], NULL)
pcor(score3$score[ind.val], y[ind.val], NULL)
big <- snp_attach('containers/usecases/LDpred2_example/data/EUR.rds')

# This function make a persistent change to the genotype matrix
# I think this is faster than zeroMissingGenotypes that copies the entire matrix
zMiss <-  function (genoMat, cores=nb_cores()) {
  big_apply(genoMat, function(X, ind) {
    # have an idea of progress
    #print(ind[1])
    # access a subset of columns as a standard R matrix
    X.sub <- X[, ind, drop = FALSE]
    # get the location (i, j) of missing values
    ind_na <- which(is.na(X.sub), arr.ind = TRUE)
    # compute the corresponding mean for each column j
    #means <- colMeans(X.sub, na.rm = TRUE)[ind_na[, 2]]
    # update j (relative to subset) to global 'ind'
    ind_na[, 2] <- ind[ind_na[, 2]]
    # fill positions with corresponding means
    X[ind_na] <- 0
  }, a.combine = 'c', block.size = 500, ncores=cores)
}
