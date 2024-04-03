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
    """Class defining a workflow to test antenna models bowtie."""
    def test_01_bowtie(self, aedt_common):
        antenna_module = getattr(antenna_models, "BowTie")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        aedt_common.connect_design()
        aedt_common.aedtapp.design_name = "Bowtie"
        aedt_common.save_project(release_aedt=False)

        oantenna1 = antenna_module(aedt_common.aedtapp, frequency=1.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(aedt_common.aedtapp,
                                   frequency=1.0,
                                   outer_boundary="Radiation",
                                   length_unit="mm")

        assert oantenna1.name != oantenna2.name
        aedt_common.release_aedt(False, False)

    def test_02_bowtie_rounded(self, aedt_common):
        antenna_module = getattr(antenna_models, "BowTieRounded")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        aedt_common.connect_design()
        aedt_common.aedtapp.design_name = "BowTieRounded"
        aedt_common.save_project(release_aedt=False)

        oantenna1 = antenna_module(aedt_common.aedtapp, frequency=1.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(aedt_common.aedtapp,
                                   frequency=1.0,
                                   length_unit="mm",
                                   outer_boundary="Radiation")

        assert oantenna1.name != oantenna2.name
        aedt_common.release_aedt(False, False)

    def test_03_bowtie_slot(self, aedt_common):
        antenna_module = getattr(antenna_models, "BowTieSlot")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        aedt_common.connect_design()
        aedt_common.aedtapp.design_name = "BowTieSlot"
        aedt_common.save_project(release_aedt=False)

        oantenna1 = antenna_module(aedt_common.aedtapp, frequency=1.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)
        oantenna2 = antenna_module(aedt_common.aedtapp, frequency=1.0, length_unit="mm", outer_boundary="Radiation")

        assert oantenna1.name != oantenna2.name
        aedt_common.release_aedt(False, False)
