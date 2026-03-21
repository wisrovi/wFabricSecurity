# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Custom targets

# Build HTML documentation
html:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

# Build HTML documentation with verbose output
html-verbose:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" -v $(SPHINXOPTS) $(O)

# Clean build files
clean:
	rm -rf $(BUILDDIR)/*

# Build and open in browser
serve: html
	@echo "Starting server at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	cd $(BUILDDIR)/html && python -m http.server 8000

# Build and open in browser (alternative)
view: html
	@echo "Documentation built. Opening in browser..."
	@python -c "import webbrowser; webbrowser.open('file://$(shell pwd)/$(BUILDDIR)/html/index.html')"

# Build PDF documentation (requires LaTeX)
pdf:
	@$(SPHINXBUILD) -b latex "$(SOURCEDIR)" "$(BUILDDIR)/latex" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. Run 'make all-pdf' in the $(BUILDDIR)/latex directory."

# Build singlehtml documentation
singlehtml:
	@$(SPHINXBUILD) -b singlehtml "$(SOURCEDIR)" "$(BUILDDIR)/singlehtml" $(SPHINXOPTS) $(O)
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml/index.html."

# Linkcheck for verifying links
linkcheck:
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" $(SPHINXOPTS) $(O)

# Spell check (requires sphinxcontrib-spelling)
spellcheck:
	@$(SPHINXBUILD) -b spelling "$(SOURCEDIR)" "$(BUILDDIR)/spelling" $(SPHINXOPTS) $(O)

# Development: build and watch for changes
dev:
	@sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

# Full build: clean and rebuild everything
all: clean html

# Show statistics about documentation
stats:
	@echo "Documentation source files:"
	@find $(SOURCEDIR) -name "*.rst" -o -name "*.md" | wc -l
	@echo ""
	@echo "HTML pages generated:"
	@find $(BUILDDIR)/html -name "*.html" 2>/dev/null | wc -l
	@echo ""
	@echo "Static files:"
	@find $(BUILDDIR)/html/_static -type f 2>/dev/null | wc -l
