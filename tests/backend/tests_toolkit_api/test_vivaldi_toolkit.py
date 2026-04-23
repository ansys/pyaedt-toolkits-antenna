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

import pytest

from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend

pytestmark = [pytest.mark.antenna_toolkit_api]


def test_vivaldi_synth_only_registration():
    toolkit = ToolkitBackend()

    assert "Vivaldi" in toolkit.available_antennas
    assert "VivaldiStepped" in toolkit.available_antennas

    toolkit.properties.antenna.synthesis.start_frequency = 8.0
    toolkit.properties.antenna.synthesis.stop_frequency = 21.0

    parameters = toolkit.get_antenna("Vivaldi", synth_only=True)

    assert parameters
    assert "taper_length" in parameters
    assert "sub_x" in parameters
