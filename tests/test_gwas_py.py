# encoding: utf-8

"""
Test module for ``gwas.py`` script
"""

import os
import subprocess
import tempfile

p3_sif = os.path.abspath(os.path.join("singularity", "python3.sif"))
cwd = os.getcwd()
ref = os.path.join(cwd, "reference", "examples", "regenie")

os.environ["SINGULARITY_BIND"] = f"{os.path.join(cwd,'reference')}:/REF:ro"
os.environ["COMORMENT"] = f"{os.path.join(cwd, '..')}"


def test_gwas_py_plink():

    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'config.yaml')} {d}")
        call = (
            f"singularity exec -B {ref} --home {d}:/home {p3_sif} python"
            " gwas.py gwas --argsfile"
            f" {os.path.join(ref, 'example_3chr.argsfile')} --pheno CASE CASE2"
            " --covar PC1 PC2 BATCH --analysis plink2 figures --out"
            " run1_plink2"
        )
        out = subprocess.run(call.split(" "))
        expected_files = [
            "run1_plink2.1.job",
            "run1_plink2.2.job",
            "run1_plink2.3.job",
            "run1_plink2.covar",
            "run1_plink2.log",
            "run1_plink2.pheno",
            "run1_plink2.sample",
            "run1_plink2_cmd.sh",
        ]
        assert all(map(os.path.isfile, expected_files))
        assert out.returncode == 0
        os.chdir(cwd)


def test_gwas_py_regenie():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'config.yaml')} {d}")
        call = (
            f"singularity exec -B {ref} --home {d}:/home {p3_sif} python"
            " gwas.py gwas --argsfile"
            f" {os.path.join(ref, 'example_3chr.argsfile')} --pheno PHENO"
            " PHENO2 --covar PC1 PC2 BATCH --analysis regenie figures --out"
            " run2_regenie"
        )
        out = subprocess.run(call.split(" "))
        expected_files = [
            "run2_regenie.1.job",
            "run2_regenie.3.job",
            "run2_regenie.covar",
            "run2_regenie.pheno",
            "run2_regenie_cmd.sh",
            "run2_regenie.2.job",
            "run2_regenie.4.job",
            "run2_regenie.log",
            "run2_regenie.sample",
        ]
        assert all(map(os.path.isfile, expected_files))
        assert out.returncode == 0
        os.chdir(cwd)

def test_gwas_py_variance_standardize():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'config.yaml')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.pheno')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.pheno.dict')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.bed')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.info')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.fam')} {d}")
        os.system(
            "awk -F, 'NR>1 {$2=0}1' OFS=, example_3chr.pheno >"
            " example_3chr.pheno.tmp && mv example_3chr.pheno.tmp"
            " example_3chr.pheno"
        )
        call = (
            f"singularity exec --home {d}:/home {p3_sif} python"
            " gwas.py gwas --pheno-file example_3chr.pheno --geno-fit-file"
            " example_3chr.bed --geno-file example_3chr.bed --info-file"
            " example_3chr.info --fam example_3chr.fam --info 0.8 --chr2use"
            " 1-3 --variance-standardize --maf 0.1 --geno 0.5 --hwe 0.01"
            " --pheno PHENO PHENO2 --covar PC1 PC2 BATCH"
        )
        out = subprocess.run(call.split(" "), capture_output=True)
        assert out.returncode == 1
        assert "column has no variation" in str(out.stderr)
        os.chdir(cwd)


def test_gwas_py_identical_FIDs():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'config.yaml')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.pheno')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.pheno.dict')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.bed')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.info')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.fam')} {d}")
        os.system(
            "awk -F'\t' '{$1=2}1' OFS='\t' example_3chr.fam > "
            "example_3chr.fam.tmp $$ mv example_3chr.fam.tmp example_3chr.fam"
        )
        call = (
            f"singularity exec --home {d}:/home {p3_sif} python"
            " gwas.py gwas --pheno-file example_3chr.pheno --geno-fit-file"
            " example_3chr.bed --geno-file example_3chr.bed --info-file"
            " example_3chr.info --fam example_3chr.fam --info 0.8 --chr2use"
            " 1-3 --variance-standardize --maf 0.1 --geno 0.5 --hwe 0.01"
            " --pheno PHENO PHENO2 --covar PC1 PC2 BATCH"
        )
        out = subprocess.run(call.split(" "), capture_output=True)
        assert out.returncode == 0
        os.chdir(cwd)


# py.test tests/test_gwas_py.py -k test_gwas_py_custom_IIDs
def test_gwas_py_custom_IIDs():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'scripts', 'gwas', 'config.yaml')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.pheno')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.pheno.dict')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.bed')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.info')} {d}")
        os.system(f"cp {os.path.join(ref, 'example_3chr.fam')} {d}")
        os.system(
            "awk -F'\t' '{$1=2}1' OFS='\t' example_3chr.fam > "
            "example_3chr.fam.tmp $$ mv example_3chr.fam.tmp example_3chr.fam"
        )
        os.system(
            "sed -i '2s/.*/SENTRIXID,IID,Identifier/' example_3chr.pheno.dict"
        )
        os.system(
            "sed -i '1s/IID/SENTRIXID/' example_3chr.pheno"
        )
        call = (
            f"singularity exec --home {d}:/home {p3_sif} python"
            " gwas.py gwas --pheno-file example_3chr.pheno --geno-fit-file"
            " example_3chr.bed --geno-file example_3chr.bed --info-file"
            " example_3chr.info --fam example_3chr.fam --info 0.8 --chr2use"
            " 1-3 --variance-standardize --maf 0.1 --geno 0.5 --hwe 0.01"
            " --pheno PHENO PHENO2 --covar PC1 PC2 BATCH"
        )
        out = subprocess.run(call.split(" "))
        assert out.returncode == 0
        os.chdir(cwd)
