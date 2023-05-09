library(argparser, quietly=T)
library(dplyr, quietly=T)
# Source functions
coms <- commandArgs()
coms <- coms[substr(coms, 1, 7) == '--file=']
dirScript <- dirname(substr(coms, 8, nchar(coms)))
source(paste0(dirScript, '/fun.R'))

par <- arg_parser('Complement GWAS summary statistics')
par <- add_argument(par, '--sumstats', nargs=1, help='Summary statistics file. Anything accepted by bigreadr::fread2')
par <- add_argument(par, '--reference', nargs=1, default='/REF/hrc/HRC.r1-1.GRCh37.wgs.mac5.sites.tab.gz',
                    help='Reference data file to complement summary statistics with. Anything accepted by bigreadr::fread2')
par <- add_argument(par, '--col-sumstats-snp-id', nargs=1, default='SNP', help='SNP ID (RSID) column in sumstats')
par <- add_argument(par, '--col-reference-snp-id', nargs=1, default='ID', help='SNP ID (RSID) column in reference file')
par <- add_argument(par, '--columns-append', nargs="*", default=c('#CHROM', 'POS'), help='Columns from reference data to append to sumstats. Defaults to #CHROM and POS')
par <- add_argument(par, '--column-names-output', nargs="*", default=c('CHR', 'POS'), help='Column names in output. Defaults to column names in sumstats. Defaults to CHR and POS')
par <- add_argument(par, '--file-output-col-sep', nargs=1, default='\t', help='Column separator in output. Anything accepted by bigreadr::fwrite2')
par <- add_argument(par, '--file-output', nargs=1, default=tempfile(), help='Output file name. Defaults to a temporary file (<tempdir>/<tempfilename>)')
parsed <- parse_args(par)
fileSumstats <- parsed$sumstats
reference <- parsed$reference
fileOut <- parsed$file_output
fileOutColSep <- parsed$file_output_col_sep
noPrint <- ifelse(fileOut == '', T, F)
colSumstatsSnpId <- parsed$col_sumstats_snp_id
colRefSnpId <- parsed$col_reference_snp_id
colsAppend <- parsed$columns_append

# assert that length of columns-append and column-names-output are the same
if (length(colsAppend) != length(parsed$column_names_output)) {
  stop('Length of columns-append and column-names-output must be the same')
}

if (!noPrint) cat('Reading sumstats', fileSumstats, '\n')
sumstats <- bigreadr::fread2(fileSumstats)
if (!noPrint) cat('Reading reference file', reference, '\n')
reference <- bigreadr::fread2(reference)
if (!noPrint) cat('Complementing sumstats\n')
sumstats <- complementSumstats(sumstats, reference, colRsidSumstats=colSumstatsSnpId, colRsidRef=colRefSnpId, colsKeepReference=colsAppend)
if (!noPrint) cat('Renaming columns\n')
sumstats <- rename_columns(sumstats, colsAppend, parsed$column_names_output)
if (!noPrint) cat('Writing output file', fileOut, '\n')
bigreadr::fwrite2(sumstats, file=fileOut, sep=fileOutColSep)
