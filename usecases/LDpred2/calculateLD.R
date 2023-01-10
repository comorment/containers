# Calculate LD
library(bigsnpr, quietly = T)
options(bigstatsr.check.parallel.blas = FALSE)
options(default.nproc.blas = NULL)
library(argparser, quietly = T)
library(stringr)

par <- arg_parser('Calculate linkage disequillibrium (LD) using bigSNPr')
# Mandatory arguments
par <- add_argument(par, "--geno-file", nargs=1, help="Input .rds (bigSNPR) file with genotypes")
par <- add_argument(par, "--file-ld-blocks", nargs=1, default="LD_with_blocks_chr@.rds", help="Template name of output files using @ to indicate chromosome nr")
par <- add_argument(par, "--file-ld-map", nargs=1, default="map.rds", help="Name of LD map file")
# Directories
par <- add_argument(par, "--dir-genetic-maps", default=tempdir(), 
                    help="Directory containing 1000 Genomes genetic maps. Either a directory to store files to be downloaded, or a directory contaning the unpacked files.")
# Optional arguments
par <- add_argument(par, "--genetic-maps-type", default="hapmap", help="Which genetic map to use, hapmap or OMNI.")
par <- add_argument(par, "--chr2use", help="list of chromosomes to use (by default it uses chromosomes 1 to 22)", nargs=Inf)
par <- add_argument(par, "--file-keep-snps", help="File with RSIDs of SNPs to keep")
par <- add_argument(par, "--sumstats", help="Input file with GWAS summary statistics")
par <- add_argument(par, "--window-size", help="Window size in centimorgans, used for LD calculation", default=3)
par <- add_argument(par, "--cores", help="Specify the number of processor cores to use, otherwise use the available - 1", default=nb_cores())

parsed <- parse_args(par)
fileLDBlocks <- parsed$file_ld_blocks
if (!dir.exists(dirname(fileLDBlocks))) dir.create(dirname(fileLDBlocks))
fileLDMap <- parsed$file_ld_map
fileKeepSNPs <- parsed$file_keep_snps
fileSumstats <- parsed$sumstats
dirGeneticMaps <- parsed$dir_genetic_maps
argGeneticMapsType <- parsed$genetic_maps_type
argWindowSize <- parsed$window_size

NCORES <- parsed$cores

obj.bigSNP <- snp_attach(parsed$geno_file)

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
colnames(MAP) <- c('chr', 'rsid', 'pos', 'a0', 'a1')

keepSNPs <- c()
if (!is.na(fileKeepSNPs)) {
  cat('Filtering ',nrow(obj.bigSNP$map),' SNPs...')
  keepSNPs <- read.table(fileKeepSNPs)[,1]
  #sbs <- which(obj.bigSNP$map$marker.ID %in% SNPlist[,1])
  #keepSNPs <- SNPlist
  #fileSnpSub <- snp_subset(obj.bigSNP, ind.col=sbs)
  #obj.bigSNP <- snp_attach(fileSnpSub)
  cat('retained', nrow(obj.bigSNP$map), 'SNPs\n')
}
if (!is.na(fileSumstats)) {
  cat('Filtering on SNPs in sumstats\n')
  fileSumstats <- read.table(fileSumstats, header=T, sep=',')
  keepSNPs <- c(keepSNPs, fileSumstats$rsid)
  #sums <- snp_match(fileSumstats, MAP, join_by_pos = F)
  #MAP <- subset(MAP, rsid %in% fileSumstats$rsid) 
  cat('Retained', nrow(MAP), 'SNPs\n')
}
#MAP$NUM_ID <- rows_along(MAP)

cat('Calculating SNP correlation/LD using', NCORES, 'cores\n')
temp <- tempfile(tmpdir='temp')
cat('Using file', temp, 'to store matrixes\n')
chromosomes <- unique(CHR)
ld <- c()
MAP$ld <- NA
cat('Chromosome: ')
snps <- MAP$rsid %in% keepSNPs
for (chr in chromosomes) {
  cat(chr, '...', sep='')
  # indices in sums
  ind.chr2 <- which(MAP$chr == chr & snps)
  #ind.chr <- which(sums$chr == chr)
  # indices in G
  #ind.chr2 <- sums$`_NUM_ID_`[ind.chr]
  nMarkers <- length(ind.chr2)

  corr0 <- snp_cor(G, ind.col=ind.chr2, size=argWindowSize/1000,
                   infos.pos=GD[ind.chr2], ncores=NCORES)
  fileName <- str_replace(fileLDBlocks, "@", toString(chr))
  ldE <- Matrix::colSums(corr0^2)
  MAP$ld[ind.chr2] <- ldE
  saveRDS(corr0, file=fileName)
}
cat('\n')
saveRDS(MAP, file=fileLDMap)

