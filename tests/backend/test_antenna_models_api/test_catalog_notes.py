# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from ansys.aedt.toolkits.antenna.ui.windows.antenna_catalog.antenna_catalog_menu import _extract_numpy_docstring_section
from ansys.aedt.toolkits.antenna.ui.windows.antenna_catalog.antenna_catalog_menu import _get_antenna_notes_markdown


def test_extract_numpy_docstring_notes_section():
    docstring = """
    Example antenna.

    Notes
    -----
    .. [1] Reference one.
    .. [2] Reference two.

    Examples
    --------
    >>> pass
    """

    notes = _extract_numpy_docstring_section(docstring, "Notes")

    assert "Reference one." in notes
    assert "Examples" not in notes


def test_get_antenna_notes_markdown_returns_formatted_references():
    notes = _get_antenna_notes_markdown("BowTieNormal")

    assert notes.startswith("1. ")
    assert "Balanis" in notes
