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
import json

from tests.backend.conftest import PROJECT_NAME

pytestmark = [pytest.mark.antenna_toolkit_rest_api]

from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antenna.backend import antenna_models


class TestClass:
    """Class defining a workflow to test rest api toolkit."""
    def test_01_get_antenna(self, client):
        new_properties = {
            "model": "RectangularPatchProbe",
            "length_unit": "cm",
            "create_setup": True,
            "outer_boundary": "Radiation",
            "synth_only": False,
        }
        client.put("/properties", json=new_properties)
        response = client.post("/create_antenna")
        assert response.status_code == 200
        data = json.loads(response.data.decode("utf-8"))
        assert isinstance(data, dict)

    def test_02_update_parameters(self, client):
        response1 = client.patch("/hfss_parameters", json={})
        assert response1.status_code == 500

        be_properties = client.get("/properties").json
        parameter_list = list(be_properties["antenna"]["parameters"].keys())

        property_key = parameter_list[0]

        response2 = client.patch("/hfss_parameters", json={"key": property_key, "value": "0.03"})

        assert response2.status_code == 200

    def test_03_analyze(self, client):
        new_properties = {
            "num_cores": 4,
        }
        client.put("/properties", json=new_properties)

        response1 = client.post("/analyze")

        assert response1.status_code == 200

    def test_04_scattering_results(self, client):
        response2 = client.get("/scattering_results")
        assert response2.status_code == 200
        data = json.loads(response2.data.decode("utf-8"))
        assert len(data) == 2

    def test_05_farfield_results(self, client):
        response2 = client.get("/export_farfield", json={"sphere": "3D"})
        assert response2.status_code == 200
        data = json.loads(response2.data.decode("utf-8"))
        assert len(data) == 5
