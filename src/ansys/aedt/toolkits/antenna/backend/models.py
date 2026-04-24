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

from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from typing import Any
from typing import Dict
from typing import List

from pydantic import BaseModel

from ansys.aedt.toolkits.common.backend.models import CommonProperties
from ansys.aedt.toolkits.common.backend.models import common_properties


class Synthesis(BaseModel, validate_assignment=True):
    """Stores antenna synthesis properties."""

    name: str = ""
    coordinate_system: str = "Global"
    element_1_port_phase: float = 0.0
    element_1_rotation_angle: float = 0.0
    element_2_port_phase: float = 90.0
    element_2_rotation_angle: float = -90.0
    element_3_port_phase: float = 180.0
    element_3_rotation_angle: float = -180.0
    element_4_port_phase: float = 270.0
    element_4_rotation_angle: float = -270.0
    feed_rotation_angle: float = 45.0
    frequency: float = 10.0
    frequency_unit: str = "GHz"
    feeder_length: float = 0.0
    gain: float = 0.0
    length_unit: str = "meter"
    material: str = "pec"
    material_properties: Dict[str, Any] = {}
    number_of_patches_x: int = 2
    number_of_patches_y: int = 3
    origin: List[float] = [0.0, 0.0, 0.0]
    outer_boundary: str = ""
    start_frequency: float = 0.0
    stop_frequency: float = 0.0
    substrate_height: float = 0.1


class Setup(BaseModel, validate_assignment=True):
    """Stores antenna setup properties."""

    component_3d: bool = False
    create_setup: bool = False
    lattice_pair: bool = False
    num_cores: int = 4
    sweep: int = 20


class AntennaProperties(BaseModel, validate_assignment=True):
    """Stores antenna properties."""

    model: str = ""
    is_created: bool = False
    parameters: Dict[str, Any] = {}
    parameters_hfss: Dict[str, Any] = {}
    synth_only: bool = False
    synthesis: Synthesis = Synthesis()
    setup: Setup = Setup()


class BackendProperties(BaseModel):
    """Stores toolkit properties."""

    antenna: AntennaProperties


class Properties(BackendProperties, CommonProperties, validate_assignment=True):
    """Stores all properties."""


backend_properties = {}
backend_properties_file = Path(__file__).parent / "backend_properties.toml"
if backend_properties_file.is_file():
    with backend_properties_file.open(mode="rb") as file_handler:
        backend_properties = tomllib.load(file_handler)

toolkit_property = {}
if backend_properties:
    for backend_key in backend_properties:
        if backend_key == "defaults":
            for toolkit_key in backend_properties["defaults"]:
                if hasattr(common_properties, toolkit_key):
                    setattr(common_properties, toolkit_key, backend_properties["defaults"][toolkit_key])
        else:
            toolkit_property[backend_key] = backend_properties[backend_key]

new_common_properties = {}
for common_key in common_properties:
    new_common_properties[common_key[0]] = common_key[1]

properties = Properties(antenna=AntennaProperties(**toolkit_property), **new_common_properties)
