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
from pyaedt import is_linux

from tests.backend.conftest import PROJECT_NAME

pytestmark = [pytest.mark.antenna_toolkit_api]

from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antenna.backend import antenna_models


class TestClass:
    """Class defining a workflow to test antenna toolkit."""
    def test_01_get_antenna(self, aedt_common):
        antenna_parameters_1 = aedt_common.get_antenna("RectangularPatchProbe", synth_only=True)

        assert antenna_parameters_1

        aedt_common.properties.antenna.setup.create_setup = True
        aedt_common.properties.antenna.synthesis.outer_boundary = "Radiation"
        aedt_common.properties.antenna.synthesis.length_unit = "cm"

        antenna_parameters_2 = aedt_common.get_antenna("RectangularPatchProbe")

        assert antenna_parameters_2

        new_antenna = aedt_common.get_antenna("BowTie")

        assert not new_antenna

        aedt_common.release_aedt(False, False)

    def test_02_update_parameters(self, aedt_common):
        parameter_list = list(aedt_common.properties.antenna.parameters.keys())

        property_key = aedt_common.properties.antenna.parameters_hfss[parameter_list[0]]

        assert aedt_common.update_hfss_parameters(parameter_list[0], "0.03")

        aedt_common.connect_design()
        assert aedt_common.aedtapp[property_key] == "0.03" + aedt_common.properties.antenna.synthesis.length_unit
        aedt_common.release_aedt(False, False)

        assert not aedt_common.update_hfss_parameters("hola", "0.03")

    @pytest.mark.skipif(is_linux, reason="Crashes on Linux")
    def test_03_analyze(self, aedt_common):

        aedt_common.properties.antenna.setup.num_cores = 2
        aedt_common.connect_design()
        aedt_common.aedtapp.setups[0].props["MaxDeltaS"] = 1
        aedt_common.aedtapp.setups[0].props["MaximumPasses"] = 1

        aedt_common.release_aedt(False, False)

        assert aedt_common.analyze()

    @pytest.mark.skipif(is_linux, reason="Crashes on Linux")
    def test_04_scattering_results(self, aedt_common):
        sweep, data = aedt_common.scattering_results()

        assert len(sweep) == len(data)

    @pytest.mark.skipif(is_linux, reason="Crashes on Linux")
    def test_05_export_farfield(self, aedt_common):
        """Get aedt model."""
        frequency = (str(aedt_common.properties.antenna.synthesis.frequency) +
                     aedt_common.properties.antenna.synthesis.frequency_unit)
        encoded_files = aedt_common.export_farfield(frequencies=frequency, encode=True, sphere="3D")
        assert isinstance(encoded_files, tuple)
        assert len(encoded_files) == 5
        farfield_data = aedt_common.export_farfield(frequencies=frequency, encode=False, sphere="3D")
        assert isinstance(farfield_data, tuple)
        assert len(farfield_data) == 2
