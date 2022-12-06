# PGS toolset

More on PGS: https://choishingwan.github.io/PRS-Tutorial/


## Environment variables


```
export CONTAINERS=<path/to/containers/repo>  # modify accordingly
export SIF=$CONTAINERS/singularity
export REFERENCE=$CONTAINERS/reference
export SINGULARITY_BIND=$REFERENCE:/REF
```


## 1. Summary statistics file

Before anything, define path to summary statistics file from GWAS. 
We also create a working dir in the local folder
```
export fileSumstats=/REF/examples/prsice2/Height.gwas.txt.gz
export QCDIR=QC_data
export WORKDIR=$PWD/$QCDIR
mkdir $WORKDIR
```

Create aliases for different containerized tools and utilities
```
export BASH_EXEC="singularity exec --home=$PWD:/home $SIF/gwas.sif bash"
export GUNZIP_EXEC="singularity exec --home=$PWD:/home $SIF/gwas.sif gunzip"
export GZIP_EXEC="singularity exec --home=$PWD:/home $SIF/gwas.sif gzip"
export AWK_EXEC="singularity exec --home=$PWD:/home $SIF/gwas.sif awk"
export RSCRIPT="singularity exec --home=$PWD:/home $SIF/r.sif Rscript"
export PLINK="singularity exec --home=$PWD:/home $SIF/gwas.sif plink"
export PRSICE="singularity exec --home=$PWD:/home $SIF/gwas.sif PRSice_linux"
```

### Standard GWAS QC 

Taken from:
https://choishingwan.github.io/PRS-Tutorial/base/#standard-gwas-qc

Filter summary statistics file, zip output.
```
$GUNZIP_EXEC -c $fileSumstats |\
$AWK_EXEC 'NR==1 || ($11 > 0.01) && ($10 > 0.8) {print}' |\
$GZIP_EXEC -> $QCDIR/Height.gz
```

Remove duplicates
```
$GUNZIP_EXEC -c $QCDIR/Height.gz |\
$AWK_EXEC '{seen[$3]++; if(seen[$3]==1){ print}}' |\
$GZIP_EXEC -> $QCDIR/Height.nodup.gz
```

Retain nonambiguous SNPs:
```
$GUNZIP_EXEC -c $QCDIR/Height.nodup.gz |\
$AWK_EXEC '!( ($4=="A" && $5=="T") ||  ($4=="T" && $5=="A") || ($4=="G" && $5=="C") || ($4=="C" && $5=="G")) {print}' |\
$GZIP_EXEC -> $WORKDIR/Height.QC.gz
```

### QC target data

Modified from
https://choishingwan.github.io/PRS-Tutorial/target/#qc-of-target-data

Standard GWAS QC. First export some environment variables:
```
export INPUTDATAPATH=/REF/examples/prsice2
export DATAPREFIX=EUR
```


```
$PLINK --bfile $INPUTDATAPATH/$DATAPREFIX \
       --maf 0.01 \
       --hwe 1e-6 \
       --geno 0.01 \
       --mind 0.01 \
       --write-snplist \
       --make-just-fam \
       --out $QCDIR/$DATAPREFIX.QC
```

Prune to remove highly correlated SNPs
```
$PLINK --bfile $INPUTDATAPATH/$DATAPREFIX \
       --keep $QCDIR/$DATAPREFIX.QC.fam \
       --extract $QCDIR/$DATAPREFIX.QC.snplist \
       --indep-pairwise 200 50 0.25 \
       --out $QCDIR/$DATAPREFIX.QC
```

Compute heterozygosity rates, generating the EUR.QC.het file:
```
$PLINK --bfile $INPUTDATAPATH/$DATAPREFIX \
       --extract $QCDIR/$DATAPREFIX.QC.prune.in \
       --keep $QCDIR/$DATAPREFIX.QC.fam \
       --het \
       --out $QCDIR/$DATAPREFIX.QC
```

remove individuals with F coefficients that are more than 3 standard deviation (SD) units from the mean in ``R``:
```
$RSCRIPT create_valid_sample.R \
       $QCDIR/$DATAPREFIX.QC.het \
       $QCDIR/$DATAPREFIX.valid.sample
```

strand-flipping the alleles to their complementary alleles
```
$RSCRIPT strand_flipping.R \
    $INPUTDATAPATH/$DATAPREFIX.bim \
    $QCDIR/Height.QC.gz \
    $QCDIR/$DATAPREFIX.QC.snplist \
    $QCDIR/$DATAPREFIX.a1 \
    $QCDIR/$DATAPREFIX.mismatch
```


Sex-check pre-pruning, generating EUR.QC.sexcheck:
```
$PLINK --bfile $INPUTDATAPATH/$DATAPREFIX \
       --extract $QCDIR/$DATAPREFIX.QC.prune.in \
       --keep $QCDIR/$DATAPREFIX.valid.sample \
       --check-sex \
       --out $QCDIR/$DATAPREFIX.QC
```
Assign individuals as biologically male if F-statistic is > 0.8; biologically female if F < 0.2:
```
$RSCRIPT create_QC_valid.R \
    $QCDIR/$DATAPREFIX.valid.sample \
    $QCDIR/$DATAPREFIX.QC.sexcheck \
    $QCDIR/$DATAPREFIX.QC.valid
```

