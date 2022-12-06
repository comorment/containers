# Calculate polygenic scores using ldpred2
# this script is an adaptation of the demo script available at the bigsnpr homepage
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(tools)
library(argparser, quietly=T)
par <- arg_parser('Calculate polygenic scores using ldpred2')
# Mandatory arguments (files)
par <- add_argument(par, "file-geno", help="Input .rds (bigSNPR) file with genotypes")
par <- add_argument(par, "file-sumstats", help="Input file with GWAS summary statistics")
par <- add_argument(par, "file-output", help="Output file with calculated PGS")
# Optional files
par <- add_argument(par, "--file-keep-snps", help="File with RSIDs of SNPs to keep")
par <- add_argument(par, "--file-pheno", help="File with phenotype data (if not part of BED file")
par <- add_argument(par, "--file-gene-corr", help="Filename with LD and genetic correlation, if omitted it will be estimated")
# Directories
par <- add_argument(par, "--dir-genetic-maps", default=tempdir(), 
                    help="Directory containing 1000 Genomes genetic maps. Either a directory to store files to be downloaded, or a directory contaning the unpacked files.")
# Phenotype
par <- add_argument(par, "--col-pheno", help="Column name of phenotype in --file-pheno.", nargs=1)
par <- add_argument(par, "--col-pheno-from-fam", help="Use phenotype in fam file", nargs=0)
# Genotype
par <- add_argument(par, "--geno-ld-sample", help="Draw N random individuals when performing LD estimation.", nargs=1, default=0)
par <- add_argument(par, "--geno-impute", help="Imputation method for missing genotypes (preimpute genotypes to avoid warning).", 
                    nargs=1, default="mean0")
# Sumstats file.
par <- add_argument(par, "--col-chr", help="CHR number column", default="CHR", nargs=1)
par <- add_argument(par, "--col-snp-id", help="SNP ID (RSID) column", default="SNP", nargs=1)
par <- add_argument(par, "--col-A1", help="Effective allele column", default="A1", nargs=1)
par <- add_argument(par, "--col-A2", help="Noneffective allele column", default="A2", nargs=1)
par <- add_argument(par, "--col-bp", help="SNP position column", default="BP", nargs=1)
par <- add_argument(par, "--col-stat", help="Effect estimate column", default="BETA", nargs=1)
par <- add_argument(par, "--col-stat-se", help="Effect estimate standard error column", default="BETA_SE", nargs=1)
par <- add_argument(par, "--col-pvalue", help="P-value column", default="P", nargs=1)
par <- add_argument(par, "--col-n", help="Effective sample size. Override with --effective-sample-size", default="N", nargs=1)
par <- add_argument(par, "--stat-type", help="Effect estimate type (BETA for linear, OR for odds-ratio", default="BETA", nargs=1)
par <- add_argument(par, "--effective-sample-size", help="Effective sample size, if unavailable in sumstats (--col-n)", nargs=1)
# Polygenic score
par <- add_argument(par, "--name-score", help="Set column name for the created score", nargs=1, default='score')
# Parameters to LDpred
par <- add_argument(par, "--genetic-maps-type", default="hapmap", help="Which genetic map to use, hapmap or OMNI.")
par <- add_argument(par, "--window-size", help="Window size in centimorgans, used for LD calculation", default=3)
par <- add_argument(par, "--hyper-p-length", help="Length of hyperparameter p sequence to use for ldpred-auto", default=30)
# Others
par <- add_argument(par, "--ldpred-mode", help='Ether "auto" or "inf" (infinitesimal)', default="inf")
par <- add_argument(par, "--cores", help="Specify the number of processor cores to use, otherwise use the available", default=nb_cores())
par <- add_argument(par, '--set-seed', help="Set a seed for reproducibility", nargs=1)

parsed <- parse_args(par)

