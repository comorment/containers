.. template documentation master file, created by
   sphinx=quickstart on Fri Oct 14 10:51:33 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the CoMorMent-container's documentation!
===================================================

This is the online documentation for the CoMorMent-containers project, 
hosted at `GitHub.com/CoMorMent/containers <https://github.com/comorment/containers>`_. 

.. toctree::
   :caption: Containers
   :maxdepth: 0
   
   README

.. toctree::
   :caption: Documentation
   :glob:
   :maxdepth: 0
   
   docs/README
   docs/singularity/*
   docs/specifications/*

.. toctree::
   :caption: Docker
   :maxdepth: 0
   
   docker/README

.. toctree::
   :caption: Reference
   
   reference/README

.. toctree::
   :caption: Scripts
   :maxdepth: 0
   
   scripts/README
   scripts/gwas/README
   scripts/pgs/README
   scripts/pgs/LDpred2/README
   scripts/pgs/pgs_toolkit/README

.. toctree::
   :caption: Singularity
   :maxdepth: 0
   
   singularity/README

.. toctree::
   :caption: Usecases
   :glob:
   :maxdepth: 0
   
   usecases/*

.. toctree::
   :caption: Other
   :maxdepth: 0
   
   CHANGELOG
   CONTRIBUTING


.. include:: ../../README.md
   :parser: myst_parser.sphinx_

.. include:: ../../docs/README.md
   :parser: myst_parser.sphinx_

.. include:: ../../docker/README.md
   :parser: myst_parser.sphinx_

.. include:: ../../reference/README.md
   :parser: myst_parser.sphinx_

.. include:: ../../scripts/README.md
   :parser: myst_parser.sphinx_

.. include:: ../../usecases/README.md
   :parser: myst_parser.sphinx_

.. include:: ../../CHANGELOG.md
   :parser: myst_parser.sphinx_

.. include:: ../../CONTRIBUTING.md
   :parser: myst_parser.sphinx_


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
