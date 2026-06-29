# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

from collections import OrderedDict
import math

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import TransmissionLine
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import CommonPatch


class PlanarDipole(CommonPatch):
    """Manages a planar dipole antenna.

    Notes
    -----
    .. [1] C. Balanis, "Linear Wire Antennas"
        *Antenna Theory*, New York, 1997.
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "Teflon (tm)",
        "material_properties": {"permittivity": 2.1},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "PlanarDipole"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = light_speed / freq_hz

        if self._app and (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            mat_props = self._app.materials[self.material]
            permittivity = mat_props.permittivity.value
            self._input_parameters.material_properties["permittivity"] = permittivity
        elif self.material_properties:
            permittivity = self.material_properties["permittivity"]
        else:
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
            return parameters

        sub_permittivity = float(permittivity)
        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")

        tl = TransmissionLine(self.frequency, self.frequency_unit)
        eff_permittivity = tl.suspended_strip_calculator(wavelength, wavelength / 80.0, sub_meters, sub_permittivity)
        eff_wl_meters = wavelength / math.sqrt(eff_permittivity)
        eff_wl_working_units = constants.unit_converter(eff_wl_meters, output_units=self.length_unit)
        correction_factor = 0.92

        parameters["dipole_length"] = round(correction_factor * eff_wl_working_units / 2.0, 2)
        parameters["dipole_width"] = round(correction_factor * eff_wl_working_units / 80.0, 2)
        parameters["feed_gap_width"] = round(correction_factor * eff_wl_working_units / 80.0, 2)
        parameters["sub_x"] = round(correction_factor * 0.75 * eff_wl_working_units, 1)
        parameters["sub_y"] = round(correction_factor * eff_wl_working_units, 1)
        parameters["sub_h"] = self.substrate_height
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a planar dipole antenna."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        dipole_length = self.synthesis_parameters.dipole_length.hfss_variable
        dipole_width = self.synthesis_parameters.dipole_width.hfss_variable
        feed_gap_width = self.synthesis_parameters.feed_gap_width.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "-" + sub_h],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        ant = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=["-" + dipole_width + "/2", feed_gap_width + "/2", 0.0],
            sizes=[dipole_width, dipole_length + "/2-" + feed_gap_width + "/2"],
            name="ant_arm",
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1

        ant2_name = ant.duplicate_around_axis(Axis.Z, 180, 2)[0]
        ant2 = self._app.modeler[ant2_name]
        ant2.transparency = 0.1

        port = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=["-" + dipole_width + "/2", "-" + feed_gap_width + "/2", 0.0],
            sizes=[dipole_width, feed_gap_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        sub.group_name = antenna_name
        ant.group_name = antenna_name
        ant2.group_name = antenna_name
        port.group_name = antenna_name

        self.object_list[sub.name] = sub
        self.object_list[ant.name] = ant
        self.object_list[ant2.name] = ant2
        self.object_list[port.name] = port
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemented."""
        pass


class WireDipole(CommonAntenna):
    """Manages a wire dipole antenna.

    Notes
    -----
    .. [1] C. Balanis, "Linear Wire Antennas"
        *Antenna Theory*, New York, 1997.
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonAntenna.antenna_type = "Dipole"
        CommonAntenna.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "WireDipole"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = constants.unit_converter(light_speed / freq_hz, "Length", "meter", self.length_unit)

        parameters["dipole_length"] = round(0.45 * wavelength, 2)
        parameters["port_gap"] = round(0.0075 * wavelength, 3)
        parameters["wire_rad"] = round(0.0075 * wavelength, 3)
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a wire dipole antenna."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        self.set_variables_in_hfss()

        dipole_length = self.synthesis_parameters.dipole_length.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        wire_rad = self.synthesis_parameters.wire_rad.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        wire = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0.0, 0.0, port_gap + "/2"],
            radius=wire_rad,
            height=dipole_length + "/2-" + port_gap + "/2",
            name="wire_arm",
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        wire.color = (255, 128, 65)

        wire2_name = wire.duplicate_around_axis(Axis.X, 180, 2)[0]
        wire2 = self._app.modeler[wire2_name]
        wire2.color = (255, 128, 65)

        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0.0, "-" + wire_rad, "-" + port_gap + "/2"],
            sizes=["2*" + wire_rad, port_gap],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        wire.group_name = antenna_name
        wire2.group_name = antenna_name
        port.group_name = antenna_name

        self.object_list[wire.name] = wire
        self.object_list[wire2.name] = wire2
        self.object_list[port.name] = port
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemented."""
        pass
