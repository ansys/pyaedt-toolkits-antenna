# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Sphinx documentation configuration file."""
from datetime import datetime
import os
import pathlib
import sys

from ansys_sphinx_theme import ansys_favicon
from ansys_sphinx_theme import ansys_logo_white
from ansys_sphinx_theme import ansys_logo_white_cropped
from ansys_sphinx_theme import get_version_match
from ansys_sphinx_theme import latex
from ansys_sphinx_theme import pyansys_logo_black
from ansys_sphinx_theme import watermark
from sphinx.util import logging

root_path = str(pathlib.Path(__file__).parent.parent.parent)

try:
    from ansys.aedt.toolkits.antenna import __version__
except ImportError:
    sys.path.append(root_path)
    src_path = os.path.join(root_path, "src")
    sys.path.append(src_path)
    from ansys.aedt.toolkits.antenna import __version__

logger = logging.getLogger(__name__)
path = pathlib.Path(os.path.join(root_path, "examples"))
EXAMPLES_DIRECTORY = path.resolve()

# Sphinx event hooks


def check_pandoc_installed(app):
    """Ensure that pandoc is installed"""
    import pypandoc

    try:
        pandoc_path = pypandoc.get_pandoc_path()
        pandoc_dir = os.path.dirname(pandoc_path)
        if pandoc_dir not in os.environ["PATH"].split(os.pathsep):
            logger.info("Pandoc directory is not in $PATH.")
            os.environ["PATH"] += os.pathsep + pandoc_dir
            logger.info(f"Pandoc directory '{pandoc_dir}' has been added to $PATH")
    except OSError:
        logger.error("Pandoc was not found, please add it to your path or install pypandoc-binary")


def setup(app):
    app.connect("builder-inited", check_pandoc_installed)


print(__version__)
# Project information
project = "ansys-aedt-toolkits-antenna"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
release = version = __version__
cname = os.getenv("DOCUMENTATION_CNAME", "nocname.com")
switcher_version = get_version_match(__version__)
print(copyright)

# Select desired logo, theme, and declare the html title
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_short_title = html_title = "ansys-aedt-toolkits-antenna"

# specify the location of your GitHub repo
html_context = {
    "github_user": "ansys",
    "github_repo": "pyaedt-toolkits-antenna",
    "github_version": "main",
    "doc_path": "doc/source",
}
html_theme_options = {
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "check_switcher": False,
    "github_url": "https://github.com/ansys/pyaedt-toolkits-antenna.git",
    "navigation_with_keys": False,
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "collapse_navigation": True,
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "icon_links": [
        {
            "name": "Support",
            "url": "https://github.com/ansys/pyaedt-toolkits-antenna/issues",
            "icon": "fa fa-comment fa-fw",
        },
        {
            "name": "Download documentation in PDF",
            "url": f"https://{cname}/version/{switcher_version}/_static/assets/download/ansys-aedt-toolkits-antenna.pdf",  # noqa: E501
            "icon": "fa fa-file-pdf fa-fw",
        },
    ],
}

# Sphinx extensions
extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx_copybutton",
    "sphinx_design",
    "recommonmark",
    "numpydoc",
    "nbsphinx",
]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

# Removing check on repo lines of code as using line numbers as anchor is not working
linkcheck_ignore = [
    "https://github.com/ansys/pyaedt-toolkits-antenna/blob/main/src/ansys/aedt/toolkits/antenna/ui/" "actions.py#L165",
    "https://github.com/ansys/pyaedt-toolkits-antenna/blob/main/src/ansys/aedt/toolkits/antenna/ui/" "actions.py#L143",
]

# Add replace in RST files
github_releases_dl_url = "https://github.com/ansys/pyaedt-toolkits-antenna/releases/download"
installer = "Antenna-Toolkit-Installer"
rst_epilog = f"""
.. |github_release_url| replace:: https://github.com/ansys/pyaedt-toolkits-antenna/releases/tag/v{release}
.. |github_windows_installer| replace:: {github_releases_dl_url}/v{release}/{installer}.exe
.. |github_ubuntu_22_installer| replace:: {github_releases_dl_url}/v{release}/{installer}-ubuntu_22_04.zip
.. |github_ubuntu_24_installer| replace:: {github_releases_dl_url}/v{release}/{installer}-ubuntu_24_04.zip
"""
# static path
html_static_path = ["_static"]

html_css_files = [
    "custom.css",
]

html_favicon = ansys_favicon

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# Execute notebooks before conversion
nbsphinx_execute = "always"

# Allow errors to help debug.
nbsphinx_allow_errors = True

# Sphinx gallery customization

nbsphinx_thumbnails = {}

nbsphinx_custom_formats = {
    ".py": ["jupytext.reads", {"fmt": ""}],
}

exclude_patterns = ["_build", "sphinx_boogergreen_theme_1", "Thumbs.db", ".DS_Store", "*.txt", "conf.py"]

# -- Options for LaTeX output ------------------------------------------------

# additional logos for the latex coverage
latex_additional_files = [watermark, ansys_logo_white, ansys_logo_white_cropped]

# change the preamble of latex with customized title page
# variables are the title of pdf, watermark
latex_elements = {"preamble": latex.generate_preamble(html_title)}
