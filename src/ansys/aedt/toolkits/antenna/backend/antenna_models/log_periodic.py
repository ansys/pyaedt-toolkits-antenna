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

from collections import OrderedDict
import math

from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonLogPeriodic(CommonAntenna):
    """Provides base methods common to log periodic antennas."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "LogPeriodic"
        CommonAntenna.__init__(self, _default_input_parameters, *args, **kwargs)

    def _refresh_model(self):
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    @property
    def gain(self):
        """Expected antenna directivity in dBi."""
        return self._input_parameters.gain

    @gain.setter
    def gain(self, value):
        self._input_parameters.gain = value
        self._refresh_model()

    @property
    def input_resistance(self):
        """Feed resistance."""
        return self._input_parameters.input_resistance

    @input_resistance.setter
    def input_resistance(self, value):
        self._input_parameters.input_resistance = value
        self._refresh_model()

    @property
    def load_impedance(self):
        """Termination resistance."""
        return self._input_parameters.load_impedance

    @load_impedance.setter
    def load_impedance(self, value):
        self._input_parameters.load_impedance = value
        self._refresh_model()

    @property
    def boom_spacing(self):
        """Spacing between the two booms."""
        return self._input_parameters.boom_spacing

    @boom_spacing.setter
    def boom_spacing(self, value):
        self._input_parameters.boom_spacing = value
        self._refresh_model()

    @property
    def tau_ratio(self):
        """Element scaling ratio."""
        return self._input_parameters.tau_ratio

    @tau_ratio.setter
    def tau_ratio(self, value):
        self._input_parameters.tau_ratio = value
        self._refresh_model()

    @property
    def sigma_ratio(self):
        """Element spacing ratio."""
        return self._input_parameters.sigma_ratio

    @sigma_ratio.setter
    def sigma_ratio(self, value):
        self._input_parameters.sigma_ratio = value
        self._refresh_model()

    @property
    def base_element_length(self):
        """Length of the longest element."""
        return self._input_parameters.base_element_length

    @base_element_length.setter
    def base_element_length(self, value):
        self._input_parameters.base_element_length = value
        self._refresh_model()

    @property
    def base_element_radius(self):
        """Radius of each dipole element."""
        return self._input_parameters.base_element_radius

    @base_element_radius.setter
    def base_element_radius(self, value):
        self._input_parameters.base_element_radius = value
        self._refresh_model()

    @property
    def number_of_elements(self):
        """Number of dipole elements."""
        return self._input_parameters.number_of_elements

    @number_of_elements.setter
    def number_of_elements(self, value):
        self._input_parameters.number_of_elements = value
        self._refresh_model()

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class LogPeriodicArray(CommonLogPeriodic):
    """Manages a log periodic dipole array antenna."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 5.05,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
        "gain": 10.0,
        "input_resistance": 100.0,
        "load_impedance": 118.7921,
        "boom_spacing": 0.22693,
        "tau_ratio": 0.9265,
        "sigma_ratio": 0.198,
        "base_element_length": 32.98,
        "base_element_radius": 0.093165,
        "number_of_elements": 8,
    }

    def __init__(self, *args, **kwargs):
        CommonLogPeriodic.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "LogPeriodicArray"

    @staticmethod
    def _find_tau_sigma(directivity):
        directivity = min(max(directivity, 7.0), 11.0)
        if 7.0 <= directivity < 7.5:
            tau = 0.78 + (directivity - 7.0) / 0.5 * 0.044
        elif 7.5 <= directivity < 8.0:
            tau = 0.824 + (directivity - 7.5) / 0.5 * 0.041
        elif 8.0 <= directivity < 8.5:
            tau = 0.865 + (directivity - 8.0) / 0.5 * 0.03
        elif 8.5 <= directivity < 9.0:
            tau = 0.895 + (directivity - 8.5) / 0.5 * 0.022
        elif 9.0 <= directivity < 9.5:
            tau = 0.917 + (directivity - 9.0) / 0.5 * 0.008
        elif 9.5 <= directivity < 10.0:
            tau = 0.925 + (directivity - 9.5) / 0.5 * 0.017
        elif 10.0 <= directivity < 10.5:
            tau = 0.942 + (directivity - 10.0) / 0.5 * 0.013
        else:
            tau = 0.955 + (directivity - 10.5) / 0.5 * 0.012
        sigma = 0.237838 * tau - 0.047484
        return tau, sigma

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}

        tau_ratio = self.tau_ratio
        sigma_ratio = self.sigma_ratio
        if tau_ratio <= 0.0:
            tau_ratio, sigma_ratio = self._find_tau_sigma(self.gain or 10.0)

        number_of_elements = max(int(round(self.number_of_elements)), 2)
        base_element_length = self.base_element_length
        base_element_radius = self.base_element_radius

        if base_element_length <= 0.0:
            base_element_length = 32.98
        if base_element_radius <= 0.0:
            base_element_radius = base_element_length * 0.0028255

        if math.isclose(1.0 - tau_ratio, 0.0):
            s_feed = base_element_radius + 2 * sigma_ratio * tau_ratio * base_element_length * (number_of_elements - 1)
        else:
            s_feed = base_element_radius + 2 * sigma_ratio * tau_ratio * base_element_length * (
                (1 - tau_ratio ** (number_of_elements - 1)) / (1 - tau_ratio)
            )
        r_wire = base_element_radius * tau_ratio ** ((number_of_elements - 1) / 2.0)

        parameters["base_element_length"] = base_element_length
        parameters["base_element_radius"] = base_element_radius
        parameters["boom_spacing"] = self.boom_spacing
        parameters["input_resistance"] = self.input_resistance
        parameters["load_impedance"] = self.load_impedance
        parameters["number_of_elements"] = number_of_elements
        parameters["tau_ratio"] = tau_ratio
        parameters["sigma_ratio"] = sigma_ratio
        parameters["r_wire"] = r_wire
        parameters["s_feed"] = s_feed
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a log periodic dipole array antenna."""
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        antenna_name = self.name
        coordinate_system = self.coordinate_system
        self._app.modeler.set_working_coordinate_system(coordinate_system)

        base_element_length = self.synthesis_parameters.base_element_length.hfss_variable
        base_element_radius = self.synthesis_parameters.base_element_radius.hfss_variable
        boom_spacing = self.synthesis_parameters.boom_spacing.hfss_variable
        tau_ratio = self.synthesis_parameters.tau_ratio.hfss_variable
        sigma_ratio = self.synthesis_parameters.sigma_ratio.hfss_variable
        r_wire = self.synthesis_parameters.r_wire.hfss_variable
        s_feed = self.synthesis_parameters.s_feed.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        number_of_elements = max(int(round(self.synthesis_parameters.number_of_elements.value)), 2)

        upper_boom = self._app.modeler.create_cylinder(
            orientation=Axis.X,
            origin=["-" + base_element_radius, boom_spacing + "/2", "0"],
            radius=r_wire,
            height=s_feed + "+" + base_element_radius,
            name="upper_boom_" + antenna_name,
            material=self.material,
        )
        lower_boom = self._app.modeler.create_cylinder(
            orientation=Axis.X,
            origin=["-" + base_element_radius, "-" + boom_spacing + "/2", "0"],
            radius=r_wire,
            height=s_feed + "+" + base_element_radius,
            name="lower_boom_" + antenna_name,
            material=self.material,
        )

        upper_boom.color = (255, 128, 65)
        lower_boom.color = (255, 128, 65)

        upper_parts = [upper_boom.name]
        lower_parts = [lower_boom.name]
        total_x_position = "0"
        for idx in range(number_of_elements):
            if idx > 0:
                total_x_position += "+2*{}*{}^({})*{}".format(sigma_ratio, tau_ratio, idx, base_element_length)

            half_length = "0.5*{}^({})*{}".format(tau_ratio, idx, base_element_length)
            if idx == 0:
                half_length = "0.5*{}".format(base_element_length)

            upper_height = half_length
            lower_height = "-" + half_length
            if idx % 2 == 0:
                upper_height, lower_height = lower_height, half_length

            upper_element = self._app.modeler.create_cylinder(
                orientation=Axis.Z,
                origin=[total_x_position, boom_spacing + "/2", "0"],
                radius=base_element_radius,
                height=upper_height,
                name="upper_element_{}_{}".format(idx, antenna_name),
                material=self.material,
            )
            lower_element = self._app.modeler.create_cylinder(
                orientation=Axis.Z,
                origin=[total_x_position, "-" + boom_spacing + "/2", "0"],
                radius=base_element_radius,
                height=lower_height,
                name="lower_element_{}_{}".format(idx, antenna_name),
                material=self.material,
            )
            upper_parts.append(upper_element.name)
            lower_parts.append(lower_element.name)

        self._app.modeler.unite(upper_parts)
        self._app.modeler.unite(lower_parts)

        upper_boom = self._app.modeler[upper_boom.name]
        lower_boom = self._app.modeler[lower_boom.name]

        feed_sheet = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[s_feed, "-" + boom_spacing + "/2", "-" + r_wire],
            sizes=[boom_spacing, "2*" + r_wire],
            name="port_lump_" + antenna_name,
            material="vacuum",
            is_covered=True,
        )
        feed_sheet.color = (128, 0, 0)

        load_sheet = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=["-" + base_element_radius, "-" + boom_spacing + "/2", "-" + r_wire],
            sizes=[boom_spacing, "2*" + r_wire],
            name="load_sheet_" + antenna_name,
            material="vacuum",
            is_covered=True,
        )
        load_sheet.color = (128, 0, 0)

        for obj in [upper_boom, lower_boom, feed_sheet, load_sheet]:
            obj.group_name = antenna_name
            self.object_list[obj.name] = obj

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        return True

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Set up a log periodic dipole array antenna in HFSS."""
        feed_name = "port_lump_" + self.name
        load_name = "load_sheet_" + self.name

        feed_sheet = self.object_list[feed_name]
        terminal_references = []
        for obj_name in feed_sheet.touching_objects:
            if obj_name in self.object_list and obj_name not in [feed_name, load_name]:
                terminal_references.append(obj_name)

        port = self._app.lumped_port(
            assignment=feed_name,
            reference=terminal_references,
            impedance=self.synthesis_parameters.input_resistance.hfss_variable,
            name="port_" + self.name + "_1",
            renormalize=True,
            deembed=False,
        )
        self.excitations[port.name] = port

        if self._app.solution_type == "Terminal":
            self._CommonAntenna__excitation_type = "Terminal_Lumped"
        else:
            self._app.solution_type = "Modal_Lumped"

        load_line = [
            [
                self.origin[0] - self.synthesis_parameters.base_element_radius.value,
                self.origin[1] - self.synthesis_parameters.boom_spacing.value / 2.0,
                self.origin[2],
            ],
            [
                self.origin[0] - self.synthesis_parameters.base_element_radius.value,
                self.origin[1] + self.synthesis_parameters.boom_spacing.value / 2.0,
                self.origin[2],
            ],
        ]
        load = self._app.assign_lumped_rlc_to_sheet(
            assignment=load_name,
            start_direction=load_line,
            name="load_" + self.name,
            resistance=self.synthesis_parameters.load_impedance.hfss_variable,
        )
        self.boundaries[load.name] = load
        return True
