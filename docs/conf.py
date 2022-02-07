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
# import os
# import sys
# sys.path.insert(0, os.path.abspath("."))
import datetime

import pkg_resources
import pylons_sphinx_themes

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
]

# General substitutions.
author = "Pylons Project"
year = datetime.datetime.now().year
copyright = "2012-%s Pylons Project <pylons-discuss@googlegroups.com>" % year

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = pkg_resources.get_distribution("venusian").version
# The full version, including alpha/beta/rc tags.
release = version

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pylons"
html_theme_path = pylons_sphinx_themes.get_html_themes_path()
html_theme_options = dict(
    github_url="https://github.com/Pylons/venusian",
    canonical_url="https://docs.pylonsproject.org/projects/venusian/en/latest/",
)

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# Control display of sidebars
html_sidebars = {
    "**": [
        "localtoc.html",
        "ethicalads.html",
        "relations.html",
        "sourcelink.html",
        "searchbox.html",
    ]
}

# If not "", a "Last updated on:" timestamp is inserted at every page
# bottom, using the given strftime format.
html_last_updated_fmt = "%b %d, %Y"

# Do not use smart quotes.
smartquotes = False

# Output file base name for HTML help builder.
htmlhelp_basename = "atemplatedoc"


# -- Options for LaTeX output -------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, document class [howto/manual]).
latex_documents = [
    ("index", "atemplate.tex", "venusian Documentation", "Pylons Project", "manual"),
]
