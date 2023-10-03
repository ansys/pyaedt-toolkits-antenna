import os

from flask import request

from ansys.aedt.toolkits.antenna.backend.api import Toolkit
from ansys.aedt.toolkits.antenna.backend.common.multithreading_server import MultithreadingServer
from ansys.aedt.toolkits.antenna.backend.common.rest_api_generic import app
from ansys.aedt.toolkits.antenna.backend.common.rest_api_generic import jsonify
from ansys.aedt.toolkits.antenna.backend.common.rest_api_generic import logger
from ansys.aedt.toolkits.antenna.backend.common.rest_api_generic import settings

toolkit = Toolkit()


@app.route("/create_antenna", methods=["POST"])
def create_antenna_call():
    logger.info("[POST] /create_antenna (create antenna in HFSS)")

    properties = toolkit.get_properties()

    antenna = properties["antenna_type"]
    synth_only = properties["synth_only"]

    response = toolkit.get_antenna(antenna, synth_only=synth_only)
    if response:
        return jsonify(response), 200
    else:
        return jsonify("Antenna not created"), 500


@app.route("/get_hfss_model", methods=["GET"])
def get_hfss_model_call():
    logger.info("[GET] /get_hfss_model (Get antenna model in HFSS)")

    response = toolkit.export_hfss_model()
    if response:
        model_info = {}
        for element in response:
            element_path = element[0]
            encoded_obj = toolkit._serialize_obj_base64(element_path)
            name = os.path.splitext(os.path.basename(element_path))[0]
            model_info[name] = [encoded_obj.decode("utf-8"), element[1], element[2]]

        return jsonify(model_info), 200
    else:
        return jsonify("Antenna not created"), 500


@app.route("/update_parameters", methods=["PUT"])
def update_parameters_call():
    logger.info("[POST] /update_parameters (Update parameters in HFSS)")

    body = request.json
    if not body:
        msg = "body is empty!"
        logger.error(msg)
        return jsonify(msg), 500

    key = body["key"]
    value = body["value"]

    response = toolkit.update_parameters(key, value)
    if response:
        return jsonify(response), 200
    else:
        return jsonify("Antenna not created"), 500


@app.route("/analyze", methods=["POST"])
def analyze_call():
    logger.info("[POST] /analyze (analyze AEDT project in batch)")

    response = toolkit.analyze()
    if response:
        return jsonify("AEDT design launched"), 200
    else:
        return jsonify("Fail to launch design"), 500


@app.route("/scattering_results", methods=["GET"])
def scattering_results_call():
    logger.info("[POST] scattering_results (Get antenna scattering results)")

    response = toolkit.scattering_results()
    if response:
        return jsonify(response), 200
    else:
        return jsonify("Fail to get results"), 500


@app.route("/farfield_results", methods=["GET"])
def farfield_results_call():
    logger.info("[POST] farfield_results (Get antenna far field results)")

    response = toolkit.farfield_results()
    if response:
        return jsonify(response), 200
    else:
        return jsonify("Fail to get results"), 500


if __name__ == "__main__":
    app.debug = True
    server = MultithreadingServer()
    server.run(host=settings["url"], port=settings["port"], app=app)
