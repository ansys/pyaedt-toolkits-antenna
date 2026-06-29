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
    """Class defining a workflow to test Yagi-Uda antenna models."""

    def test_quasi_yagi_synthesis_only(self):
        antenna_module = getattr(antenna_models, "QuasiYagi")
        oantenna = antenna_module(None, frequency=2.0, length_unit="mm")

        assert oantenna.synthesis_parameters.sub_length.value == 86.5
        assert oantenna.synthesis_parameters.launcher_length.value == 62.5

    def test_quasi_yagi(self, toolkit):
        antenna_module = getattr(antenna_models, "QuasiYagi")
        oantenna0 = antenna_module(None, frequency=2.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna1 = antenna_module(toolkit.aedtapp, frequency=2.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

    def test_wire_yagi_uda_synthesis_only(self):
        antenna_module = getattr(antenna_models, "WireYagiUda")
        oantenna = antenna_module(None, frequency=1.0, length_unit="cm", gain=11.36)

        assert oantenna.synthesis_parameters.number_of_directors.value == 3
        assert oantenna.synthesis_parameters.director_03_length.value > 0.0

    def test_wire_yagi_uda(self, toolkit):
        antenna_module = getattr(antenna_models, "WireYagiUda")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="cm", gain=11.36)
        assert oantenna0.synthesis_parameters.number_of_directors.value == 3

        toolkit.connect_design("HFSS")
        toolkit.aedtapp.solution_type = "Terminal"

        oantenna1 = antenna_module(toolkit.aedtapp, frequency=1.0, length_unit="cm", gain=11.36)
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1.object_list
        assert "port_lump_" + oantenna1.name in oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)
