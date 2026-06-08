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

from ansys.aedt.core.modeler.cad.object_3d import Object3d
import pytest

from ansys.aedt.toolkits.antenna.backend import antenna_models

pytestmark = [pytest.mark.antenna_models_api]


class TestClass:
    """Class defining a workflow to test PIFA antenna models."""

    def test_planar_inverted_f(self, toolkit):
        antenna_module = getattr(antenna_models, "PlanarInvertedF")
        oantenna = antenna_module(None, frequency=2.4, length_unit="mm")
        assert oantenna.synthesis_parameters.length1.value

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Modal"

        cs = toolkit.aedtapp.modeler.create_coordinate_system(origin=[10, 20, 30])

        oantenna = antenna_module(toolkit.aedtapp, frequency=2.4, length_unit=toolkit.aedtapp.modeler.model_units)
        oantenna.coordinate_system = cs.name
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna.object_list
        assert oantenna.excitations
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(toolkit.aedtapp, frequency=2.4, length_unit=toolkit.aedtapp.modeler.model_units)
        assert oantenna.name != oantenna2.name

    def test_shorting_pin(self, toolkit):
        antenna_module = getattr(antenna_models, "ShortingPin")
        oantenna = antenna_module(None, frequency=2.45, length_unit="mm")
        assert oantenna.synthesis_parameters.coax_inner_rad.value

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna = antenna_module(toolkit.aedtapp, frequency=2.45, length_unit=toolkit.aedtapp.modeler.model_units)
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna.object_list
        assert oantenna.excitations
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(toolkit.aedtapp, frequency=2.45, length_unit=toolkit.aedtapp.modeler.model_units)
        assert oantenna.name != oantenna2.name

    def test_shorting_plate(self, toolkit):
        antenna_module = getattr(antenna_models, "ShortingPlate")
        oantenna = antenna_module(None, frequency=3.0, length_unit="mm")
        assert oantenna.synthesis_parameters.plate_w.value

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna = antenna_module(toolkit.aedtapp, frequency=3.0, length_unit=toolkit.aedtapp.modeler.model_units)
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna.object_list
        assert oantenna.excitations
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(toolkit.aedtapp, frequency=3.0, length_unit=toolkit.aedtapp.modeler.model_units)
        assert oantenna.name != oantenna2.name
