library(data.table)
library(argparser, quietly=T)

par <- arg_parser('extract columns ')
par <- add_argument(par, "--input-file", help=".csv input file")
par <- add_argument(par, "--columns", default=c("FID", "IID"), help="sequence of column headers to be copied", nargs='+')
par <- add_argument(par, "--output-file", help=".csv output output file")
par <- add_argument(par, "--header", type="bool", default=T, help="include column headers in output file (T/F)")
par <- add_argument(par, "--sep", default=" ", help='output file separator')
par <- add_argument(par, "--na", default="", help='value for missing values')
par <- add_argument(par, "--quote", default=F, type="bool", help="data.table::fwrite quote flag")

parsed <- parse_args(par)

csv <- fread(parsed$input_file)
cols <- parsed$columns
out <- csv[, ..cols]
fwrite(out, parsed$output_file, sep=parsed$sep, col.names=parsed$header, na=parsed$na, quote=parsed$quote)
