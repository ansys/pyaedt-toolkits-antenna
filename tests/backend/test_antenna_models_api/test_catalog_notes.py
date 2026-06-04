# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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
