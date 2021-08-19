import sys
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as sstats
import argparse
import pandas as pd
import json

# Examples:
# python qq.py MSA_MSA_2016_lift_noMHC_correct_case_control.csv.gz --strata CTG_COG_2018.csv.gz --strata-num PVAL --top-as-dot 100 --weights weights.tld.txt.gz --out qq.msa_cog.top100.tld.png
# python qq.py PGC_MDD_2018_no23andMe.csv.gz --strata PGC_MDD_2018_no23andMe.csv.gz --strata-cat CHR --strata-cat-ids 'chr1_10=1:2:3:4:5:6:7:8:9:10,chr11_20=11:12:13:14:15:16:17:18:19:20,chr21_22=21:22' --top-as-dot 100 --weights weights.prune.txt.gz --y-lim 7.301029995663981 --out qq.mdd.chr.top100.prune.png
# python qq.py PGC_SCZ_2014_EUR_qc.csv.gz --strata PGC_MDD_2018_no23andMe.csv.gz --strata-num PVAL --top-as-dot 100 --weights weights.prune.txt.gz --out qq.scz_mdd.top100.prune.png --y-lim 7.301029995663981

example_text =  """Example 1:
python qq.py PGC_BIP_2016_qc.csv.gz
Example 2:
python qq.py PGC_SCZ_2014_EUR_qc.csv.gz --strata PGC_MDD_2018_no23andMe.csv.gz \\
--strata-num PVAL --top-as-dot 100 --weights weights.prune.txt.gz \\
--out qq.scz_mdd.top100.prune.png --y-lim 15
Example 3:
python qq.py PGC_MDD_2018_no23andMe.csv.gz --strata PGC_MDD_2018_no23andMe.csv.gz \\
--strata-cat CHR --strata-cat-ids 'chr1_7=1:2:3:4:5:6:7,chr18_21=18:19:20:21' \\
--weights weights.tld.txt.gz --y-lim 7.301029995663981 --out qq.mdd.chr.png"""


def parse_args(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A tool to qq plots from sumstats.",
        epilog=example_text)

    parser.add_argument("sumstats", help="Sumstats file")
    parser.add_argument("--sep", default='\t',
        help="Column separator in sumstat file")
    parser.add_argument("--p", default="PVAL",
        help="A column with SNP p-values in sumstats file")
    parser.add_argument("--snp", default="SNP",
        help="A column with SNP ids in sumstats file")
    parser.add_argument("--strata", default="NA",
        help="A file with at least 2 columns: SNP id and SNP stratum")
    parser.add_argument("--strata-sep", default='\t',
        help="Column separator in strata file")
    parser.add_argument("--strata-snp", default="SNP",
        help="A column with SNP ids in strata file")
    parser.add_argument("--strata-cat", default="NA",
        help="A column with SNP categories. Each category represents a separate stratum in qq plot")
    parser.add_argument("--strata-cat-ids", default="NA",
        help=("Comma-separated list of categories from --strata-cat column to plot "
            "and corresponding names, e.g. 'chr1_2_6=1:2:6' (defines strata chr1_2_6 "
            "containinfg all variants with value in --strata-cat column = 1,2 or 6). "
            "By default all categories are plotted with original names"))
    parser.add_argument("--strata-num", default="NA",
        help="A column with SNP numerical value (e.g. p-value)")
    parser.add_argument("--strata-num-intervals", type=str,
        default="p<10^-1=:0.1,p<10^-2=:0.01,p<10^-3=:0.001", help=("Comma-separated "
            "intervals defining SNP strata based on values from --strata-num column "
            "and corresponding names, e.g.: 'A=:-1,B=0:6' (defines stratum A "
            "corresponding to the interval (-inf, -1] and stratum B = (0,6].  "
            "If there is a '-' charecter in any of values, the whole argument value should be quoted"))
    parser.add_argument("--strata-bin", nargs='+', default="NA",
        help=("A list of columns (each column representing one stratum) with binary data "
            "0/1 or False/True for each variant indicatig whether the variant belongs to "
            "the corresponding strata"))
    parser.add_argument("--weights", default="NA",
        help=("Tab-separated file without header and with 2 columns: SNP id and SNP weight. "
            "Don't need to be normalized"))
    parser.add_argument("--top-as-dot", default=0, type=int,
        help="Number of top associations (lowest p-values) to mark as a separate dot")
    parser.add_argument("--x-lim", default=None, type=float,
        help="X-axis maximum limit on -log10 scale")
    parser.add_argument("--y-lim", default=None, type=float,
        help="Y-axis maximum limit on -log10 scale (e.g. gws threshold = 7.3)")
    parser.add_argument("--out", default="qq.png", help="Output file name")

    return parser.parse_args(args)


