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

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Archimedean as ConicalArchimedean
from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Log as ConicalLog
from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Sinuous as ConicalSinuous
from ansys.aedt.toolkits.common.backend.logger_handler import logger


def _ordered_parameters(parameters):
    parameter_keys = list(parameters.keys())
    parameter_keys.sort()
    return OrderedDict([(i, parameters[i]) for i in parameter_keys])


class _PlanarSpiralCavityMixin:
    _cavity_defaults = {
        "cavity_height": None,
        "cavity_diameter": None,
        "top_absorber_material": "teflon_based",
        "top_absorber_thickness": None,
        "middle_absorber_material": "teflon_based",
        "middle_absorber_thickness": None,
        "bottom_absorber_material": "FR4_epoxy",
        "bottom_absorber_thickness": None,
    }

    def _cavity_parameters(self, outer_radius):
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = constants.SpeedOfLight / start_freq_hz
        wavelength = constants.unit_converter(wavelength, "Length", "meter", self.length_unit)

        cavity_height = self._input_parameters.cavity_height or wavelength / 4.0
        cavity_diameter = self._input_parameters.cavity_diameter or outer_radius * 2.0 * 1.05
        top_absorber_thickness = self._input_parameters.top_absorber_thickness or wavelength / 16.0
        middle_absorber_thickness = self._input_parameters.middle_absorber_thickness or wavelength / 16.0
        bottom_absorber_thickness = self._input_parameters.bottom_absorber_thickness or wavelength / 16.0

        return {
            "bottom_absorber_thickness": bottom_absorber_thickness,
            "cavity_diameter": cavity_diameter,
            "cavity_height": cavity_height,
            "middle_absorber_thickness": middle_absorber_thickness,
            "top_absorber_thickness": top_absorber_thickness,
        }

    def _resolve_material(self, material_name, fallback="vacuum"):
        if (
            material_name in self._app.materials.mat_names_aedt
            or material_name.lower() in self._app.materials.mat_names_aedt_lower
        ):
            return material_name
        logger.warning(f"Material {material_name} not found. Using {fallback} instead.")
        return fallback

    def _add_cavity(self):
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        cavity_height = self.synthesis_parameters.cavity_height.hfss_variable
        cavity_diameter = self.synthesis_parameters.cavity_diameter.hfss_variable
        top_absorber_thickness = self.synthesis_parameters.top_absorber_thickness.hfss_variable
        middle_absorber_thickness = self.synthesis_parameters.middle_absorber_thickness.hfss_variable
        bottom_absorber_thickness = self.synthesis_parameters.bottom_absorber_thickness.hfss_variable

        cavity = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[pos_x, pos_y, pos_z],
            radius=f"{cavity_diameter}/2*1.01",
            height=f"-{cavity_height}*1.01",
            name="gnd_cavity_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        cavity_inner = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[pos_x, pos_y, pos_z],
            radius=f"{cavity_diameter}/2",
            height=f"-{cavity_height}",
            name="cavity_inner_" + self.name,
            material="vacuum",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        self._app.modeler.subtract(blank_list=[cavity.name], tool_list=[cavity_inner.name], keep_originals=False)

        bottom_absorber = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[pos_x, pos_y, f"{pos_z}-{cavity_height}"],
            radius=f"{cavity_diameter}/2",
            height=bottom_absorber_thickness,
            name="bottom_absorber_" + self.name,
            material=self._resolve_material(self._input_parameters.bottom_absorber_material),
            new_properties={"Coordinate System": self.coordinate_system},
        )
        middle_absorber = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[pos_x, pos_y, f"{pos_z}-{cavity_height}+{bottom_absorber_thickness}"],
            radius=f"{cavity_diameter}/2",
            height=middle_absorber_thickness,
            name="middle_absorber_" + self.name,
            material=self._resolve_material(self._input_parameters.middle_absorber_material),
            new_properties={"Coordinate System": self.coordinate_system},
        )
        top_absorber = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[pos_x, pos_y, f"{pos_z}-{cavity_height}+{bottom_absorber_thickness}+{middle_absorber_thickness}"],
            radius=f"{cavity_diameter}/2",
            height=top_absorber_thickness,
            name="top_absorber_" + self.name,
            material=self._resolve_material(self._input_parameters.top_absorber_material),
            new_properties={"Coordinate System": self.coordinate_system},
        )

        for obj in [cavity, bottom_absorber, middle_absorber, top_absorber]:
            obj.group_name = self.name
            self.object_list[obj.name] = obj


class PlanarArchimedean(ConicalArchimedean):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "meter",
        "coordinate_system": "Global",
        "start_frequency": 4.0,
        "stop_frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.antenna_type = "PlanarArchimedean"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")
        center_freq_hz = (stop_freq_hz - start_freq_hz) / 2.0 + start_freq_hz

        light_speed_cm = constants.unit_converter(constants.SpeedOfLight, "Length", "meter", "cm")
        wavelength = constants.SpeedOfLight / center_freq_hz
        wavelength = constants.unit_converter(wavelength, "Length", "meter", self.length_unit)
        outer_radius_cm = light_speed_cm / (2 * math.pi * start_freq_hz)
        inner_radius_cm = light_speed_cm / (2 * math.pi * stop_freq_hz)
        inner_radius = constants.unit_converter(inner_radius_cm, "Length", "cm", self.length_unit)
        turns_number = round((outer_radius_cm - inner_radius_cm) / 2.0 / math.pi / 0.1, 2)
        points = max(32, int(math.ceil(turns_number * 32)))

        parameters["arms_number"] = 2
        parameters["cone_height"] = 0.0
        parameters["expansion_coefficient"] = 1.0
        parameters["inner_rad"] = round(inner_radius, 6)
        parameters["offset_angle"] = 90.0
        parameters["points"] = points
        parameters["port_extension"] = wavelength * 0.01
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]
        parameters["spiral_coefficient"] = 1.0
        parameters["turns_number"] = turns_number

        return _ordered_parameters(parameters)


