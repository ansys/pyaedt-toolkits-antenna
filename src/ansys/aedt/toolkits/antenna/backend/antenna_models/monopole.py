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

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna


class CommonMonopole(CommonAntenna):
    """Provides base methods common to monopole antennas."""

    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Monopole"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)

    def _length_value(self, value, unit="meter"):
        return constants.unit_converter(value, "Length", unit, self.length_unit)

    def _sorted_parameters(self, parameters):
        keys = list(parameters.keys())
        keys.sort()
        return OrderedDict((key, parameters[key]) for key in keys)

    def _set_object_properties(self, obj, color, transparency, group_name):
        obj.color = color
        obj.transparency = transparency
        obj.group_name = group_name
        try:
            obj.history().properties["Coordinate System"] = self.coordinate_system
        except Exception:
            pass

    def _finalize_objects(self, objects):
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        self._app.modeler.move(list(objects), [pos_x, pos_y, pos_z])
        return True

    def _ground_thickness(self, dimension):
        return f"{dimension}/50"


class BladeAntenna(CommonMonopole):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.2,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMonopole.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "BladeAntenna"

    @pyaedt_function_handler()
    def synthesis(self):
        scale = 1.2 / constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        parameters = {
            "flare_angle": 40.0,
            "width_blade_base": 23.6 * scale,
            "width_blade_top": 14.7 * scale,
            "height_blade": 36.3 * scale,
            "thickness_blade": 0.2 * scale,
            "width_feed_base": 5.7 * scale,
            "width_feed_top": 5.7 * scale,
            "height_feed": 5.5 * scale,
            "spacing_feed": 0.0,
            "height_port": 1.0 * scale,
            "spacing_port": 0.0,
            "width_slot_1": 4.8 * scale,
            "height_slot_1": 9.1 * scale,
            "width_slot_2": 15.8 * scale,
            "height_slot_2": 18.0 * scale,
            "width_slot_3": 11.7 * scale,
            "height_slot_3": 27.2 * scale,
            "thickness_slot": 0.858 * scale,
            "ground_x": 160.0 * scale,
            "ground_y": 200.0 * scale,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return self._sorted_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            return False

        self.set_variables_in_hfss()
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        flare_angle = self.synthesis_parameters.flare_angle.hfss_variable
        width_blade_base = self.synthesis_parameters.width_blade_base.hfss_variable
        width_blade_top = self.synthesis_parameters.width_blade_top.hfss_variable
        height_blade = self.synthesis_parameters.height_blade.hfss_variable
        thickness_blade = self.synthesis_parameters.thickness_blade.hfss_variable
        width_feed_base = self.synthesis_parameters.width_feed_base.hfss_variable
        width_feed_top = self.synthesis_parameters.width_feed_top.hfss_variable
        height_feed = self.synthesis_parameters.height_feed.hfss_variable
        spacing_feed = self.synthesis_parameters.spacing_feed.hfss_variable
        height_port = self.synthesis_parameters.height_port.hfss_variable
        spacing_port = self.synthesis_parameters.spacing_port.hfss_variable
        width_slot_1 = self.synthesis_parameters.width_slot_1.hfss_variable
        height_slot_1 = self.synthesis_parameters.height_slot_1.hfss_variable
        width_slot_2 = self.synthesis_parameters.width_slot_2.hfss_variable
        height_slot_2 = self.synthesis_parameters.height_slot_2.hfss_variable
        width_slot_3 = self.synthesis_parameters.width_slot_3.hfss_variable
        height_slot_3 = self.synthesis_parameters.height_slot_3.hfss_variable
        thickness_slot = self.synthesis_parameters.thickness_slot.hfss_variable
        ground_x = self.synthesis_parameters.ground_x.hfss_variable
        ground_y = self.synthesis_parameters.ground_y.hfss_variable

        blade_points = [
            [0, 0, height_feed],
            [0, width_blade_base, height_feed],
            [0, f"{height_blade}*tan({flare_angle})+{width_blade_top}", f"{height_feed}+{height_blade}"],
            [0, f"{height_blade}*tan({flare_angle})", f"{height_feed}+{height_blade}"],
            [0, 0, height_feed],
        ]
        blade_sheet = self._app.modeler.create_polyline(blade_points, cover_surface=True, close_surface=True)

        # Set coordinate system of polyline
        blade_sheet_obj = self._app.get_oo_object(self._app.oeditor, blade_sheet.name)
        self._app.set_oo_property_value(
            aedt_object=blade_sheet_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        feed_points = [
            [0, f"abs({spacing_feed})+({width_feed_top}/2)-({width_feed_base}/2)", 0],
            [0, f"abs({spacing_feed})+({width_feed_top}/2)+({width_feed_base}/2)", 0],
            [0, f"abs({spacing_feed})+{width_feed_top}", height_feed],
            [0, f"abs({spacing_feed})", height_feed],
            [0, f"abs({spacing_feed})+({width_feed_top}/2)-({width_feed_base}/2)", 0],
        ]
        feed_sheet = self._app.modeler.create_polyline(feed_points, cover_surface=True, close_surface=True)

        # Set coordinate system of polyline
        feed_sheet_obj = self._app.get_oo_object(self._app.oeditor, feed_sheet.name)
        self._app.set_oo_property_value(
            aedt_object=feed_sheet_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        blade_sheet.unite(feed_sheet)

        slot_1 = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[
                0,
                f"{height_slot_1}*tan({flare_angle})-{width_slot_1}",
                f"{height_feed}+{height_slot_1}-{thickness_slot}/2",
            ],
            sizes=[f"2*{width_slot_1}", thickness_slot],
            new_properties={"Coordinate System": coordinate_system},
        )
        right_slope = f"abs({width_blade_base}-({height_blade}*tan({flare_angle})+{width_blade_top}))/{height_blade}"
        slot_2 = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[
                0,
                f"{width_blade_base}+{height_slot_2}*{right_slope}-{width_slot_2}",
                f"{height_feed}+{height_slot_2}-{thickness_slot}/2",
            ],
            sizes=[f"2*{width_slot_2}", thickness_slot],
            new_properties={"Coordinate System": coordinate_system},
        )
        slot_3 = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[
                0,
                f"{height_slot_3}*tan({flare_angle})-{width_slot_3}",
                f"{height_feed}+{height_slot_3}-{thickness_slot}/2",
            ],
            sizes=[f"2*{width_slot_3}", thickness_slot],
            new_properties={"Coordinate System": coordinate_system},
        )
        blade_sheet.subtract([slot_1, slot_2, slot_3], keep_originals=False)
        antenna = self._app.modeler.thicken_sheet(blade_sheet, thickness_blade, both_sides=True)
        antenna.material_name = self.material
        antenna.name = f"antenna_{antenna_name}"
        antenna.move([0, 0, height_port])

        ground = self._app.modeler.create_box(
            origin=[f"-{ground_x}/2", f"-{ground_y}/2", f"-{thickness_blade}/2"],
            sizes=[ground_x, ground_y, thickness_blade],
            name=f"ground_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )

        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"abs({spacing_feed})+abs({spacing_port})+({width_feed_top}/2)-({height_port}/4)", 0],
            sizes=[f"{height_port}/2", height_port],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )

        antenna.color = (255, 128, 65)
        antenna.transparency = 0.1
        ground.color = (255, 128, 65)
        ground.transparency = 0.1
        port.color = (255, 128, 65)
        port.transparency = 0.2

        self.object_list[antenna.name] = antenna
        self.object_list[ground.name] = ground
        self.object_list[port.name] = port

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        ground.group_name = antenna_name
        antenna.group_name = antenna_name
        port.group_name = antenna_name
        self._app.modeler.fit_all()

        return True


