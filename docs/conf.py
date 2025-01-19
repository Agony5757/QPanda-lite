# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pathlib
parent_path = pathlib.Path(__file__).resolve().parent.parent

sys.path.insert(0, os.path.abspath(parent_path))
sys.path.insert(0, os.path.abspath(parent_path / 'simulator'))
sys.path.insert(0, os.path.abspath(parent_path / 'originir'))
sys.path.insert(0, os.path.abspath(parent_path / 'task'))
sys.path.insert(0, os.path.abspath(parent_path / 'task' / 'originq'))
sys.path.insert(0, os.path.abspath(parent_path / 'task' / 'quafu'))
sys.path.insert(0, os.path.abspath(parent_path / 'task' / 'ibm'))

# -- Project information -----------------------------------------------------

project = 'QPanda-lite'
copyright = '2023, Agony5757'
author =  ', '.join(['Agony5757', 'YunJ1e', 'automatic-code-ztr', 'didaozi'])

# The full version, including alpha/beta/rc tags
release = '0.1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'recommonmark',
    'myst_parser',
    'sphinx.ext.viewcode'
]

# -- Options for myst_parser
# See https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# Sphinx's autodoc can be configured to mock certain imports so that they don't actually get executed. 
autodoc_mock_imports = ["qiskit", "qiskit_ibm_provider", "quafu", "pandas", "QPandaLitePy"]
os.environ['SPHINX_DOC_GEN'] = '1'
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'zh_CN'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autodoc_typehints = "description"
source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

try:
    import sphinx_rtd_theme
    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except:
    import warnings
    warnings.warn('sphinx_rtd_theme is not installed in this environment.\n'
                  'Compilation continues.')
