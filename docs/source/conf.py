"""
Sphinx configuration for wFabricSecurity documentation.
Professional documentation with modern design and features.
"""

import os
import sys
from datetime import datetime

# -- Project Information -----------------------------------------------------
project = "wFabricSecurity"
copyright = f"{datetime.now().year}, William Rodriguez"
author = "William Rodriguez"
author_url = "https://es.linkedin.com/in/wisrovi-rodriguez"
release = "1.0.0"
version = "1.0"

# -- General Configuration ---------------------------------------------------
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.md",
    "_inc",
    "*.pyc",
    "*.tmp",
]

sys.path.insert(0, os.path.abspath("../.."))

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"
language = "en"

# -- Extensions Configuration ------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_parser",
    "sphinx_sitemap",
    "sphinx.ext.inheritance_diagram",
]

# -- Autodoc Configuration ---------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
    "exclude-members": "__weakref__",
    "inherited-members": True,
    "autosummary": True,
}

autodoc_typehints = "description"
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"

# -- Napoleon (Google/NumPy Style) -------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# -- Intersphinx Configuration -----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "fabric": ("https://hyperledger-fabric.readthedocs.io/en/latest/", None),
}
intersphinx_timeout = 10
intersphinx_cache_limit = 5

# -- Viewcode Configuration --------------------------------------------------
viewcode_follow_imported_members = True

# -- Todo Configuration ------------------------------------------------------
todo_include_todos = True
todo_app以北 = "See the :doc:`changelog` for details"

# -- Copybutton Configuration ------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[.*\]: |Out \[.*\]: "
copybutton_copy_empty_lines = False
copybutton_nesting_indent = False
copybutton_known_references = ["# In\\[.*\\]:", "# Out\\[.*\\]:"]
copybutton_gt_label = "Out"

# -- Graphviz Configuration -------------------------------------------------
graphviz_output_format = "svg"
graphviz_dot_args = [
    "-Gfontname=Helvetica",
    "-Nfontname=Helvetica",
    "-Efontname=Helvetica",
]

# -- HTML Output Configuration ----------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includeboostrap": True,
    "boostrap_version": "3",
}

html_title = "wFabricSecurity Documentation"
html_short_title = "wFabricSecurity"
html_description = "Zero Trust Security System for Hyperledger Fabric - Cryptographic identity verification, code integrity, and secure communication"
html_last_updated = datetime.now().strftime("%B %d, %Y")

html_context = {
    "display_github": True,
    "github_user": "wisrovi",
    "github_repo": "wFabricSecurity",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
    "source_suffix": ".rst",
    "use_edit_page": True,
    "github_url": "https://github.com/wisrovi/wFabricSecurity",
}

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

# -- Favicon -----------------------------------------------------------------
html_favicon = "_static/favicon.ico"

# -- Additional files --------------------------------------------------------
html_extra_path = ["_extra"]

# -- HTML Help Output -------------------------------------------------------
htmlhelp_basename = "wFabricSecuritydoc"

# -- Qt Help Output ---------------------------------------------------------
qthelp_basename = "wFabricSecuritydoc"

# -- LaTeX Output ----------------------------------------------------------
latex_documents = [
    (
        master_doc,
        "wFabricSecurity.tex",
        "wFabricSecurity Documentation",
        "William Rodriguez",
        "manual",
    ),
]

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "\\usepackage{hyperref}",
}

# -- Linkcheck --------------------------------------------------------------
linkcheck_retries = 3
linkcheck_timeout = 30
linkcheck_anchors = True
linkcheck_ignore = [
    r"https://es\.linkedin\.com/.*",
    r"https://twitter\.com/.*",
    r"https://github\.com/.*",
]

# -- Sitemap Configuration --------------------------------------------------
html_baseurl = "https://wFabricSecurity.readthedocs.io/en/latest/"
sitemap_url_scheme = "https"
sitemap_loc = "https://wFabricSecurity.readthedocs.io/en/latest/sitemap.xml"

# -- Canonical URL -----------------------------------------------------------
html_context["canonical_url"] = "https://wFabricSecurity.readthedocs.io/en/latest/"

# -- Templates --------------------------------------------------------------
templates_path = ["_templates"]

# -- Suppress Warnings -----------------------------------------------------
suppress_warnings = [
    "myst.xref_missing",
    "autosectionlabel.*",
    "image.not_readable",
]

# -- Nitpicky Mode ---------------------------------------------------------
nitpicky = False

# -- Extensions Settings ----------------------------------------------------
myst_heading_anchors = 3
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "amsmath",
    " Substitution",
]

myst_substitutions = {
    "project": "wFabricSecurity",
    "version": "1.0.0",
    "author": "William Rodriguez",
    "year": datetime.now().year,
}
