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
        os.system(f"cp {os.path.join(cwd, 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'gwas', 'config.yaml')} {d}")
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
        os.system(f"cp {os.path.join(cwd, 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'gwas', 'config.yaml')} {d}")
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


def test_gwas_py_saige():
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        os.system(f"cp {os.path.join(cwd, 'gwas', 'gwas.py')} {d}")
        os.system(f"cp {os.path.join(cwd, 'gwas', 'config.yaml')} {d}")
        call = (
            f"singularity exec -B {ref} --home {d}:/home {p3_sif} python"
            " gwas.py gwas --argsfile"
            f" {os.path.join(ref, 'example_3chr_vcf.argsfile')} --pheno PHENO"
            " PHENO2 --covar PC1 PC2 BATCH --analysis saige figures --out"
            " run3_saige"
        )
        out = subprocess.run(call.split(" "))
        expected_files = [
            "run3_saige.1.job",
            "run3_saige.2.job",
            "run3_saige.3.job",
            "run3_saige.4.job",
            "run3_saige.5.job",
            "run3_saige.log",
            "run3_saige.pheno",
            "run3_saige.sample",
            "run3_saige_cmd.sh",
        ]
        assert all(map(os.path.isfile, expected_files))
        assert out.returncode == 0
        os.chdir(cwd)
