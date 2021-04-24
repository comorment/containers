README:

Association results from "GWAS meta-analysis in 269,867 individuals identifies new genetic and functional links to intelligence" (Savage et al., Nature Genetics, 2018), a GWAS meta-analysis of intelligence measures in 14 independent cohorts.

GWAS was performed using various software (PLINK, SNPTEST, RAREMETALWORKER, etc.) in individual cohorts using a linear or logistic regression model and meta-analyzed using METAL. SNPs with MAC < 100, INFO < 0.6, indels, multiallelic, or N < 50,000 are excluded.

Columns:
SNP: rs number
UNIQUE_ID: unique SNP id based on chromosome, position
CHR: chromosome number
POS: base pair position reported on GRCh37
A1: effect allele
A2: non-effect allele
EAF_HRC: effect allele frequency in the Haplotype Reference Consortium reference panel (HRC)
Zscore: meta-analysis Z score
stdBeta: standardized beta coefficient*
SE: standard error of the beta coefficient*
P: P-value
N_analyzed: sample size
minINFO: minimum info score (SNP quality measure) across all cohorts
EffectDirection: direction of the effect in each of the cohorts, order: COGENT,GENR,GfG,IMAGEN,NESCOG,BLTS-A,BLTS-C,RS,S4S,STSA-SATSA+GENDER,STSA-HARMONY,DTR-L,DTR-M,STR,TEDS1,TEDS2,UKB-ts,UKB-wb,HIQ

*Beta/SE were calculated from METAL Z-scores using the formula from Zhu et al (Nature Genetics, 2016):
Beta = Zscore / sqrt( 2 * MAF * ( 1 - MAF) * ( N + Zscore^2 ) )
SE = 1 / sqrt( 2 * MAF * ( 1 - MAF ) * ( N + Zscore^2 ) )