class CircularDiscMonopole(CommonMonopole):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 0.9,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMonopole.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "CircularDiscMonopole"

    @pyaedt_function_handler()
    def synthesis(self):
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wavelength = constants.SpeedOfLight / constants.unit_converter(
            self.frequency, "Freq", self.frequency_unit, "Hz"
        )
        wavelength = self._length_value(wavelength)
        pin_height = 1.17 / freq_ghz
        pin_diameter = 1.17 / freq_ghz
        parameters = {
            "disc_diameter": 58.5 / freq_ghz,
            "pin_height": pin_height,
            "pin_diameter": pin_diameter,
            "groundplane_width": 0.75 * wavelength,
            "port_gap": pin_height / 20.0,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return self._sorted_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            return False

        self.set_variables_in_hfss()
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        coordinate_system = self.coordinate_system
        antenna_name = self.name
        disc_diameter = self.synthesis_parameters.disc_diameter.hfss_variable
        pin_height = self.synthesis_parameters.pin_height.hfss_variable
        pin_diameter = self.synthesis_parameters.pin_diameter.hfss_variable
        groundplane_width = self.synthesis_parameters.groundplane_width.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable

        pin = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0, 0, port_gap],
            radius=f"{pin_diameter}/2",
            height=f"{pin_height}-{port_gap}",
            name=f"pin_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        disc = self._app.modeler.create_cylinder(
            orientation=Axis.X,
            origin=[f"-{pin_diameter}/2", 0, f"{pin_height}+{disc_diameter}/2"],
            radius=f"{disc_diameter}/2",
            height=pin_diameter,
            name=f"disc_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        antenna = pin.unite(disc)
        antenna.name = f"antenna_{antenna_name}"

        ground = self._app.modeler.create_box(
            origin=[
                f"-{groundplane_width}/2",
                f"-{groundplane_width}/2",
                f"-{self._ground_thickness(groundplane_width)}",
            ],
            sizes=[groundplane_width, groundplane_width, self._ground_thickness(groundplane_width)],
            name=f"ground_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"-{pin_diameter}/2", 0],
            sizes=[pin_diameter, port_gap],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )

        antenna.color = (255, 128, 65)
        antenna.transparency = 0.1
        ground.color = (255, 128, 65)
        ground.transparency = 0.1
        port.color = (255, 128, 65)
        port.transparency = 0.2

        self.object_list[antenna.name] = antenna
        self.object_list[ground.name] = ground
        self.object_list[port.name] = port

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        ground.group_name = antenna_name
        antenna.group_name = antenna_name
        port.group_name = antenna_name
        self._app.modeler.fit_all()

        return True


