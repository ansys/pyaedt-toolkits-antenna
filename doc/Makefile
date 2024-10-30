# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j auto --color
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

.install-deps:
	@pip freeze | grep -q "vtk-osmesa" && is_vtk_osmesa_installed="yes" || is_vtk_osmesa_installed="no"
	@if [ "${ON_CI}" = "True" ] && [ "$$is_vtk_osmesa_installed" != "yes" ]; then \
		@echo "Removing vtk to avoid conflicts with vtk-osmesa needed for CI/CD"; \
		pip uninstall --yes vtk; \
		@echo "Installing vtk-osmesa"; \
		pip install --extra-index-url https://wheels.vtk.org vtk-osmesa; \
	fi

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: .install-deps Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean: .install-deps
	rm -rf $(BUILDDIR)/*
	rm -rf examples/
	find . -type d -name "_autosummary" -exec rm -rf {} +

# build html docs in parallel using all available CPUs
# WARNING: this is a resource hog
html: .install-deps
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -j auto

# Build pdf docs.
pdf: .install-deps
	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
	(test -f $(BUILDDIR)/latex/ansys-aedt-toolkits-antenna.pdf && echo pdf exists) || exit 1

# build docs like the CI build
cibuild:
	mkdir source/examples -p
	echo 'Examples' > source/examples/index.rst
	echo '========' >> source/examples/index.rst
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O) -j auto -w build_errors.txt -N
	python print_errors.py