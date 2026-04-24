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
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Elliptical
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Pyramidal
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonReflector(CommonAntenna):
    """Provides methods shared by reflector antennas."""

    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Reflector"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)

    @property
    def material(self):
        """Reflector material."""
        return self._input_parameters.material

    @material.setter
    def material(self, value):
        if self._app:
            if (
                value
                and value not in self._app.materials.mat_names_aedt
                and value not in self._app.materials.mat_names_aedt_lower
            ):
                logger.debug("Material not defined")
                return
            for antenna_obj in self.object_list.values():
                if hasattr(antenna_obj, "material_name") and antenna_obj.material_name == self.material.lower():
                    antenna_obj.material_name = value
        self._input_parameters.material = value

    @property
    def feed_type(self):
        """Feed type."""
        return self._input_parameters.feed_type

    @feed_type.setter
    def feed_type(self, value):
        self._input_parameters.feed_type = value

    @property
    def origin(self):
        """Reflector origin."""
        return self._input_parameters.origin

    @origin.setter
    def origin(self, value):
        old_origin = list(self._input_parameters.origin)
        self._input_parameters.origin = value
        if self.object_list:
            delta = [new - old for new, old in zip(value, old_origin)]
            vector = [f"{component}{self.length_unit}" for component in delta]
            self._app.modeler.move(list(self.object_list.keys()), vector)

    def _ordered(self, parameters):
        return OrderedDict((key, parameters[key]) for key in sorted(parameters))

    def _frequency_scale(self):
        frequency_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        if frequency_ghz == 0:
            return 1.0
        return 10.0 / frequency_ghz

    def _cm_value(self, value_cm):
        return constants.unit_converter(value_cm * self._frequency_scale(), "Length", "cm", self.length_unit)

    def _waveguide_name(self):
        return f"feed_{self.name}"

    def _move_to_origin(self, object_names):
        if any(component != 0 for component in self.origin):
            vector = [f"{component}{self.length_unit}" for component in self.origin]
            self._app.modeler.move(object_names, vector)

    def _rotate_and_move(self, object_names, angle=0.0, vector=None):
        if angle:
            self._app.modeler.rotate(object_names, "X", angle)
        if vector:
            move_vector = [f"{component}{self.length_unit}" for component in vector]
            self._app.modeler.move(object_names, move_vector)

    def _add_profile(self, name, points):
        polyline = self._app.modeler.create_polyline(points, name=name)
        self._app.modeler.sweep_around_axis(polyline, "Y")
        return self._app.modeler[name]

    def _trim_with_aperture(self, reflector_name, major_radius, focal_length, offset=0.0, minor_radius=None):
        if not minor_radius:
            minor_radius = major_radius

        aperture = self._app.modeler.create_ellipse(
            orientation="ZX",
            origin=[0.0, 50.0 * focal_length, offset],
            major_radius=major_radius,
            ratio=minor_radius / major_radius,
            name=f"aperture_{reflector_name}",
        )
        self._app.modeler.sweep_along_vector(aperture, [0.0, -100.0 * focal_length, 0.0])
        self._app.modeler.intersect([reflector_name, aperture.name], keep_originals=False)
        return self._app.modeler[reflector_name]

    def _add_primary_reflector(self, major_radius, focal_length, name, offset=0.0, minor_radius=None, samples=24):
        points = []
        for index in range(samples + 1):
            radial_value = major_radius * index / samples
            axial_value = (radial_value**2) / (4.0 * focal_length) - focal_length
            points.append([0.0, axial_value, offset + radial_value])
        reflector = self._add_profile(name, points)
        reflector = self._trim_with_aperture(reflector.name, major_radius, focal_length, offset, minor_radius)
        self.object_list[reflector.name] = reflector
        return reflector

    def _add_cassegrain_subreflector(self, semi_major, semi_minor, focal_shift, radius, name, samples=24):
        points = []
        for index in range(samples + 1):
            radial_value = radius * index / samples
            axial_value = semi_major * math.sqrt(1.0 + (radial_value**2) / max(semi_minor**2, 1e-9))
            points.append([0.0, axial_value - focal_shift, radial_value])
        reflector = self._add_profile(name, points)
        self.object_list[reflector.name] = reflector
        return reflector

    def _add_gregorian_subreflector(self, semi_major, semi_minor, focal_shift, radius, name, samples=24):
        radius = min(radius, max(0.95 * semi_minor, 1e-6))
        points = []
        for index in range(samples + 1):
            radial_value = radius * index / samples
            curve_argument = max(1.0 - (radial_value**2) / max(semi_minor**2, 1e-9), 0.0)
            axial_value = semi_major * math.sqrt(curve_argument)
            points.append([0.0, axial_value - focal_shift, radial_value])
        reflector = self._add_profile(name, points)
        self.object_list[reflector.name] = reflector
        return reflector

    def _feed_rotation(self, offset, focal_length, feed_location):
        return 90.0 - math.degrees(math.atan2(offset, focal_length + feed_location))

    def _feed_position_dual(self, interfocal_distance, swing_angle):
        swing_radians = math.radians(swing_angle)
        return [
            0.0,
            -interfocal_distance * math.cos(swing_radians),
            -interfocal_distance * math.sin(swing_radians),
        ]

    def _create_horn_feed(self, horn_class, angle, position):
        feed = horn_class(
            self._app,
            name=self._waveguide_name(),
            frequency=self.frequency,
            frequency_unit=self.frequency_unit,
            length_unit=self.length_unit,
            material=self.material,
            outer_boundary="",
        )
        feed.init_model()
        feed.model_hfss()
        feed.setup_hfss()
        feed_names = list(feed.object_list.keys())
        self._rotate_and_move(feed_names, angle=angle, vector=position)
        self.object_list.update(feed.object_list)
        self.boundaries.update(feed.boundaries)
        self.excitations.update(feed.excitations)

    def _create_choke_feed(self, angle, position):
        wavelength = constants.SpeedOfLight / constants.unit_converter(
            self.frequency, "Freq", self.frequency_unit, "Hz"
        )
        wavelength_in = constants.unit_converter(wavelength, "Length", "meter", "in")
        wg_length = constants.unit_converter(1.2 * wavelength_in, "Length", "in", self.length_unit)
        wall_thickness = constants.unit_converter(0.04 * wavelength_in, "Length", "in", self.length_unit)
        choke_depth = constants.unit_converter(wavelength_in / 4.0, "Length", "in", self.length_unit)
        wg_radius = constants.unit_converter(
            100.0 / constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz"),
            "Length",
            "mm",
            self.length_unit,
        )
        feed_name = self._waveguide_name()
        waveguide = self._app.modeler.create_cylinder(
            orientation="Y",
            origin=[0.0, -wg_length, 0.0],
            radius=wg_radius + wall_thickness,
            height=wg_length,
            name=f"metal_{feed_name}",
            material=self.material,
        )
        inner_air = self._app.modeler.create_cylinder(
            orientation="Y",
            origin=[0.0, -wg_length, 0.0],
            radius=wg_radius,
            height=wg_length,
            name=f"feed_air_{feed_name}",
            material="vacuum",
        )
        choke = self._app.modeler.create_cylinder(
            orientation="Y",
            origin=[0.0, -choke_depth, 0.0],
            radius=wg_radius + 2.0 * wall_thickness,
            height=choke_depth,
            name=f"choke_{feed_name}",
            material=self.material,
        )
        port = self._app.modeler.create_circle(
            "ZX",
            [0.0, -wg_length, 0.0],
            wg_radius,
            name=f"port_{feed_name}",
            material="vacuum",
        )
        port_cap = self._app.modeler.create_circle(
            "ZX",
            [0.0, -wg_length - wall_thickness / 10.0, 0.0],
            wg_radius,
            name=f"port_cap_{feed_name}",
            material="vacuum",
        )
        object_names = [waveguide.name, inner_air.name, choke.name, port.name, port_cap.name]
        self._rotate_and_move(object_names, angle=angle, vector=position)
        port_excitation = self._app.wave_port(assignment=port, name=f"port_{feed_name}_1")
        self.excitations[port_excitation.name] = port_excitation
        for new_object in [waveguide, inner_air, choke, port, port_cap]:
            self.object_list[new_object.name] = new_object

    def _create_feed(self, angle, position):
        feed_map = {
            "Conical": Conical,
            "Elliptical": Elliptical,
            "Pyramidal": Pyramidal,
        }
        if self.feed_type in feed_map:
            self._create_horn_feed(feed_map[self.feed_type], angle, position)
        else:
            self._create_choke_feed(angle, position)

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Assign reflector boundaries."""
        for object_name, antenna_object in self.object_list.items():
            if (
                object_name.startswith(("reflector_", "subreflector_", "splash_plate_"))
                and antenna_object.object_type == "Sheet"
            ):
                bound = self._app.assign_perfecte_to_sheets(object_name)
                bound.name = "PerfE_" + object_name
                self.boundaries[bound.name] = bound
        return True


class Parabolic(CommonReflector):
    """Manage a parabolic reflector antenna."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
        "feed_type": "Pyramidal",
        "feed_location": 0.0,
        "major_radius": 20.0,
        "minor_radius": 10.0,
        "focal_length": 50.0,
        "offset": 20.0,
    }

    def __init__(self, *args, **kwargs):
        CommonReflector.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Parabolic"

    @property
    def feed_location(self):
        return self._input_parameters.feed_location

    @feed_location.setter
    def feed_location(self, value):
        self._input_parameters.feed_location = value

    @property
    def major_radius(self):
        return self._input_parameters.major_radius

    @major_radius.setter
    def major_radius(self, value):
        self._input_parameters.major_radius = value

    @property
    def minor_radius(self):
        return self._input_parameters.minor_radius

    @minor_radius.setter
    def minor_radius(self, value):
        self._input_parameters.minor_radius = value

    @property
    def focal_length(self):
        return self._input_parameters.focal_length

    @focal_length.setter
    def focal_length(self, value):
        self._input_parameters.focal_length = value

    @property
    def offset(self):
        return self._input_parameters.offset

    @offset.setter
    def offset(self, value):
        self._input_parameters.offset = value

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {
            "feed_location": self.feed_location if self.feed_location else self._cm_value(0.0),
            "major_radius": self.major_radius if self.major_radius else self._cm_value(20.0),
            "minor_radius": self.minor_radius if self.minor_radius else self._cm_value(10.0),
            "focal_length": self.focal_length if self.focal_length else self._cm_value(50.0),
            "offset": self.offset if self.offset else self._cm_value(20.0),
        }
        return self._ordered(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        self._app.solution_type = "Modal"
        self.set_variables_in_hfss()
        reflector = self._add_primary_reflector(
            major_radius=self.major_radius,
            focal_length=self.focal_length,
            name=f"reflector_{self.name}",
            offset=self.offset,
            minor_radius=self.minor_radius,
        )
        self._move_to_origin([reflector.name])
        feed_angle = self._feed_rotation(self.offset, self.focal_length, self.feed_location)
        self._create_feed(feed_angle, [self.origin[0], self.origin[1] + self.feed_location, self.origin[2]])
        return True


class CommonDualReflector(CommonReflector):
    """Provide shared methods for dual-reflector antennas."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
        "feed_type": "Pyramidal",
        "swing_angle": 0.0,
        "diameter_primary": 70.0,
        "focal_length": 50.0,
        "eccentricity": 2.0,
        "interfocal_distance": 25.0,
    }

    @property
    def swing_angle(self):
        return self._input_parameters.swing_angle

    @swing_angle.setter
    def swing_angle(self, value):
        self._input_parameters.swing_angle = value

    @property
    def diameter_primary(self):
        return self._input_parameters.diameter_primary

    @diameter_primary.setter
    def diameter_primary(self, value):
        self._input_parameters.diameter_primary = value

    @property
    def focal_length(self):
        return self._input_parameters.focal_length

    @focal_length.setter
    def focal_length(self, value):
        self._input_parameters.focal_length = value

    @property
    def eccentricity(self):
        return self._input_parameters.eccentricity

    @eccentricity.setter
    def eccentricity(self, value):
        self._input_parameters.eccentricity = value

    @property
    def interfocal_distance(self):
        return self._input_parameters.interfocal_distance

    @interfocal_distance.setter
    def interfocal_distance(self, value):
        self._input_parameters.interfocal_distance = value

    def _dual_parameters(self):
        eccentricity = self.eccentricity
        interfocal_distance = self.interfocal_distance
        focal_length = self.focal_length
        diameter_primary = self.diameter_primary
        swing_angle = self.swing_angle
        magnification = (eccentricity + 1.0) / (eccentricity - 1.0)
        feed_tilt = math.degrees(2.0 * math.atan(magnification * math.tan(math.radians(swing_angle) / 2.0)))
        offset_primary = (-2.0 * focal_length) * (
            (math.tan(math.radians(swing_angle) / 2.0) - magnification * math.tan(math.radians(feed_tilt) / 2.0))
            / (
                1.0
                + magnification * math.tan(math.radians(swing_angle) / 2.0) * math.tan(math.radians(feed_tilt) / 2.0)
            )
        )
        psi_u = math.degrees(-2.0 * math.atan((2.0 * offset_primary + diameter_primary) / (4.0 * focal_length)))
        theta_e = abs(
            math.degrees(
                2.0 * math.atan((1.0 / magnification) * math.tan(math.radians(psi_u - swing_angle) / 2.0))
                + math.radians(feed_tilt)
            )
        )
        cone_height = 5.0 * interfocal_distance
        subreflector_radius = cone_height * math.tan(math.radians(theta_e))
        focal_shift = interfocal_distance / 2.0
        semi_major = focal_shift / eccentricity
        return {
            "swing_angle": swing_angle,
            "diameter_primary": diameter_primary,
            "focal_length": focal_length,
            "eccentricity": eccentricity,
            "interfocal_distance": interfocal_distance,
            "feed_tilt": feed_tilt,
            "offset_primary": offset_primary,
            "theta_e": theta_e,
            "subreflector_radius": abs(subreflector_radius),
            "semi_major": semi_major,
            "focal_shift": focal_shift,
        }

    def _model_feed(self, feed_tilt):
        feed_position = self._feed_position_dual(self.interfocal_distance, self.swing_angle)
        feed_angle = -90.0 + self.swing_angle + feed_tilt
        position = [feed_position[index] + self.origin[index] for index in range(3)]
        self._create_feed(feed_angle, position)


class Cassegrain(CommonDualReflector):
    """Manage a Cassegrain reflector antenna."""

    _default_input_parameters = dict(CommonDualReflector._default_input_parameters)

    def __init__(self, *args, **kwargs):
        CommonDualReflector.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Cassegrain"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = self._dual_parameters()
        semi_minor = math.sqrt(max(parameters["focal_shift"] ** 2 - parameters["semi_major"] ** 2, 1e-9))
        parameters["semi_minor"] = semi_minor
        return self._ordered(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False
        self._app.solution_type = "Modal"
        self.set_variables_in_hfss()
        parameters = self.synthesis()
        primary = self._add_primary_reflector(
            major_radius=self.diameter_primary / 2.0,
            focal_length=self.focal_length,
            name=f"reflector_{self.name}",
            offset=parameters["offset_primary"],
        )
        secondary = self._add_cassegrain_subreflector(
            semi_major=parameters["semi_major"],
            semi_minor=parameters["semi_minor"],
            focal_shift=parameters["focal_shift"],
            radius=parameters["subreflector_radius"],
            name=f"subreflector_{self.name}",
        )
        self._app.modeler.rotate([secondary.name], "X", self.swing_angle)
        self._move_to_origin([primary.name, secondary.name])
        self._model_feed(parameters["feed_tilt"])
        return True


class Gregorian(CommonDualReflector):
    """Manage a Gregorian reflector antenna."""

    _default_input_parameters = dict(CommonDualReflector._default_input_parameters)
    _default_input_parameters["eccentricity"] = 0.5

    def __init__(self, *args, **kwargs):
        CommonDualReflector.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Gregorian"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = self._dual_parameters()
        semi_minor = math.sqrt(max(parameters["semi_major"] ** 2 - parameters["focal_shift"] ** 2, 1e-9))
        parameters["semi_minor"] = semi_minor
        return self._ordered(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False
        self._app.solution_type = "Modal"
        self.set_variables_in_hfss()
        parameters = self.synthesis()
        primary = self._add_primary_reflector(
            major_radius=self.diameter_primary / 2.0,
            focal_length=self.focal_length,
            name=f"reflector_{self.name}",
            offset=parameters["offset_primary"],
        )
        secondary = self._add_gregorian_subreflector(
            semi_major=parameters["semi_major"],
            semi_minor=parameters["semi_minor"],
            focal_shift=parameters["focal_shift"],
            radius=parameters["subreflector_radius"],
            name=f"subreflector_{self.name}",
        )
        self._app.modeler.rotate([secondary.name], "X", self.swing_angle)
        self._move_to_origin([primary.name, secondary.name])
        self._model_feed(parameters["feed_tilt"])
        return True


class SplashPlate(CommonReflector):
    """Manage a splash-plate reflector antenna."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 20.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
        "feed_type": "CircularWG_Choke",
        "primary_diameter": 308.0,
        "primary_focal": 200.0,
        "sub_diameter": 56.0,
        "sub_focal": 20.0,
        "sub_thickness": 1.0,
        "sub_height": 1.0,
    }

    def __init__(self, *args, **kwargs):
        CommonReflector.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "SplashPlate"

    @property
    def primary_diameter(self):
        return self._input_parameters.primary_diameter

    @primary_diameter.setter
    def primary_diameter(self, value):
        self._input_parameters.primary_diameter = value

    @property
    def primary_focal(self):
        return self._input_parameters.primary_focal

    @primary_focal.setter
    def primary_focal(self, value):
        self._input_parameters.primary_focal = value

    @property
    def sub_diameter(self):
        return self._input_parameters.sub_diameter

    @sub_diameter.setter
    def sub_diameter(self, value):
        self._input_parameters.sub_diameter = value

    @property
    def sub_focal(self):
        return self._input_parameters.sub_focal

    @sub_focal.setter
    def sub_focal(self, value):
        self._input_parameters.sub_focal = value

    @property
    def sub_thickness(self):
        return self._input_parameters.sub_thickness

    @sub_thickness.setter
    def sub_thickness(self, value):
        self._input_parameters.sub_thickness = value

    @property
    def sub_height(self):
        return self._input_parameters.sub_height

    @sub_height.setter
    def sub_height(self, value):
        self._input_parameters.sub_height = value

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {
            "primary_diameter": self.primary_diameter if self.primary_diameter else self._cm_value(30.8),
            "primary_focal": self.primary_focal if self.primary_focal else self._cm_value(20.0),
            "sub_diameter": self.sub_diameter if self.sub_diameter else self._cm_value(5.6),
            "sub_focal": self.sub_focal if self.sub_focal else self._cm_value(2.0),
            "sub_thickness": self.sub_thickness if self.sub_thickness else self._cm_value(0.1),
            "sub_height": self.sub_height if self.sub_height else self._cm_value(0.1),
        }
        return self._ordered(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False
        self._app.solution_type = "Modal"
        self.set_variables_in_hfss()
        reflector = self._add_primary_reflector(
            major_radius=self.primary_diameter / 2.0,
            focal_length=self.primary_focal,
            name=f"reflector_{self.name}",
            offset=0.0,
        )
        splash_plate = self._app.modeler.create_cylinder(
            orientation="Z",
            origin=[0.0, 0.0, self.sub_focal],
            radius=self.sub_diameter / 2.0,
            height=-self.sub_thickness,
            name=f"splash_plate_{self.name}",
            material=self.material,
        )
        splash_cone = self._app.modeler.create_cone(
            orientation="Z",
            origin=[0.0, 0.0, self.sub_focal],
            bottom_radius=self.sub_diameter / 4.0,
            top_radius=0.0,
            height=self.sub_height,
            name=f"splash_plate_cone_{self.name}",
            material=self.material,
        )
        self._app.modeler.unite([splash_plate.name, splash_cone.name])
        splash_plate = self._app.modeler[splash_plate.name]
        self.object_list[splash_plate.name] = splash_plate
        self._move_to_origin([reflector.name, splash_plate.name])
        self._create_feed(0.0, self.origin)
        return True
