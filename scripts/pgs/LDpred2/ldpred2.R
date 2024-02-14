# Calculate polygenic scores using ldpred2
# this script is an adaptation of the demo script available at the bigsnpr homepage
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(tools)
library(argparser, quietly=T)
library(stringr)

### Maybe there's some environment variable availble to determine the location of the script instead
coms <- commandArgs()
coms <- coms[substr(coms, 1, 7) == '--file=']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))

par <- arg_parser('Calculate polygenic scores using ldpred2')
# Mandatory arguments (files)
par <- add_argument(par, "--geno-file-rds", help="Input .rds (bigSNPR) file with genotypes. A similarly named .bk (backing) file must exist in the same location")
par <- add_argument(par, "--sumstats", help="Input file with GWAS summary statistics")
par <- add_argument(par, "--out", help="Output file with calculated PGS")

# Optional files
par <- add_argument(par, "--out-merge", flag=T, help="Merge output with existing file.")
par <- add_argument(par, "--out-merge-ids", nargs=2, help='Pass ID columns in this order: [family ID] [individual ID]')
par <- add_argument(par, "--file-keep-snps", help="File with RSIDs of SNPs to keep")
par <- add_argument(par, "--ld-file", default="/ldpred2_ref/ldref_hm3_plus/LD_with_blocks_chr@.rds", help="LD reference files, split per chromosome; chr label should be indicated by '@' symbol")
par <- add_argument(par, "--ld-meta-file", default="/ldpred2_ref/map_hm3_plus.rds", help="list of variants in --ld-file")

# Genotype
par <- add_argument(par, "--geno-impute-zero", help="Set missing genotypes to zero.", flag=T)
# Sumstats file.
par <- add_argument(par, "--chr2use", help="list of chromosomes to use (by default it uses chromosomes 1 to 22)", nargs=Inf)
par <- add_argument(par, "--col-chr", help="CHR number column", default="CHR", nargs=1)
par <- add_argument(par, "--col-snp-id", help="SNP ID (RSID) column", default="SNP", nargs=1)
par <- add_argument(par, "--col-A1", help="Effective allele column", default="A1", nargs=1)
par <- add_argument(par, "--col-A2", help="Noneffective allele column", default="A2", nargs=1)
par <- add_argument(par, "--col-bp", help="SNP position column. Will be ignored if --merge-by-rsid flag is used", default="BP", nargs=1)
par <- add_argument(par, "--col-stat", help="Effect estimate column", default="BETA", nargs=1)
par <- add_argument(par, "--col-stat-se", help="Effect estimate standard error column", default="SE", nargs=1)
par <- add_argument(par, "--col-pvalue", help="P-value column", default="P", nargs=1)
par <- add_argument(par, "--col-n", help="Effective sample size. Override with --effective-sample-size", default="N", nargs=1)
par <- add_argument(par, "--stat-type", help="Effect estimate type (BETA for linear, OR for odds-ratio)", default="BETA", nargs=1)
par <- add_argument(par, "--effective-sample-size", help="Effective sample size, if unavailable in sumstats (--col-n)", nargs=1)
par <- add_argument(par, "--n-cases", help="Nr cases when phenotype is binary. For calculating effective sample size.", nargs=1)
par <- add_argument(par, "--n-controls", help="Nr controls when phenotype is binary. For calculating effective sample size.", nargs=1)
# Polygenic score
par <- add_argument(par, "--name-score", help="Set column name for the created score", nargs=1, default='score')
# Parameters to LDpred
par <- add_argument(par, "--hyper-p-length", help="Length of hyperparameter p sequence to use for --ldpred-mode auto", default=30)
par <- add_argument(par, "--hyper-p-max", help="Maximum (<1) of hyperparameter p sequence to use for --ldpred-mode auto", default=0.2)
# Others
par <- add_argument(par, "--ldpred-mode", help='Ether "auto" or "inf" (infinitesimal)', default="inf")
par <- add_argument(par, "--cores", help="Number of CPU cores to use, otherwise use the available number of cores minus 1", default=nb_cores())
par <- add_argument(par, '--set-seed', help="Set a seed for reproducibility", nargs=1)
par <- add_argument(par, "--merge-by-rsid", help="Merge using rsid (the default is to merge by chr:bp:a1:a2 codes).", flag=TRUE)
par <- add_argument(par, "--genomic-build", help="Genomic build to use. Either hg19, hg18 or hg38", default="hg19", nargs=1)
par <- add_argument(par, "--tmp-dir", help="Directory to store temporary files. Default is output of base::tempdir()", default=tempdir())

