# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

from pathlib import Path
import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

pytestmark = [pytest.mark.antenna_toolkit_api]

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOG_DIR = REPO_ROOT / "src" / "ansys" / "aedt" / "toolkits" / "antenna" / "ui" / "windows" / "antenna_catalog"
HELIX_DIR = CATALOG_DIR / "helix"
HELIX_MODELS = ["AxialMode", "AxialModeTaper", "NormalMode", "QuadrifilarOpen", "QuadrifilarShort"]


def _read_toml(file_path):
    with file_path.open("rb") as file_handler:
        return tomllib.load(file_handler)


class TestClass:
    def test_helix_catalog_lists_family(self):
        catalog = _read_toml(CATALOG_DIR / "antenna_catalog.toml")

        assert catalog["Helix"]["models"] == HELIX_MODELS

    @pytest.mark.parametrize("antenna_name", HELIX_MODELS)
    def test_helix_catalog_assets(self, antenna_name):
        antenna_dir = HELIX_DIR / antenna_name.lower()
        parameters = _read_toml(antenna_dir / "parameters.toml")
        model_properties = _read_toml(antenna_dir / "model" / "properties.toml")

        assert parameters["Coordinate_System"] == "Global"
        assert any(path.suffix.lower() in {".jpg", ".jpeg", ".png"} for path in antenna_dir.iterdir())

        for key, value in model_properties.items():
            if key == "name":
                continue
            assert (antenna_dir / "model" / f"{value['name']}.obj").is_file()
