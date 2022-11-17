# Calculate polygenic scores using ldpred2
# this script is an adaptation of the demo script available at the bigsnpr homepage
library(bigsnpr)
library(tools)
library(argparser, quietly=T)
par <- arg_parser('Calculate polygenic scores using ldpred2')
# Mandatory arguments (files)
par <- add_argument(par, "file-geno", help="Input file with genotypes")
par <- add_argument(par, "file-sumstats", help="Input file with GWAS summary statistics")
par <- add_argument(par, "file-output", help="Output file with calculated PGS")
# Optional files
par <- add_argument(par, "--file-backing", help="Filename of intermediate bigsnpr file, if file-geno is not rds this argument specifies the output name of this file")
par <- add_argument(par, "--file-keep-snps", help="File with RSIDs of SNPs to keep")
par <- add_argument(par, "--file-pheno", help="File with phenotype data (if not part of BED file")
par <- add_argument(par, "--file-gene-corr", help="Filename with LD and genetic correlation, if omitted it will be estimated")
# Phenotype file
par <- add_argument(par, "--col-pheno", help="Column name of phenotype in --file-pheno.")
# Sumstats file. The defaults follow PRSICE2.
par <- add_argument(par, "--col-chr", help="CHR number column", default="CHR")
par <- add_argument(par, "--col-snp-id", help="SNP ID (RSID) column", default="SNP")
par <- add_argument(par, "--col-A1", help="Effective allele column", default="A1")
par <- add_argument(par, "--col-A2", help="Noneffective allele column", default="A2")
par <- add_argument(par, "--col-bp", help="SNP position column", default="BP")
par <- add_argument(par, "--col-stat", help="Effect estimate column", default="BETA")
par <- add_argument(par, "--col-stat-se", help="Effect estimate standard error column", default="BETA_SE")
par <- add_argument(par, "--col-pvalue", help="P-value column", default="P")
par <- add_argument(par, "--col-n", help="Effective sample size. Override with --sample-size", default="N")
par <- add_argument(par, "--stat-type", help="Effect estimate type (BETA for linear, OR for odds-ratio", default="BETA")
# Parameters
par <- add_argument(par, "--effective-sample-size", help="Effective sample size, overrides --col-n", nargs=1)
par <- add_argument(par, "--window-size", help="Window size in centimorgans, used for LD calculation", default=3)
par <- add_argument(par, "--ldpred-mode", help='Ether "auto" or "inf" (infinitesimal)', default="inf")
par <- add_argument(par, "--cores", help="Specify the number of processor cores to use, otherwise use the available - 1", default=nb_cores()-1)

parsed <- parse_args(par)
### Mandatory
fileGeno <- parsed$file_geno
fileSumstats <- parsed$file_sumstats
fileOutput <- parsed$file_output
### Optional
fileBacking <- parsed$file_backing
fileKeepSNPs <- parsed$file_keep_snps
filePheno <- parsed$file_pheno
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
# Others
argEffectiveSampleSize <- parsed$effective_sample_size
argWindowSize <- parsed$window_size
argLdpredMode <- parsed$ldpred_mode
argStatType <- parsed$stat_type

# These vectors are used to convert headers in the sumstat files to those
# used by bigsnpr
colSumstatsOld <- c(  colChr, colSNPID, colBP, colA1, colA2, colStat, colStatSE)
colSumstatToGeno <- c("chr",  "rsid",   "bp",  "a0",  "a1",  "beta",  "beta_se")

library(tools) # Used for file utilities
# This creates a new genotype object in the specified directory
if (is.na(fileBacking)) fileBacking <- basename(file_path_sans_ext(fileGeno))
# The RDS file is used to load genotype data
fileBackingRDS <- paste0(fileBacking, '.rds')
# Convert the input file to the bigsnpr format
if (!file.exists(fileBackingRDS)) {
  cat('Creating backingfile:', fileBacking, "\n")
  snp_readBed(fileGeno, backingfile=fileBacking)
} else {
  cat('Using existing backingfile:', fileBackingRDS, "\n")
}

cat('Loading backingfile\n')
obj.bigSNP <- snp_attach(fileBackingRDS)
if (!is.na(filePheno)) {
  cat('Loading external phenotype in file', filePheno, '\n')
  dataPheno <- bigreadr::fread2(filePheno)
  obj.bigSNP$fam <- merge(obj.bigSNP$fam, dataPheno, by.x = c('family.ID','sample.ID'), by.y=c('FID','IID'), all.x=T)
}

# Store some key variables
G <- obj.bigSNP$genotypes
CHR <- obj.bigSNP$map$chromosome
POS <- obj.bigSNP$map$physical.pos
y <- obj.bigSNP$fam$Height

NCORES <- nb_cores()
cat('Reading summary statistics', fileSumstats,'\n')
sumstats <- bigreadr::fread2(fileSumstats)


colMap <- c('chr', 'rsid', 'pos', 'a0', 'a1')
map <- setNames(obj.bigSNP$map[-3], colMap)

