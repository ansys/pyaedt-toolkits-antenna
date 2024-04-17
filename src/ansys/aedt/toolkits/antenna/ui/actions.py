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

from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from ansys.aedt.toolkits.common.ui.actions_generic import FrontendGeneric
from ansys.aedt.toolkits.common.ui.logger_handler import logger
from pyaedt.generic.general_methods import generate_unique_project_name
import requests

number_pattern = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")


class Frontend(FrontendGeneric):
    def __init__(self):
        FrontendGeneric.__init__(self)

    def antenna_synthesis(self):

        be_properties = requests.get(self.url + "/properties").json()

        new_properties = {
            "model": self.properties.antenna.antenna_selected,
            "length_unit": self.antenna_synthesis_menu.length_unit.text(),
            "frequency_unit": self.antenna_synthesis_menu.frequency_unit.text(),
            "synth_only": True,
        }

        synthesis_inputs = {}
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

        response_1 = requests.put(self.url + "/properties", json=new_properties)

        if response_1.ok:
            response_2 = requests.post(self.url + "/create_antenna")
            if response_2.ok:
                self.ui.update_logger("{} synthesis".format(self.properties.antenna.antenna_selected))
                return response_2.json()
            else:
                self.ui.update_logger("Wrong synthesis")
                return False
        else:
            self.ui.update_logger(response_1.json())
            return False