Relatedness pruning of individuals that have a first or second degree relative
```
$PLINK --bfile $INPUTDATAPATH/$DATAPREFIX \
       --extract $QCDIR/$DATAPREFIX.QC.prune.in \
       --keep $QCDIR/$DATAPREFIX.QC.valid \
       --rel-cutoff 0.125 \
       --out $QCDIR/$DATAPREFIX.QC
```

Generate a QC'ed data set, creating .ai and .mismatch files:
```
$PLINK --bfile $INPUTDATAPATH/$DATAPREFIX \
       --make-bed \
       --keep $QCDIR/$DATAPREFIX.QC.rel.id \
       --out $QCDIR/$DATAPREFIX.QC \
       --extract $QCDIR/$DATAPREFIX.QC.snplist  \
       --a1-allele $QCDIR/$DATAPREFIX.a1 \
       --exclude $QCDIR/$DATAPREFIX.mismatch
```


## PGS

export fileGeno=/REF/examples/prsice2/EUR.bed
# export fileImputedGeno=EUR.imputed.bed
export file
export filePheno=/REF/examples/prsice2/EUR.height
export fileKeepSNPS=/REF/hapmap3/w_hm3.justrs


### LDpred2

The LDPred2 implementation has a few options, ``inf``, ``auto``, and ``grid``, 
but shares the same input files(?)

Required files:
Height.QC.gz	The post-QCed summary statistic
EUR.QC.bed	The genotype file after performing some basic filtering
EUR.QC.bim	This file contains the SNPs that passed the basic filtering
EUR.QC.fam	This file contains the samples that passed the basic filtering
EUR.height	This file contains the phenotype of the samples
EUR.cov	This file contains the covariates of the samples
EUR.eigenvec	This file contains the PCs of the samples

#### LDpred2-inf

Infinitesimal model.

```
export LDPRED2DIR='PGS_ldpred2_inf'
mkdir $LDPRED2DIR
```

Test score output file
```
export fileOut=$LDPRED2DIR/test.score
```

Input files
```
export QC_Sumstats_file=$QCDIR/Height.QC.gz
export QC_Bed_file=$QCDIR/$DATAPREFIX.QC.bed
# export QC_Bim_file=$QCDIR/$DATAPREFIX.QC.bim  # not used
# export QC_Fam_file=$QCDIR/$DATAPREFIX.QC.fam  # not used
# export QC_Pheno_file=$QCDIR/Heigh.QC.gz  # not used
# export Cov_file=/REF/examples/prsice2/$DATAPREFIX.cov  # not used

# Generate PGS using LDPRED2-inf
$RSCRIPT ldpred2.R \
--ldpred-mode inf \
--file-keep-snps $fileKeepSNPS \
--file-pheno $filePheno \
--col-stat OR --col-stat-se SE \
--stat-type OR \
$QC_Bed_file $QC_Sumstats_file $fileOut
```

#### LDpred2-auto

Automatic model

```
export LDPRED2DIR='PGS_ldpred2_auto'
mkdir $LDPRED2DIR
```

Test score output file
```
export fileOut=$LDPRED2DIR/test.score
```

```
export QC_Sumstats_file=$QCDIR/Height.QC.gz
export QC_Bed_file=$QCDIR/$DATAPREFIX.QC.bed

# Generate PGS using LDPRED2-inf
$RSCRIPT ldpred2.R \
--ldpred-mode auto \
--file-keep-snps $fileKeepSNPS \
--file-pheno $filePheno \
--col-stat OR --col-stat-se SE \
--stat-type OR \
$QC_Bed_file $QC_Sumstats_file $fileOut
```

### *LDpred2-grid
### *MegaPRS
### *Plink

Full tutorial
https://choishingwan.github.io/PRS-Tutorial/plink/

Required data:

Height.QC.gz:	The post-QCed summary statistic
EUR.QC.bed:	The genotype file after performing some basic filtering
EUR.QC.bim:	This file contains the SNPs that passed the basic filtering
EUR.QC.fam:	This file contains the samples that passed the basic filtering
EUR.height:	This file contains the phenotype of the samples
EUR.cov:	This file contains the covariates of the samples

#### Preprocessing

environment variables
```
export QC_Sumstats_file=$QCDIR/Height.QC.gz
export QC_Bed_file=$QCDIR/$DATAPREFIX.QC.bed
export QC_Bim_file=$QCDIR/$DATAPREFIX.QC.bim
export QC_Fam_file=$QCDIR/$DATAPREFIX.QC.fam
export QC_Pheno_file=$QCDIR/$DATAPREFIX.height
export Cov_file=/REF/examples/prsice2/$DATAPREFIX.cov
```

