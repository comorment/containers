library(bigsnpr, quietly = T)

# 3 SNPs missing from the reference (just no such SNPs in the sumstats)
# 2 more SNPs missing from the reference due to other alleles
# 4 non-ambiguous SNPs present in reference
# 2   ambiguous SNP present in reference
sumstats <- data.frame(
  chr = c(21, 21,    1, 2, 3, 4,         5, 6),
  pos = c(5,  6,     10, 20, 30, 40,     50, 60),
  a0 = c( "A", "C",  "T", "G", "C", "A", "T", "G"),
  a1 = c( "C", "G",  "G", "A", "T", "G", "A", "C"),
  beta = c(1, 1 ,     1, 1, 1, 1,         1, 1),
  p = c(0.5, 0.5,    0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
)

info_snp <- data.frame(
  id = c("rsX", "rsY", "rsZ", "rsA", "rsB",  "rs1", "rs2", "rs3", "rs4", "rs5", "rs6"),
  chr = c(22, 22, 22,          21,   21,    1, 2, 3, 4,         5,  6),
  pos = c(1, 2, 3,             5,    6,     10, 20, 30, 40,     50, 60),
  a0 = c("G", "G", "G",        "A",  "C",   "T", "A", "G", "C",   "T", "C"),
  a1 = c("T", "T", "T",        "G",  "T",    "G", "G", "A", "T",   "A", "G")
)

sumstats_matched = snp_match(sumstats, info_snp)
#8 variants to be matched.
#3 ambiguous SNPs have been removed.
#4 variants have been matched; 2 were flipped and 2 were reversed.
#  chr pos a0 a1 beta   p _NUM_ID_.ss  id _NUM_ID_
#1   1  10  T  G    1 0.5           3 rs1        6
#2   2  20  A  G   -1 0.5           4 rs2        7
#3   3  30  G  A    1 0.5           5 rs3        8
#4   4  40  C  T   -1 0.5           6 rs4        9
if (!all(sumstats_matched$`_NUM_ID_.ss` == c(3,4,5,6))) { stop('error'); }
if (!all(sumstats_matched$`_NUM_ID_` == c(6,7,8,9))) { stop('error'); }
if (!all(sumstats_matched$beta == c(1,-1,1,-1))) { stop('error'); }
