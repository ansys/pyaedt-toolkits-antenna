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

import pytest

pytestmark = [pytest.mark.toolkit_api]


class TestClass:
    """Class defining focused toolkit tests for the PIFA family."""

    def test_pifa_models_available(self, aedt_common):
        for antenna_name in ("PlanarInvertedF", "ShortingPin", "ShortingPlate"):
            assert antenna_name in aedt_common.available_antennas
            assert aedt_common.get_antenna(antenna_name, synth_only=True)

    def test_pifa_catalog_assets(self):
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
            / "pifa"
        )

        expected_assets = {
            "planarinvertedf": {
                "image": "PlanarInvertedF.png",
                "objs": [
                    "sub_PlanarInvertedF.obj",
                    "gnd_PlanarInvertedF.obj",
                    "ant_feed_PlanarInvertedF.obj",
                    "ant_short_arm_PlanarInvertedF.obj",
                    "ant_short_wall_PlanarInvertedF.obj",
                    "ant_top_PlanarInvertedF.obj",
                    "ant_microstrip_PlanarInvertedF.obj",
                    "port_lump_PlanarInvertedF.obj",
                ],
            },
            "shortingpin": {
                "image": "ShortingPin.png",
                "objs": [
                    "sub_ShortingPin.obj",
                    "gnd_ShortingPin.obj",
                    "ant_ShortingPin.obj",
                    "feed_pin_ShortingPin.obj",
                    "feed_coax_ShortingPin.obj",
                    "coax_ShortingPin.obj",
                    "port_cap_ShortingPin.obj",
                    "port_ShortingPin.obj",
                    "short_pin_ShortingPin.obj",
                ],
            },
            "shortingplate": {
                "image": "ShortingPlate.png",
                "objs": [
                    "sub_ShortingPlate.obj",
                    "gnd_ShortingPlate.obj",
                    "ant_ShortingPlate.obj",
                    "feed_pin_ShortingPlate.obj",
                    "feed_coax_ShortingPlate.obj",
                    "coax_ShortingPlate.obj",
                    "port_cap_ShortingPlate.obj",
                    "port_ShortingPlate.obj",
                    "shorting_plate_ShortingPlate.obj",
                ],
            },
        }

        for model_dir, assets in expected_assets.items():
            model_root = catalog_root / model_dir
            assert (model_root / "parameters.toml").is_file()
            assert (model_root / assets["image"]).is_file()
            assert (model_root / "model" / "properties.toml").is_file()
            for obj_name in assets["objs"]:
                assert (model_root / "model" / obj_name).is_file()
