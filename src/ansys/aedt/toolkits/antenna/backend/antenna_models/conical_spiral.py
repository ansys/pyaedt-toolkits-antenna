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
        CommonAntenna.antenna_type = "ConicalSpiral"
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
        self.antenna_type = "Archimedean"

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

        This method builds the geometry natively using PyAEDT modeler primitives,
        without relying on the AEDT UDM (User-Defined Model) to avoid known UDM bugs.

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
        spiral_coefficient = self.synthesis_parameters.spiral_coefficient.value  # sc exponent (sc = 1/value in UDM)
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
        # Replicate the UDM geometry algorithm (Archimedean.py)
        # r(phi) = inner_rad + a * phi^(1/sc)
        # ---------------------------------------------------------------
        a = expansion_coefficient
        sc = 1.0 / spiral_coefficient  # matches UDM: SC = 1/SpiralCoefficient
        offset = math.radians(offset_angle_deg)

        # Number of phi samples (must be odd, matching UDM logic)
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
        # Port1: closed polygon at inner_rad, z=cone_height (UDM identical)
        # For planar cone_height=0 so z=0.
        # ---------------------------------------------------------------
        port_pts = [
            [inner_rad + pos_x, pos_y, cone_height + pos_z],
            [inner_rad * math.cos(offset) + pos_x, inner_rad * math.sin(offset) + pos_y, cone_height + pos_z],
            [-inner_rad + pos_x, pos_y, cone_height + pos_z],
            [-inner_rad * math.cos(offset) + pos_x, -inner_rad * math.sin(offset) + pos_y, cone_height + pos_z],
            [inner_rad + pos_x, pos_y, cone_height + pos_z],
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

        # ---------------------------------------------------------------
        # Build the closed flat arm polygon (always z=0, matching UDM)
        # ---------------------------------------------------------------
        outer_facets = max(1, int(n_per_turn / 4))
        num_points = int(2 * n + outer_facets)
        num_segments = num_points - 1

        positions = [None] * num_points

        for i in range(n):
            # Outer edge of arm (curve 1)
            r = inner_rad + a * math.pow(phi[i], sc)
            positions[i] = [r * math.cos(phi[i]) + pos_x, r * math.sin(phi[i]) + pos_y, pos_z]
            # Inner edge of arm (curve 2, reversed, offset by 'offset')
            j = n - i - 1
            r2 = inner_rad + a * math.pow(phi[j], sc)
            positions[i + n + outer_facets - 1] = [
                r2 * math.cos(phi[j] + offset) + pos_x,
                r2 * math.sin(phi[j] + offset) + pos_y,
                pos_z,
            ]

        # Outer tip facets connecting outer curve end to inner curve start
        outer_facet_angle_step = offset / outer_facets
        r_outer = inner_rad + a * math.pow(phi[n - 1], sc)
        for k in range(1, outer_facets):
            angle = phi[n - 1] + outer_facet_angle_step * k
            positions[n + k - 1] = [r_outer * math.cos(angle) + pos_x, r_outer * math.sin(angle) + pos_y, pos_z]

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

        # ---------------------------------------------------------------
        # Conical mapping: sweep flat arm along Z then intersect with cone,
        # extract the conical face and top face, unite them, delete solid.
        # Replicates the UDM SweepAlongVector + Intersect + CreateObjectFromFace approach.
        # ---------------------------------------------------------------
        if cone_height > 0:
            self._app.modeler.sweep_along_vector(
                assignment=arm1.name,
                sweep_vector=[0, 0, cone_height],
            )
            cone_obj = self._app.modeler.create_cone(
                orientation="Z",
                origin=[pos_x, pos_y, pos_z],
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
            # Point near the outer edge at phi[n-1], slightly above z=0
            actual_cone_h = cone_height * r_max / (r_max - inner_rad)
            face_z = pos_z + 0.0001
            face_r = (actual_cone_h - 0.0001) / actual_cone_h * r_max
            face_x = pos_x + face_r * math.cos(phi[n - 1])
            face_y = pos_y + face_r * math.sin(phi[n - 1])

            face_id = self._app.modeler.get_faceid_from_position(
                [face_x, face_y, face_z], arm1.name, self._app.modeler.model_units
            )

            if not face_id:
                logger.error("Geometry creation failed, it can not be retrieved the arm face.")
                return False

            arm_sheet = self._app.modeler.create_object_from_face(face_id)

            # --- Extract top face (at z = cone_height) ---
            top_z = pos_z + cone_height
            top_r = (actual_cone_h - cone_height) / actual_cone_h * r_max - 0.0001
            top_x = pos_x + top_r * math.cos(offset / 2.0)
            top_y = pos_y + top_r * math.sin(offset / 2.0)
            top_face = self._app.modeler.get_faceid_from_position(
                [top_x, top_y, top_z], arm1.name, self._app.modeler.model_units
            )

            top_sheet = self._app.modeler.create_object_from_face(top_face)

            # --- Unite both faces into a single surface, delete solid ---
            self._app.modeler.unite([arm_sheet.name, top_sheet.name])
            self._app.modeler.delete(arm1.name)

            # Update arm1 reference to the resulting sheet
            old_name = arm1.name
            arm_sheet.name = "ant_AntennaArm1_" + antenna_name
            arm_sheet.group_name = antenna_name
            if old_name in self.object_list:
                del self.object_list[old_name]
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm_sheet
            arm1 = arm_sheet
        else:
            arm1.name = "ant_AntennaArm1_" + antenna_name
            arm1.group_name = antenna_name
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm1

        # ---------------------------------------------------------------
        # Duplicate arms around Z axis (UDM: DuplicateAroundAxis)
        # ---------------------------------------------------------------
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
        self.antenna_type = "Log"

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

        This method builds the geometry natively using PyAEDT modeler primitives,
        without relying on the AEDT UDM (User-Defined Model) to avoid known UDM bugs.

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
        # where a = log(E) / (2*pi)  (matches UDM Log.py exactly)
        # ---------------------------------------------------------------
        a = math.log(expansion_coefficient) / (2.0 * math.pi)
        offset = math.radians(offset_angle_deg)

        # Number of phi samples (must be odd, matching UDM logic)
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

        # ---------------------------------------------------------------
        # Port1: closed polygon at inner_rad, z=cone_height (UDM identical)
        # For planar cone_height=0 so z=pos_z.
        # ---------------------------------------------------------------
        port_pts = [
            [inner_rad + pos_x, pos_y, cone_height + pos_z],
            [inner_rad * math.cos(offset) + pos_x, inner_rad * math.sin(offset) + pos_y, cone_height + pos_z],
            [-inner_rad + pos_x, pos_y, cone_height + pos_z],
            [-inner_rad * math.cos(offset) + pos_x, -inner_rad * math.sin(offset) + pos_y, cone_height + pos_z],
            [inner_rad + pos_x, pos_y, cone_height + pos_z],
        ]
        port1 = self._app.modeler.create_polyline(
            points=port_pts,
            cover_surface=True,
            close_surface=True,
            name="port_lump_" + antenna_name,
        )
        port1.color = (128, 0, 0)
        port1.transparency = 0.1

        # ---------------------------------------------------------------
        # Build the closed flat arm polygon (always z=pos_z, matching UDM)
        # ---------------------------------------------------------------
        outer_facets = max(1, int(n_per_turn / 4))
        if outer_facets % 2 != 0:
            outer_facets += 1
        num_points = int(2 * n + outer_facets)
        num_segments = num_points - 1

        positions = [None] * num_points

        for i in range(n):
            # Outer edge of arm (curve 1)
            r = inner_rad * math.exp(a * phi[i])
            positions[i] = [r * math.cos(phi[i]) + pos_x, r * math.sin(phi[i]) + pos_y, pos_z]
            # Inner edge of arm (curve 2, reversed, offset by 'offset')
            j = n - i - 1
            r2 = inner_rad * math.exp(a * phi[j])
            positions[i + n + outer_facets - 1] = [
                r2 * math.cos(phi[j] + offset) + pos_x,
                r2 * math.sin(phi[j] + offset) + pos_y,
                pos_z,
            ]

        # Outer tip facets connecting outer curve end to inner curve start
        outer_facet_angle_step = offset / outer_facets
        r_outer = inner_rad * math.exp(a * phi[n - 1])
        for k in range(1, outer_facets):
            angle = phi[n - 1] + outer_facet_angle_step * k
            positions[n + k - 1] = [r_outer * math.cos(angle) + pos_x, r_outer * math.sin(angle) + pos_y, pos_z]

        # Close the polygon (repeat first point)
        positions[num_segments] = list(positions[0])

        arm1 = self._app.modeler.create_polyline(
            points=positions,
            cover_surface=True,
            close_surface=True,
            name="ant_AntennaArm1_base_" + antenna_name,
        )
        arm1.group_name = antenna_name

        # ---------------------------------------------------------------
        # Conical mapping: sweep flat arm along Z then intersect with cone,
        # extract the conical face and top face, unite them, delete solid.
        # Replicates the UDM SweepAlongVector + Intersect + CreateObjectFromFace approach.
        # ---------------------------------------------------------------
        if cone_height > 0:
            self._app.modeler.sweep_along_vector(
                assignment=arm1.name,
                sweep_vector=[0, 0, cone_height],
            )
            cone_obj = self._app.modeler.create_cone(
                orientation="Z",
                origin=[pos_x, pos_y, pos_z],
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
            actual_cone_h = cone_height * r_max / (r_max - inner_rad)
            face_z = pos_z + 0.0001
            face_r = (actual_cone_h - 0.0001) / actual_cone_h * r_max
            face_x = pos_x + face_r * math.cos(phi[n - 1])
            face_y = pos_y + face_r * math.sin(phi[n - 1])

            face_id = self._app.modeler.get_faceid_from_position(
                [face_x, face_y, face_z], arm1.name, self._app.modeler.model_units
            )
            if not face_id:
                logger.error("Geometry creation failed, cannot retrieve the arm face.")
                return False

            arm_sheet = self._app.modeler.create_object_from_face(face_id)

            # --- Extract top face (at z = cone_height) ---
            top_z = pos_z + cone_height
            top_r = (actual_cone_h - cone_height) / actual_cone_h * r_max - 0.0001
            top_x = pos_x + top_r * math.cos(offset / 2.0)
            top_y = pos_y + top_r * math.sin(offset / 2.0)
            top_face_id = self._app.modeler.get_faceid_from_position(
                [top_x, top_y, top_z], arm1.name, self._app.modeler.model_units
            )
            top_sheet = self._app.modeler.create_object_from_face(top_face_id)

            # --- Delete solid, unite the two face sheets ---
            self._app.modeler.delete(arm1.name)
            self._app.modeler.unite([arm_sheet.name, top_sheet.name])

            arm_sheet.name = "ant_AntennaArm1_" + antenna_name
            arm_sheet.group_name = antenna_name
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm_sheet
            arm1 = arm_sheet
        else:
            arm1.name = "ant_AntennaArm1_" + antenna_name
            arm1.group_name = antenna_name
            self.object_list["ant_AntennaArm1_" + antenna_name] = arm1

        # ---------------------------------------------------------------
        # Duplicate arms around Z axis (UDM: DuplicateAroundAxis)
        # ---------------------------------------------------------------
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
    >>> antenna = Archimedean(
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
        self.antenna_type = "Log"

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
        """Draw a sinuous log spiral antenna. This method uses the User Defined Model from AEDT installation.

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

        # Map parameters
        alpha_angle = self.synthesis_parameters.alpha_angle.hfss_variable
        self._app[alpha_angle] = str(self.synthesis_parameters.alpha_angle.value) + "deg"
        delta_angle = self.synthesis_parameters.delta_angle.hfss_variable
        self._app[delta_angle] = str(self.synthesis_parameters.delta_angle.value) + "deg"
        growth_rate = self.synthesis_parameters.growth_rate.hfss_variable
        self._app[growth_rate] = str(self.synthesis_parameters.growth_rate.value)

        cone_height = self.synthesis_parameters.cone_height.hfss_variable
        outer_rad = self.synthesis_parameters.outer_rad.hfss_variable

        arms = self.synthesis_parameters.arms_number.hfss_variable
        self._app[arms] = str(self.synthesis_parameters.arms_number.value)
        points = self.synthesis_parameters.points.hfss_variable
        self._app[points] = str(self.synthesis_parameters.points.value)
        cell_number = self.synthesis_parameters.cell_number.hfss_variable
        self._app[cell_number] = str(self.synthesis_parameters.cell_number.value)
        port_extension = self.synthesis_parameters.port_extension.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        self._app.modeler.set_working_coordinate_system(coordinate_system)

        my_udm_pairs = []
        mypair = ["NumberOfPoints", points]
        my_udm_pairs.append(mypair)
        mypair = ["NumberOfCells", cell_number]
        my_udm_pairs.append(mypair)
        mypair = ["Alpha", alpha_angle]
        my_udm_pairs.append(mypair)
        mypair = ["GrowRate", growth_rate]
        my_udm_pairs.append(mypair)
        mypair = ["OuterRadius", outer_rad]
        my_udm_pairs.append(mypair)
        mypair = ["Delta", delta_angle]
        my_udm_pairs.append(mypair)
        mypair = ["NumberOfArms", arms]
        my_udm_pairs.append(mypair)
        mypair = ["ConeHeight", cone_height]
        my_udm_pairs.append(mypair)
        mypair = ["Port_Extension", port_extension]
        my_udm_pairs.append(mypair)
        obj_udm = self._app.modeler.create_udm(
            udm_full_name="HFSS/Antenna Toolkit/Spiral/Sinuous.py",
            parameters=my_udm_pairs,
            library="syslib",
            name="log",
        )
        port_cont = 1
        gnd_cont = 1
        for part in obj_udm.parts:
            comp = obj_udm.parts[part]

            if "AntennaArm" in comp.name:
                comp.name = "ant_" + comp.name + antenna_name
            elif "Port" in comp.name:
                comp.name = "port_lump_" + antenna_name + "_" + str(port_cont)
                port_cont += 1
            else:
                comp.name = "gnd_" + str(gnd_cont) + "_" + antenna_name
                gnd_cont += 1

            self.object_list[comp.name] = comp

        obj_udm.move([pos_x, pos_y, pos_z])

        obj_udm.group_name = antenna_name
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
