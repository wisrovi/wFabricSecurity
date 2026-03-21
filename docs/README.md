# Documentation

**Sphinx documentation for wFabricSecurity**

## Overview

This directory contains the Sphinx-based documentation source files for the project.

## Directory Structure

```
docs/
├── Makefile              # Build commands
└── source/
    ├── conf.py           # Sphinx configuration
    ├── index.rst         # Main documentation page
    ├── getting_started.rst
    ├── installation.rst
    ├── usage.rst
    ├── api_reference.rst
    ├── tutorials.rst
    ├── faq.rst
    ├── bibliography.rst
    └── _static/
        └── css/
            └── custom.css
```

## Building Documentation

```bash
cd docs

# Build HTML documentation
make html

# Build PDF (requires LaTeX)
make latexpdf

# Clean build artifacts
make clean

# Serve locally
make serve
```

## Viewing Documentation

```bash
# Open in browser
open build/html/index.html
# or
firefox build/html/index.html
```

## Documentation Sections

| Section | Description |
|---------|-------------|
| `index.rst` | Main documentation page with overview |
| `getting_started.rst` | Quick start guide |
| `installation.rst` | Installation instructions |
| `usage.rst` | Usage examples and patterns |
| `api_reference.rst` | Detailed API documentation |
| `tutorials.rst` | Step-by-step tutorials |
| `faq.rst` | Frequently asked questions |
| `bibliography.rst` | References and citations |

## Sphinx Configuration

Key settings in `conf.py`:
- Theme: `sphinx_rtd_theme`
- Extensions: `sphinx.ext.autodoc`, `sphinx.ext.viewcode`
- Output: HTML, PDF (via LaTeX)

## Requirements

```bash
pip install sphinx sphinx_rtd_theme
```

## Contributing to Docs

1. Edit `.rst` files in `source/`
2. Rebuild with `make html`
3. Preview in browser
4. Commit changes
