# 2016-03-31

Here are a list of sites included in the Haplotype Reference Consortium Release 1.1 (HRC.r1-1).
See the HRC website for more details:

	http://www.haplotype-reference-consortium.org/

## Release summary

The HRC.r1-1 release consists of 39,131,578 autosomal polymorphic SNPs from 32,470 samples.
Additionally, we have now added 1,273,927 chromosome X polymorphic SNPs from 31,500 samples (13,752 male/17,748 female).
The reference coordinates are GRCh37.

## Changes since HRC.r1

 1. A set of 18 samples from the AMD cohorts were removed due to not having permission to use. Now 32,470 samples total.
 2. After identifying a processing issue with chromosomes 9,10,11,12,13,14,15,17, haplotypes for these chromsosomes have bee recalulated from scratch as been replaced.
 3. The minor allele count >= 5 (MAC5) cutoff has been re-applied after above removals/replacements.
 4. chrX has been added with 31,500 samples (does not include PROJECTMINE and 35 other samples).
 5. Ancestral allele (AA) has been added to the INFO field.

## Release files

The VCF is tabix indexed, so one can query a region remotely using `tabix` or `bcftools`.

	tabix ftp://ngs.sanger.ac.uk/production/hrc/HRC.r1-1/HRC.r1-1.GRCh37.wgs.mac5.sites.vcf.gz 16:235540-236540
	bcftools view ftp://ngs.sanger.ac.uk/production/hrc/HRC.r1-1/HRC.r1-1.GRCh37.wgs.mac5.sites.vcf.gz 16:235540-236540

One can also use bcftools to remotely to filter sites. For example to select sites with a minor allele count of 10 or more on chromosome 20:

	bcftools view -c10:minor ftp://ngs.sanger.ac.uk/production/hrc/HRC.r1/HRC.r1.GRCh37.autosomes.mac5.sites.vcf.gz 20

The INFO fields available in the VCF are:

	AC: Non-reference allele count across all HRC.r1 cohorts
	AN: Non-reference allele number across all HRC.r1 cohorts
	AF: Non-reference allele frequency across all HRC.r1 cohorts (AC/AN)
	AC_EXCLUDING_1000G: Non-reference allele count across all HRC.r1 cohorts excluding 1000G samples
	AN_EXCLUDING_1000G: Non-reference allele number across all HRC.r1 cohorts excluding 1000G samples
	AF_EXCLUDING_1000G: Non-reference allele frequency across all HRC.r1 cohorts excluding 1000G samples (AC_EXCLUDING_1000G/AN_EXCLUDING_1000G)
	AA: Ancestral allele (based on ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/pilot_data/technical/reference/ancestral_alignments)

The ID column is annotated with rsids from dbSNP142.

There is also a tab-delimited file available with these fields as columns.
This tab-delimited file has also been indexed with tabix, so regions can be queried like:

	tabix ftp://ngs.sanger.ac.uk/production/hrc/HRC.r1-1/HRC.r1-1.GRCh37.wgs.mac5.sites.tab.gz 16:235540-236540

Use the `tabix -h` option to include column headers.

## Site counts

Site counts per-chromosome are:

1	3069931
2	3392237
3	2821894
4	2787581
5	2588168
6	2460111
7	2289305
8	2242705
9	1686471
10	1927503
11	1936990
12	1848117
13	1385433
14	1270436
15	1139215
16	1281297
17	1090072
18	1104755
19	868554
20	884983
21	531276
22	524544
X.PAR1	42298
X.nonPAR	1228034
X.PAR2	3595