parsed <- parse_args(par)

### Mandatory
fileGeno <- parsed$geno_file_rds
fileSumstats <- parsed$sumstats
fileOutput <- parsed$out
fileOutputPlot <- fileOutput # diagnostic plot
fileLD <- parsed$ld_file
fileMetaLD <- parsed$ld_meta_file

### Optional
fileKeepSNPs <- parsed$file_keep_snps
fileOutputMerge <- parsed$out_merge
fileOutputMergeIDs <- parsed$out_merge_ids
# Vectors as defaults causes a warning for argparse, so the default is set this way instead
if (fileOutputMerge & isVarNA(fileOutputMergeIDs)) fileOutputMergeIDs <- COLNAMES_ID_PLINK
### Genotype
genoImputeZero <- parsed$geno_impute_zero

# Sumstats file
chr2use <- parsed$chr2use
if (any(is.na(chr2use))) chr2use <- 1:22

colChr <- parsed$col_chr
colSNPID <- parsed$col_snp_id
colA1 <- parsed$col_A1
colA2 <- parsed$col_A2
colBP <- parsed$col_bp
colStat <- parsed$col_stat
colStatSE <- parsed$col_stat_se
colPValue <- parsed$col_pvalue
colN <- parsed$col_n
mergeByRsid <- parsed$merge_by_rsid

# unset colBP in case of merging by rsid
if (mergeByRsid) {
  cat(paste('The --merge-by-rsid flag is used; --col-bp', colBP, 'will be ignored\n'))
  colBP <- NULL
}

# Polygenic score
nameScore <- parsed$name_score
# If the PGS is assigned a name, the diagnostic plot (auto mode only)
# will get this name and placed in the same directory as the score
if (!is.na(nameScore)) {
	dirPlot <- dirname(fileOutput)
	fileOutputPlot <- paste0(dirPlot, '/', nameScore, '.png')
}
# Parameters to LDpred
parHyperPLength <- parsed$hyper_p_length
parHyperPMax <- parsed$hyper_p_max
# Others
argEffectiveSampleSize <- parsed$effective_sample_size
# These two have to be accessed differently due to some argparser bug
argNCases <- parsed$`n-cases`
argNControls <- parsed$`n_controls`

argLdpredMode <- parsed$ldpred_mode
validModes <- c('inf', 'auto')
if (!argLdpredMode %in% validModes) stop("--ldpred-mode should be one of: ", paste0(validModes, collapse=', '))
argStatType <- parsed$stat_type
if (!argStatType %in% c('BETA', 'OR')) stop('--stat-type should be one of "BETA" or "OR"')
setSeed <- parsed$set_seed

# These vectors are used to convert headers in the sumstat files to those
# used by bigsnpr
if (mergeByRsid) {
  colSumstatsOld <- c(colChr, colSNPID, colA1, colA2, colStat, colStatSE)
  colSumstatToGeno <- c("chr",  "rsid",  "a1",  "a0",  "beta",  "beta_se")
} else {
  colSumstatsOld <- c(colChr, colSNPID, colBP, colA1, colA2, colStat, colStatSE)
  colSumstatToGeno <- c("chr",  "rsid",  "pos",  "a1",  "a0",  "beta",  "beta_se")
}

# If the user has requested to merge scores to an existing output file
if (fileOutputMerge) {
  cat('Checking ability to merge score with file', fileOutput, 'due to --out-merge\n')
  verifyScoreOutputFile(fileOutput, nameScore, fileOutputMergeIDs)
}

# check if tmp dir exists
if (!file.exists(parsed$tmp_dir)) stop("Temporary directory", parsed$tmp_dir, "does not exist") 

cat('Loading backingfile:', fileGeno ,'\n')
obj.bigSNP <- snp_attach(fileGeno)

# Store some key variables
G <- obj.bigSNP$genotypes
CHR <- obj.bigSNP$map$chromosome
POS <- obj.bigSNP$map$physical.pos
NCORES <- parsed$cores

# Check genotype data for missingness
if (genoImputeZero) {
  cat('### Imputing missing genotypes with zero\n')
  G <- zeroMissingGenotypes(G)
}

cat('\n### Reading LD reference meta-file from ', fileMetaLD, '\n')
map_ldref <- readRDS(fileMetaLD)

# rename pos column in map_ldref if another genomic build is assumed:
if (!parsed$genomic_build %in% c('hg18', 'hg19', 'hg38')) stop('Genomic build should be one of "hg19", "hg18", "hg38"')
if (parsed$genomic_build == 'hg38') {
  cat('Renaming "pos_hg38" column in LD reference meta info as "pos"\n')
  map_ldref$pos <- map_ldref$pos_hg38
  map_ldref$pos_hg38 <- NULL
} else if (parsed$genomic_build == 'hg18') {
  cat('Renaming "pos_hg18" column in LD reference meta info as "pos"\n')
  map_ldref$pos <- map_ldref$pos_hg18
  map_ldref$pos_hg18 <- NULL
}

cat('\n### Reading summary statistics', fileSumstats,'\n')
sumstats <- bigreadr::fread2(fileSumstats)
cat('Loaded', nrow(sumstats), 'SNPs\n')

# Rename columns in bigSNP object
colMap <- c('chr', 'rsid', 'pos', 'a1', 'a0')
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

# Check that there are no characters in chromosome column (causes snp_match to fail)
if (!isOnlyNumeric(sumstats$chr)) {
  cat('Removing rows with non-integers in column', colChr, '\n')
  numeric <- getNumericIndices(sumstats$chr)
  cat('Removing', nrow(sumstats) - length(numeric), 'SNPs...\n')
  sumstats <- sumstats[numeric,]
  cat('Retained', nrow(sumstats), 'SNPs\n')
  sumstats$chr <- as.numeric(sumstats$chr)
}

### Determine effective sample-size
if (!is.na(colN)) colN <- tolower(colN)
sumstats$n_eff <- getEffectiveSampleSize(sumstats, effectiveSampleSize=argEffectiveSampleSize, cases=argNCases, controls=argNControls, colES=colN)

if (!is.na(fileKeepSNPs)) {
  cat('Filtering sumstats by SNPs using', fileKeepSNPs, '\n')
  sumstats <- filterFromFile(sumstats, fileKeepSNPs, colFilter='rsid')
}

# If the statistic is an OR, convert it into a log-OR
if (argStatType == "OR") {
  cat('Converting odds-ratio to log scale\n')
  sumstats$beta <- log(sumstats$beta)
}

cat('Filtering SNPs based on --chr2use\n')
nSNPsBefore <- nrow(sumstats)
sumstats <- sumstats[sumstats$chr %in% chr2use,]
nSNPsAfter <- nrow(sumstats)
cat('Retained', nSNPsAfter, 'out of', nSNPsBefore,'\n')

# match sumstats to genotypes
# (df_beta is quite an ugly name for GWAS sumstats, but let it be so 
# for consistency with original LDpred2 tutorial)
cat('Matching sumstats to genotypes\n')
df_beta <- snp_match(sumstats, map, join_by_pos=!mergeByRsid, match.min.prop=0)
drops <- c("_NUM_ID_.ss", "_NUM_ID_", "rsid.ss")
df_beta <- df_beta[ , !(names(df_beta) %in% drops)]

cat('Matching sumstats to LD reference\n')
df_beta <- snp_match(df_beta, map_ldref, join_by_pos=!mergeByRsid, match.min.prop=0)  # this adds af_UKBB and ld columns
drops <- c("_NUM_ID_.ss", "rsid.ss", 'block_id', 'pos_hg18', 'pos_hg38')
df_beta <- df_beta[ , !(names(df_beta) %in% drops)]  

