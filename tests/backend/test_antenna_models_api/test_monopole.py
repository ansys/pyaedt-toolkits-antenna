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

from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
import pytest

from ansys.aedt.toolkits.antenna.backend import antenna_models

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

pytestmark = [pytest.mark.antenna_models_api]

MODELS = [
    ("BladeAntenna", "width_blade_base", 1.2),
    ("CircularDiscMonopole", "disc_diameter", 1.0),
    ("EllipticalBaseStripMonopole", "strip_width", 1.0),
    ("VerticalTrapezoidalMonopole", "monopole_height", 1.0),
    ("WireMonopole", "monopole_length", 1.0),
]

CATALOG_ROOT = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "ansys"
    / "aedt"
    / "toolkits"
    / "antenna"
    / "ui"
    / "windows"
    / "antenna_catalog"
    / "monopole"
)


class TestClass:
    @pytest.mark.parametrize(("model_name", "_parameter_name", "_frequency"), MODELS)
    def test_monopole_catalog_assets(self, model_name, _parameter_name, _frequency):
        antenna_dir = CATALOG_ROOT / model_name.lower()
        assert antenna_dir.is_dir()
        assert (antenna_dir / "parameters.toml").is_file()
        assert any(path.suffix.lower() in {".jpg", ".jpeg", ".png"} for path in antenna_dir.iterdir())

        properties_file = antenna_dir / "model" / "properties.toml"
        assert properties_file.is_file()
        with properties_file.open("rb") as file_handler:
            antenna_info = tomllib.load(file_handler)

        assert antenna_info["name"]
        for object_name, object_properties in antenna_info.items():
            if object_name == "name":
                continue
            assert (antenna_dir / "model" / f"{object_properties['name']}.obj").is_file()

    @pytest.mark.parametrize(("model_name", "parameter_name", "frequency"), MODELS)
    def test_monopoles(self, toolkit, model_name, parameter_name, frequency):
        antenna_module = getattr(antenna_models, model_name)
        antenna_no_app = antenna_module(None, frequency=frequency, length_unit="mm")
        assert getattr(antenna_no_app.synthesis_parameters, parameter_name).value

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        antenna = antenna_module(toolkit.aedtapp, frequency=frequency, length_unit=toolkit.aedtapp.modeler.model_units)
        antenna.init_model()
        antenna.model_hfss()
        antenna.setup_hfss()

        assert antenna.object_list
        for comp in antenna.object_list.values():
            assert isinstance(comp, Object3d)

        face_center = list(antenna.object_list.values())[0].faces[0].center
        antenna.origin = [10, 20, 50]
        face_center_new = list(antenna.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3

        antenna_duplicate = antenna_module(toolkit.aedtapp, name=antenna.name)
        assert antenna.name != antenna_duplicate.name
