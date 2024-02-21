# Calculate LD
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(argparser, quietly = T)
library(stringr)
library(data.table)

# Load some functions
coms <- commandArgs()
coms <- coms[substr(coms, 1, 7) == '--file=']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))

par <- arg_parser('Calculate linkage disequillibrium (LD) using bigSNPr')
# Mandatory arguments
par <- add_argument(par, "--geno-file-rds", nargs=1, help="Input .rds (bigSNPR) file with genotypes")
par <- add_argument(par, "--file-ld-chr", nargs=1, default="LD_chr@.rds", help="Template name of output files using @ to indicate chromosome nr")
par <- add_argument(par, "--file-ld-map", nargs=1, default="map.rds", help="Name of outputted LD map file")
# Directories
par <- add_argument(par, "--dir-genetic-maps", default=tempdir(), 
                    help="Directory containing 1000 Genomes genetic maps. Either a directory to store files to be downloaded, or a directory contaning the unpacked files.")
# Optional arguments
par <- add_argument(par, "--genetic-maps-type", default="hapmap", help="Which genetic map to use, hapmap or OMNI.")
par <- add_argument(par, "--sample-individuals", nargs=1, help="Specify a number of individuals to draw at random")
par <- add_argument(par, "--sample-seed", nargs=1, help="Set a seed for reproducibility before sampling individuals")
par <- add_argument(par, "--chr2use", nargs=Inf, help="List of chromosomes to use (by default it uses chromosomes 1 to 22)")
par <- add_argument(par, "--sumstats", nargs=2, help="Input file with GWAS summary statistics. First argument is the file, second is RSID column position (integer) or name.")
par <- add_argument(par, "--extract", help="File with RSIDs of SNPs to extract from summary statistics")
par <- add_argument(par, "--extract-individuals", help="File with individual identifiers to extract from genotype data")
par <- add_argument(par, "--window-size", default=3, nargs=1, help="Window size in centimorgans, used for LD calculation")
par <- add_argument(par, "--thres-r2", default=0.01, nargs=1, help="Threshold to restrict included SNPs in LD calculations")
par <- add_argument(par, "--cores", default=nb_cores(), nargs=1, help="Specify the number of processor cores to use, otherwise use the available - 1")

parsed <- parse_args(par)
fileLDChr <- parsed$file_ld_chr
if (!dir.exists(dirname(fileLDChr))) dir.create(dirname(fileLDChr))
fileLDMap <- parsed$file_ld_map
fileKeepSNPs <- parsed$extract
# Sumstats file
fileSumstats <- parsed$sumstats[1]
columnRsidSumstats <- parsed$sumstats[2]
# Check extract individuals
extractIndividuals <- parsed$extract_individuals
if (!is.na(extractIndividuals)) {
  if (!file.exists(extractIndividuals)) stop('--extract-individuals: Could not find file ', extractIndividuals)
}
# Check sample individuals
sampleIndividuals <- parsed$sample_individuals
if (!is.na(sampleIndividuals)) {
  sampleIndividuals <- as.numeric(sampleIndividuals)
  if (!is.numeric(sampleIndividuals)) stop('--sample-individuals needs to be numeric, got ', sampleIndividuals)
}
sampleSeed <- parsed$sample_seed
if (!is.na(sampleSeed) & !isNumeric(sampleSeed)) stop('--sample-seed must be numeric, got ', sampleSeed)

# Chromosomes to use
chr2use <- parsed$chr2use
if (any(is.na(chr2use))) chr2use <- 1:22
dirGeneticMaps <- parsed$dir_genetic_maps
# Parameters to bigsnpr functions
argGeneticMapsType <- parsed$genetic_maps_type
argWindowSize <- parsed$window_size
argThresholdR2 <- parsed$thres_r2

NCORES <- parsed$cores

obj.bigSNP <- snp_attach(parsed$geno_file_rds)

