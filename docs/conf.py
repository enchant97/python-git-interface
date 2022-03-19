# Configuration file for the Sphinx documentation builder.
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
from git_interface import __version__

# -- Project information -----------------------------------------------------

project = 'Git Interface'
copyright = '2021, Leo Spratt'
author = 'Leo Spratt'
version = __version__
release = version

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",
]

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_mock_imports = ["aiofiles", "quart", "async_timeout"]

autodoc_typehints = "description"

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']
