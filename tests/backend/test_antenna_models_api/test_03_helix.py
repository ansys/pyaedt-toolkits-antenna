# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

import os
import pytest

from tests.backend.conftest import PROJECT_NAME

pytestmark = [pytest.mark.antenna_models_api]

from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antenna.backend import antenna_models


class TestClass:
    """Class defining a workflow to test antenna models helix."""

    def test_01_helix_axial(self, aedt_common):
        antenna_module = getattr(antenna_models, "AxialMode")
        oantenna = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        aedt_common.connect_design()
        aedt_common.aedtapp.design_name = "helix_axial_antenna"
        aedt_common.aedtapp.solution_type = "Modal"
        aedt_common.save_project(release_aedt=False)

        oantenna = antenna_module(aedt_common.aedtapp,
                                  frequency=1.0,
                                  length_unit=aedt_common.aedtapp.modeler.model_units)
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            outer_boundary="Radiation"
        )

        assert oantenna.name != oantenna2.name
