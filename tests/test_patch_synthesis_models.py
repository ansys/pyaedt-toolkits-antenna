# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.toolkits.antenna.backend import antenna_models


@pytest.mark.parametrize(
    ("antenna_name", "parameter_name"),
    [
        ("EllipticalEdge", "edge_feed_width"),
        ("EllipticalInset", "inset_gap"),
        ("EllipticalProbe", "coax_inner_rad"),
        ("MbyNPatchArray", "patch_count_x"),
        ("SeqRotated2Patch", "patch_diameter"),
    ],
)
def test_patch_family_synthesis_parameters(antenna_name, parameter_name):
    antenna_module = getattr(antenna_models, antenna_name)
    antenna = antenna_module(None, frequency=1.0, length_unit="mm")
    assert getattr(antenna.synthesis_parameters, parameter_name).value


def test_m_by_n_patch_array_respects_patch_counts():
    antenna = antenna_models.MbyNPatchArray(
        None,
        frequency=1.0,
        length_unit="mm",
        number_of_patches_x=4,
        number_of_patches_y=2,
    )
    assert antenna.synthesis_parameters.patch_count_x.value == 4
    assert antenna.synthesis_parameters.patch_count_y.value == 2


def test_seq_rotated_patch_preserves_rotation_and_phase_inputs():
    antenna = antenna_models.SeqRotated2Patch(
        None,
        frequency=5.0,
        length_unit="mm",
        feed_rotation_angle=30.0,
        element_2_rotation_angle=-120.0,
        element_4_port_phase=315.0,
    )
    assert antenna.synthesis_parameters.feed_rotation_angle.value == 30.0
    assert antenna.synthesis_parameters.element_2_rotation_angle.value == -120.0
    assert antenna.synthesis_parameters.element_4_port_phase.value == 315.0
