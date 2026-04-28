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

"""
Antenna models API conftest.

-------------------------

Description
===========
This module contains the configuration and fixture for the pytest-based tests for the antenna models API.

The default configuration can be changed by placing a file called local_config.json.
An example of the contents of local_config.json:

{
  "desktop_version": "2026.1",
  "non_graphical": false,
  "use_grpc": true
}

You can enable the API log file in the backend_properties.json.

"""

import pytest

from ansys.aedt.core import Desktop
from ansys.aedt.core import generate_unique_project_name
from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
from tests.backend.conftest import DEFAULT_CONFIG
from tests.backend.conftest import read_local_config
from tests.backend.conftest import setup_aedt_settings

# Setup config
config = DEFAULT_CONFIG.copy()
local_cfg = read_local_config()
config.update(local_cfg)

# Update AEDT settings
setup_aedt_settings(config)

VERSION = config["desktop_version"]
NONGRAPHICAL = config["non_graphical"]
USE_GRPC = config["use_grpc"]
DEBUG = config["debug"]


@pytest.fixture(scope="session", autouse=True)
def desktop(common_temp_dir):
    desktop = Desktop(VERSION, NONGRAPHICAL, True)
    desktop.odesktop.SetTempDirectory(str(common_temp_dir))
    desktop.disable_autosave()
    port = desktop.port
    test_session_info = {"version": VERSION, "non_graphical": NONGRAPHICAL, "port": port}
    yield test_session_info
    desktop = Desktop(VERSION, NONGRAPHICAL, False, port=port)
    desktop.close_desktop()


@pytest.fixture
def toolkit(logger, common_temp_dir):
    """Initialize toolkit with common API."""
    logger.info("AEDTCommon API initialization")
    toolkit = ToolkitBackend()

    new_properties = {
        "aedt_version": VERSION,
        "non_graphical": NONGRAPHICAL,
        "use_grpc": config["use_grpc"],
    }
    toolkit.set_properties(new_properties)
    toolkit.launch_aedt()

    # Close project if there are
    if toolkit.desktop and toolkit.desktop.project_list:
        projects = toolkit.desktop.project_list.copy()
        for project_name in projects:
            toolkit.desktop.odesktop.CloseProject(project_name)
        toolkit.properties.active_project = ""
        toolkit.properties.design_list = {}
        toolkit.properties.active_design = ""
        toolkit.properties.project_list = []

    active_project = generate_unique_project_name(common_temp_dir, project_name="Test_Antenna")
    toolkit.properties.active_project = active_project
    toolkit.connect_design("HFSS")

    toolkit.release_aedt(False, False)
    yield toolkit

    # Close project if there are
    toolkit.connect_aedt()
    if toolkit.desktop and toolkit.desktop.project_list:
        projects = toolkit.desktop.project_list.copy()
        for project_name in projects:
            toolkit.desktop.odesktop.CloseProject(project_name)
        toolkit.properties.active_project = ""
        toolkit.properties.design_list = {}
        toolkit.properties.active_design = ""
        toolkit.properties.project_list = []

    toolkit.release_aedt(False, False)
