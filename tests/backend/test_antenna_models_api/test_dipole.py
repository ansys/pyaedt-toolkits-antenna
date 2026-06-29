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
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
import pytest

from ansys.aedt.toolkits.antenna.backend import antenna_models

pytestmark = [pytest.mark.antenna_models_api]


class TestClass:
    """Class defining a workflow to test antenna models dipole."""

    def test_planar_dipole(self, toolkit):
        antenna_module = getattr(antenna_models, "PlanarDipole")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters.dipole_length.value

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        cs = toolkit.aedtapp.modeler.create_coordinate_system(origin=[10, 20, 30])

        oantenna1 = antenna_module(
            toolkit.aedtapp,
            frequency=1.0,
            length_unit=toolkit.aedtapp.modeler.model_units,
            material="FR4_epoxy",
        )
        oantenna1.coordinate_system = cs.name
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        face_center = list(oantenna1.object_list.values())[0].faces[0].center
        assert oantenna1.origin == [0, 0, 0]
        oantenna1.origin = [10, 20, 50]
        assert oantenna1.origin == [10, 20, 50]

        face_center_new = list(oantenna1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3

        oantenna2 = antenna_module(toolkit.aedtapp, frequency=1.0, material="FR4_epoxy", name=oantenna1.name)
        assert oantenna1.name != oantenna2.name

    def test_wire_dipole(self, toolkit):
        antenna_module = getattr(antenna_models, "WireDipole")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters.wire_rad.value

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna1 = antenna_module(toolkit.aedtapp, frequency=1.0, length_unit=toolkit.aedtapp.modeler.model_units)
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(toolkit.aedtapp, frequency=1.0, name=oantenna1.name)
        assert oantenna1.name != oantenna2.name

    def test_wire_dipole_duplicate_along_line(self, toolkit):
        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        antenna_module = getattr(antenna_models, "WireDipole")
        oantenna = antenna_module(toolkit.aedtapp, frequency=1.0, origin=[500, 20, 50])
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        new = oantenna.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3
