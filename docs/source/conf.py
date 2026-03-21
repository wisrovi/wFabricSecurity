"""
Sphinx configuration for wFabricSecurity documentation.
Professional, paginated documentation with search and navigation features.
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
# Patterns to ignore when building docs
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.md",
    "_inc",
    "*.pyc",
]

# Add project root to path for autodoc
sys.path.insert(0, os.path.abspath("../.."))

# Supported source file extensions
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# Master doc (top-level document)
master_doc = "index"

# Language for content
language = "en"

# -- Extensions Configuration ------------------------------------------------
extensions = [
    # Documentation
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    # UI/UX
    "sphinx_copybutton",
    "sphinx_design",
    # Markdown
    "myst_parser",
    # SEO/Sitemap
    "sphinx_sitemap",
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
}

# Autodoc type hints
autodoc_typehints = "description"
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"

# -- Napoleon (Google/NumPy Style) Configuration ------------------------------
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
}
intersphinx_timeout = 10
intersphinx_cache_limit = 5

# -- Viewcode Configuration --------------------------------------------------
viewcode_follow_imported_members = True

# -- Todo Configuration ------------------------------------------------------
todo_include_todos = True

# -- Copybutton Configuration ------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_copy_empty_lines = False
copybutton_nesting_indent = False
copybutton_known_references = ["# In\\[.*\\]:", "# Out\\[.*\\]:"]

# -- HTML Output Configuration ----------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "both",
    "style_external_links": True,
    "style_nav_header_depth": 2,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
    "navigation_expand_ids": True,
    "navigation_expand_articles": True,
    "navigation_expand_that": True,
    "navigation_expand_nested": True,
    "use_edit_page_button": True,
    "show_powered_by": False,
    "analytics_id": "",
    "logo": {
        "image_light": "_static/logo-light.png",
        "image_dark": "_static/logo-dark.png",
    },
}

# Meta tags
html_title = "wFabricSecurity Documentation"
html_short_title = "wFabricSecurity"
html_description = "Zero Trust Security System for Hyperledger Fabric"
html_last_updated = datetime.now().strftime("%B %d, %Y")

# Additional context for templates
html_context = {
    "display_github": True,
    "github_user": "wisrovi",
    "github_repo": "wFabricSecurity",
    "github_version": "main",
    "conf_py_path": "/docs/source/",
    "source_suffix": ".rst",
    "use_edit_page": True,
}

# Static files
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

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

# -- Linkcheck --------------------------------------------------------------
linkcheck_retries = 3
linkcheck_timeout = 30
linkcheck_anchors = True
linkcheck_ignore = [
    r"https://es\.linkedin\.com/.*",
    r"https://twitter\.com/.*",
]

# -- Sitemap Configuration --------------------------------------------------
html_baseurl = "https://wFabricSecurity.readthedocs.io/en/latest/"
sitemap_url_scheme = "https"

# -- Page Pagination --------------------------------------------------------
# Custom JavaScript for pagination (if needed)
templates_path = ["_templates"]

# -- Suppress Warnings -----------------------------------------------------
suppress_warnings = [
    "myst.xref_missing",
    "autosectionlabel.*",
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
]