### Mandatory
fileGeno <- parsed$file_geno
fileSumstats <- parsed$file_sumstats
fileOutput <- parsed$file_output
### Optional
fileKeepSNPs <- parsed$file_keep_snps
filePheno <- parsed$file_pheno
### Directories
dirGeneticMaps <- parsed$dir_genetic_maps
### Genotype
genoLDSample <- parsed$geno_ld_sample
genoImpute <- parsed$geno_impute
genoImputeValid <- c('mode', 'mean0', 'mean2', 'random')
if (!genoImpute %in% genoImputeValid) stop('--geno-impute accepts the following values: ',paste0(genoImputeValid, collapse=', '))
# Sumstats file
colChr <- parsed$col_chr
colSNPID <- parsed$col_snp_id
colA1 <- parsed$col_A1
colA2 <- parsed$col_A2
colBP <- parsed$col_bp
colStat <- parsed$col_stat
colStatSE <- parsed$col_stat_se
colPValue <- parsed$col_pvalue
colN <- parsed$col_n
# Column pheno (needs to account for when phenotype is stored in the fam file)
colPheno <- parsed$col_pheno
colPhenoFromFam <- parsed$col_pheno_from_fam
if (!is.na(colPheno) & !is.na(colPhenoFromFam)) stop("Only one of --col-pheno and --col-pheno-from-fam should be provided")
if (!is.na(colPhenoFromFam)) colPheno <- 'affection'
# Polygenic score
nameScore <- parsed$name_score
# Parameters to LDpred
parGeneticMapsType <- parsed$genetic_maps_type
parWindowSize <- parsed$window_size
parHyperPLength <- parsed$hyper_p_length
# Others
argEffectiveSampleSize <- parsed$effective_sample_size
print(argEffectiveSampleSize)
if (!is.na(argEffectiveSampleSize)) {
  argEffectiveSampleSize <- as.numeric(argEffectiveSampleSize)
  if (!is.numeric(argEffectiveSampleSize)) stop('Effective sample size needs to be numeric, received: ', argEffectiveSampleSize)
}
argLdpredMode <- parsed$ldpred_mode
validModes <- c('inf', 'auto')
if (!argLdpredMode %in% validModes) stop("--ldpred-mode should be one of: ", paste0(validModes, collapse=', '))
argStatType <- parsed$stat_type
setSeed <- parsed$set_seed

# These vectors are used to convert headers in the sumstat files to those
# used by bigsnpr
colSumstatsOld <- c(  colChr, colSNPID, colBP, colA1, colA2, colStat, colStatSE)
colSumstatToGeno <- c("chr",  "rsid",   "bp",  "a0",  "a1",  "beta",  "beta_se")

cat('Loading backingfile:', fileGeno ,'\n')
obj.bigSNP <- snp_attach(fileGeno)
if (!is.na(filePheno)) {
  cat('Loading external phenotype in file', filePheno, '\n')
  dataPheno <- bigreadr::fread2(filePheno)
  obj.bigSNP$fam <- merge(obj.bigSNP$fam, dataPheno, by.x = c('family.ID','sample.ID'), by.y=c('FID','IID'), all.x=T)
}

# Store some key variables
G <- obj.bigSNP$genotypes
CHR <- obj.bigSNP$map$chromosome
POS <- obj.bigSNP$map$physical.pos
phenotype <- NA
if (!is.na(colPheno)) phenotype <- obj.bigSNP$fam[,colPheno]
NCORES <- nb_cores()

cat('\n### Reading summary statistics', fileSumstats,'\n')
sumstats <- bigreadr::fread2(fileSumstats)
cat('Loaded', nrow(sumstats), 'SNPs\n')

# Reame columns in bigSNP object
colMap <- c('chr', 'rsid', 'pos', 'a0', 'a1')
map <- setNames(obj.bigSNP$map[-3], colMap)

# Rename headers in sumstats file if necessary
colSumstats <- colnames(sumstats)
# Lowercase them
colSumstats <- tolower(colSumstats)
colSumstatsOld <- tolower(colSumstatsOld)
# Check that all necessary columns are present
colReplacements <- match(colSumstatsOld, colSumstats)
if (sum(is.na(colReplacements)) > 0) {
  cat('The following necessary columns could not be found in', basename(fileSumstats), '\n')
  for (i in 1:length(colReplacements)) {
    if (is.na(colReplacements[i])) {
      cat('\t', colSumstatsOld[i],'\n')
    }
  }
  cat('Columns in ', basename(fileSumstats), ': ', paste0(colSumstats, collapse=' | '), '\n', sep='')
  stop('Necessary columns not found')
}

