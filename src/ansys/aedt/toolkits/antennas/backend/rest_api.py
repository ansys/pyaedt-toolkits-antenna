from ansys.aedt.toolkits.antennas.backend.common.rest_api_generic import app
from ansys.aedt.toolkits.antennas.backend.common.rest_api_generic import jsonify
from ansys.aedt.toolkits.antennas.backend.common.rest_api_generic import logger
from flask import request
from ansys.aedt.toolkits.antennas.backend.common.rest_api_generic import service
from ansys.aedt.toolkits.antennas.backend.common.rest_api_generic import settings
from ansys.aedt.toolkits.antennas.backend.common.multithreading_server import MultithreadingServer


@app.route("/create_antenna", methods=["POST"])
def create_antennay_call():
    logger.info("[POST] /create_antenna (create antenna in HFSS)")

    body = request.json

    if not body:
        msg = "body is empty!"
        logger.error(msg)
        return jsonify(msg), 500
    elif not isinstance(body, dict):
        msg = "body not correct"
        logger.error(msg)
        return jsonify(msg), 500

    antenna = body["antenna_type"]
    synth_only = body["synth_only"]

    response = service.get_antenna(antenna, synth_only=synth_only)
    if response:
        return jsonify("Antenna created"), 200
    else:
        return jsonify("Antenna not created"), 500


if __name__ == "__main__":
    app.debug = True
    server = MultithreadingServer()
    server.run(host=settings["url"], port=settings["port"], app=app)
