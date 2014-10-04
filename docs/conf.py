#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Flask-Permissions documentation build configuration file, created by
# sphinx-quickstart on Mon Sep 29 10:40:21 2014.
#

import sys
import os

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('..'))
#sys.path.append(os.path.abspath('./_themes'))

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = 'Flask-Permissions'
copyright = '2014, Kai Wohlfahrt'

# The short X.Y version.
version = '0.1'
# The full version, including alpha/beta/rc tags.
release = '0.1-alpha'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

html_theme = 'flask_small'
html_theme_path = ['_themes']
html_theme_options = {
	'github_fork': 'kwohlfahrt/flask-permissions',
	'index_logo': '',
}

latex_elements = { 'papersize': 'a4paper', 'preamble': '', }
latex_documents = [
  ('index', 'Flask-Permissions.tex', 'Flask-Permissions Documentation',
   'Kai Wohlfahrt', 'manual'),
]

man_pages = [
    ('index', 'flask-permissions', 'Flask-Permissions Documentation',
     ['Kai Wohlfahrt'], 1)
]

texinfo_documents = [
  ('index', 'Flask-Permissions', 'Flask-Permissions Documentation',
   'Kai Wohlfahrt', 'Flask-Permissions', 'One line description of project.',
   'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}
