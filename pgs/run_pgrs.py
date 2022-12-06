# run script
import os
import pgrs
import subprocess

if __name__ == '__main__':
    # enviroment variables for test runs
    os.environ.update(dict(
        CONTAINERS=os.path.split(os.getcwd())[0],
    ))
    os.environ.update(dict(
        SIF=os.path.join(os.environ['CONTAINERS'], 'singularity'),
        REFERENCE=os.path.join(os.environ['CONTAINERS'], 'reference')
    ))
    os.environ.update(dict(
        SINGULARITY_BIND=f'{os.environ["REFERENCE"]}:/REF'
    ))

    # Executables in containers
    SIF = os.environ['SIF']
    PWD = os.getcwd()
    os.environ.update(
        dict(
            BASH_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif bash",
            GUNZIP_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif gunzip",
            GZIP_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif gzip",
            AWK_EXEC=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif awk",
            RSCRIPT=f"singularity exec --home={PWD}:/home {SIF}/r.sif Rscript",
            PLINK=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif plink",
            PRSICE=f"singularity exec --home={PWD}:/home {SIF}/gwas.sif PRSice_linux",
        ))

    #######################################
    # Standard GWAS QC. 
    # Note: This will perform the QC steps from 
    # https://choishingwan.github.io/PRS-Tutorial/ 
    # but is probably not something you would apply without caution.
    #######################################

    # output dir for QC'd data.
    QC_data = 'QC_data'

    qc = pgrs.Standard_GWAS_QC(
        Sumstats_file='/REF/examples/prsice2/Height.gwas.txt.gz',
        Pheno_file='/REF/examples/prsice2/EUR.height',
        Input_dir='/REF/examples/prsice2',
        Data_prefix='EUR',
        Output_dir=QC_data,
        Phenotype='Height',
    )
    for call in qc.get_str():
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0


    #######################################
    # Plink
    #######################################
    plink = pgrs.PGS_Plink(
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file='/REF/examples/prsice2/EUR.height',
        Input_dir=QC_data,
        Data_prefix='EUR',
        Output_dir='PGS_plink',
        Cov_file='/REF/examples/prsice2/EUR.cov',
        clump_p1=1,
        clump_r2=0.1,
        clump_kb=250,
        range_list=[0.001, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
        strat_indep_pairwise=[250, 50, 0.25],
        nPCs=6,
        score_args=[3, 4, 12, 'header'],
    )
    # run preprocessing steps for plink
    for call in plink.get_str(mode='preprocessing'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True)
        assert proc.returncode == 0    

    # run basic plink PGS
    for call in plink.get_str(mode='basic'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

    # run plink PGS with population stratification
    for call in plink.get_str(mode='stratification'):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0


    #######################################
    # PRSice-2
    #######################################
    prsice2 = pgrs.PGS_PRSice2(
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file=f'/REF/examples/prsice2/EUR.height',
        Input_dir=QC_data,
        Data_prefix='EUR',
        Output_dir='PGS_prsice2',
        Cov_file='/REF/examples/prsice2/EUR.cov',
        Eigenvec_file='/REF/examples/prsice2/EUR.eigenvec',
        nPCs=6,
        MAF=0.01,
        INFO=0.8
    )
    for call in prsice2.get_str():
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0


    #######################################
    # LDpred2 infinitesimal model
    #######################################
    ldpred2_inf = pgrs.PGS_LDpred2(
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file='/REF/examples/prsice2/EUR.height',
        Input_dir=QC_data,
        Data_prefix='EUR.QC',
        Output_dir='PGS_LDpred2_inf',
        method='inf',
        keep_SNPs_file='/REF/hapmap3/w_hm3.justrs', 
    )
    # run
    for call in ldpred2_inf.get_str(create_backing_file=True):
        print(f'\nevaluating: {call}\n')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0
    

    #######################################
    # LDpred2 automatic model
    #######################################
    ldpred2_auto = pgrs.PGS_LDpred2(
        Sumstats_file=os.path.join(QC_data, 'Height.QC.gz'),
        Pheno_file='/REF/examples/prsice2/EUR.height',
        Input_dir=QC_data,
        Data_prefix='EUR.QC',
        Output_dir='PGS_LDpred2_auto',
        method='auto',
        keep_SNPs_file='/REF/hapmap3/w_hm3.justrs', 
    )
    # run
    for call in ldpred2_auto.get_str(create_backing_file=True):
        print(f'evaluating: {call}')
        proc = subprocess.run(call, shell=True, check=True)
        assert proc.returncode == 0

