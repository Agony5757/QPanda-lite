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

# Only the project root is needed; qpandalite/ lives directly under it.
sys.path.insert(0, os.path.abspath(parent_path))

# Read version from setuptools_scm or git tags
# For stable releases: set DOCS_STABLE_VERSION env var to force clean version

import subprocess
import os

def get_version_from_setuptools_scm(strip_dev=False):
    """Get version from setuptools_scm.

    Args:
        strip_dev: If True, strip .devN+g... suffix to get base version.
                   Used for stable/release builds.
    """
    try:
        from setuptools_scm import get_version
        version = get_version(root=str(parent_path), relative_to=__file__)
        if strip_dev:
            # Extract base version (strip .devN+g... suffix)
            import re
            match = re.match(r'^(\d+\.\d+\.\d+)', version)
            return match.group(1) if match else version
        return version
    except Exception:
        return None

def get_version_from_git_tag():
    """Get clean version from nearest git tag (e.g., v0.3.0 -> 0.3.0)."""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, check=True,
            cwd=str(parent_path)
        )
        tag = result.stdout.strip()
        return tag[1:] if tag.startswith('v') else tag
    except Exception:
        return None

def get_version_from_metadata():
    """Get version from installed package metadata."""
    try:
        from importlib.metadata import version as get_version, PackageNotFoundError
        return get_version('qpandalite')
    except (PackageNotFoundError, Exception):
        return None

def get_version_from_file():
    """Get version from _version.py file."""
    try:
        _version_file = parent_path / 'qpandalite' / '_version.py'
        if _version_file.exists():
            exec(_version_file.read_text())
            return __version__
    except Exception:
        pass
    return None

# If DOCS_STABLE_VERSION=1, use clean version from git tag (for releases)
# Otherwise, use setuptools_scm which shows dev versions for main branch
# RTD sets READTHEDOCS_VERSION env var: 'stable', 'latest', or tag name

# Determine if this is a stable/release build
is_stable = (
    os.environ.get('DOCS_STABLE_VERSION') == '1' or
    os.environ.get('READTHEDOCS_VERSION') == 'stable' or
    (os.environ.get('READTHEDOCS_VERSION', '').startswith('v') and
     os.environ.get('READTHEDOCS') == 'True')
)

if is_stable:
    release = (
        get_version_from_git_tag() or
        get_version_from_setuptools_scm(strip_dev=True) or
        get_version_from_metadata() or
        get_version_from_file() or
        '0.0.0+unknown'
    )
else:
    # Default: show actual version (including dev versions for unreleased changes)
    release = (
        get_version_from_setuptools_scm(strip_dev=False) or
        get_version_from_git_tag() or
        get_version_from_metadata() or
        get_version_from_file() or
        '0.0.0+unknown'
    )

# Get RTD version for version switcher
rtd_version = os.environ.get('READTHEDOCS_VERSION', 'latest')
version_match = rtd_version if rtd_version in ('stable', 'latest') else release

copyright = '2025, Agony5757'
author = ', '.join(['Agony5757', 'YunJ1e', 'automatic-code-ztr', 'didaozi'])
project = 'QPanda-lite'

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
    # 'recommonmark',
    'myst_parser',
    'sphinx.ext.viewcode'
]

# -- Options for myst_parser
# See https://myst-parser.readthedocs.io/en/latest/syntax/optional.html
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "attrs_block",
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
autodoc_mock_imports = ["qiskit", 
                        "qiskit_ibm_provider", 
                        "quafu", 
                        "pandas", 
                        "qpandalite_cpp",
                        "qiskit-aer", 
                        "qutip",
                        "qutip_qip",
                        "matplotlib",
                        "matplotlib.pyplot",
                        "pyqpanda3"]

os.environ['SPHINX_DOC_GEN'] = '1'
# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'zh-CN'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'source/qpandalite.test.rst']
autodoc_typehints = "description"
source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"

import pydata_sphinx_theme, os
_html_theme_path = os.path.dirname(pydata_sphinx_theme.__file__)
html_theme_path = [_html_theme_path]

html_theme_options = {
    "show_nav_level": 1,
    "navigation_with_keys": True,
    "show_toc_level": 2,
    "header_links_before_dropdown": 6,
    # Version switcher configuration for RTD
    "switcher": {
        "json_url": "https://qpandalite.readthedocs.io/zh-cn/latest/_static/switcher.json",
        "version_match": version_match,
    },
    # Add version switcher to navbar
    "navbar_end": ["theme-switcher", "version-switcher"],
}

suppress_warnings = ["myst.xref_missing"]

autodoc_default_options = {"no-index": True}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_js_files = ['hide_myst_anchors.js']

# pydata-sphinx-theme uses breadcrumbs by default; keep it enabled
breadcrumbs = True