cat('\n### Loading LD reference from ', fileLD, '\n')
tmp_file <- tempfile(tmpdir=parsed$tmp_dir)
ld_size <- 0; corr <- NULL
for (chr in chr2use) {
  ## indices in 'df_beta' corresponding to a particular 'chr'
  ind.chr <- which(df_beta$chr == chr)
  if (length(ind.chr) == 0) next
  ## indices in 'map_ldref'
  ind.chr2 <- df_beta$`_NUM_ID_`[ind.chr]
  ## indices in 'corr_chr'
  ind.chr3 <- match(ind.chr2, which(map_ldref$chr == chr))

  num_ldref_snps <- sum(map_ldref$chr == chr)
  ld_size <- ld_size + num_ldref_snps

  fileLD_chr <- str_replace(fileLD, "@", toString(chr))
  cat('\t', basename(fileLD_chr), ': loading LD for', length(ind.chr),  'out of', num_ldref_snps, 'SNPs\n')

  corr_chr <- readRDS(fileLD_chr)[ind.chr3, ind.chr3]

  if (is.null(corr)) {
    corr <- as_SFBM(corr_chr, tmp_file, compact = TRUE)
  } else {
    corr$add_columns(corr_chr, nrow(corr))
  }
}

cat('\n### Running LD score regression\n')
ldsc <- with(df_beta, snp_ldsc(ld, ld_size, chi2=(beta/beta_se)^2, sample_size=n_eff, blocks=NULL, ncores=NCORES))
h2_est <- ldsc[["h2"]]
cat('Results:', 'Intercept =', ldsc[["int"]], 'H2 =', h2_est, '\n')

cat('\n### Starting polygenic scoring\n')
# LDPRED2-Inf: Infinitesimal model
if (argLdpredMode == 'inf') {
  cat ('Running LDPRED2 infinitesimal model\n')
  beta <- snp_ldpred2_inf(corr, df_beta, h2=h2_est)
# LDPRED2-Auto
} else if (argLdpredMode == 'auto') {
  cat('Running LDPRED2 auto model\n')
  if (!is.na(setSeed)) set.seed(setSeed)
  multi_auto <- snp_ldpred2_auto(corr, df_beta, h2_init=h2_est, vec_p_init=seq_log(1e-4, parHyperPMax, length.out=parHyperPLength), 
                                 allow_jump_sign=F, shrink_corr=0.95, ncores=NCORES)
  cat('Plotting diagnostics: ', fileOutputPlot, '\n', sep='')
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
  ggsave(plt, file=fileOutputPlot)
  cat('Filtering chains\n')
  beta <- getBetasAuto(multi_auto)
}

cat('Scoring all individuals...\n')
# find which SNPs to use, and whether we need to flip their sign
map_pgs <- df_beta[1:4]; map_pgs$beta <- 1
map_pgs2 <- snp_match(map_pgs, map, join_by_pos=!mergeByRsid, match.min.prop=0)

tryCatch(
  pred_all <- big_prodVec(G, beta * map_pgs2$beta, ind.col=map_pgs2[['_NUM_ID_']], ncores=NCORES),
  error=function(er) {
    cat('bigstatsr::big_prodVec threw an error:\n')
    message(er)
    cat('\n\nErrors regarding "missingness in X" may be solved by imputing genotype data or passing --geno-impute-zero\n')
    er
    quit(status=1, save='no')
  }, 
  warning=function(er) {
    cat('bigstatsr::big_prodVec threw a warning:\n')
    message(er)
  }
)
obj.bigSNP$fam[,nameScore] <- pred_all

cat('\n### Writing file with PGS\n')
if (fileOutputMerge) cat('Merging by', paste0(fileOutputMergeIDs, collapse=', '), '\n')
writeScore(obj.bigSNP$fam, fileOutput, nameScore, fileOutputMerge, fileOutputMergeIDs)
cat('Scores written to', fileOutput, '\n')
# Drop temporary file
fileRemoved <- file.remove(paste0(tmp_file, '.sbk'))