def drop_duplicated_ind(df):
    i = df.index.duplicated(keep='first')
    if i.any():
        print("The table contains %d duplicated ids" % sum(i))
        print("Only the first row with duplicated id will be retained")
        df = df.loc[~i,:]
    return df


def process_args(args):
    """
    Check whether provided arguments are correct, change list-type arguments
    with single value to have a length = length of sumstats argument and process
    chr2use arument.
    """
    assert os.path.isfile(args.sumstats), "'%s' file doesn't exist" % args.sumstats
    assert os.path.isfile(args.strata) or args.strata=="NA", "'%s' file doesn't exist" % args.strata
    assert os.path.isfile(args.weights) or args.weights=="NA", "'%s' file doesn't exist" % args.weights

    # process special arguments
    arg_dict = vars(args)
    if args.strata_num != "NA":
        intervals = {}
        for name_i in arg_dict["strata_num_intervals"].split(","):
            name, i = name_i.split("=")
            name = name.strip()
            assert name != "", "Stratum name should not be an empty string"
            start,end = i.split(":")
            start = -np.inf if start == "" else float(start)
            end = np.inf if end == "" else float(end)
            assert not name in intervals, "Stratum name must be unique (duplicated name: %s)" % name
            intervals[name] = (start, end)
        arg_dict["strata_num_intervals"] = intervals
    if args.strata_cat != "NA" and args.strata_cat_ids != "NA":
        categories = {}
        for name_c in arg_dict["strata_cat_ids"].split(","):
            name, c = name_c.split("=")
            name = name.strip()
            assert name != "", "Stratum name should not be an empty string"
            c = frozenset(map(str.strip, c.split(":")))
            assert not name in categories, "Strata name must be unique (duplicated name: %s)" % name
            categories[name] = c
        arg_dict["strata_cat_ids"] = categories


def read_sumstats(sumstats_f, sep, snpid_col, pval_col):
    """
    Filter original summary stats file.
    Args:
        sumstats_f: sumstats file name
        sep: column separator in sumstats_f
        snpid_col: a name of column with variant ids
        pval_col: a name of column with variant p-values
    Returns:
        df: filtered p-values, pd.DataFrame(index=snp_id, values=pval)
    """
    print("Reading %s" % sumstats_f)
    cols2use = [snpid_col, pval_col]
    df = pd.read_csv(sumstats_f, usecols=cols2use, index_col=snpid_col,
        sep=sep)
    print("%d SNPs in %s" % (len(df), sumstats_f))
    df = df.loc[np.isfinite(df[pval_col]),:]
    print("%d SNPs with defined p-value" % len(df))
    df = df.loc[df[pval_col]>0,:]
    print("%d SNPs with non-zero p-value" % len(df))
    df = drop_duplicated_ind(df)
    return df


def read_strata_cat(strata_f, sep, snpid_col, strata_cat_col, strata_cat_ids):
    print("Reading strata file %s" % strata_f)
    cols2use = [snpid_col, strata_cat_col]
    df = pd.read_csv(strata_f, usecols=cols2use, index_col=snpid_col, sep=sep,
        dtype={strata_cat_col:str})
    # make a standard name for variant strata column
    if strata_cat_ids == "NA":
        for s in df[strata_cat_col].unique():
            stratum_i = (df[strata_cat_col] == s)
            df.loc[:,s] = stratum_i
    else:
        for name, ids_set in strata_cat_ids.items():
            stratum_i = df[strata_cat_col].isin(ids_set)
            df.loc[:,name] = stratum_i
    df.drop([strata_cat_col], axis=1, inplace=True)
    # keep only variants which are within any stratum
    df = df.loc[df.any(axis=1)]
    assert len(df) > 0, "All strata are empty"
    df = drop_duplicated_ind(df)
    return df


def read_strata_num(strata_f, sep, snpid_col, strata_num_col, strata_num_intervals):
    print("Reading strata file %s" % strata_f)
    cols2use = [snpid_col, strata_num_col]
    df = pd.read_csv(strata_f, usecols=cols2use, index_col=snpid_col, sep=sep,
        dtype={strata_num_col:float})
    for name, (start, end) in strata_num_intervals.items():
        stratum_i = (start<df[strata_num_col]) & (df[strata_num_col]<end)
        df.loc[:,name] = stratum_i
    df.drop([strata_num_col], axis=1, inplace=True)
    # keep only variants which are within any stratum
    df = df.loc[df.any(axis=1)]
    assert len(df) > 0, "All strata are empty"
    df = drop_duplicated_ind(df)
    return df


