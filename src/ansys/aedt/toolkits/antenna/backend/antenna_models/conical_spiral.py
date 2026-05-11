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
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonConicalSpiral(CommonAntenna):
    """Provides base methods common to conical spiral antenna."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.__init__(self, _default_input_parameters, *args, **kwargs)

    @property
    def material(self):
        """Horn material.

        Returns
        -------
        str
        """
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
            else:
                if value != self.material and self.object_list:
                    for antenna_obj in self.object_list:
                        if (
                            self.object_list[antenna_obj].material_name == self.material.lower()
                            and "port_cap" not in antenna_obj
                        ):
                            self.object_list[antenna_obj].material_name = value

                    self._input_parameters.material = value
                    parameters = self.synthesis()
                    self.update_synthesis_parameters(parameters)
                    self.set_variables_in_hfss()
        else:
            self._input_parameters.material = value

    @property
    def frequency(self):
        """Central frequency.

        Returns
        -------
        float
        """
        return (self.stop_frequency - self.start_frequency) / 2.0 + self.start_frequency

    @property
    def start_frequency(self):
        """Start frequency.

        Returns
        -------
        float
        """
        return self._input_parameters.start_frequency

    @start_frequency.setter
    def start_frequency(self, value):
        self._input_parameters.start_frequency = value
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    @property
    def stop_frequency(self):
        """Stop frequency.

        Returns
        -------
        float
        """
        return self._input_parameters.stop_frequency

    @stop_frequency.setter
    def stop_frequency(self, value):
        self._input_parameters.stop_frequency = value
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class Archimedean(CommonConicalSpiral):
    """Manages conical archimedeal spiral antenna.

    This class is accessible through the app hfss object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Horn material. If a material is not defined, a new material, ``parametrized``, is defined.
        The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are ``"FEBI"``, ``"PML"``,
        ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    parametrized : bool, optional
        Whether to create a parametrized antenna.  The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.Archimedean`
        Conical archimedean spiral object.

    Notes
    -----
    .. [1] R. Johnson, "Frequency Independent Antennas," Antenna Engineering Handbook,
        3rd ed. New York, McGraw-Hill, 1993.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Archimedean
    >>> hfss = Hfss()
    >>> antenna = Archimedean(
    ...     hfss,
    ...     start_frequency=20.0,
    ...     stop_frequency=50.0,
    ...     frequency_unit="GHz",
    ...     outer_boundary="Radiation",
    ...     length_unit="mm",
    ...     antenna_name="Archimedean",
    ...     origin=[1, 100, 50],
    ... )
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> hfss.release_desktop(False, False)

    """

    antenna_type = "Archimedean"
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
        CommonConicalSpiral.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        light_speed = constants.SpeedOfLight
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")

        expansion_coefficient = 1.0
        offset_angle = 90.0
        spiral_coefficient = 1.0
        points = 200
        arms = 2
        port_extension = 0.1

        outer_rad_calc = light_speed / (2 * math.pi * start_freq_hz)
        outer_rad_calc = constants.unit_converter(outer_rad_calc, "Length", "meter", self.length_unit)
        outer_rad_calc_cm = constants.unit_converter(outer_rad_calc, "Length", self.length_unit, "cm")
        inner_rad_calc = light_speed / (2 * math.pi * stop_freq_hz)
        inner_rad = constants.unit_converter(inner_rad_calc, "Length", "meter", self.length_unit)
        inner_rad_cm = constants.unit_converter(inner_rad, "Length", self.length_unit, "cm")
        port_extension = constants.unit_converter(port_extension, "Length", "cm", self.length_unit)

        parameters["expansion_coefficient"] = expansion_coefficient
        parameters["offset_angle"] = offset_angle
        parameters["spiral_coefficient"] = spiral_coefficient
        parameters["inner_rad"] = round(inner_rad, 6)
        parameters["turns_number"] = round((outer_rad_calc_cm - inner_rad_cm) / 2.0 / math.pi / 0.1, 2)
        parameters["cone_height"] = round((outer_rad_calc - inner_rad) * math.tan(math.radians(66.66)), 2)
        parameters["points"] = points
        parameters["arms_number"] = arms
        parameters["port_extension"] = port_extension

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical archimedean spiral antenna.

        Once the antenna is created, this method is not used anymore.
        """
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

        # Read synthesized parameter values
        expansion_coefficient = self.synthesis_parameters.expansion_coefficient.value  # a
        offset_angle_deg = self.synthesis_parameters.offset_angle.value  # degrees
        spiral_coefficient = self.synthesis_parameters.spiral_coefficient.value  # sc exponent (sc = 1/value)
        inner_rad = self.synthesis_parameters.inner_rad.value
        turns_number = self.synthesis_parameters.turns_number.value
        cone_height = self.synthesis_parameters.cone_height.value
        arms_number = int(self.synthesis_parameters.arms_number.value)
        n_points = int(self.synthesis_parameters.points.value)

        pos_x = self.synthesis_parameters.pos_x.value
        pos_y = self.synthesis_parameters.pos_y.value
        pos_z = self.synthesis_parameters.pos_z.value
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        self._app.modeler.set_working_coordinate_system(coordinate_system)

        # r(phi) = inner_rad + a * phi^(1/sc)
        a = expansion_coefficient
        sc = 1.0 / spiral_coefficient  # SC = 1/SpiralCoefficient
        offset = math.radians(offset_angle_deg)

        # Number of phi samples (must be odd)
        n_per_turn = n_points / turns_number
        n = int(n_points) + 1
        if n % 2 == 0:
            n += 1
        turns_adj = turns_number + 1.0 / n_per_turn
        max_phi_rad = math.radians(360.0 * turns_adj)
        step = max_phi_rad / n

        phi = [i * step for i in range(n)]

        # Outer radius at end of spiral (needed for conical operations)
        r_max = inner_rad + a * math.pow(phi[n - 1], sc)

        # ---------------------------------------------------------------
        # Port1: closed polygon at inner_rad, z=cone_height (built at origin)
        # ---------------------------------------------------------------
        port_pts = [
            [inner_rad, 0, cone_height],
            [inner_rad * math.cos(offset), inner_rad * math.sin(offset), cone_height],
            [-inner_rad, 0, cone_height],
            [-inner_rad * math.cos(offset), -inner_rad * math.sin(offset), cone_height],
            [inner_rad, 0, cone_height],
        ]
        port1 = self._app.modeler.create_polyline(
            points=port_pts,
            cover_surface=True,
            close_surface=True,
            name="port_lump_" + antenna_name,
        )

        # Set coordinate system of polyline
        port1_obj = self._app.get_oo_object(self._app.oeditor, port1.name)
        self._app.set_oo_property_value(
            aedt_object=port1_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )
        port1.color = (128, 0, 0)
        port1.transparency = 0.1

        # Build the closed flat arm polygon at origin
        outer_facets = max(1, int(n_per_turn / 4))
        num_points = int(2 * n + outer_facets)
        num_segments = num_points - 1

        positions = [None] * num_points

        for i in range(n):
            # Outer edge of arm (curve 1)
            r = inner_rad + a * math.pow(phi[i], sc)
            positions[i] = [r * math.cos(phi[i]), r * math.sin(phi[i]), 0]
            # Inner edge of arm (curve 2, reversed, offset by 'offset')
            j = n - i - 1
            r2 = inner_rad + a * math.pow(phi[j], sc)
            positions[i + n + outer_facets - 1] = [
                r2 * math.cos(phi[j] + offset),
                r2 * math.sin(phi[j] + offset),
                0,
            ]

        # Outer tip facets connecting outer curve end to inner curve start
        outer_facet_angle_step = offset / outer_facets
        r_outer = inner_rad + a * math.pow(phi[n - 1], sc)
        for k in range(1, outer_facets):
            angle = phi[n - 1] + outer_facet_angle_step * k
            positions[n + k - 1] = [r_outer * math.cos(angle), r_outer * math.sin(angle), 0]

        # Close the polygon (repeat first point)
        positions[num_segments] = list(positions[0])

        arm1 = self._app.modeler.create_polyline(
            points=positions,
            cover_surface=True,
            close_surface=True,
            name="ant_AntennaArm1_base_" + antenna_name,
        )

        # Set coordinate system of polyline
        arm1_obj = self._app.get_oo_object(self._app.oeditor, arm1.name)
        self._app.set_oo_property_value(
            aedt_object=arm1_obj, object_name="CreatePolyline:1", prop_name="Coordinate System", value=coordinate_system
        )

        # Conical mapping: sweep flat arm along Z then intersect with cone,
        # extract the conical face and top face, unite them, delete solid.
        if cone_height > 0:
            self._app.modeler.sweep_along_vector(
                assignment=arm1.name,
                sweep_vector=[0, 0, cone_height],
            )
            cone_obj = self._app.modeler.create_cone(
                orientation="Z",
                origin=[0, 0, 0],
                bottom_radius=r_max,
                top_radius=inner_rad,
                height=cone_height,
                name="cone_ref_" + antenna_name,
                material="vacuum",
                new_properties={"Coordinate System": coordinate_system},
            )
            self._app.modeler.intersect(
                assignment=[arm1.name, cone_obj.name],
                keep_originals=False,
            )

            # --- Extract lateral face (conical surface of the arm) ---
            eps = cone_height * 1e-4
            actual_cone_h = cone_height * r_max / (r_max - inner_rad)
            face_z = eps
            face_r = (actual_cone_h - eps) / actual_cone_h * r_max
            face_x = face_r * math.cos(phi[n - 1])
            face_y = face_r * math.sin(phi[n - 1])

            face_id = self._app.modeler.get_faceid_from_position([face_x, face_y, face_z], arm1.name, self.length_unit)

            if not face_id:
                logger.error("Geometry creation failed, it can not be retrieved the arm face.")
                return False

            arm_sheet = self._app.modeler.create_object_from_face(face_id)

            # --- Extract top face (at z = cone_height) ---
            top_z = cone_height
            top_r = (actual_cone_h - cone_height) / actual_cone_h * r_max - eps
            top_x = top_r * math.cos(offset / 2.0)
            top_y = top_r * math.sin(offset / 2.0)
            top_face = self._app.modeler.get_faceid_from_position([top_x, top_y, top_z], arm1.name, self.length_unit)

            top_sheet = self._app.modeler.create_object_from_face(top_face)

            # --- Unite both faces into a single surface, delete solid ---
            self._app.modeler.unite([arm_sheet.name, top_sheet.name])
            self._app.modeler.delete(arm1.name)

            old_name = arm1.name
            arm_sheet.name = "ant_AntennaArm1_" + antenna_name
            arm_sheet.group_name = antenna_name
            arm_sheet.color = (255, 128, 65)
            arm_sheet.transparency = 0.1
            if old_name in self.object_list:
                del self.object_list[old_name]
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm_sheet
            arm1 = arm_sheet
        else:
            arm1.name = "ant_AntennaArm1_" + antenna_name
            arm1.group_name = antenna_name
            arm1.color = (255, 128, 65)
            arm1.transparency = 0.1
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm1

        # Duplicate arms around Z axis
        if arms_number > 1:
            angle_step = 360.0 / arms_number
            duplicated = arm1.duplicate_around_axis(
                axis="Z",
                angle=angle_step,
                clones=arms_number,
            )
            for idx, dup_name in enumerate(duplicated, start=2):
                dup_obj = self._app.modeler[dup_name]
                new_name = "ant_AntennaArm" + str(idx) + "_" + antenna_name
                dup_obj.name = new_name
                dup_obj.group_name = antenna_name
                self.object_list[new_name] = dup_obj

        port1.group_name = antenna_name
        self.object_list[port1.name] = port1

        # Move all objects to final position
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass


class Log(CommonConicalSpiral):
    """Manages conical log spiral antenna.

    This class is accessible through the app hfss object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Horn material. If a material is not defined, a new material, ``parametrized``, is defined.
        The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are ``"FEBI"``, ``"PML"``,
        ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.Log`
        Conical archimedean spiral object.

    Notes
    -----
    .. [1] R. Johnson, "Frequency Independent Antennas," Antenna Engineering Handbook,
        3rd ed. New York, McGraw-Hill, 1993.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Log
    >>> hfss = Hfss()
    >>> antenna = Log(
    ...     hfss,
    ...     start_frequency=20.0,
    ...     stop_frequency=50.0,
    ...     frequency_unit="GHz",
    ...     outer_boundary="Radiation",
    ...     length_unit="mm",
    ...     antenna_name="Log",
    ...     origin=[1, 100, 50],
    ... )
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> hfss.release_desktop(False, False)

    """

    antenna_type = "Log"
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
        CommonConicalSpiral.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")
        scale_factor = 1.1
        turns_number = 2
        offset_angle = 90.0
        spiral_coefficient = 1.0
        points = 200
        arms = 2

        outer_rad_calc = scale_factor * 3e10 / (2 * math.pi * start_freq_hz)
        outer_rad_calc = constants.unit_converter(outer_rad_calc, "Length", "cm", self.length_unit)
        inner_rad_calc = scale_factor * 3e10 / (2 * math.pi * stop_freq_hz)
        inner_rad = constants.unit_converter(inner_rad_calc, "Length", "cm", self.length_unit)
        expansion_coefficient = round(math.pow(outer_rad_calc / inner_rad, 1.0 / turns_number), 2)

        parameters["expansion_coefficient"] = expansion_coefficient
        parameters["offset_angle"] = offset_angle
        parameters["spiral_coefficient"] = spiral_coefficient
        parameters["inner_rad"] = inner_rad
        parameters["turns_number"] = turns_number
        parameters["cone_height"] = (outer_rad_calc - inner_rad) * math.tan(math.radians(66.66))
        parameters["points"] = points
        parameters["arms_number"] = arms

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical log spiral antenna.

        Once the antenna is created, this method is not used anymore.
        """
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

        # Read synthesized parameter values
        expansion_coefficient = self.synthesis_parameters.expansion_coefficient.value  # E (growth per turn)
        offset_angle_deg = self.synthesis_parameters.offset_angle.value  # arm width in degrees
        inner_rad = self.synthesis_parameters.inner_rad.value
        turns_number = self.synthesis_parameters.turns_number.value
        cone_height = self.synthesis_parameters.cone_height.value
        arms_number = int(self.synthesis_parameters.arms_number.value)
        n_points = int(self.synthesis_parameters.points.value)

        pos_x = self.synthesis_parameters.pos_x.value
        pos_y = self.synthesis_parameters.pos_y.value
        pos_z = self.synthesis_parameters.pos_z.value
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        self._app.modeler.set_working_coordinate_system(coordinate_system)

        # ---------------------------------------------------------------
        # Logarithmic spiral: r(phi) = inner_rad * exp(a * phi)
        # where a = log(E) / (2*pi)
        # ---------------------------------------------------------------
        a = math.log(expansion_coefficient) / (2.0 * math.pi)
        offset = math.radians(offset_angle_deg)

        # Number of phi samples (must be odd)
        n_per_turn = n_points / turns_number
        n = int(n_points) + 1
        if n % 2 == 0:
            n += 1
        turns_adj = turns_number + 1.0 / n_per_turn
        max_phi_rad = math.radians(360.0 * turns_adj)
        step = max_phi_rad / n

        phi = [i * step for i in range(n)]

        # Outer radius at end of spiral (needed for conical operations)
        r_max = inner_rad * math.exp(a * phi[n - 1])

        # Port1: closed polygon at inner_rad, z=cone_height (built at origin)
        port_pts = [
            [inner_rad, 0, cone_height],
            [inner_rad * math.cos(offset), inner_rad * math.sin(offset), cone_height],
            [-inner_rad, 0, cone_height],
            [-inner_rad * math.cos(offset), -inner_rad * math.sin(offset), cone_height],
            [inner_rad, 0, cone_height],
        ]
        port1 = self._app.modeler.create_polyline(
            points=port_pts,
            cover_surface=True,
            close_surface=True,
            name="port_lump_" + antenna_name,
        )

        # Set coordinate system of polyline
        port1_obj = self._app.get_oo_object(self._app.oeditor, port1.name)
        self._app.set_oo_property_value(
            aedt_object=port1_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        port1.color = (128, 0, 0)
        port1.transparency = 0.1

        # Build the closed flat arm polygon at origin
        outer_facets = max(1, int(n_per_turn / 4))
        if outer_facets % 2 != 0:
            outer_facets += 1
        num_points = int(2 * n + outer_facets)
        num_segments = num_points - 1

        positions = [None] * num_points

        for i in range(n):
            # Outer edge of arm (curve 1)
            r = inner_rad * math.exp(a * phi[i])
            positions[i] = [r * math.cos(phi[i]), r * math.sin(phi[i]), 0]
            # Inner edge of arm (curve 2, reversed, offset by 'offset')
            j = n - i - 1
            r2 = inner_rad * math.exp(a * phi[j])
            positions[i + n + outer_facets - 1] = [
                r2 * math.cos(phi[j] + offset),
                r2 * math.sin(phi[j] + offset),
                0,
            ]

        # Outer tip facets connecting outer curve end to inner curve start
        outer_facet_angle_step = offset / outer_facets
        r_outer = inner_rad * math.exp(a * phi[n - 1])
        for k in range(1, outer_facets):
            angle = phi[n - 1] + outer_facet_angle_step * k
            positions[n + k - 1] = [r_outer * math.cos(angle), r_outer * math.sin(angle), 0]

        # Close the polygon (repeat first point)
        positions[num_segments] = list(positions[0])

        arm1 = self._app.modeler.create_polyline(
            points=positions,
            cover_surface=True,
            close_surface=True,
            name="ant_AntennaArm1_base_" + antenna_name,
        )

        # Set coordinate system of polyline
        arm1_obj = self._app.get_oo_object(self._app.oeditor, arm1.name)
        self._app.set_oo_property_value(
            aedt_object=arm1_obj, object_name="CreatePolyline:1", prop_name="Coordinate System", value=coordinate_system
        )

        # Conical mapping: sweep flat arm along Z then intersect with cone,
        # extract the conical face and top face, unite them, delete solid.
        if cone_height > 0:
            self._app.modeler.sweep_along_vector(
                assignment=arm1.name,
                sweep_vector=[0, 0, cone_height],
            )
            cone_obj = self._app.modeler.create_cone(
                orientation="Z",
                origin=[0, 0, 0],
                bottom_radius=r_max,
                top_radius=inner_rad,
                height=cone_height,
                name="cone_ref_" + antenna_name,
                material="vacuum",
                new_properties={"Coordinate System": coordinate_system},
            )
            self._app.modeler.intersect(
                assignment=[arm1.name, cone_obj.name],
                keep_originals=False,
            )

            # --- Extract lateral face (conical surface of the arm) ---
            eps = cone_height * 1e-4
            actual_cone_h = cone_height * r_max / (r_max - inner_rad)
            face_z = eps
            face_r = (actual_cone_h - eps) / actual_cone_h * r_max
            face_x = face_r * math.cos(phi[n - 1])
            face_y = face_r * math.sin(phi[n - 1])

            face_id = self._app.modeler.get_faceid_from_position([face_x, face_y, face_z], arm1.name, self.length_unit)
            if not face_id:
                logger.error("Geometry creation failed, cannot retrieve the arm face.")
                return False

            arm_sheet = self._app.modeler.create_object_from_face(face_id)

            # --- Extract top face (at z = cone_height) ---
            top_z = cone_height
            top_r = (actual_cone_h - cone_height) / actual_cone_h * r_max - eps
            top_x = top_r * math.cos(offset / 2.0)
            top_y = top_r * math.sin(offset / 2.0)
            top_face_id = self._app.modeler.get_faceid_from_position([top_x, top_y, top_z], arm1.name, self.length_unit)
            top_sheet = self._app.modeler.create_object_from_face(top_face_id)

            # --- Delete solid, unite the two face sheets ---
            self._app.modeler.delete(arm1.name)
            self._app.modeler.unite([arm_sheet.name, top_sheet.name])

            arm_sheet.name = "ant_AntennaArm1_" + antenna_name
            arm_sheet.group_name = antenna_name
            arm_sheet.color = (255, 128, 65)
            arm_sheet.transparency = 0.1
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm_sheet
            arm1 = arm_sheet
        else:
            arm1.name = "ant_AntennaArm1_" + antenna_name
            arm1.group_name = antenna_name
            arm1.color = (255, 128, 65)
            arm1.transparency = 0.1
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm1

        # Duplicate arms around Z axis
        if arms_number > 1:
            angle_step = 360.0 / arms_number
            duplicated = arm1.duplicate_around_axis(
                axis="Z",
                angle=angle_step,
                clones=arms_number,
            )
            for idx, dup_name in enumerate(duplicated, start=2):
                dup_obj = self._app.modeler[dup_name]
                new_name = "ant_AntennaArm" + str(idx) + "_" + antenna_name
                dup_obj.name = new_name
                dup_obj.group_name = antenna_name
                self.object_list[new_name] = dup_obj

        port1.group_name = antenna_name
        self.object_list[port1.name] = port1

        # Move all objects to final position
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass


class Sinuous(CommonConicalSpiral):
    """Manages conical sinuous spiral antenna.

    This class is accessible through the app hfss object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Horn material. The default is ``"pec"``. If a material is not defined, a new material,
        ``parametrized``, is defined. The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are ``"FEBI"``, ``"PML"``,
        ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    parametrized : bool, optional
        Whether to create a parametrized antenna.  The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.Sinuous`
        Conical Sinuous spiral object.

    Notes
    -----
    .. [1] R. Johnson, "Frequency Independent Antennas," Antenna Engineering Handbook,
        3rd ed. New York, McGraw-Hill, 1993.

    Examples
    --------
    >>> from ansys.aedt.core import Hfss
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Sinuous
    >>> hfss = Hfss()
    >>> antenna = Sinuous(
    ...     hfss,
    ...     start_frequency=20.0,
    ...     stop_frequency=50.0,
    ...     frequency_unit="GHz",
    ...     outer_boundary="Radiation",
    ...     length_unit="cm",
    ...     antenna_name="Sinuous",
    ...     origin=[1, 100, 50],
    ... )
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> hfss.release_desktop(False, False)

    """

    antenna_type = "Sinuous"
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
        CommonConicalSpiral.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        light_speed = constants.SpeedOfLight
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")

        scale_factor = 1.25
        cell_number = 8
        alpha_angle = 45.0
        delta_angle = 22.5
        port_extension = 0.1
        points = 200
        arms = 4

        outer_rad_calc = (
            scale_factor * light_speed / start_freq_hz / 4.0 / (math.radians(alpha_angle) + math.radians(delta_angle))
        )
        outer_rad = constants.unit_converter(outer_rad_calc, "Length", "meter", self.length_unit)
        inner_rad_calc = (
            scale_factor
            * light_speed
            / stop_freq_hz
            / 4.0
            / 2.0
            / (math.radians(alpha_angle) + math.radians(delta_angle))
        )
        inner_rad = constants.unit_converter(inner_rad_calc, "Length", "meter", self.length_unit)
        port_extension = constants.unit_converter(port_extension, "Length", "cm", self.length_unit)

        parameters["alpha_angle"] = alpha_angle
        parameters["delta_angle"] = delta_angle
        parameters["port_extension"] = port_extension
        parameters["outer_rad"] = outer_rad
        parameters["cell_number"] = cell_number
        parameters["cone_height"] = (outer_rad - inner_rad) * math.tan(math.radians(66.66))
        parameters["points"] = points
        parameters["arms_number"] = arms
        parameters["growth_rate"] = round(math.pow(inner_rad / outer_rad, 1.0 / (cell_number - 1)), 2)

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a sinuous spiral antenna.

        Once the antenna is created, this method is not used anymore.
        """
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

        # Read synthesized parameter values
        alpha_deg = self.synthesis_parameters.alpha_angle.value
        delta_deg = self.synthesis_parameters.delta_angle.value
        growth_rate = self.synthesis_parameters.growth_rate.value  # T
        outer_rad = self.synthesis_parameters.outer_rad.value  # R
        cells = int(self.synthesis_parameters.cell_number.value)
        arms_number = int(self.synthesis_parameters.arms_number.value)
        n_points = int(self.synthesis_parameters.points.value)
        cone_height = self.synthesis_parameters.cone_height.value
        port_ext = self.synthesis_parameters.port_extension.value

        pos_x = self.synthesis_parameters.pos_x.value
        pos_y = self.synthesis_parameters.pos_y.value
        pos_z = self.synthesis_parameters.pos_z.value
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        self._app.modeler.set_working_coordinate_system(coordinate_system)

        alpha_rad = math.radians(alpha_deg)
        delta_rad = math.radians(delta_deg)
        rotation = 0.0
        t = growth_rate  # T (grow rate)
        r = outer_rad  # R (current radius, decremented)

        step_size = outer_rad / n_points

        # Build RP array: RP[i] = outer_rad * T^i
        rp = [0.0] * (cells + 1)
        rp[0] = outer_rad
        last_i = 0
        for i in range(1, cells):
            rp[i] = rp[i - 1] * t
            last_i = i
        min_rp = rp[last_i]
        rp[cells] = min_rp

        # Build phi1, phi2 and rad arrays
        phi1 = [0.0] * n_points
        phi2 = [0.0] * n_points
        rad = [0.0] * n_points
        q = 0

        for i in range(cells):
            p = i + 1
            while r <= rp[i] and r >= rp[i + 1]:
                phi1[q] = (
                    ((-1.0) ** p) * alpha_rad * math.sin(math.log(r / rp[i]) / math.log(t) * math.pi)
                    + delta_rad
                    + rotation
                )
                phi2[q] = (
                    ((-1.0) ** p) * alpha_rad * math.sin(math.log(r / rp[i]) / math.log(t) * math.pi)
                    - delta_rad
                    + rotation
                )
                r -= step_size
                q += 1

        max_phi = q  # actual number of points used
        rad[0] = outer_rad
        for i in range(1, max_phi):
            rad[i] = rad[i - 1] - step_size

        inner_rad = rad[max_phi - 1]

        # Build arm polygon (NoOfPoints = 2*max_phi + OuterFacets)
        outer_facets = 100
        num_points = 2 * max_phi + outer_facets
        num_segments = num_points - 1

        positions = [None] * num_points

        for i in range(max_phi):
            positions[i] = [
                rad[i] * math.cos(phi1[i]),
                rad[i] * math.sin(phi1[i]),
                0,
            ]

        for i in range(1, max_phi + 1):
            idx = max_phi - i
            positions[i + max_phi - 1] = [
                rad[idx] * math.cos(phi2[idx]),
                rad[idx] * math.sin(phi2[idx]),
                0,
            ]

        outer_facet_angle_step = delta_rad / outer_facets * 2.0
        for i in range(max_phi * 2, num_segments):
            step_num = i - max_phi * 2 + 1
            positions[i] = [
                outer_rad * math.cos(rotation - delta_rad + outer_facet_angle_step * step_num),
                outer_rad * math.sin(rotation - delta_rad + outer_facet_angle_step * step_num),
                0,
            ]

        # Close polygon
        positions[num_segments] = list(positions[0])

        arm1 = self._app.modeler.create_polyline(
            points=positions,
            cover_surface=True,
            close_surface=True,
            name="ant_AntennaArm1_base_" + antenna_name,
        )
        # Set coordinate system of polyline
        arm1_obj = self._app.get_oo_object(self._app.oeditor, arm1.name)
        self._app.set_oo_property_value(
            aedt_object=arm1_obj, object_name="CreatePolyline:1", prop_name="Coordinate System", value=coordinate_system
        )

        # ---------------------------------------------------------------
        # Conical mapping (same approach as Archimedean/Log)
        # ---------------------------------------------------------------
        if cone_height > 0:
            self._app.modeler.sweep_along_vector(
                assignment=arm1.name,
                sweep_vector=[0, 0, cone_height],
            )
            cone_obj = self._app.modeler.create_cone(
                orientation="Z",
                origin=[0, 0, 0],
                bottom_radius=outer_rad,
                top_radius=inner_rad,
                height=cone_height,
                name="cone_ref_" + antenna_name,
                material="vacuum",
                new_properties={"Coordinate System": coordinate_system},
            )
            self._app.modeler.intersect(
                assignment=[arm1.name, cone_obj.name],
                keep_originals=False,
            )

            eps = cone_height * 1e-4
            actual_cone_h = cone_height * outer_rad / (outer_rad - inner_rad)
            face_z = eps
            face_r = (actual_cone_h - eps) / actual_cone_h * outer_rad
            face_x = face_r * math.cos(phi1[max_phi - 1])
            face_y = face_r * math.sin(phi1[max_phi - 1])

            face_id = self._app.modeler.get_faceid_from_position([face_x, face_y, face_z], arm1.name, self.length_unit)
            if not face_id:
                logger.error("Geometry creation failed, cannot retrieve the arm face.")
                return False

            arm_sheet = self._app.modeler.create_object_from_face(face_id)

            # Top face: midpoint between positions[max_phi-1] and positions[max_phi]
            top_z = cone_height
            top_x = (positions[max_phi - 1][0] + positions[max_phi][0]) / 2.0 + eps
            top_y = (positions[max_phi - 1][1] + positions[max_phi][1]) / 2.0 + eps
            top_face_id = self._app.modeler.get_faceid_from_position([top_x, top_y, top_z], arm1.name, self.length_unit)
            top_sheet = self._app.modeler.create_object_from_face(top_face_id)

            self._app.modeler.delete(arm1.name)
            self._app.modeler.unite([arm_sheet.name, top_sheet.name])

            arm_sheet.name = "ant_AntennaArm1_" + antenna_name
            arm_sheet.group_name = antenna_name
            arm_sheet.color = (255, 128, 65)
            arm_sheet.transparency = 0.1
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm_sheet
            arm1 = arm_sheet
        else:
            arm1.name = "ant_AntennaArm1_" + antenna_name
            arm1.group_name = antenna_name
            arm1.color = (255, 128, 65)
            arm1.transparency = 0.1
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm1

        # Duplicate arms around Z axis
        if arms_number > 1:
            angle_step = 360.0 / arms_number
            duplicated = arm1.duplicate_around_axis(
                axis="Z",
                angle=angle_step,
                clones=arms_number,
            )
            for idx, dup_name in enumerate(duplicated, start=2):
                dup_obj = self._app.modeler[dup_name]
                new_name = "ant_AntennaArm" + str(idx) + "_" + antenna_name
                dup_obj.name = new_name
                dup_obj.group_name = antenna_name
                self.object_list[new_name] = dup_obj

        # Port positions: inner gap midpoint of arm1 at origin
        mid_dx = (positions[max_phi - 1][0] + positions[max_phi][0]) / 2.0
        mid_dy = (positions[max_phi - 1][1] + positions[max_phi][1]) / 2.0
        mid_z = cone_height

        angle_step_rad = math.radians(360.0 / arms_number)

        # Port 1: arm1 (index 0) and arm3 (index 2) — opposite pair, rotated 180 deg
        mid3_dx = mid_dx * math.cos(2 * angle_step_rad) - mid_dy * math.sin(2 * angle_step_rad)
        mid3_dy = mid_dx * math.sin(2 * angle_step_rad) + mid_dy * math.cos(2 * angle_step_rad)
        arm3_name = "ant_AntennaArm3_" + antenna_name if arms_number >= 3 else arm1.name

        edge_id1 = self._app.modeler.get_edgeid_from_position([mid_dx, mid_dy, mid_z], arm1.name, self.length_unit)
        edge_id3 = self._app.modeler.get_edgeid_from_position([mid3_dx, mid3_dy, mid_z], arm3_name, self.length_unit)

        if edge_id1 and edge_id3:
            obj_edge1 = self._app.modeler.create_object_from_edge(edge_id1)
            obj_edge3 = self._app.modeler.create_object_from_edge(edge_id3)
            self._app.modeler.connect([obj_edge1.name, obj_edge3.name])
            obj_edge1.name = "port_lump_" + antenna_name + "_1"
            obj_edge1.color = (255, 0, 0)
            obj_edge1.group_name = antenna_name
            self.object_list[obj_edge1.name] = obj_edge1
        else:
            port1_pts = [
                [mid_dx, mid_dy, mid_z],
                [mid3_dx, mid3_dy, mid_z],
            ]
            port1 = self._app.modeler.create_polyline(
                points=port1_pts,
                cover_surface=False,
                close_surface=False,
                name="port_lump_" + antenna_name + "_1",
            )
            port1.color = (255, 0, 0)
            port1.group_name = antenna_name
            self.object_list[port1.name] = port1

        if arms_number == 4:
            # Port 2: arm2 (index 1) and arm4 (index 3) — opposite pair, rotated 90 and 270 deg
            mid2_dx = mid_dx * math.cos(angle_step_rad) - mid_dy * math.sin(angle_step_rad)
            mid2_dy = mid_dx * math.sin(angle_step_rad) + mid_dy * math.cos(angle_step_rad)
            mid4_dx = mid_dx * math.cos(3 * angle_step_rad) - mid_dy * math.sin(3 * angle_step_rad)
            mid4_dy = mid_dx * math.sin(3 * angle_step_rad) + mid_dy * math.cos(3 * angle_step_rad)

            arm2_name = "ant_AntennaArm2_" + antenna_name
            arm4_name = "ant_AntennaArm4_" + antenna_name

            edge_id2 = self._app.modeler.get_edgeid_from_position(
                [mid2_dx, mid2_dy, mid_z], arm2_name, self.length_unit
            )
            edge_id4 = self._app.modeler.get_edgeid_from_position(
                [mid4_dx, mid4_dy, mid_z], arm4_name, self.length_unit
            )

            if edge_id2 and edge_id4:
                obj_edge2 = self._app.modeler.create_object_from_edge(edge_id2)
                obj_edge4 = self._app.modeler.create_object_from_edge(edge_id4)
                self._app.modeler.sweep_along_vector(obj_edge2.name, [0, 0, port_ext])
                self._app.modeler.sweep_along_vector(obj_edge4.name, [0, 0, port_ext])
                obj_edge2.name = "ant_ext1_" + antenna_name
                obj_edge2.color = (65, 65, 65)
                obj_edge2.group_name = antenna_name
                self.object_list[obj_edge2.name] = obj_edge2
                obj_edge4.name = "gnd_2_" + antenna_name
                obj_edge4.color = (65, 65, 65)
                obj_edge4.group_name = antenna_name
                self.object_list[obj_edge4.name] = obj_edge4

                edge_id2a = self._app.modeler.get_edgeid_from_position(
                    [mid2_dx, mid2_dy, mid_z + port_ext], obj_edge2.name, self.length_unit
                )
                edge_id4a = self._app.modeler.get_edgeid_from_position(
                    [mid4_dx, mid4_dy, mid_z + port_ext], obj_edge4.name, self.length_unit
                )
                if edge_id2a and edge_id4a:
                    obj_edge2a = self._app.modeler.create_object_from_edge(edge_id2a)
                    obj_edge4a = self._app.modeler.create_object_from_edge(edge_id4a)
                    self._app.modeler.connect([obj_edge2a.name, obj_edge4a.name])
                    obj_edge2a.name = "port_lump_" + antenna_name + "_2"
                    obj_edge2a.color = (255, 0, 0)
                    obj_edge2a.group_name = antenna_name
                    self.object_list[obj_edge2a.name] = obj_edge2a
                else:
                    port2_pts = [
                        [mid2_dx, mid2_dy, mid_z + port_ext],
                        [mid4_dx, mid4_dy, mid_z + port_ext],
                    ]
                    port2 = self._app.modeler.create_polyline(
                        points=port2_pts,
                        cover_surface=False,
                        close_surface=False,
                        name="port_lump_" + antenna_name + "_2",
                    )
                    port2.color = (255, 0, 0)
                    port2.group_name = antenna_name
                    self.object_list[port2.name] = port2
            else:
                port2_pts = [
                    [mid2_dx, mid2_dy, mid_z + port_ext],
                    [mid4_dx, mid4_dy, mid_z + port_ext],
                ]
                port2 = self._app.modeler.create_polyline(
                    points=port2_pts,
                    cover_surface=False,
                    close_surface=False,
                    name="port_lump_" + antenna_name + "_2",
                )
                port2.color = (255, 0, 0)
                port2.group_name = antenna_name
                self.object_list[port2.name] = port2

        # Move all objects to final position
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass
