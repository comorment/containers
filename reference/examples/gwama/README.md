This folder downloaded from https://genomics.ut.ee/en/tools/gwama

#GWAMA
Software tool for meta analysis of whole genome association data

Background

Genome-wide association (GWA) studies have proved to be extremely successful in identifying moderate genetic effects contributing to complex human phenotypes. However, to gain insights into increasingly more modest signals of association, samples of many thousands of individuals are required. One approach to overcome this problem is to combine the results of GWA studies from closely related populations via meta-analysis, without direct exchange of genotype and phenotype data.

We have developed the GWAMA (Genome-Wide Association Meta Analysis) software to perform meta-analysis of the results of GWA studies of binary or quantitative phenotypes. Fixed- and random-effect meta-analyses are performed for both directly genotyped and imputed SNPs using estimates of the allelic odds ratio and 95% confidence interval for binary traits, and estimates of the allelic effect size and standard error for quantitative phenotypes. GWAMA can be used for analysing the results of all different genetic models (multiplicative, additive, dominant, recessive). The software incorporates error trapping facilities to identify strand alignment errors and allele flipping, and performs tests of heterogeneity of effects between studies.

Citations:
GWAMA PROGRAM:
Magi R, Morris AP: GWAMA: software for genome-wide association meta-analysis. BMC Bioinformatics 2010, 11:288. (link)

SEX-SPECIFIC ANALYSIS METHOD:
Magi R, Lindgren CM, Morris AP: Meta-analysis of sex-specific genome-wide association studies. Genetic Epidemiology 2010, 34(8):846-853. (link)

# https://genomics.ut.ee/en/tools/gwama-tutorial

GWAMA tutorial
INTRODUCTION
GWAMA (Genome-Wide Association Meta Analysis) software has been developed to perform meta-analysis of the results of GWA studies of binary or quantitative phenotypes. The software incorporates error trapping facilities to identify strand alignment errors and allele flipping, and performs tests of heterogeneity of effects between studies.

INSTALLATION (UNIX)
Copy gwama.zip file into your computer, unzip the file:

unzip gwama.zip

To compile GWAMA program, use command:

make

in the folder where files have been unpacked. The program can be run by typing:

GWAMA

INSTALLATION (WINDOWS)
Copy gwama.zip file into your computer and unpack the *.msi file.

Double-click on the *.msi file and follow the installation instructions.

The program can be run by typing:

c:\Program Files\WTCHG\gwama\gwama (if installed into default folder)
In case of any questions or comments please dont hesitate to contact the authors.
 

INPUT FILES
For running GWAMA you have to create an input file (default name “gwama.in”), which contains the list of all study files. The should have each results' file on separate row. If genderwise heterogeneity analysis option is used, second column should identify if the cohort contains males (M) or females (F) data.

Sample “gwama.in” file:

Pop1.txt M
Pop2.txt M
Pop3.txt F
 

Each GWA study file has mandatory column headers:

1) MARKERNAME – snp name

2) EA – effect allele

3) NEA – non effect allele

4) OR - odds ratio

5) OR_95L - lower confidence interval of OR

6) OR_95U - upper confidence interval of OR

In case of quantitative trait:

4) BETA – beta

5) SE – std. error

Study files might also contain columns:

7) N - number of samples

8) EAF – effect allele frequency

9) STRAND – marker strand (if the column is missing then program expects all markers being on positive strand)

10) IMPUTED – if marker is imputed or not (if the column is missing then all markers are counted as directly genotyped ones)

 

Sample study file (NB! This file is a quantitative trait one and GWAMA has to be run with -qt command line option):

MARKERNAME STRAND CHR POS IMP EA NEA BETA SE
rs12565286 + 1 761153 0 G C -0.02 0.0403
rs2977670 + 1 763754 0 C G -0.01 0.40612
rs12138618 + 1 790098 0 G A -0.07 0.37
rs3094315 + 1 792429 0 G A 0.0258 0.1012
rs3131968 + 1 794055 0 G A -0.373 0.0101
rs2519016 + 1 805811 0 T C 0.26 0.3472
rs12562034 + 1 808311 0 G A 0.0092 0.2

Input files must be either tab or space delimited. Files must not have empty columns as multiple separators are treated as one. Files may contain additional columns, which are not used by GWAMA.

RUNNING GWAMA
Command line options:

GWAMA

--filelist {filename} or -i {filename} Specify studies' result files. Default = gwama.in

--output {fileroot} or -o {fileroot} Specify file root for output of analysis. Default = gwama (gwama.out, gwama.gc.out)

--random or -r Use random effect correction. Default = disabled

--genomic_control or -gc Use genomic control for adjusting studies' result files. Default = disabled

