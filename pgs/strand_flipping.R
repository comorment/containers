library(argparser, quietly=T)

# capture command-line input
par <- arg_parser('Perform strand-flipping as described at https://choishingwan.github.io/PRS-Tutorial/target/#mismatching-snps')
par <- add_argument(par, "bim_file", help=".bim input file")
par <- add_argument(par, "QC_file", help=".QC.gz input file")
par <- add_argument(par, "QC_snplist_file", help=".QC.snplist input file")
par <- add_argument(par, "ai_file", help=".ai output file")
par <- add_argument(par, "mismatch_file", help=".mismatch output file")
parsed <- parse_args(par)

# 1. Load the bim file, the summary statistic and the QC SNP list into R
# magrittr allow us to do piping, which help to reduce the 
# amount of intermediate data types
library(data.table)
library(magrittr)

# Read in bim file 
bim <- fread(parsed$bim_file) %>%
    # Note: . represents the output from previous step
    # The syntax here means, setnames of the data read from
    # the bim file, and replace the original column names by 
    # the new names
    setnames(., colnames(.), c("CHR", "SNP", "CM", "BP", "B.A1", "B.A2")) %>%
    # And immediately change the alleles to upper cases
    .[,c("B.A1","B.A2"):=list(toupper(B.A1), toupper(B.A2))]
# Read in summary statistic data (require data.table v1.12.0+)
# height <- fread("Height.QC.gz") %>%
height <- fread(parsed$QC_file) %>%
    # And immediately change the alleles to upper cases
    .[,c("A1","A2"):=list(toupper(A1), toupper(A2))]
# Read in QCed SNPs
# qc <- fread("EUR.QC.snplist", header=F)
qc <- fread(parsed$QC_snplist_file, header=F)



# 2. Identify SNPs that require strand flipping 
# Merge summary statistic with target
info <- merge(bim, height, by=c("SNP", "CHR", "BP")) %>%
    # And filter out QCed SNPs
    .[SNP %in% qc[,V1]]

# Function for calculating the complementary allele
complement <- function(x){
    switch (x,
        "A" = "T",
        "C" = "G",
        "T" = "A",
        "G" = "C",
        return(NA)
    )
} 
# Get SNPs that have the same alleles across base and target
info.match <- info[A1 == B.A1 & A2 == B.A2, SNP]
# Identify SNPs that are complementary between base and target
com.snps <- info[sapply(B.A1, complement) == A1 &
                    sapply(B.A2, complement) == A2, SNP]
# Now update the bim file
bim[SNP %in% com.snps, c("B.A1", "B.A2") :=
        list(sapply(B.A1, complement),
            sapply(B.A2, complement))]




# 3. Identify SNPs that require recoding in the target 
# (to ensure the coding allele in the target data is the 
# effective allele in the base summary statistic)

# identify SNPs that need recoding
recode.snps <- info[B.A1==A2 & B.A2==A1, SNP]
# Update the bim file
bim[SNP %in% recode.snps, c("B.A1", "B.A2") :=
        list(B.A2, B.A1)]

# identify SNPs that need recoding & complement
com.recode <- info[sapply(B.A1, complement) == A2 &
                    sapply(B.A2, complement) == A1, SNP]
# Now update the bim file
bim[SNP %in% com.recode, c("B.A1", "B.A2") :=
        list(sapply(B.A2, complement),
            sapply(B.A1, complement))]
# Write the updated bim file
# fwrite(bim[,c("SNP", "B.A1")], "EUR.a1", col.names=F, sep="\t")
fwrite(bim[,c("SNP", "B.A1")], parsed$ai_file, col.names=F, sep="\t")



# 4. Identify SNPs that have different allele in base and target 
# (usually due to difference in genome build or Indel)
mismatch <- bim[!(SNP %in% info.match |
                    SNP %in% com.snps |
                    SNP %in% recode.snps |
                    SNP %in% com.recode), SNP]
write.table(mismatch, parsed$mismatch_file, quote=F, row.names=F, col.names=F)
