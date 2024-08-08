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

"""
API Test Configuration Module
-----------------------------

Description
===========
This module contains the configuration and fixture for the pytest-based tests for the API.

The default configuration can be changed by placing a file called local_config.json.
An example of the contents of local_config.json:

{
  "desktop_version": "2024.2",
  "non_graphical": false,
  "use_grpc": true
}

You can enable the API log file in the backend_properties.json.

"""

import os
import pytest
import sys

from pyaedt import generate_unique_project_name

from tests.backend.conftest import read_local_config, setup_aedt_settings, DEFAULT_CONFIG, PROJECT_NAME

from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
from ansys.aedt.toolkits.antenna.backend.models import properties

from ansys.aedt.toolkits.antenna.backend import api
sys.path.append(os.path.dirname(api.__file__))

from ansys.aedt.toolkits.antenna.backend.run_backend import app

# Setup config
config = DEFAULT_CONFIG.copy()
local_cfg = read_local_config()
config.update(local_cfg)

# Update AEDT settings
setup_aedt_settings(config)


@pytest.fixture(scope="session")
def client(logger, common_temp_dir):
    """Create a test client."""

    logger.info("AEDTCommon API initialization")

    properties.aedt_version = config["desktop_version"]
    properties.non_graphical = config["non_graphical"]
    properties.use_grpc = config["use_grpc"]
    properties.debug = config["debug"]

    aedt_common = ToolkitBackend()
    aedt_common.launch_thread(aedt_common.launch_aedt)
    is_aedt_launched = aedt_common.wait_to_be_idle()

    aedt_common.active_project = generate_unique_project_name(common_temp_dir, project_name="Test_Antenna")
    aedt_common.connect_aedt()
    aedt_common.desktop.odesktop.NewProject(aedt_common.active_project)
    aedt_common.connect_design()
    aedt_common.aedtapp.design_name = "antenna_test"
    aedt_common.save_project()
    aedt_common.release_aedt(False, False)

    if not is_aedt_launched:
        logger.error("AEDT is not launched")
        raise Exception

    logger.info("Client initialization")
    app.testing = True

    with app.test_client() as client:
        new_properties = {
            "aedt_version": properties.aedt_version,
            "non_graphical": properties.non_graphical,
            "use_grpc": properties.use_grpc,
            "debug": properties.debug,
            "active_design": properties.active_design,
            "active_project": properties.active_project,
            "design_list": properties.design_list,
            "project_list": properties.project_list,
            "selected_process": properties.selected_process,
        }
        client.put("/properties", json=new_properties)
        yield client

        close_properties = {"close_projects": True, "close_on_exit": True}
        client.post("/close_aedt", json=close_properties)