def read_strata_bin(strata_f, sep, snpid_col, strata_bin):
    print("Reading strata file %s" % strata_f)
    cols2use = [snpid_col] + strata_bin
    df = pd.read_csv(strata_f, usecols=cols2use, index_col=snpid_col, sep=sep,
        dtype=dict.fromkeys(strata_bin, bool))
    df = df.loc[df.any(axis=1)]
    assert len(df) > 0, "All strata are empty"    
    df = drop_duplicated_ind(df)
    return df


def read_weights(weights_f):
    print("Reading weights file %s" % weights_f)
    df = pd.read_csv(weights_f, sep='\t', header=None, names=["snp", "w"],
        index_col="snp")
    # drop zero weights
    df = df.loc[df.w>0,:]
    drop_duplicated_ind(df)
    return df


def get_xy_from_p(p, top_as_dot, p_weights, nbins=200):
    if p_weights is None:
        p_weights = np.ones(len(p))
    p_weights /= sum(p_weights) # normalize weights

    i = np.argsort(p)
    p = p[i]
    p_weights = p_weights[i]
    p_ecdf = np.concatenate([[0], np.cumsum(p_weights)])

    y = np.logspace(np.log10(p[-1]), np.log10(p[top_as_dot]), nbins)
    i = np.searchsorted(p, y, side='right')
    i[0] = len(p)  # last index in p_ecdf
    i[-1] = top_as_dot+1 # top_as_dot index in p_ecdf
    # estimate standard uniform quantiles corresponding to y observed quantiles
    uniform_quantiles = p_ecdf[i]
    x = -np.log10(uniform_quantiles)
    y = -np.log10(y)
    # if top_as_dot = 0, then x_dot and y_dot are empty arrays
    x_dot = -np.log10(p_ecdf[1:top_as_dot+1])
    y_dot = -np.log10(p[:top_as_dot]).values
    return x, y, x_dot, y_dot


