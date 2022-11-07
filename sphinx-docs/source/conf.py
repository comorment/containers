# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath('.'))


# -- Release information
_d = {}
exec(open(os.path.join('..', '..', 'version', 'version.py')
          ).read(), None, _d)
_release = _d['VERSION']


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'CoMorMent-containers'
copyright = '2022, Richard Zetterberg, John Shorter, Espen Hagen, Bayram Cevdet Akdeniz, Alexander Frei'
author = 'Richard Zetterberg, John Shorter, Espen Hagen, Bayram Cevdet Akdeniz, Alexander Frei'
release = _release

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'm2r2'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']