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

import re
import tempfile
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit

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