# Replace columns in sumstat data so the match bigSNP
colSumstats[colReplacements] <- colSumstatToGeno
colnames(sumstats) <- colSumstats
sumstats$a0 <- toupper(sumstats$a0)
sumstats$a1 <- toupper(sumstats$a1)

# Add effective sample size
if (!is.na(argEffectiveSampleSize)) {
  sumstats$n_eff <- argEffectiveSampleSize
} else {
  colN <- tolower(colN)
  if (!colN %in% colSumstats) {
    stop("Effective sample size has not been provided as an argument and no such column was found in the sumstats (expected ", colN, ")")
  }
  sumstats$n_eff <- sumstats[,colN]
}

if (!is.na(fileKeepSNPs)) {
  cat('Filtering SNPs using', fileKeepSNPs, '\n')
  keepSNPs <- read.table(fileKeepSNPs)
  nSNPsBefore <- nrow(sumstats)
  sumstats <- sumstats[sumstats$rsid %in% keepSNPs[,1],]
  nSNPsAfter <- nrow(sumstats)
  cat('Retained', nSNPsAfter, 'out of', nSNPsBefore,'\n')
}

# If the statistic is an OR, convert it into a log-OR
if (argStatType == "OR") {
  cat('Converting odds-ratio to log scale\n')
  sumstats$beta <- log(sumstats$beta)
}

# Match SNPs by RSID
df_beta <- snp_match(sumstats, map, join_by_pos=F)

cat('\n### Calculating SNP correlation/LD using', NCORES, 'cores\n')
individualSample <- rows_along(G)
if (genoLDSample > 0) {
  cat('Drawing', genoLDSample, 'individuals at random\n')
  individualSample <- sample(nrow(G), genoLDSample)
}
cat("Converting from physical position to genetic position\n")
# Genetic maps (these are only available for chromosomes 1 to 22)
chromosomeSet <- 1:22
chromosomes <- unique(CHR)
if (23 %in% chromosomes) cat('NOTE: Omitting chromosome 23 in LD estimation\n')
validCrh <- CHR %in% chromosomeSet
POS2 <- snp_asGeneticPos(CHR[validCrh], POS[validCrh], dir=dirGeneticMaps, ncores=NCORES, type=parGeneticMapsType)
temp <- tempfile(tmpdir='temp')
cat('Using file', temp, 'to store matrixes\n')
ld <- c()
cat('Chromosome: ')
for (chr in chromosomeSet) {
  cat(chr, '...', sep='')
  # indices in df_beta
  ind.chr <- which(df_beta$chr == chr)
  # indices in G
  ind.chr2 <- df_beta$`_NUM_ID_`[ind.chr]
  nMarkers <- length(ind.chr2)
  if (nMarkers > 0) {
    corr0 <- snp_cor(G, ind.col=ind.chr2, ind.row=individualSample, size=parWindowSize/1000,
                   infos.pos=POS2[ind.chr2], ncores=NCORES)
    if (is.null(ld)) {
      ld <- Matrix::colSums(corr0^2)
      corr <- as_SFBM(corr0, temp)
    } else {
      ld <- c(ld, Matrix::colSums(corr0^2))
      corr$add_columns(corr0, nrow(corr))
    }
  } else {
    cat('\nSkipped chromosome ', chr, '. Reason: Nr of SNPs was ', nMarkers, '\n', sep='')
    df_beta <- df_beta[df_beta$chr != chr,]
  }
}
nrMissingLDs <- sum(is.na(ld))
if (nrMissingLDs > 0) {
  details <- ifelse(genoLDSample > 0, paste0(genoLDSample, ' individuals used, which may be too small'))
  stop('Missing LD blocks (', nrMissingLDs,')! ', details)
}