# Rename headers in sumstats file
colSumstats <- colnames(sumstats)
colReplacements <- match(colSumstatsOld, colSumstats)
colSumstats[colReplacements] <- colSumstatToGeno
colnames(sumstats) <- colSumstats

# Add effective sample size
if (!is.na(argEffectiveSampleSize)) {
  sustats$n_eff <- argEffectiveSampleSize
} else {
  sumstats$n_eff <- sumstats[,colN]
}

if (!is.na(fileKeepSNPs)) {
  cat('Filtering SNPs using', fileKeepSNPs, '\n')
  keepSNPs <- read.table(fileKeepSNPs)
  sumstats <- sumstats[sumstats$rsid %in% keepSNPs[,1],]
}

# Testing data. Currently not used in any meaningful way
set.seed(123)
ind.val <- sample(nrow(G), 100) # Validation sample
ind.test <- setdiff(rows_along(G), ind.val) # Testing sample

# If the statistic is an OR, convert it into a log-OR
if (argStatType == "OR") sumstats$beta <- log(sumstats$beta)
# Match SNPs by RSID
df_beta <- snp_match(sumstats, map, join_by_pos=F)


POS2 <- obj.bigSNP$map$genetic.dist

cat('Calculating SNP correlation/LD using', NCORES, 'cores\n')
temp <- tempfile(tmpdir='temp')
cat('Using file', temp, 'to store matrixes\n')
chromosomes <- unique(CHR)
ld <- c()
cat('Chromosome: ')
for (chr in chromosomes) {
  cat(chr, '...', sep='')
  # indices in df_beta
  ind.chr <- which(df_beta$chr == chr)
  # indices in G
  ind.chr2 <- df_beta$`_NUM_ID_`[ind.chr]
  nMarkers <- length(ind.chr2)
  if (nMarkers > 0) {
    corr0 <- snp_cor(G, ind.col=ind.chr2, size=argWindowSize/1000,
                   infos.pos=POS2[ind.chr2], ncores=NCORES)
    if (is.null(ld)) {
      ld <- Matrix::colSums(corr0^2)
      corr <- as_SFBM(corr0, temp)
    } else {
      ld <- c(ld, Matrix::colSums(corr0^2))
      corr$add_columns(corr0, nrow(corr))
    }
  } else {
    cat('Skipped chromosome ', chr, '. Reason: Nr of SNPs was ', nMarkers, '\n')
    df_beta <- df_beta[df_beta$chr != chr,]
  }
}

cat('Running LD score regression\n')
ldsc <- with(df_beta, snp_ldsc(ld, length(ld), chi2=(beta/beta_se)^2, sample_size=n_eff, blocks=NULL))
h2_est <- ldsc[["h2"]]
cat('SNP heritability estimated to ', h2_est, '\n')

# LDPRED2-Inf: Infinitesimal model
if (argLdpredMode == 'inf') {
  cat ('Running LDPRED2 infinitesimal model\n')
  cat('Calculating beta inf\n')
  beta_inf <- snp_ldpred2_inf(corr, df_beta, h2=h2_est)
  cat('Calculating PGS\n')
  pred_inf <- big_prodVec(G, beta_inf, ind.row=ind.test, ind.col=df_beta[['_NUM_ID_']])

  #print(pcor(pred_inf, y[ind.test], NULL))
  cat('Calculating PGS for all individuals\n')
  pred_all <- big_prodVec(G, beta_inf, ind.col=df_beta[['_NUM_ID_']])
  obj.bigSNP$fam$score <- pred_all
# LDPRED2-Auto
} else if (argLdpredMode == 'auto') {
  cat ('Running LDPRED2 auto model\n')
  multi_auto <- snp_ldpred2_auto(corr, df_beta, h2_init=h2_est, vec_p_init=seq_log(1e-4,0.2,length.out=5), allow_jump_sign=F, 
                                 shrink_corr=0.95, ncores=NCORES)
  cat('Evaluating\n')
  range <- sapply(multi_auto, function(auto) diff(range(auto$corr_est)))
  keep <- (range > (0.95 * quantile(range, 0.95)))
  beta_auto <- rowMeans(sapply(multi_auto[keep], function (auto) auto$beta_est))
  cat('Predict in test sample\n')
  pred_auto <- big_prodVec(G, beta_auto, ind.row=ind.test, ind.col=df_beta[["_NUM_ID_"]])
  cat('Predict among all\n')
  pred_all <- big_prodVec(G, beta_auto, ind.col=df_beta[['_NUM_ID_']])
  obj.bigSNP$fam$score <- pred_all
}

# Output PGS
outputData <- obj.bigSNP$fam[,c('family.ID','sample.ID','Height','score')]
colnames(outputData) <- c('FID', 'IID', 'Height', 'score')
write.table(outputData, file=fileOutput, row.names = F, quote=F)
# Drop temporary file
fileRemoved <- file.remove(paste0(temp, '.sbk'))
