# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import os
import sys
from typing import Any
from typing import Dict
from typing import List

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ansys.aedt.toolkits.common.ui.models import UIProperties
from ansys.aedt.toolkits.common.ui.models import general_settings
from pydantic import BaseModel
from pydantic import Field


class AntennaProperties(BaseModel):
    """Stores toolkit properties."""

    antenna_created: str = ""
    available_models: List[str] = Field(default_factory=list)
    antenna_model_selected: str = ""
    antenna_selected: str = ""
    antenna_parameters: Dict[str, Any] = Field(default_factory=dict)
    create_setup: bool = True


class FrontendProperties(BaseModel):
    """Stores toolkit properties."""

    antenna: AntennaProperties


class Properties(FrontendProperties, UIProperties, validate_assignment=True):
    """Stores all properties."""


frontend_properties = {}
if os.path.isfile(os.path.join(os.path.dirname(__file__), "frontend_properties.toml")):
    with open(os.path.join(os.path.dirname(__file__), "frontend_properties.toml"), mode="rb") as file_handler:
        frontend_properties = tomllib.load(file_handler)

toolkit_property = {}
if frontend_properties:
    for frontend_key in frontend_properties:
        if frontend_key == "defaults":
            for toolkit_key in frontend_properties["defaults"]:
                if hasattr(general_settings, toolkit_key):
                    setattr(general_settings, toolkit_key, frontend_properties["defaults"][toolkit_key])
        else:
            toolkit_property[frontend_key] = frontend_properties[frontend_key]

new_common_properties = {}
for common_key in general_settings:
    new_common_properties[common_key[0]] = common_key[1]

properties = Properties(**toolkit_property, **new_common_properties)