class PlanarArchimedeanCavity(_PlanarSpiralCavityMixin, PlanarArchimedean):
    _default_input_parameters = {
        **PlanarArchimedean._default_input_parameters,
        **_PlanarSpiralCavityMixin._cavity_defaults,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.antenna_type = "PlanarArchimedeanCavity"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = dict(super().synthesis())
        turns_number = parameters["turns_number"]
        outer_radius = constants.unit_converter(parameters["inner_rad"], "Length", self.length_unit, "cm")
        outer_radius += (
            parameters["expansion_coefficient"]
            * (turns_number * 2 * math.pi) ** (1.0 / parameters["spiral_coefficient"])
            * 1.0e-3
        )
        outer_radius = constants.unit_converter(outer_radius, "Length", "cm", self.length_unit)
        parameters.update(self._cavity_parameters(outer_radius))
        return _ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if not super().model_hfss():
            return False
        self._app.modeler.set_working_coordinate_system(self.coordinate_system)
        self._add_cavity()
        return True


class PlanarLog(ConicalLog):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "meter",
        "coordinate_system": "Global",
        "start_frequency": 4.0,
        "stop_frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.antenna_type = "PlanarLog"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")

        scale_factor = 1.25
        turns_number = 1.25
        light_speed_cm = constants.unit_converter(constants.SpeedOfLight, "Length", "meter", "cm")
        outer_radius_cm = scale_factor * light_speed_cm / (2 * math.pi * start_freq_hz)
        inner_radius_cm = scale_factor * light_speed_cm / (2 * math.pi * stop_freq_hz)
        inner_radius = constants.unit_converter(inner_radius_cm, "Length", "cm", self.length_unit)
        expansion_coefficient = round(math.pow(outer_radius_cm / inner_radius_cm, 1.0 / turns_number), 2)
        points = max(32, int(math.ceil(turns_number * 32)))

        parameters["arms_number"] = 2
        parameters["cone_height"] = 0.0
        parameters["expansion_coefficient"] = expansion_coefficient
        parameters["inner_rad"] = round(inner_radius, 6)
        parameters["offset_angle"] = 90.0
        parameters["points"] = points
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]
        parameters["spiral_coefficient"] = 1.0
        parameters["turns_number"] = turns_number

        return _ordered_parameters(parameters)


class PlanarLogCavity(_PlanarSpiralCavityMixin, PlanarLog):
    _default_input_parameters = {
        **PlanarLog._default_input_parameters,
        **_PlanarSpiralCavityMixin._cavity_defaults,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.antenna_type = "PlanarLogCavity"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = dict(super().synthesis())
        outer_radius = parameters["inner_rad"] * math.exp(
            math.log(parameters["expansion_coefficient"]) * parameters["turns_number"]
        )
        parameters.update(self._cavity_parameters(outer_radius))
        return _ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if not super().model_hfss():
            return False
        self._app.modeler.set_working_coordinate_system(self.coordinate_system)
        self._add_cavity()
        return True


class PlanarSinuous(ConicalSinuous):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "meter",
        "coordinate_system": "Global",
        "start_frequency": 4.0,
        "stop_frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.antenna_type = "PlanarSinuous"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")

        scale_factor = 1.25
        cell_number = 8
        alpha_angle = 45.0
        delta_angle = 22.5
        angle_sum = math.radians(alpha_angle) + math.radians(delta_angle)
        outer_radius = scale_factor * constants.SpeedOfLight / start_freq_hz / 4.0 / angle_sum
        outer_radius = constants.unit_converter(outer_radius, "Length", "meter", self.length_unit)
        inner_radius = scale_factor * constants.SpeedOfLight / stop_freq_hz / 4.0 / 2.0 / angle_sum
        inner_radius = constants.unit_converter(inner_radius, "Length", "meter", self.length_unit)
        port_extension = constants.unit_converter(0.1, "Length", "cm", self.length_unit)

        parameters["alpha_angle"] = alpha_angle
        parameters["arms_number"] = 4
        parameters["cell_number"] = cell_number
        parameters["cone_height"] = 0.0
        parameters["delta_angle"] = delta_angle
        parameters["growth_rate"] = round(math.pow(inner_radius / outer_radius, 1.0 / (cell_number - 1)), 2)
        parameters["outer_rad"] = outer_radius
        parameters["points"] = 200
        parameters["port_extension"] = port_extension
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return _ordered_parameters(parameters)


class PlanarSinuousCavity(_PlanarSpiralCavityMixin, PlanarSinuous):
    _default_input_parameters = {
        **PlanarSinuous._default_input_parameters,
        **_PlanarSpiralCavityMixin._cavity_defaults,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.antenna_type = "PlanarSinuousCavity"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = dict(super().synthesis())
        parameters.update(self._cavity_parameters(parameters["outer_rad"]))
        return _ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if not super().model_hfss():
            return False
        self._app.modeler.set_working_coordinate_system(self.coordinate_system)
        self._add_cavity()
        return True