def get_ci(p, p_weights, ci_alpha=0.05, nbins=200):
    # TODO: the first part of this function is identical to the first part of
    # get_xy_from_p(), so probably should be merged??
    if p_weights is None:
        p_weights = np.ones(len(p))
    p_weights *= len(p)/sum(p_weights) # normalize weights and imitate order statistics

    i = np.argsort(p)
    p = p[i]
    p_weights = p_weights[i]
    cum_p_weights = np.cumsum(p_weights)

    y = np.logspace(np.log10(p[-1]), np.log10(p[0]), nbins)
    # the following code is inspired by:
    # https://genome.sph.umich.edu/wiki/Code_Sample:_Generating_QQ_Plots_in_R
    # beta_a is our order statistics. For standard uniform distr (expected under null)
    # it follows beta distr:
    # https://en.wikipedia.org/wiki/Order_statistic#Order_statistics_sampled_from_a_uniform_distribution
    i = np.searchsorted(p, y, side='left')
    i[0] = len(p) - 1
    i[-1] = 0
    beta_a = cum_p_weights[i]
    beta_b = len(p) + 1 - beta_a
    lower_ci = -np.log10(sstats.beta.ppf(1-ci_alpha/2, beta_a, beta_b))
    upper_ci = -np.log10(sstats.beta.ppf(ci_alpha/2, beta_a, beta_b))
    x_ci = -np.log10(beta_a/len(p))
    return x_ci, lower_ci, upper_ci

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if callable(obj):
            return str(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series) or isinstance(obj, pd.Index):
            return obj.values.tolist()
        if isinstance(obj, np.float32):
            return np.float64(obj)
        return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    process_args(args)

    df_sumstats = read_sumstats(args.sumstats, args.sep, args.snp, args.p)

    df_strata = None
    if args.strata_cat != "NA":
        df_strata = read_strata_cat(args.strata, args.strata_sep, args.strata_snp,
            args.strata_cat, args.strata_cat_ids)
    elif args.strata_num != "NA":
        df_strata = read_strata_num(args.strata, args.strata_sep, args.strata_snp,
            args.strata_num, args.strata_num_intervals)
    elif args.strata_bin != "NA":
        df_strata = read_strata_bin(args.strata, args.strata_sep, args.strata_snp,
            args.strata_bin)

    if args.weights != 'NA':
        df_weights = read_weights(args.weights)
        snps_with_weight = df_sumstats.index.intersection(df_weights.index)
        print("%d varints from %s have weight" % (len(snps_with_weight), args.sumstats))
        assert len(snps_with_weight) > 0, ("At least one variant from %s must "
            "have weight in %s if weights are provided" % (args.sumstats, args.weights))
        print("Only they will be plotted") 
        df_sumstats = df_sumstats.loc[snps_with_weight,:]
        df_sumstats["weights"] = df_weights.loc[snps_with_weight,:]
    else:
        # if weights are not provided set equal weights to all SNPs
        df_sumstats["weights"] = 1.

    if not df_strata is None:
        # drop variants which are not in df_sumstats
        df_strata = df_strata.loc[df_strata.index.isin(df_sumstats.index),:]
    # df_strata is either None or:
    # df_strata = DataFrame(index=snp_ids, columns=boolean_strata)

    x, y, x_dot, y_dot = get_xy_from_p(df_sumstats[args.p], args.top_as_dot,
        df_sumstats["weights"])
    x_ci, lower_ci, upper_ci = get_ci(df_sumstats[args.p], df_sumstats["weights"])

    # estimate axis limits
    max_x_lim = max(x[-1],x_ci[-1], 0 if args.top_as_dot==0 else x_dot[0])
    max_y_lim = max(y[-1],upper_ci[-1], 0 if args.top_as_dot==0 else y_dot[0])

    print("Making plot")
    json_data = {}
    fig, ax = plt.subplots(figsize=(6,6), dpi=200)

    # plot null and ci
    ax.fill_between(x_ci, lower_ci, upper_ci, color="0.8"); json_data['x_ci'] = x_ci; json_data['lower_ci'] = lower_ci; json_data['upper_ci'] = upper_ci
    ax.plot([0,x_ci[-1]], [0,x_ci[-1]], ls='--', lw=1, marker=' ', color="k")
    # plot all data
    if df_strata is None:
        ax.plot(x, y, ls='-', lw=1, marker=' ', label="all variants", color='C0'); json_data['x'] = x; json_data['y'] = y
        if args.top_as_dot > 0:
            ax.plot(x_dot, y_dot, ls=' ', marker='.', ms=1, color='C0'); json_data['x_dot'] = x_dot; json_data['y_dot'] = y_dot

    # plot strata
    if not df_strata is None:
        json_data['stratum'] = []
        for j, stratum_id in enumerate(df_strata.columns):
            i = df_strata.index[df_strata[stratum_id]]
            json_stratum = {'stratum_id':stratum_id}
            x, y, x_dot, y_dot = get_xy_from_p(df_sumstats.loc[i,args.p],
                args.top_as_dot, df_sumstats.loc[i,"weights"])
            color = "C%d" % ((j%9)+1); json_stratum['color'] = color
            ax.plot(x, y, ls='-', lw=1, marker=' ', label=stratum_id, color=color); json_stratum['x'] = x; json_stratum['y'] = y
            if args.top_as_dot > 0:
                ax.plot(x_dot, y_dot, ls=' ', marker='.', ms=1, color=color); json_stratum['x_dot'] = x_dot; json_stratum['y_dot'] = y_dot
            # update upper limits if needed
            max_x_lim = max(max_x_lim, x[-1], 0 if args.top_as_dot==0 else x_dot[0])
            max_y_lim = max(max_y_lim, y[-1], 0 if args.top_as_dot==0 else y_dot[0])
            json_data['stratum'].append(json_stratum)

    ax.set_xlabel(r"expected $\mathrm{-log_{10}(P)}$")
    ax.set_ylabel(r"observed $\mathrm{-log_{10}(P)}$")

    if not args.x_lim is None:
        max_x_lim = args.x_lim
    if not args.y_lim is None:
        max_y_lim = args.y_lim
    ax.set_xlim((-0.005*max_x_lim, 1.01*max_x_lim))
    ax.set_ylim((-0.005*max_y_lim, 1.01*max_y_lim))

    # configure and set title
    title = os.path.splitext(os.path.basename(args.sumstats))[0]
    if args.strata != "NA":
        strata = os.path.splitext(os.path.basename(args.strata))[0]
        title = "%s | %s" % (title, strata)
    ax.set_title(title, fontsize='small'); json_data['title'] = title

    ax.legend(loc='upper left', fontsize="small")

    # remove top and right spines
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    # add offset for left spine
    # ax.spines['left'].set_position(('outward',1))
    # ax.spines['bottom'].set_position(('outward',1))

    plt.grid(True)
    # plt.axis('equal')
    plt.tight_layout()
    # plt.show()

    plt.savefig(args.out)
    print("%s was generated" % args.out)

    with open(args.out + '.json', 'w') as outfile:  
        json.dump(json_data, outfile, cls=NumpyEncoder)    
    print("%s.json was generated" % args.out)

    print("Done.")
