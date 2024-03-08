# FOR TEST #
sys.path.extend(["C:\\AnsysDev\\repos\\pyaedt-toolkits-common\\src"])

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


import json
import os

from ansys.aedt.toolkits.common.backend.models import CommonProperties
from ansys.aedt.toolkits.common.backend.models import common_properties
from pydantic import BaseModel


class BackendProperties(BaseModel):
    """Store toolkit properties."""

    antenna_type: str = ""
    antenna_name: str = ""
    antenna_created: bool = False
    component_3d: bool = False
    coordinate_system: str = "Global"
    create_setup: bool = False
    feeder_length: float = 0.0
    frequency: float = 10.0
    frequency_unit: str = "GHz"
    gain_value: float = 0.0
    lattice_pair: bool = False
    length_unit: str = "meter"
    material: str = "pec"
    material_properties: dict = {}
    origin: list = [0.0, 0.0, 0.0]
    outer_boundary: str = ""
    parameters: dict = {}
    parameters_hfss: dict = {}
    sweep: int = (20,)
    substrate_height: float = (0.1,)
    start_frequency: float = (0.0,)
    stop_frequency: float = 0.0
    synth_only: bool = False


class Properties(BackendProperties, CommonProperties, validate_assignment=True):
    """Store all properties."""


backend_properties = {}
if os.path.expanduser(os.path.join(os.path.dirname(__file__), "backend_properties.json")):
    with open(os.path.join(os.path.dirname(__file__), "backend_properties.json")) as file_handler:
        backend_properties = json.load(file_handler)

toolkit_property = {}
if backend_properties:
    for backend_key in backend_properties:
        if hasattr(common_properties, backend_key):
            setattr(common_properties, backend_key, backend_properties[backend_key])
        else:
            toolkit_property[backend_key] = backend_properties[backend_key]

new_common_properties = {}
for common_key in common_properties:
    new_common_properties[common_key[0]] = common_key[1]

properties = Properties(**toolkit_property, **new_common_properties)