--genomic_control_output or -gco Use genomic control on meta-analysis summary (i.e. results of meta- analysis are corrected for gc). Default = disabled

--quantitative or -qt Select quantitative trait version (BETA and SE columns). Default = binary trait

--map {filename} or -m {filename} Select file name for marker map.

--threshold {0-1} or -t {0-1} The p-value threshold for showing direction in summary effect directions. Default = 1

--no_alleles No allele information has been given. Expecting always the same EA.

--indel_alleles Allele labes might contain more than single letter. No strand checks.

--sex Run gender-differentiated and gender- heterogeneity analysis (method described in paper Magi, Lindgren & Morris 2010). Gender info must be provided in filelist file. (second column after file names is either M or F).

--name_marker alternative header to marker name column

--name_strand alternative header to strand column

--name_n alternative header to sample size col

--name_ea alternative header to effect allele column

--name_nea alternative header to non-effect allele column

--name_eaf alternative header to effect allele frequency column

--name_beta alternative header to beta column

--name_se alternative header to std. err. col

--name_or alternative header to OR column

--name_or_95l alternative header to OR 95L column

--name_or_95u alternative header to OR 95U column

--help or -h Print this help

--version or -v Print GWAMA version number
 

OUTPUT FILES
GWAMA generates following output files:

gwama.out (or 'fileroot'.out if --output option is used)
This file contains results of meta-analysis. Output file has following columns:

chromosome - Marker chromosome
position - Marker position (bp)
rs_number - Marker ID
reference_allele - Effect allele
other_allele - Non effect allele

OR - Overall odds ratio for meta-analysis
OR_95L - Lower 95% CI for OR
OR_95U - Upper 95% CI for OR

IN CASE OF QUANTITATIVE TRAIT (-qt)
beta - Overall beta value for meta-analysis
beta_95L - Lower 95% CI for BETA
beta_95U - Upper 95% CI for BETA

z - Z-score
p-value - Meta-analysis p-value
-log10_p-value - Absolut value of logarithm of meta-analysis p-value to the base of 10.
q_statistic - Cochran's heterogeneity statistic
q_p-value - Cochran's heterogeneity statistic's p-value
i2 - Heterogeneity index I2 by Higgins et al 2003
n_studies - Number of studies with marker present
n_samples - Number of samples with marker present (will be NA if marker is present in any input file where N column is not present)
effects - Summary of effect directions ('+' - positive effect of reference allele, '-' - negative effect of reference allele, '0' - no effect (or non-significant) effect of reference allele, '?' - missing data)

gwama.gc.out (or 'fileroot'.gc.out if --output option is used)
This file contains lambda values for GC correction. The file is only generated, if -gc oprion is used.

gwama.log.out
This file contains all log information about current GWAMA run. Each error and warning has unique error code. More information for them can be found from gwama.err.out file.

gwama.err.out
This file contains all errors and warning generated during GWAMA run. Information about any error can be searched according to error code. For example in UNIX:
grep E000000001 gwama.err.out
gives information about error E000000001

GENDER SPECIFIC ANALYSIS
If gender specific analysis option is used, additional columns will appear into output file. All male_ and female_ columns are calculated using cohorts with defined gender.

male_eaf
male_OR (or beta if quantitative trait is analysed)
male_OR_se
male_OR_95L
male_OR_95U
male_z
male_p-value
male_n_studies
male_n_samples
female_eaf
female_OR
female_OR_se
female_OR_95L
female_OR_95U
female_z
female_p-value
female_n_studies
female_n_samples
gender_differentiated_p-value - combined p-value of males and females assuming different effect sizes between genders (2 degrees of freedom)
gender_heterogeneity_p-value - heterogeneity between genders (1 degree of freedom)

Paper describing gender specific analysis framework has beed submitted.

CREATING PLOTS
Manhattan and QQ plots can be created with accompanied R scripts.

R --slave --vanilla < MANH.R

R --slave --vanilla < QQ.R

By default they expect input file name "gwama.out" and they create output files: "gwama.out.qq.png" and "gwama.out.manh.png". Different names can be used as:

R --slave --vanilla --args input=inputfilename out=outputfilename < QQ.R

Manhattan plot can be drawn, if chromosomal position have been added to the file (for example command line: --map hapmap35.map)

R version 2.9.0 or later must be used with png support

CITING REFERENCES
Magi R, Morris AP: GWAMA: software for genome-wide association meta-analysis. BMC Bioinformatics 2010, 11:288.

Magi R, Lindgren CM, Morris AP: Meta-analysis of sex-specific genome-wide association studies. Genetic Epidemiology 2010, 34(8):846-853.
