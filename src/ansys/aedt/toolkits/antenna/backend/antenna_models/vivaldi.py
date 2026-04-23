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
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import CommonPatch
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonVivaldi(CommonPatch):
    """Provides base methods common to the Vivaldi antenna family."""

    _point_parameter_name = "number_of_points"
    _point_count = 20
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 14.5,
        "frequency_unit": "GHz",
        "start_frequency": 8.0,
        "stop_frequency": 21.0,
        "feeder_length": 0.0,
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, default_input_parameters=None, *args, **kwargs):
        if default_input_parameters is None:
            default_input_parameters = self._default_input_parameters
        CommonPatch.__init__(self, default_input_parameters, *args, **kwargs)
        self._sync_center_frequency()
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)

    @property
    def start_frequency(self):
        """Lower edge of the operating band."""
        return self._input_parameters.start_frequency

    @start_frequency.setter
    def start_frequency(self, value):
        self._input_parameters.start_frequency = value
        self._sync_center_frequency()
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    @property
    def stop_frequency(self):
        """Upper edge of the operating band."""
        return self._input_parameters.stop_frequency

    @stop_frequency.setter
    def stop_frequency(self, value):
        self._input_parameters.stop_frequency = value
        self._sync_center_frequency()
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    @property
    def feeder_length(self):
        """Feed section length before the taper starts."""
        return self._input_parameters.feeder_length

    @feeder_length.setter
    def feeder_length(self, value):
        self._input_parameters.feeder_length = value
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    def _sync_center_frequency(self):
        self._input_parameters.frequency = (self.start_frequency + self.stop_frequency) / 2.0

    def _get_material_permittivity(self):
        if self._app and (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            mat_props = self._app.materials[self.material]
            permittivity = mat_props.permittivity.value
            self._input_parameters.material_properties["permittivity"] = permittivity
            return float(permittivity)
        if self.material_properties:
            return float(self.material_properties["permittivity"])
        if self._app:
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
        return None

    def _point_count_value(self):
        point_count = getattr(self.synthesis_parameters, self._point_parameter_name).value
        return max(2, int(round(float(point_count))))

    def _taper_points(self, stepped=False):
        point_count = self._point_count_value()
        total_length = self.synthesis_parameters.sub_y.hfss_variable
        taper_length = self.synthesis_parameters.taper_length.hfss_variable
        taper_start = f"{total_length}-{taper_length}"
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        taper_width = self.synthesis_parameters.taper_width.hfss_variable

        def y_expr(x_expr):
            return (
                f"{taper_width}/2*exp((-log({slot_width}/{taper_width})/{taper_length})*((({x_expr})-{total_length})))"
            )

        x_points = [f"{taper_start}+{idx}*{taper_length}/{point_count}" for idx in range(point_count + 1)]

        if stepped:
            points = []
            for idx in range(point_count, 0, -1):
                points.append([x_points[idx], y_expr(x_points[idx]), "0"])
                points.append([x_points[idx - 1], y_expr(x_points[idx]), "0"])
        else:
            points = [[x_points[idx], y_expr(x_points[idx]), "0"] for idx in range(point_count, -1, -1)]

        points.extend(
            [
                [taper_start, "0", "0"],
                [total_length, "0", "0"],
                [total_length, y_expr(total_length), "0"],
            ]
        )
        points.append(points[0])
        return points

    def _create_vivaldi_conductor(self, name, elevation, coordinate_system, stepped=False):
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        feeder_length = self.synthesis_parameters.feeder_length.hfss_variable
        taper_length = self.synthesis_parameters.taper_length.hfss_variable
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        balun_width = self.synthesis_parameters.balun_width.hfss_variable
        balun_length = self.synthesis_parameters.balun_length.hfss_variable
        total_length = sub_y
        feed_start = f"{total_length}-{taper_length}-{feeder_length}"
        balun_start = f"{feed_start}-{balun_length}"

        conductor = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=["0", f"-{sub_x}/2", elevation],
            sizes=[sub_y, sub_x],
            name=name,
            new_properties={"Coordinate System": coordinate_system},
        )

        slot_half = self._app.modeler.create_polyline(
            self._taper_points(stepped=stepped),
            cover_surface=True,
            name=f"{name}_slot_half",
        )

        tool_objects = [slot_half.name]

        if self.feeder_length > 0:
            feed = self._app.modeler.create_rectangle(
                orientation=Plane.XY,
                origin=[feed_start, "0", elevation],
                sizes=[feeder_length, f"{slot_width}/2"],
                name=f"{name}_feed_half",
                new_properties={"Coordinate System": coordinate_system},
            )
            tool_objects.append(feed.name)

        balun = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=[balun_start, "0", elevation],
            sizes=[balun_length, f"{balun_width}/2"],
            name=f"{name}_balun_half",
            new_properties={"Coordinate System": coordinate_system},
        )
        tool_objects.append(balun.name)

        if len(tool_objects) > 1:
            self._app.modeler.unite(tool_objects)

        mirrored = self._app.modeler.duplicate_and_mirror(slot_half, origin=[0, 0, 0], vector=[0, 1, 0])
        mirror_name = mirrored[0] if mirrored else None
        if mirror_name:
            self._app.modeler.unite([slot_half.name, mirror_name])

        self._app.modeler.subtract(blank_list=[conductor.name], tool_list=[slot_half.name], keep_originals=False)
        return conductor

    def _create_stripline(self, name, coordinate_system):
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        stripline_width = self.synthesis_parameters.stripline_width.hfss_variable
        stripline_length = self.synthesis_parameters.stripline_length.hfss_variable
        stripline_offset = self.synthesis_parameters.stripline_offset.hfss_variable
        taper_length = self.synthesis_parameters.taper_length.hfss_variable
        feeder_length = self.synthesis_parameters.feeder_length.hfss_variable
        total_length = self.synthesis_parameters.sub_y.hfss_variable
        feed_offset = self.synthesis_parameters.feed_offset.hfss_variable
        feed_start = f"{total_length}-{taper_length}-{feeder_length}+{feed_offset}"

        stripline = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=["0", f"-{stripline_length}", f"{sub_h}/2"],
            sizes=[feed_start, stripline_width],
            name=name,
            new_properties={"Coordinate System": coordinate_system},
        )
        stripline_leg = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=[feed_start, f"-{stripline_length}", f"{sub_h}/2"],
            sizes=[stripline_width, stripline_length],
            name=f"{name}_leg",
            new_properties={"Coordinate System": coordinate_system},
        )
        parts = [stripline.name, stripline_leg.name]

        if float(self.synthesis_parameters.stripline_offset.value) > 0:
            stripline_offset_part = self._app.modeler.create_rectangle(
                orientation=Plane.XY,
                origin=[feed_start, "0", f"{sub_h}/2"],
                sizes=[stripline_width, stripline_offset],
                name=f"{name}_offset",
                new_properties={"Coordinate System": coordinate_system},
            )
            parts.append(stripline_offset_part.name)

        if len(parts) > 1:
            self._app.modeler.unite(parts)
        return stripline

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        permittivity = self._get_material_permittivity()
        if permittivity is None:
            return parameters

        freqlo_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        freqhi_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")
        freqmid_hz = (freqhi_hz - freqlo_hz) / 2.0 + freqlo_hz
        light_speed = constants.SpeedOfLight
        wl_meters_low = light_speed / freqlo_hz
        wl_meters_mid = light_speed / freqmid_hz

        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        stripline_width = self._transmission_line_calculator.stripline_calculator(
            sub_meters, permittivity, impedance=50.0
        )
        slot_width = max(stripline_width / 4.33, stripline_width * 0.2)

        length_unit = self.length_unit
        mid_quarter_guided = wl_meters_mid / math.sqrt(permittivity) / 4.0
        extra_length = constants.unit_converter(5.0, "Length", "mm", "meter")

        parameters["slot_width"] = constants.unit_converter(slot_width, "Length", "meter", length_unit)
        parameters["feeder_length"] = self.feeder_length
        parameters["taper_width"] = constants.unit_converter(wl_meters_low / 2.0, "Length", "meter", length_unit)
        parameters["taper_length"] = constants.unit_converter(wl_meters_low, "Length", "meter", length_unit)
        parameters["balun_width"] = constants.unit_converter(mid_quarter_guided, "Length", "meter", length_unit)
        parameters["balun_length"] = constants.unit_converter(mid_quarter_guided, "Length", "meter", length_unit)
        parameters[self._point_parameter_name] = self._point_count
        parameters["stripline_width"] = constants.unit_converter(stripline_width, "Length", "meter", length_unit)
        parameters["stripline_length"] = constants.unit_converter(
            mid_quarter_guided * 1.4, "Length", "meter", length_unit
        )
        parameters["stripline_offset"] = constants.unit_converter(mid_quarter_guided, "Length", "meter", length_unit)
        parameters["feed_offset"] = 0.0
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(wl_meters_low, "Length", "meter", length_unit)
        parameters["sub_y"] = constants.unit_converter(
            wl_meters_low + mid_quarter_guided + extra_length, "Length", "meter", length_unit
        )
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict((i, parameters[i]) for i in my_keys)

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a Vivaldi antenna."""
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss(not_used=[self._point_parameter_name + "_" + self.name])

        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        stripline_width = self.synthesis_parameters.stripline_width.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["0", f"-{sub_x}/2", "0"],
            sizes=[sub_y, sub_x, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        ant_bottom = self._create_vivaldi_conductor(
            name="ant_bottom_" + antenna_name,
            elevation="0",
            coordinate_system=coordinate_system,
            stepped=self._point_parameter_name == "number_of_steps",
        )
        ant_bottom.color = (255, 128, 65)
        ant_bottom.transparency = 0.1

        ant_top = self._create_vivaldi_conductor(
            name="ant_top_" + antenna_name,
            elevation=sub_h,
            coordinate_system=coordinate_system,
            stepped=self._point_parameter_name == "number_of_steps",
        )
        ant_top.color = (255, 128, 65)
        ant_top.transparency = 0.1

        stripline = self._create_stripline("ant_stripline_" + antenna_name, coordinate_system)
        stripline.color = (255, 128, 65)
        stripline.transparency = 0.1

        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=["0", f"-{sub_x}/2", "0"],
            sizes=[f"{sub_x}/2", sub_h],
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        port_cap = self._app.modeler.create_box(
            origin=[f"-{stripline_width}/10", f"-{sub_x}/2", "0"],
            sizes=[f"{stripline_width}/10", f"{sub_x}/2", sub_h],
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (255, 128, 65)
        port_cap.transparency = 0.1

        self.object_list[sub.name] = sub
        self.object_list[ant_bottom.name] = ant_bottom
        self.object_list[ant_top.name] = ant_top
        self.object_list[stripline.name] = stripline
        self.object_list[port.name] = port
        self.object_list[port_cap.name] = port_cap

        for antenna_object in self.object_list.values():
            antenna_object.group_name = antenna_name

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        return True

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Set up a Vivaldi antenna in HFSS."""
        for obj_name in ("ant_bottom_" + self.name, "ant_top_" + self.name, "ant_stripline_" + self.name):
            bound = self._app.assign_perfecte_to_sheets(obj_name)
            bound.name = "PerfE_" + obj_name
            self.boundaries[bound.name] = bound

        self._app.solution_type = "Terminal"
        port = self._app.wave_port(
            assignment="port_" + self.name,
            reference="port_cap_" + self.name,
            name="port_" + self.name + "_1",
        )
        self.excitations[port.name] = port
        return True


class Vivaldi(CommonVivaldi):
    """Manages a continuous Vivaldi antenna."""

    def __init__(self, *args, **kwargs):
        CommonVivaldi.__init__(self, self._default_input_parameters, *args, **kwargs)
        self.antenna_type = "Vivaldi"


class VivaldiStepped(CommonVivaldi):
    """Manages a stepped Vivaldi antenna."""

    _point_parameter_name = "number_of_steps"
    _point_count = 20

    def __init__(self, *args, **kwargs):
        CommonVivaldi.__init__(self, self._default_input_parameters, *args, **kwargs)
        self.antenna_type = "VivaldiStepped"
