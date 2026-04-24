# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#

from pathlib import Path

import pytest

from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.toolkits.antenna.backend import antenna_models

pytestmark = [pytest.mark.antenna_models_api]


class TestClass:
    """Class defining a workflow to test reflector antenna models."""

    @pytest.mark.parametrize("antenna_name", ["Cassegrain", "Gregorian", "Parabolic", "SplashPlate"])
    def test_reflector_synthesis(self, antenna_name):
        antenna_module = getattr(antenna_models, antenna_name)
        antenna = antenna_module(None, frequency=10.0, length_unit="mm")
        assert antenna.synthesis_parameters
        assert antenna.feed_type

    def test_reflector_assets(self):
        catalog_root = (
            Path(__file__).resolve().parents[3]
            / "src"
            / "ansys"
            / "aedt"
            / "toolkits"
            / "antenna"
            / "ui"
            / "windows"
            / "antenna_catalog"
            / "reflector"
        )
        expected_assets = {
            "cassegrain": ["reflector.obj", "subreflector.obj", "feed.obj", "port.obj", "port_cap.obj"],
            "gregorian": ["reflector.obj", "subreflector.obj", "feed.obj", "port.obj", "port_cap.obj"],
            "parabolic": ["reflector.obj", "feed.obj", "port.obj", "port_cap.obj"],
            "splashplate": ["reflector.obj", "splash_plate.obj", "feed.obj", "port.obj", "port_cap.obj"],
        }

        for antenna_name, object_files in expected_assets.items():
            antenna_dir = catalog_root / antenna_name
            assert antenna_dir.is_dir()
            assert (antenna_dir / "parameters.toml").is_file()
            assert any(path.suffix.lower() in {".png", ".jpg", ".jpeg"} for path in antenna_dir.iterdir())
            for object_file in object_files:
                assert (antenna_dir / "model" / object_file).is_file()

    @pytest.mark.parametrize("antenna_name", ["Parabolic", "Cassegrain", "Gregorian", "SplashPlate"])
    def test_reflector_model_hfss(self, toolkit, antenna_name):
        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Modal"
        antenna_module = getattr(antenna_models, antenna_name)
        antenna = antenna_module(toolkit.aedtapp, frequency=10.0, length_unit=toolkit.aedtapp.modeler.model_units)
        antenna.init_model()
        antenna.model_hfss()
        antenna.setup_hfss()

        assert antenna.object_list
        assert antenna.excitations
        assert any(isinstance(comp, Object3d) for comp in antenna.object_list.values())

    def test_parabolic_model_hfss_uses_elliptical_aperture(self, toolkit):
        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Modal"
        antenna = antenna_models.Parabolic(
            toolkit.aedtapp,
            frequency=10.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
            major_radius=20.0,
            minor_radius=10.0,
        )
        antenna.init_model()
        antenna.model_hfss()
        antenna.setup_hfss()

        reflector = next(component for name, component in antenna.object_list.items() if name.startswith("reflector_"))
        bounding_box = reflector.bounding_box
        z_size = abs(bounding_box[5] - bounding_box[2])
        x_size = abs(bounding_box[3] - bounding_box[0])

        assert z_size > x_size
        assert pytest.approx(z_size / x_size, rel=0.25) == 2.0

    def test_splash_plate_model_hfss_unites_plate_geometry(self, toolkit):
        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Modal"
        antenna = antenna_models.SplashPlate(
            toolkit.aedtapp,
            frequency=20.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
        )
        antenna.init_model()
        antenna.model_hfss()
        antenna.setup_hfss()

        assert any(name.startswith("splash_plate_") for name in antenna.object_list)
        assert not any(name.startswith("splash_plate_cone_") for name in antenna.object_list)
