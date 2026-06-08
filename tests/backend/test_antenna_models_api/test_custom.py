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

import math

from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
import pytest

from ansys.aedt.toolkits.antenna.backend import antenna_models

pytestmark = [pytest.mark.antenna_models_api]


class TestClass:
    """Class defining a workflow to test custom antenna models."""

    def test_gps_patch_ceramic_synthesis_matches_act_reference(self):
        antenna_module = getattr(antenna_models, "GPSPatchCeramic")
        opatch = antenna_module(None, frequency=1.575, length_unit="mm")

        assert math.isclose(opatch.synthesis_parameters.patch_x.value, 12.0, rel_tol=1e-6)
        assert math.isclose(opatch.synthesis_parameters.patch_y.value, 12.0, rel_tol=1e-6)
        assert math.isclose(opatch.synthesis_parameters.cutout.value, 1.1, rel_tol=1e-6)
        assert math.isclose(opatch.synthesis_parameters.feed_x.value, -0.4, rel_tol=1e-6)
        assert math.isclose(opatch.synthesis_parameters.feed_y.value, 0.9, rel_tol=1e-6)
        assert math.isclose(opatch.synthesis_parameters.gnd_x.value, 60.0, rel_tol=1e-6)
        assert math.isclose(opatch.synthesis_parameters.gnd_y.value, 60.0, rel_tol=1e-6)

    def test_gps_patch_ceramic_model_hfss(self, toolkit):
        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        antenna_module = getattr(antenna_models, "GPSPatchCeramic")
        opatch = antenna_module(toolkit.aedtapp, frequency=1.575, length_unit=toolkit.aedtapp.modeler.model_units)
        opatch.init_model()

        cs = toolkit.aedtapp.modeler.create_coordinate_system(origin=[10, 20, 30])
        opatch.coordinate_system = cs.name

        opatch.model_hfss()
        opatch.setup_hfss()

        assert opatch
        assert opatch.object_list
        for comp in opatch.object_list.values():
            assert isinstance(comp, Object3d)

        face_center = list(opatch.object_list.values())[0].faces[0].center
        assert opatch.origin == [0, 0, 0]
        opatch.origin = [10, 20, 50]
        assert opatch.origin == [10, 20, 50]

        face_center_new = list(opatch.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3

        component = opatch.create_3dcomponent(replace=True)
        assert list(toolkit.aedtapp.modeler.user_defined_components.keys())[0] == component.name