G <- obj.bigSNP$genotypes
CHR <- obj.bigSNP$map$chromosome
POS <- obj.bigSNP$map$physical.pos

# Create a dataframe to hold the ld for each SNP (uncertain about the minimum amount of variables needed here)
MAP <- obj.bigSNP$map

# NOTE
# Genetic distance is used by snp_cor, argument infos.pos. First, for some reason the documentation states that this is
# supposed to be physical position basepairs (thus integers). However, the tutorial uses genetic distance in centimorgans. 
# Second, the tutorial code won't cause an error if the genetic.dist is not available in the data.frame as accessing a
# non-existing column in a data.frame just results in NULL. If genetic.dist is not available It will result in 
# NULL and R doesn't cause an error if you try to index a variable that is NULL (NULL[1:2] = NULL). If NULL is passed to 
# infos.pos all column sums of the correlation matrix will be 1 (don't know why).
GD <- snp_asGeneticPos(CHR, POS, dir=dirGeneticMaps, type=argGeneticMapsType, ncores=NCORES)
if (is.null(GD)) stop('Genetic distance is not available')
MAP <- MAP[,c('chromosome', 'marker.ID', 'physical.pos', 'allele1', 'allele2')]

# Filtering SNPs (if those arguments have been provided)
SNPs <- MAP$marker.ID
if (!is.na(fileSumstats)) SNPs <- filterFromFile(SNPs, fileSumstats, col=columnRsidSumstats)
if (!is.na(fileKeepSNPs)) SNPs <- filterFromFile(SNPs, fileKeepSNPs)
colnames(MAP) <- c('chr', 'rsid', 'pos', 'a1', 'a0')
useSNPs <- MAP$rsid %in% SNPs
nSNPs <- sum(useSNPs)
if (nSNPs == 0) stop('No SNPs available.')
cat('A total of', nSNPs, 'will be used for LD calculation\n')

individualSample <- rows_along(G)
# Extract individuals
if (!is.na(extractIndividuals)) {
  cat('Extracting individuals...\n')
  inds <- filterFromFile(obj.bigSNP$fam, extractIndividuals, colFilter='sample.ID')
  individualSample <- which(obj.bigSNP$fam$sample.ID %in% inds$sample.ID)
}

# Sample individuals
if (!is.na(sampleIndividuals)) {
  cat('Drawing', sampleIndividuals, 'individuals at random\n')
  nInds <- length(individualSample)
  if (nInds < sampleIndividuals) stop('Requsted sample size is greater than the available:', nInds)
  if (!is.na(sampleSeed)) set.seed(sampleSeed)
  individualSample <- sample(individualSample, sampleIndividuals)
}

cat('Calculating SNP correlation/LD using', NCORES, 'cores\n')
temp <- tempfile(tmpdir='temp')
cat('Using file', temp, 'to store matrixes\n')

MAP$ld <- NA
cat('Chromosome: ')
for (chr in chr2use) {
  cat(chr, '...', sep='')
  # indices in G
  indices.G <- which(MAP$chr == chr & useSNPs)
  nDataPoints <- sum(indices.G)
  # nDataPoints could probably be a higher nr. I put this here to ensure that filtering
  # works and that the resulting MAP has NA's in it.
  if (nDataPoints == 0) {
    warning('\nSkipping chromosome ', chr,'. Reason: 0 SNPs available\n')
    next
  }
  corr0 <- snp_cor(G, ind.col=indices.G, ind.row=individualSample, size=argWindowSize/1000,
                   infos.pos=GD[indices.G], ncores=NCORES, thr_r2=argThresholdR2)
  fileName <- str_replace(fileLDChr, "@", toString(chr))
  ld <- Matrix::colSums(corr0^2)
  MAP$ld[indices.G] <- ld
  saveRDS(corr0, file=fileName)
}
cat('\nWriting map to', fileLDMap, '\n')
MAP <- MAP[useSNPs,]
saveRDS(MAP, file=fileLDMap)
