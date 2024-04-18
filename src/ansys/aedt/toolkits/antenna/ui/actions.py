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

import base64
import re
import os
import tempfile
import json
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from pyaedt.modules.solutions import FfdSolutionData
from pyaedt.generic.general_methods import read_json

# isort: off

from ansys.aedt.toolkits.common.ui.logger_handler import logger

from ansys.aedt.toolkits.common.ui.actions_generic import FrontendGeneric

# isort: on

from pyaedt.generic.general_methods import generate_unique_project_name
import requests

number_pattern = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")


class Frontend(FrontendGeneric):
    def __init__(self):
        FrontendGeneric.__init__(self)
        self.temp_folder = tempfile.mkdtemp()

    def antenna_synthesis(self):
        """Antenna synthesis."""
        if not self.__update_antenna_properties():
            return False

        response = requests.post(self.url + "/create_antenna")
        if response.ok:
            msg = "{} synthesis".format(self.properties.antenna.antenna_selected)
            self.ui.update_logger(msg)
            logger.debug(msg)
            return response.json()

        else:
            msg = response.json()
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def antenna_generate(self):
        """Generate antenna in HFSS design."""
        # Antenna properties
        if not self.__update_antenna_properties(synth_only=False):
            return False

        be_properties = self.get_properties()

        # Toolkit properties
        project_selected = be_properties["active_project"]
        design_selected = be_properties["active_design"]
        if project_selected and design_selected:
            if project_selected == "No Project":
                project_selected = generate_unique_project_name(rootname=self.temp_folder)
                be_properties["active_project"] = project_selected

            for project in be_properties["project_list"]:
                if self.get_project_name(project) == project_selected:
                    be_properties["active_project"] = project
                    if project_selected in list(be_properties["design_list"].keys()):
                        designs = be_properties["design_list"][project_selected]
                        for design in designs:
                            if design_selected == design:
                                be_properties["active_design"] = design
                                break
                    break
        else:
            project_selected = generate_unique_project_name()
            project_selected = self.get_project_name(project_selected)
            be_properties["active_project"] = project_selected

        # Set properties
        if not self.set_properties(be_properties):
            msg = "Wrong parameters {}".format(be_properties)
            self.ui.update_logger(msg)
            logger.debug(msg)
            return False

        new_properties = {
            "create_setup": self.ui.app.antenna_synthesis_menu.create_setup.isChecked(),
            "component_3d": self.ui.app.antenna_synthesis_menu.component_3d.isChecked(),
            "lattice_pair": self.ui.app.antenna_synthesis_menu.lattice_pair.isChecked(),
        }

        if not self.set_properties(new_properties):
            msg = "Wrong parameters {}".format(new_properties)
            self.ui.update_logger(msg)
            logger.debug(msg)
            return False

        response = requests.post(self.url + "/create_antenna")
        if response.ok:
            msg = "{} antenna created".format(self.properties.antenna.antenna_selected)
            self.ui.update_logger(msg)
            logger.debug(msg)
            return response.json()
        else:
            msg = "Generation failed"
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def update_antenna_parameter(self, key, value):
        """Update antenna parameter."""
        response = requests.put(self.url + "/update_parameters", json={"key": key, "value": value})
        if response.ok:
            msg = "{} updated in design".format(key)
            self.ui.update_logger(msg)
            logger.debug(msg)
            return response.json()

        else:
            msg = "{} not updated".format(key)
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def analyze_design(self):
        """Analyze design."""
        response = requests.post(self.url + "/analyze")

        if response.ok:
            msg = "Antenna solved"
            self.ui.update_logger(msg)
            logger.debug(msg)
            return response.json()

        else:
            msg = response.json()
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def export_farfield(self):
        """Get farfield data."""
        farfield_data = None
        if self.properties.backend_url in ["127.0.0.1", "localhost"]:
            response = requests.get(self.url + "/export_farfield", json={"sphere": "3D", "encode": False})
            if response.ok:
                data = response.json()
                farfield_data = FfdSolutionData(data[0], data[1])
        else:
            response = requests.get(self.url + "/export_farfield", json={"sphere": "3D", "encode": True})
            if response.ok:
                data = response.json()

                # Create directories
                cont = 0
                for encoded_data in range(len(data[0])):
                    os.mkdir(os.path.join(self.temp_folder, str(cont)))
                    os.mkdir(os.path.join(self.temp_folder, str(cont), "geometry"))
                    cont += 1

                # EEP files
                cont = 0
                eep_files = []
                for encoded_data in data[0]:
                    encoded_data_bytes = bytes(encoded_data, "utf-8")
                    decoded_data = base64.b64decode(encoded_data_bytes)
                    file_path = os.path.join(self.temp_folder, str(cont), "eep.txt")
                    eep_files.append(file_path)
                    with open(file_path, "wb") as f:
                        f.write(decoded_data)
                    cont += 1

                # JSON files
                json_data = []
                cont = 0
                for encoded_data in data[1]:
                    encoded_data_bytes = bytes(encoded_data, "utf-8")
                    decoded_data = base64.b64decode(encoded_data_bytes)
                    file_path = os.path.join(self.temp_folder, str(cont), "eep.json")
                    with open(file_path, "wb") as f:
                        f.write(decoded_data)
                    cont += 1
                    json_data.append(read_json(file_path))

                # LOAD json to know the obj names

                # Geometry files
                cont = 0
                for encoded_data in data[2].values():
                    cont_geom = 0
                    geometry_names = list(json_data[0]["model_info"].keys())
                    for encoded_geometry in encoded_data:
                        encoded_data_bytes = bytes(encoded_geometry, "utf-8")
                        decoded_data = base64.b64decode(encoded_data_bytes)
                        file_path = os.path.join(self.temp_folder, str(cont), "geometry",
                                                 geometry_names[cont_geom] + ".obj")
                        with open(file_path, "wb") as f:
                            f.write(decoded_data)
                        cont_geom += 1
                    cont += 1

                # FFD files
                cont = 0
                for encoded_data in data[3].values():
                    cont_ffd = 1
                    for encoded_ffd in encoded_data:
                        encoded_data_bytes = bytes(encoded_ffd, "utf-8")
                        decoded_data = base64.b64decode(encoded_data_bytes)
                        file_path = os.path.join(self.temp_folder, str(cont), "eep_{}.ffd".format(str(cont_ffd)))
                        with open(file_path, "wb") as f:
                            f.write(decoded_data)
                        cont_ffd += 1
                    cont += 1

                farfield_data = FfdSolutionData(eep_files[0], data[4])

        if farfield_data:
            msg = "Far field results extracted"
            self.ui.update_logger(msg)
            logger.debug(msg)
            return farfield_data

        else:
            msg = "Far field not extracted"
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def scattering_results(self):
        """Get farfield 2D results."""
        response = requests.get(self.url + "/scattering_results")

        if response.ok:
            msg = "Scattering results extracted"
            self.ui.update_logger(msg)
            logger.debug(msg)
            return response.json()

        else:
            msg = response.json()
            self.ui.update_logger(msg)
            logger.error(msg)
            return False

    def __update_antenna_properties(self, synth_only=True):
        """Update antenna backend properties."""
        be_properties = self.get_properties()

        new_properties = {
            "model": self.properties.antenna.antenna_selected,
            "length_unit": self.antenna_synthesis_menu.length_unit.text(),
            "frequency_unit": self.antenna_synthesis_menu.frequency_unit.text(),
            "synth_only": synth_only,
        }

        label = ""
        origin = [0.0, 0.0, 0.0]
        new_properties["origin"] = origin

        for antenna_input_lines in self.antenna_synthesis_menu.antenna_input_frame.children():

            if isinstance(antenna_input_lines, QLabel):
                original_label = antenna_input_lines.text()
                label = original_label.lower().replace(" ", "_")

            if label and isinstance(antenna_input_lines, QLineEdit):
                data = antenna_input_lines.text()

                if number_pattern.match(data):
                    data = float(data)

                if label in be_properties["antenna"]["synthesis"]:
                    new_properties[label] = data
                elif label == "origin_x_position":
                    new_properties["origin"][0] = data
                elif label == "origin_y_position":
                    new_properties["origin"][1] = data
                elif label == "origin_z_position":
                    new_properties["origin"][2] = data
                label = ""
            elif label and isinstance(antenna_input_lines, QComboBox):
                if label in be_properties["antenna"]["synthesis"]:
                    new_properties[label] = antenna_input_lines.currentText()
                label = ""

        if not self.set_properties(new_properties):
            msg = "Wrong parameters {}".format(new_properties)
            self.ui.update_logger(msg)
            logger.debug(msg)
            return False
        else:
            return True