class EllipticalBaseStripMonopole(CommonMonopole):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 0.9,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMonopole.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "EllipticalBaseStripMonopole"

    @pyaedt_function_handler()
    def synthesis(self):
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wavelength = constants.SpeedOfLight / constants.unit_converter(
            self.frequency, "Freq", self.frequency_unit, "Hz"
        )
        wavelength = self._length_value(wavelength)
        strip_width = 54.855 / freq_ghz
        pin_height = 1.4628 / freq_ghz
        parameters = {
            "strip_height": 54.855 / freq_ghz,
            "strip_width": strip_width,
            "base_height": 0.5 * strip_width,
            "pin_height": pin_height,
            "pin_diameter": 1.4628 / freq_ghz,
            "feed_gap": pin_height / 20.0,
            "groundplane_width": 0.75 * wavelength,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return self._sorted_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            return False

        self.set_variables_in_hfss()
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        coordinate_system = self.coordinate_system
        antenna_name = self.name

        strip_height = self.synthesis_parameters.strip_height.hfss_variable
        strip_width = self.synthesis_parameters.strip_width.hfss_variable
        base_height = self.synthesis_parameters.base_height.hfss_variable
        pin_height = self.synthesis_parameters.pin_height.hfss_variable
        pin_diameter = self.synthesis_parameters.pin_diameter.hfss_variable
        feed_gap = self.synthesis_parameters.feed_gap.hfss_variable
        groundplane_width = self.synthesis_parameters.groundplane_width.hfss_variable

        feed_pin = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0, 0, feed_gap],
            radius=f"{pin_diameter}/2",
            height=f"{pin_height}-{feed_gap}",
            name=f"feedpin_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        strip_top = self._app.modeler.create_box(
            origin=[f"-{pin_diameter}/2", f"-{strip_width}/2", f"{pin_height}+{base_height}"],
            sizes=[pin_diameter, strip_width, f"{strip_height}-{base_height}"],
            name=f"striptop_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        strip_base = self._app.modeler.create_ellipse(
            orientation=Plane.YZ,
            origin=[f"-{pin_diameter}/2", 0, f"{pin_height}+{base_height}"],
            major_radius=f"{strip_width}/2",
            ratio=f"2*{base_height}/{strip_width}",
            is_covered=True,
            name=f"stripbase_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        cut_rect = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[f"-{pin_diameter}/2", f"-{strip_width}/2", f"{pin_height}+{base_height}"],
            sizes=[strip_width, f"2*{base_height}"],
            name=f"stripcut_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        strip_base.subtract(cut_rect, keep_originals=False)
        strip_base = strip_base.sweep_along_vector([pin_diameter, 0, 0])
        antenna = strip_base.unite(strip_top)
        antenna.name = f"antenna_{antenna_name}"
        antenna.material_name = self.material

        ground = self._app.modeler.create_box(
            origin=[
                f"-{groundplane_width}/2",
                f"-{groundplane_width}/2",
                f"-{self._ground_thickness(groundplane_width)}",
            ],
            sizes=[groundplane_width, groundplane_width, self._ground_thickness(groundplane_width)],
            name=f"ground_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"-{pin_diameter}/2", 0],
            sizes=[pin_diameter, feed_gap],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )

        antenna.color = (255, 128, 65)
        antenna.transparency = 0.1
        ground.color = (255, 128, 65)
        ground.transparency = 0.1
        port.color = (255, 128, 65)
        port.transparency = 0.2
        feed_pin.color = (255, 128, 65)
        feed_pin.transparency = 0.2

        self.object_list[antenna.name] = antenna
        self.object_list[ground.name] = ground
        self.object_list[port.name] = port
        self.object_list[feed_pin.name] = feed_pin

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        ground.group_name = antenna_name
        antenna.group_name = antenna_name
        port.group_name = antenna_name
        feed_pin.group_name = antenna_name

        self._app.modeler.fit_all()

        return True


