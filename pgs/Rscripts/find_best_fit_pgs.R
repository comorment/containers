
library(argparser)
library(data.table)
library(magrittr)

par <- arg_parser('find best-fit PRS')
par <- add_argument(par, "--phenotype-file", help="Input file with phenotypes")
par <- add_argument(par, "--eigenvec-file", help=".eigenvec input file")
par <- add_argument(par, "--cov-file", help=".cov input file")
par <- add_argument(par, "--phenotype", help="Phenotype ID")
par <- add_argument(par, "--data-prefix", help='file prefix')
par <- add_argument(par, "--thresholds", default="0.001,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1", 
                    help="comma-sep list of threshold values")
par <- add_argument(par, "--nPCs", type="integer", default=6, 
                    help="Integer number of Principal Components (PCs)")
par <- add_argument(par, "--results-file", help="Output file with best-fit results (.csv)")

parsed <- parse_args(par)

p.threshold <- as.double(as.list(strsplit(parsed$thresholds, ',')[[1]]))

phenotype_data <- fread(parsed$phenotype_file)
pcs <- fread(parsed$eigenvec_file, header=F) %>%
    setnames(., colnames(.), c("FID", "IID", paste0("PC",1:parsed$nPCs)) )
covariate <- fread(parsed$cov_file)
pheno <- merge(phenotype_data, covariate) %>%
        merge(., pcs)



# phenotype <- parsed$phenotype
null.r2 <- summary(lm(paste(parsed$phenotype, '~.'), data=pheno[,-c("FID", "IID")]))$r.squared
prs.result <- NULL
for(i in p.threshold){
    pheno.prs <- paste0(parsed$data_prefix, ".", i, ".profile") %>%
        fread(.) %>%
        .[,c("FID", "IID", "SCORE")] %>%
        merge(., pheno, by=c("FID", "IID"))

    model <- lm(paste(parsed$phenotype, '~.'), data=pheno.prs[,-c("FID","IID")]) %>% summary
    #         summary
    model.r2 <- model$r.squared
    prs.r2 <- model.r2-null.r2
    prs.coef <- model$coeff["SCORE",]
    prs.result %<>% rbind(.,
        data.frame(Threshold=i, R2=prs.r2, 
                    P=as.numeric(prs.coef[4]), 
                    BETA=as.numeric(prs.coef[1]),
                    SE=as.numeric(prs.coef[2])))
}
print(prs.result$R2)
# print result
print(prs.result[which.max(prs.result$R2),])
# write
write.table(prs.result[which.max(prs.result$R2),], parsed$results_file, sep=',')