cat('\n### Running LD score regression\n')
ldsc <- with(df_beta, snp_ldsc(ld, length(ld), chi2=(beta/beta_se)^2, sample_size=n_eff, blocks=NULL))
h2_est <- ldsc[["h2"]]
cat('Results:', 'Intercept =', ldsc[["int"]], 'H2 =', h2_est, '\n')

cat('\n### Starting polygenic scoring\n')
# LDPRED2-Inf: Infinitesimal model
if (argLdpredMode == 'inf') {
  cat ('Running LDPRED2 infinitesimal model\n')
  cat('Calculating beta inf\n')
  beta <- snp_ldpred2_inf(corr, df_beta, h2=h2_est)
# LDPRED2-Auto
} else if (argLdpredMode == 'auto') {
  cat('Running LDPRED2 auto model\n')
  if (!is.na(setSeed)) set.seed(setSeed)
  multi_auto <- snp_ldpred2_auto(corr, df_beta, h2_init=h2_est, vec_p_init=seq_log(1e-4, 0.2, length.out=parHyperPLength), 
                                 allow_jump_sign=F, shrink_corr=0.95, ncores=NCORES)
  cat('Plotting diagnostics: ', fileOutput, '.png\n', sep='')
  library(ggplot2)
  auto <- multi_auto[[1]]
  dta <- data.frame(path_p_est=auto$path_p_est, path_h2_est=auto$path_h2_est, x=1:length(auto$path_p_est))
  plt <- plot_grid(
    ggplot(dta, aes(y=path_p_est, x=x)) + geom_point() + theme_bigstatsr() + 
      geom_hline(aes(yintercept=auto$p_est), col="blue") + 
      scale_y_log10() + labs(y="p"),
    ggplot(dta, aes(y=path_h2_est, x=x)) + geom_point() + theme_bigstatsr() + 
      geom_hline(aes(yintercept=auto$h2_est), col="blue") + labs(y="h2"),
    ncol=1, align="hv"
  )
  ggsave(plt, file=paste0(fileOutput, '.png'))
  cat('Filtering chains\n')
  range <- sapply(multi_auto, function(auto) diff(range(auto$corr_est)))
  # Keep chains that pass the filtering below
  keep <- (range > (0.95 * quantile(range, 0.95)))
  beta <- rowMeans(sapply(multi_auto[keep], function (auto) auto$beta_est))
}

cat('Scoring all individuals...')
# Count missingness over individuals for each SNP
nMissingGenotypes <- big_apply(G, a.FUN=function (x, ind) colSums(is.na(x[,ind])), a.combine='c')
nMissingGenotypes <- sum(nMissingGenotypes > 0)
if (nMissingGenotypes > 0) {
  warning('Missing genotypes found (N positions=', nMissingGenotypes, '). Imputing genotypes by using "', genoImpute,'" (see bigsnpr::snp_fastImputeSimple).\n')
  G <- snp_fastImputeSimple(G, method=genoImpute, ncores = NCORES)
}
pred_all <- big_prodVec(G, beta, ind.col=df_beta[['_NUM_ID_']])
obj.bigSNP$fam[,nameScore] <- pred_all
if (length(phenotype) > 1) {
  correlation <- pcor(pred_all, phenotype[ind.test], NULL)
  correlation <- round(correlation, 4)
  correlation <- paste0(correlation[1], ' (', correlation[2], ', ', correlation[3],')') # Why is this inverted compared to the tutorial?
  cat('Correlation with phenotype:', correlation, '\n')
}

cat('\n### Writing fam file with PGS and phenotype\n')
colsKeep <- c('family.ID', 'sample.ID', nameScore)
if (!is.na(colPheno)) colsKeep <- c(colsKeep, colPheno)
outputData <- obj.bigSNP$fam[,colsKeep]
# Rename to stick with plink naming
colsKeep[1:2] <- c('FID', 'IID')
colnames(outputData) <- colsKeep
write.table(outputData, file=fileOutput, row.names = F, quote=F)
# Drop temporary file
fileRemoved <- file.remove(paste0(temp, '.sbk'))