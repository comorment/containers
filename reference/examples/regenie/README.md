Files in this folder are copied from https://github.com/rgcgithub/regenie/tree/master/example

example_3chr.pheno is generated as follows:

import numpy as np
f='/home/oleksanf/github/comorment/containers/reference/examples/regenie/'
fam=read_fam(f+'example_3chr.fam')
fam=fam.sample(490)[['IID', 'PHENO']]
fam=pd.concat([fam, pd.DataFrame({'IID': [1111], 'PHENO':[6.66] } )])
fam['PHENO2'] = fam.sample(frac=1)['PHENO'].values
fam['CASE']=(fam['PHENO']>0).astype(int).astype(str)
fam['CASE2']=(fam['PHENO2']>0).astype(int).astype(str)
fam['PC1'] = fam.sample(frac=1)['PHENO'].values
fam['PC2'] = fam.sample(frac=1)['PHENO'].values

fam['BATCH']=[('B1' if (x < -0.5) else ('B2' if (x < 0.5) else 'B3')) for x in fam['PHENO'].values]
for c in fam.columns:
    if c=='IID': continue
    fam.loc[fam.sample(10).index, c] = np.nan
fam.to_csv(f+'example_3chr.pheno',sep=',', index=False)

with open(f+'example_3chr.pheno.dict', 'w') as f:
    f.write("""COLUMN,TYPE,DESCRIPTION
IID,IID,Identifier
PHENO,CONTINUOUS,phenotype
PHENO2,CONTINUOUS,second phenotype
CASE,BINARY,case/control phenotype
CASE2,BINARY,another case/control phenotype
PC1,CONTINUOUS,principal component1
PC2,CONTINUOUS,second principal component
BATCH,NOMINAL,genotype batch
""")


#.info file
import pandas as pd
import numpy as np
df=pd.read_csv('example_3chr.bim', delim_whitespace=True, header=None)
df['INFO']=[np.random.rand() for x in df[1].values]
df.rename(columns={1:'SNP'}, inplace=True)
df[['SNP', 'INFO']].to_csv('example_3chr.info',sep='\t')


bgzip -c example_3chr.vcf > example_3chr.vcf.gz
tabix -p vcf example_3chr.vcf.gz
tabix -p vcf --csi example_3chr.vcf.gz

