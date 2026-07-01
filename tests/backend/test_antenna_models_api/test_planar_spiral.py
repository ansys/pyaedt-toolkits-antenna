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
import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ansys.aedt.core.modeler.cad.object_3d import Object3d

from ansys.aedt.toolkits.antenna.backend import antenna_models

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
    / "planarspiral"
)

PLANAR_SPIRAL_ASSETS = [
    (
        "planararchimedean",
        ["ant_arm1", "ant_arm2", "port_lump"],
    ),
    (
        "planararchimedeancavity",
        ["ant_arm1", "ant_arm2", "port_lump", "gnd_cavity", "bottom_absorber", "middle_absorber", "top_absorber"],
    ),
    (
        "planarlog",
        ["ant_arm1", "ant_arm2", "port_lump"],
    ),
    (
        "planarlogcavity",
        ["ant_arm1", "ant_arm2", "port_lump", "gnd_cavity", "bottom_absorber", "middle_absorber", "top_absorber"],
    ),
    (
        "planarsinuous",
        ["ant_arm1", "ant_arm2", "ant_arm3", "ant_arm4", "port_lump_1", "port_lump_2", "gnd_1", "gnd_2"],
    ),
    (
        "planarsinuouscavity",
        [
            "ant_arm1",
            "ant_arm2",
            "ant_arm3",
            "ant_arm4",
            "port_lump_1",
            "port_lump_2",
            "gnd_1",
            "gnd_2",
            "gnd_cavity",
            "bottom_absorber",
            "middle_absorber",
            "top_absorber",
        ],
    ),
]

PLANAR_SPIRAL_MODELS = [
    ("PlanarArchimedean", ["ant_AntennaArm1", "ant_AntennaArm2", "port_lump_"]),
    (
        "PlanarArchimedeanCavity",
        ["ant_AntennaArm1", "ant_AntennaArm2", "port_lump_", "gnd_cavity_", "bottom_absorber_"],
    ),
    ("PlanarLog", ["ant_AntennaArm1", "ant_AntennaArm2", "port_lump_"]),
    ("PlanarLogCavity", ["ant_AntennaArm1", "ant_AntennaArm2", "port_lump_", "gnd_cavity_", "top_absorber_"]),
    (
        "PlanarSinuous",
        [
            "ant_AntennaArm1",
            "ant_AntennaArm2",
            "ant_AntennaArm3",
            "ant_AntennaArm4",
            "port_lump_",
            "ant_ext1_",
            "gnd_2_",
            "port_lump_",
        ],
    ),
    (
        "PlanarSinuousCavity",
        [
            "ant_AntennaArm1",
            "ant_AntennaArm2",
            "ant_AntennaArm3",
            "ant_AntennaArm4",
            "port_lump_",
            "ant_ext1_",
            "gnd_2_",
            "port_lump_",
            "gnd_cavity_",
            "bottom_absorber_",
            "middle_absorber_",
            "top_absorber_",
        ],
    ),
]


class TestClass:
    """Class defining a workflow to test planar spiral antenna models."""

    @pytest.mark.parametrize(("folder_name", "expected_objects"), PLANAR_SPIRAL_ASSETS)
    def test_catalog_assets(self, folder_name, expected_objects):
        antenna_dir = CATALOG_ROOT / folder_name
        assert antenna_dir.is_dir()
        assert (antenna_dir / "parameters.toml").is_file()
        assert len(list(antenna_dir.glob("*.png"))) == 1

        properties_file = antenna_dir / "model" / "properties.toml"
        assert properties_file.is_file()
        with properties_file.open("rb") as file_handler:
            model_properties = tomllib.load(file_handler)

        for object_name in expected_objects:
            assert (antenna_dir / "model" / f"{object_name}.obj").is_file()
            assert any(
                properties.get("name") == object_name
                for key, properties in model_properties.items()
                if key.startswith("object_")
            )

    @pytest.mark.parametrize("model_name, _", PLANAR_SPIRAL_MODELS)
    def test_planar_spiral_model_synthesis(self, model_name, _):
        antenna_module = getattr(antenna_models, model_name)
        oantenna = antenna_module(None, start_frequency=4.0, stop_frequency=10.0, length_unit="mm")

        assert oantenna.synthesis_parameters
        assert oantenna.synthesis()

    @pytest.mark.parametrize(("model_name", "expected_prefixes"), PLANAR_SPIRAL_MODELS)
    def test_planar_spiral_model_hfss(self, toolkit, model_name, expected_prefixes):
        antenna_module = getattr(antenna_models, model_name)
        oantenna = antenna_module(None, start_frequency=4.0, stop_frequency=10.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna = antenna_module(
            toolkit.aedtapp,
            start_frequency=4.0,
            stop_frequency=10.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
        )
        oantenna.init_model()
        assert oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        for prefix in expected_prefixes:
            assert any(obj_name.startswith(prefix) for obj_name in oantenna.object_list)

        oantenna2 = antenna_module(
            toolkit.aedtapp,
            start_frequency=4.0,
            stop_frequency=10.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
        )
        assert oantenna.name != oantenna2.name
