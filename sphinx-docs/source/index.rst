.. template documentation master file, created by
   sphinx=quickstart on Fri Oct 14 10:51:33 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

   Here is an overview of how we may want the doc's TOC to be
   (As a starting point we may have only root-level listed in the docs, and everything else expanding upon user clicking on that node)

   Introduction
   Getting started 
      (hello.sif)
   Installation
   Singularity containers 
      (documentation specific to each container (including containers shared in other repositories))
      hello.sif
         Software list
      gwas.sif
         Software list, including refs to documentation
      python.sif
         Software list
      R.sif
         Software list
         For more documentation on LDpred2 see [scripts] folder.
      ldsc.sif
         * reference overview
         * usage exampe
      HDL.sif (external repo)
      MAGMA.sif
      MiXeR.sif 
      ...
   specification of data formats
      geno
      pheno
      sumstats
   reference data
      For tool-specifc referece, see [container documentation]
      * opensnp dataset
      * summary statistics (HEIGHT, hair color, ...)
      * ? 1kG files if needed
   scripts (tools / toolkits / pipelines)
      gwas
         usage example (with data included in the repo, i.e. opensnp dataset)
      pgs_toolkit
         this supports usage from python
      ldpred2
   usecases / tutorials (UKB, MoBa, ADNI, ..)
      can be READMe files, but also jupyter notebooks
   API usage
      pgs_toolkit
   Contributing / dev instructions (wiki-like content)
   Change log
   Internal usage (p33/p697/Tryggve collaborators)

Welcome to the COSGAP-Container's documentation!
================================================

This is the online documentation for the COSGAP-Container project, 
hosted at `GitHub.com/CoMorMent/containers <https://github.com/comorment/containers>`_. 

.. toctree::
   :caption: Table of Contents
   :maxdepth: 1
   
   MAIN

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
