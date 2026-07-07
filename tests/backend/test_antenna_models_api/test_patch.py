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

from ansys.aedt.core.modeler.cad.object_3d import Object3d
import pytest

from ansys.aedt.toolkits.antenna.backend import antenna_models

pytestmark = [pytest.mark.antenna_models_api]


class TestClass:
    """Class defining a workflow to test patch antenna models."""

    def test_rectangular_patch_probe(self, toolkit):
        antenna_module = getattr(antenna_models, "RectangularPatchProbe")
        oantenna = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        cs = toolkit.aedtapp.modeler.create_coordinate_system(origin=[10, 20, 30])

        oantenna = antenna_module(toolkit.aedtapp, frequency=1.0, length_unit=toolkit.aedtapp.modeler.model_units)
        oantenna.coordinate_system = cs.name

        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna
        assert oantenna.excitation_type == "Terminal_Waveport"
        assert oantenna.object_list
        assert len(oantenna.excitations) == 1
        assert next(iter(oantenna.excitations.values())).children
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(
            toolkit.aedtapp,
            frequency=1.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
            outer_boundary="Radiation",
        )

        assert oantenna.name != oantenna2.name

    @pytest.mark.parametrize(
        ("antenna_name", "expected_parameters"),
        [
            ("RectangularPatchInset", ["inset_distance", "inset_gap", "feed_width"]),
            ("RectangularPatchEdge", ["edge_feed_width", "edge_feed_length", "feed_width"]),
            ("EllipticalEdge", ["edge_feed_width", "edge_feed_length", "feed_width"]),
            ("EllipticalInset", ["inset_distance", "inset_gap", "feed_width"]),
            ("EllipticalProbe", ["coax_inner_rad", "coax_outer_rad", "feed_x"]),
            ("MbyNPatchArray", ["patch_count_x", "patch_count_y", "patch_spacing_x"]),
            (
                "SeqRotated2Patch",
                ["patch_diameter", "feed_rotation_angle", "element_4_port_phase"],
            ),
        ],
    )
    def test_patch_family_synthesis(self, antenna_name, expected_parameters):
        antenna_module = getattr(antenna_models, antenna_name)
        oantenna = antenna_module(None, frequency=1.0, length_unit="mm")

        assert oantenna.synthesis_parameters
        for parameter in expected_parameters:
            assert hasattr(oantenna.synthesis_parameters, parameter)

    @pytest.mark.parametrize(
        ("antenna_name", "expected_excitations"),
        [
            ("RectangularPatchInset", 1),
            ("RectangularPatchEdge", 1),
            ("EllipticalEdge", 1),
            ("EllipticalInset", 1),
            ("EllipticalProbe", 1),
            ("MbyNPatchArray", 6),
            ("SeqRotated2Patch", 4),
        ],
    )
    def test_patch_family_models(self, toolkit, antenna_name, expected_excitations):
        antenna_module = getattr(antenna_models, antenna_name)
        toolkit.connect_design("HFSS")

        toolkit.aedtapp.solution_type = "Terminal"

        cs = toolkit.aedtapp.modeler.create_coordinate_system(origin=[10, 20, 30])

        oantenna = antenna_module(toolkit.aedtapp, frequency=1.0, length_unit=toolkit.aedtapp.modeler.model_units)
        oantenna.init_model()
        oantenna.coordinate_system = cs.name
        assert oantenna.model_hfss()
        assert oantenna.setup_hfss()
        assert len(oantenna.excitations) == expected_excitations
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
