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

import sys

# isort: off

from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend

from ansys.aedt.toolkits.common.backend.multithreading_server import MultithreadingServer
from ansys.aedt.toolkits.common.backend.rest_api import app
from ansys.aedt.toolkits.common.backend.rest_api import jsonify
from ansys.aedt.toolkits.common.backend.rest_api import logger

from flask import request

# isort: on

toolkit_api = ToolkitBackend()

if len(sys.argv) == 3:
    toolkit_api.properties.url = sys.argv[1]
    toolkit_api.properties.port = int(sys.argv[2])


@app.route("/create_antenna", methods=["POST"])
def create_antenna():
    logger.info("[POST] /reate_antenna (Create antenna in HFSS.)")

    properties = toolkit_api.get_properties()

    antenna = properties["antenna"]["model"]
    synth_only = properties["antenna"]["synth_only"]

    response = toolkit_api.get_antenna(antenna, synth_only=synth_only)
    if response:
        return jsonify(response), 200
    else:  # pragma: no cover
        return jsonify("Antenna not created"), 500


@app.route("/hfss_parameters", methods=["PATCH"])
def update_hfss_parameters():
    logger.info("[PATCH] /hfss_parameters (Update parameters in HFSS)")

    body = request.json
    if not body:
        msg = "body is empty!"
        logger.error(msg)
        return jsonify(msg), 500

    key = body["key"]
    value = body["value"]

    response = toolkit_api.update_hfss_parameters(key, value)
    if response:
        return jsonify(response), 200
    else:  # pragma: no cover
        return jsonify("Antenna not created"), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    logger.info("[POST] /analyze (analyze AEDT project in batch)")

    response = toolkit_api.analyze()
    if response:
        return jsonify("AEDT design analysis finished"), 200
    else:  # pragma: no cover
        return jsonify("Fail to launch design"), 500


@app.route("/scattering_results", methods=["GET"])
def scattering_results():
    logger.info("[GET] scattering_results (Get antenna scattering results)")

    response = toolkit_api.scattering_results()
    if response:
        return jsonify(response), 200
    else:  # pragma: no cover
        return jsonify("Fail to get results"), 500


@app.route("/export_farfield", methods=["GET"])
def export_farfield():
    logger.info("[GET] farfield_results (Get antenna far field data)")

    body = request.json

    # Default values
    default_values = {
        "frequencies": None,
        "setup": None,
        "sphere": None,
        "variations": None,
        "encode": True,
    }

    props = toolkit_api.get_properties()
    default_values["frequencies"] = [
        str(props["antenna"]["synthesis"]["frequency"]) + props["antenna"]["synthesis"]["frequency_unit"]
    ]

    # Extract values from the request body
    params = {key: body.get(key, default_values[key]) for key in default_values}

    response = toolkit_api.export_farfield(**params)

    if response:
        return jsonify(response), 200
    else:  # pragma: no cover
        return jsonify("Fail to get results"), 500


def run_backend(port=0):
    """Run the server."""
    app.debug = toolkit_api.properties.debug
    server = MultithreadingServer()
    if port == 0:
        port = toolkit_api.properties.port
    server.run(host=toolkit_api.properties.url, port=port, app=app)


if __name__ == "__main__":
    run_backend()
