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
import pyvista as pv

from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
from ansys.aedt.toolkits.antenna.backend import antenna_models

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

pytestmark = [pytest.mark.antenna_models_api]

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
    / "logperiodic"
)

PRINTED_MODELS = ["LogPeriodicToothed", "LogPeriodicTrapezoidal"]


class TestClass:
    """Class defining a workflow to test antenna models log periodic."""

    def test_log_periodic_array(self, toolkit):
        antenna_module = getattr(antenna_models, "LogPeriodicArray")
        oantenna0 = antenna_module(None, length_unit="mm")
        assert oantenna0.synthesis_parameters

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna1 = antenna_module(toolkit.aedtapp, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(toolkit.aedtapp, length_unit="mm", outer_boundary="Radiation")
        assert oantenna1.name != oantenna2.name

    @pytest.mark.parametrize("antenna_name", PRINTED_MODELS)
    def test_printed_log_periodic_family(self, toolkit, antenna_name):
        antenna_module = getattr(antenna_models, antenna_name)
        antenna_no_app = antenna_module(None, start_frequency=4.0, stop_frequency=10.0, length_unit="mm")
        assert antenna_no_app.synthesis_parameters
        assert antenna_no_app.start_frequency == 4.0
        assert antenna_no_app.stop_frequency == 10.0

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        antenna = antenna_module(
            toolkit.aedtapp,
            start_frequency=4.0,
            stop_frequency=10.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
        )
        antenna.init_model()
        antenna.model_hfss()
        antenna.setup_hfss()

        assert antenna.object_list
        for component in antenna.object_list.values():
            assert isinstance(component, Object3d)

        original_center = list(antenna.object_list.values())[0].faces[0].center
        antenna.origin = [10, 15, 5]
        moved_center = list(antenna.object_list.values())[0].faces[0].center
        expected_center = GeometryOperators.v_sum(original_center, [10, 15, 5])
        assert GeometryOperators.points_distance(expected_center, moved_center) < 1e-3


def test_log_periodic_catalog_assets():
    expected_models = {
        "logperiodicarray": 2,
        "logperiodictoothed": 4,
        "logperiodictrapezoidal": 4,
    }

    for model_name, object_count in expected_models.items():
        antenna_dir = CATALOG_ROOT / model_name
        assert (antenna_dir / "parameters.toml").is_file()
        assert any(path.suffix.lower() in {".jpg", ".jpeg", ".png"} for path in antenna_dir.iterdir())

        properties_file = antenna_dir / "model" / "properties.toml"
        assert properties_file.is_file()
        with properties_file.open("rb") as file_handler:
            antenna_info = tomllib.load(file_handler)

        assert antenna_info["name"]
        assert len([key for key in antenna_info if key != "name"]) == object_count
        for object_name, object_properties in antenna_info.items():
            if object_name == "name":
                continue
            assert (antenna_dir / "model" / f"{object_properties['name']}.obj").is_file()

        if model_name in {"logperiodictoothed", "logperiodictrapezoidal"}:
            plotter = pv.Plotter(off_screen=True, window_size=[400, 400])
            plotter.set_background("white")
            for object_name, object_properties in antenna_info.items():
                if object_name == "name":
                    continue
                mesh = pv.read(antenna_dir / "model" / f"{object_properties['name']}.obj")
                plotter.add_mesh(
                    mesh,
                    color=object_properties["color"],
                    opacity=object_properties["opacity"],
                    show_scalar_bar=False,
                )
            plotter.view_isometric()
            image = plotter.screenshot(return_img=True)
            assert int((image < 245).any(axis=2).sum()) > 1000