class VerticalTrapezoidalMonopole(CommonMonopole):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMonopole.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "VerticalTrapezoidalMonopole"

    @pyaedt_function_handler()
    def synthesis(self):
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wavelength = constants.SpeedOfLight / constants.unit_converter(
            self.frequency, "Freq", self.frequency_unit, "Hz"
        )
        wavelength = self._length_value(wavelength)
        pin_height = 3.358 / freq_ghz
        parameters = {
            "monopole_height": 56.0 / freq_ghz,
            "monopole_top_width": 56.0 / freq_ghz,
            "monopole_base_width": 56.0 / freq_ghz,
            "pin_height": pin_height,
            "pin_radius": 0.6985 / freq_ghz,
            "port_gap": pin_height / 20.0,
            "groundplane_width": 0.75 * wavelength,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return self._sorted_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            return False

        self.set_variables_in_hfss()
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        coordinate_system = self.coordinate_system
        antenna_name = self.name
        monopole_height = self.synthesis_parameters.monopole_height.hfss_variable
        monopole_top_width = self.synthesis_parameters.monopole_top_width.hfss_variable
        monopole_base_width = self.synthesis_parameters.monopole_base_width.hfss_variable
        pin_height = self.synthesis_parameters.pin_height.hfss_variable
        pin_radius = self.synthesis_parameters.pin_radius.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        groundplane_width = self.synthesis_parameters.groundplane_width.hfss_variable

        pin = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0, 0, port_gap],
            radius=pin_radius,
            height=f"{pin_height}-{port_gap}",
            name=f"pin_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        trapezoid = self._app.modeler.create_polyline(
            [
                [f"-{pin_radius}", f"-{monopole_base_width}/2", pin_height],
                [f"-{pin_radius}", f"{monopole_base_width}/2", pin_height],
                [f"-{pin_radius}", f"{monopole_top_width}/2", f"{pin_height}+{monopole_height}"],
                [f"-{pin_radius}", f"-{monopole_top_width}/2", f"{pin_height}+{monopole_height}"],
                [f"-{pin_radius}", f"-{monopole_base_width}/2", pin_height],
            ],
            cover_surface=True,
            close_surface=True,
            name=f"trapezoid_{antenna_name}",
        )

        # Set coordinate system of polyline
        trapezoid_obj = self._app.get_oo_object(self._app.oeditor, trapezoid.name)
        self._app.set_oo_property_value(
            aedt_object=trapezoid_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        trapezoid = trapezoid.sweep_along_vector([f"2*{pin_radius}", 0, 0])
        antenna = pin.unite(trapezoid)
        antenna.name = f"antenna_{antenna_name}"

        ground = self._app.modeler.create_box(
            origin=[
                f"-{groundplane_width}/2",
                f"-{groundplane_width}/2",
                f"-{self._ground_thickness(groundplane_width)}",
            ],
            sizes=[groundplane_width, groundplane_width, self._ground_thickness(groundplane_width)],
            name=f"ground_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"-{pin_radius}", 0],
            sizes=[f"2*{pin_radius}", port_gap],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )

        antenna.color = (255, 128, 65)
        antenna.transparency = 0.1
        ground.color = (255, 128, 65)
        ground.transparency = 0.1
        port.color = (255, 128, 65)
        port.transparency = 0.2

        self.object_list[antenna.name] = antenna
        self.object_list[ground.name] = ground
        self.object_list[port.name] = port

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        ground.group_name = antenna_name
        antenna.group_name = antenna_name
        port.group_name = antenna_name

        self._app.modeler.fit_all()
        return True


class WireMonopole(CommonMonopole):
    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 0.9,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMonopole.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "WireMonopole"

    @pyaedt_function_handler()
    def synthesis(self):
        wavelength = constants.SpeedOfLight / constants.unit_converter(
            self.frequency, "Freq", self.frequency_unit, "Hz"
        )
        wavelength = self._length_value(wavelength)
        correction_factor = 0.893
        port_gap = correction_factor * 0.0075 * wavelength
        parameters = {
            "monopole_length": correction_factor * (0.25 * wavelength - port_gap),
            "wire_rad": correction_factor * 0.0075 * wavelength,
            "port_gap": port_gap,
            "ground_width": correction_factor * 0.75 * wavelength,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return self._sorted_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            return False

        self.set_variables_in_hfss()
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        coordinate_system = self.coordinate_system
        antenna_name = self.name
        monopole_length = self.synthesis_parameters.monopole_length.hfss_variable
        wire_rad = self.synthesis_parameters.wire_rad.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        ground_width = self.synthesis_parameters.ground_width.hfss_variable

        wire = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0, 0, port_gap],
            radius=wire_rad,
            height=f"{monopole_length}-{port_gap}",
            name=f"wire_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        ground = self._app.modeler.create_box(
            origin=[f"-{ground_width}/2", f"-{ground_width}/2", f"-{self._ground_thickness(ground_width)}"],
            sizes=[ground_width, ground_width, self._ground_thickness(ground_width)],
            name=f"ground_{antenna_name}",
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        port = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"-{wire_rad}", 0],
            sizes=[f"2*{wire_rad}", port_gap],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )

        wire.color = (255, 128, 65)
        wire.transparency = 0.1
        ground.color = (255, 128, 65)
        ground.transparency = 0.1
        port.color = (255, 128, 65)
        port.transparency = 0.2

        self.object_list[wire.name] = wire
        self.object_list[ground.name] = ground
        self.object_list[port.name] = port

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        ground.group_name = antenna_name
        wire.group_name = antenna_name
        port.group_name = antenna_name

        self._app.modeler.fit_all()

        return True