```
export PLINKDIR=PGS_plink
mkdir $PLINKDIR
```

Update effect size:
```
$RSCRIPT update_effect_size.R \
    $QC_Sumstats_file \
    $PLINKDIR/Height.QC.transformed
```

Clumping:
```
$PLINK \
    --bfile $QCDIR/$DATAPREFIX.QC \
    --clump-p1 1 \
    --clump-r2 0.1 \
    --clump-kb 250 \
    --clump $PLINKDIR/Height.QC.transformed \
    --clump-snp-field SNP \
    --clump-field P \
    --out $PLINKDIR/$DATAPREFIX
```

Extract index SNP ID:
```
$AWK_EXEC 'NR!=1{print $3}' $PLINKDIR/$DATAPREFIX.clumped > $PLINKDIR/$DATAPREFIX.valid.snp
```

Extract P-values:
```
$AWK_EXEC '{print $3,$8}' $PLINKDIR/Height.QC.transformed > $PLINKDIR/SNP.pvalue
```

Create list of p-value ranges 
```
echo "0.001 0 0.001" > $PLINKDIR/range_list 
echo "0.05 0 0.05" >> $PLINKDIR/range_list
echo "0.1 0 0.1" >> $PLINKDIR/range_list
echo "0.2 0 0.2" >> $PLINKDIR/range_list
echo "0.3 0 0.3" >> $PLINKDIR/range_list
echo "0.4 0 0.4" >> $PLINKDIR/range_list
echo "0.5 0 0.5" >> $PLINKDIR/range_list
```

#### PGS calculation

Calculate PGS
```
$PLINK --bfile $QCDIR/$DATAPREFIX.QC \
       --score $PLINKDIR/Height.QC.transformed 3 4 12 header \
       --q-score-range $PLINKDIR/range_list $PLINKDIR/SNP.pvalue \
       --extract $PLINKDIR/$DATAPREFIX.valid.snp \
       --out $PLINKDIR/$DATAPREFIX
```

Calculate PGS, accounting for population stratification
using PCs as covariates
```
export NPCS=6  # number of PCs
# First, we need to perform prunning
$PLINK \
    --bfile $QCDIR/$DATAPREFIX.QC \
    --indep-pairwise 200 50 0.25 \
    --out $PLINKDIR/$DATAPREFIX
# Then we calculate the first 6 PCs
$PLINK \
    --bfile $QCDIR/$DATAPREFIX.QC \
    --extract $PLINKDIR/$DATAPREFIX.prune.in \
    --pca $NPCS \
    --out $PLINKDIR/$DATAPREFIX
```

### *PRSice2

Tutorial
https://choishingwan.github.io/PRS-Tutorial/prsice/

Required files:
```
Height.QC.gz	The post QC base data file. While PRSice-2 can automatically apply most filtering on the base file, it cannot remove duplicated SNPs
EUR.QC.bed	This file contains the genotype data that passed the QC steps
EUR.QC.bim	This file contains the list of SNPs that passed the QC steps
EUR.QC.fam	This file contains the samples that passed the QC steps
EUR.height	This file contains the phenotype data of the samples
EUR.cov	This file contains the covariates of the samples
EUR.eigenvec	This file contains the principal components (PCs) of the samples
```

Define environment variables
```
export QC_Sumstats_file=$QCDIR/Height.QC.gz
# export QC_Fam_file=$QCDIR/$DATAPREFIX.QC.bed
# export QC_Bim_file=$QCDIR/$DATAPREFIX.QC.bim
# export QC_Fam_file=$QCDIR/$DATAPREFIX.QC.fam
# export QC_Pheno_file=$QCDIR/$DATAPREFIX.height
export Pheno_file=/REF/examples/prsice2/$DATAPREFIX.height
export Cov_file=/REF/examples/prsice2/$DATAPREFIX.cov
export Eigenvec_file=/REF/examples/prsice2/$DATAPREFIX.eigenvec
```

Set up working dir
```
export PRSICEDIR=PGS_prsice2
mkdir $PRSICEDIR
```

Generate .covariate file combining .cov and .eigenvec input files
```
export Coviariate_file=$PRSICEDIR/$DATAPREFIX.covariate
$RSCRIPT generate_covariate.R \
       $Cov_file \
       $Eigenvec_file \
       $Coviariate_file \
       6  # number of PCs
```

Run PGS analysis
```
$RSCRIPT PRSice.R \
    --prsice /usr/bin/PRSice_linux \
    --base $QC_Sumstats_file \
    --target $QCDIR/$DATAPREFIX.QC \
    --binary-target F \
    --pheno $Pheno_file \
    --cov $Coviariate_file \
    --base-maf MAF:0.01 \
    --base-info INFO:0.8 \
    --stat OR \
    --or \
    --out $PRSICEDIR/$DATAPREFIX
```


### *PRS-CS
### SBayesR
### SBayesS