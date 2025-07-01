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

import pytest
import math

from tests.backend.conftest import PROJECT_NAME

pytestmark = [pytest.mark.antenna_models_common_api]

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import StandardWaveguide
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import TransmissionLine

test_project_name = "Patch_test"

tl_calc = TransmissionLine()
wg_standard = StandardWaveguide()


class TestClass:
    """Class defining a workflow to test antenna models common."""

    def test_01_microstrip_calculator(self):
        w1 = tl_calc.microstrip_calculator(substrate_height=0.15, permittivity=4.4)
        assert math.isclose(w1[0], 0.2867789, rel_tol=1e-6)
        assert math.isclose(w1[1], 0.006849743, rel_tol=1e-6)

        w2 = tl_calc.microstrip_calculator(substrate_height=0.15, permittivity=2)
        assert math.isclose(w2[0], 0.49071766, rel_tol=1e-6)
        assert math.isclose(w2[1], 0.0094996773, rel_tol=1e-6)

    def test_02_stripline_calculator(self):
        w1 = tl_calc.stripline_calculator(substrate_height=10, permittivity=2.2)
        assert math.isclose(w1, 8.298368009, rel_tol=1e-6)
        w2 = tl_calc.stripline_calculator(substrate_height=0.15, permittivity=4.4, impedance=100)
        assert math.isclose(w2, 0.01211778667, rel_tol=1e-6)

    def test_03_find_waveguide(self):
        w_dim = wg_standard.get_waveguide_dimensions("WR-2300", "cm")
        assert math.isclose(w_dim[0], 58.41999999, rel_tol=1e-6)
        w_name = wg_standard.find_waveguide(10, "GHz")
        assert w_name == "WR-102"
