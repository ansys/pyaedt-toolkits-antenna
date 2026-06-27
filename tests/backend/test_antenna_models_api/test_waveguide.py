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

from pathlib import Path

from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
import pytest

from ansys.aedt.toolkits.antenna.backend import antenna_models

pytestmark = [pytest.mark.antenna_models_api]


def _validate_waveguide_model(toolkit, antenna_name, frequency=10.0, origin_shift=None):
    antenna_module = getattr(antenna_models, antenna_name)
    antenna = antenna_module(None, frequency=frequency, length_unit="mm")
    assert antenna.synthesis_parameters

    toolkit.connect_design("HFSS")
    toolkit.aedtapp.solution_type = "Modal"

    antenna = antenna_module(toolkit.aedtapp, frequency=frequency, length_unit=toolkit.aedtapp.modeler.model_units)
    antenna.init_model()
    antenna.model_hfss()
    antenna.setup_hfss()

    assert antenna.object_list
    for component in antenna.object_list.values():
        assert isinstance(component, Object3d)

    original_center = list(antenna.object_list.values())[0].faces[0].center
    if origin_shift:
        antenna.origin = origin_shift
        moved_center = list(antenna.object_list.values())[0].faces[0].center
        expected_center = GeometryOperators.v_sum(original_center, origin_shift)
        assert GeometryOperators.points_distance(expected_center, moved_center) < 1e-3

    antenna_duplicate = antenna_module(
        toolkit.aedtapp,
        name=antenna.name,
        length_unit=toolkit.aedtapp.modeler.model_units,
    )
    assert antenna.name != antenna_duplicate.name


class TestClass:
    """Class defining a workflow to test antenna models waveguide."""

    def test_circular_waveguide(self, toolkit):
        _validate_waveguide_model(toolkit, "CircularWaveguide", frequency=10.0, origin_shift=[10, 20, 30])

    def test_rectangular_waveguide(self, toolkit):
        _validate_waveguide_model(toolkit, "RectangularWaveguide", frequency=10.0, origin_shift=[15, 10, 25])

    def test_rectangular_waveguide_slot_array(self, toolkit):
        _validate_waveguide_model(toolkit, "RectangularWaveguideSlotArray", frequency=10.3, origin_shift=[25, 35, 15])


def test_waveguide_catalog_resources():
    catalog_dir = (
        Path(__file__).resolve().parents[3]
        / "src"
        / "ansys"
        / "aedt"
        / "toolkits"
        / "antenna"
        / "ui"
        / "windows"
        / "antenna_catalog"
        / "waveguide"
    )

    expected_models = {
        "circularwaveguide": {"image_suffixes": {".jpg", ".jpeg", ".png"}, "model_files": 4},
        "rectangularwaveguide": {"image_suffixes": {".jpg", ".jpeg", ".png"}, "model_files": 4},
        "rectangularwaveguideslotarray": {"image_suffixes": {".jpg", ".jpeg", ".png"}, "model_files": 5},
    }

    for model_name, resource_info in expected_models.items():
        model_dir = catalog_dir / model_name
        assert (model_dir / "parameters.toml").is_file()
        assert (model_dir / "model" / "properties.toml").is_file()
        assert any(path.suffix.lower() in resource_info["image_suffixes"] for path in model_dir.iterdir())
        assert len(list((model_dir / "model").glob("*.obj"))) == resource_info["model_files"]
