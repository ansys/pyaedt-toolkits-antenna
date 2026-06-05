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
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.common.backend.logger_handler import logger

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import CommonPatch


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

    @property
    def num_sides(self):
        """Number of sides used for cylindrical sections."""
        return self._input_parameters.num_sides

    @num_sides.setter
    def num_sides(self, value):
        self._input_parameters.num_sides = value
        self._refresh_model()

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class CommonPrintedLogPeriodic(CommonPatch):
    """Provides base methods common to printed log periodic antennas."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 7.0,
        "frequency_unit": "GHz",
        "start_frequency": 4.0,
        "stop_frequency": 10.0,
        "material": "Duroid (tm)",
        "material_properties": {"permittivity": 2.2},
        "outer_boundary": "",
        "substrate_height": 1.5748,
        "tau_ratio": 0.65,
        "sigma_ratio": 0.81,
        "delta_angle": 45.0,
        "beta_angle": 45.0,
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

    def _sync_center_frequency(self):
        self._input_parameters.frequency = (self.start_frequency + self.stop_frequency) / 2.0

    def _get_material_permittivity(self):
        if self._app and (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            permittivity = self._app.materials[self.material].permittivity.value
            self._input_parameters.material_properties["permittivity"] = permittivity
            return float(permittivity)
        if self.material_properties:
            return float(self.material_properties["permittivity"])
        if self._app:
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
        return None

    def _effective_permittivity(self, high_wavelength, substrate_height, permittivity):
        effective_area = high_wavelength / 8.0
        if effective_area / 4.0 > substrate_height:
            effective_area = high_wavelength / 25.0
            return (
                permittivity * substrate_height / effective_area
                + 0.5
                + (effective_area / 2.0 - substrate_height) / effective_area
            )
        if effective_area / 2.0 > substrate_height:
            return (
                permittivity * substrate_height / effective_area
                + 0.5
                + (effective_area / 2.0 - substrate_height) / effective_area
            )
        return 0.5 * (permittivity + 1.0)

    def _ordered_parameters(self, parameters):
        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    def _apply_polyline_cs(self, polyline, coordinate_system):
        polyline_obj = self._app.get_oo_object(self._app.oeditor, polyline.name)
        self._app.set_oo_property_value(
            aedt_object=polyline_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

    def _arc_points(
        self,
        radius,
        start_angle,
        end_angle,
        elevation,
        segments=12,
        reverse=False,
    ):
        points = []
        index_range = range(segments + 1)
        if reverse:
            index_range = reversed(list(index_range))
        for index in index_range:
            if all(isinstance(value, (int, float)) for value in [radius, start_angle, end_angle, elevation]):
                angle = start_angle + (end_angle - start_angle) * index / segments
                points.append(
                    [
                        radius * math.cos(math.radians(angle)),
                        radius * math.sin(math.radians(angle)),
                        elevation,
                    ]
                )
            else:
                angle = f"(({start_angle})+((({end_angle})-({start_angle}))*{index}/{segments}))"
                points.append(
                    [
                        f"({radius})*cos(({angle})deg)",
                        f"({radius})*sin(({angle})deg)",
                        elevation,
                    ]
                )
        return points

    def _create_polygon(self, name, points, coordinate_system):
        polygon = self._app.modeler.create_polyline(
            points,
            cover_surface=True,
            close_surface=True,
            name=name,
        )
        self._apply_polyline_cs(polygon, coordinate_system)
        return polygon

    def _create_sector(
        self,
        name,
        inner_radius,
        outer_radius,
        start_angle,
        end_angle,
        elevation,
        coordinate_system,
    ):
        points = self._arc_points(
            outer_radius,
            start_angle,
            end_angle,
            elevation,
        )
        is_zero_radius = False
        if isinstance(inner_radius, (int, float)):
            is_zero_radius = math.isclose(float(inner_radius), 0.0)
        else:
            is_zero_radius = str(inner_radius).strip("() ") in {"0", "0.0"}

        if is_zero_radius:
            points.append(["0", "0", elevation])
        else:
            points.extend(
                self._arc_points(
                    inner_radius,
                    start_angle,
                    end_angle,
                    elevation,
                    reverse=True,
                )
            )
        return self._create_polygon(name, points, coordinate_system)

    def _create_swept_radial_sheet(
        self,
        name,
        inner_radius,
        outer_radius,
        sweep_angle,
        rotation_angle,
        elevation,
        coordinate_system,
    ):
        radial_profile = self._app.modeler.create_polyline(
            points=[[inner_radius, 0.0, elevation], [outer_radius, 0.0, elevation]],
            name=name,
            material=self.material,
        )
        self._apply_polyline_cs(radial_profile, coordinate_system)
        radial_profile = radial_profile.sweep_around_axis(Axis.Z, sweep_angle)
        self._apply_polyline_cs(radial_profile, coordinate_system)
        self._app.modeler.rotate(radial_profile, "Z", rotation_angle)
        return radial_profile

    def _create_feed_bridge_port(
        self,
        antenna_name,
        upper_arm,
        lower_arm,
        sub_h,
        port_gap_width,
        port_width,
        coordinate_system,
    ):
        upper_edge_id = self._app.modeler.get_edgeid_from_position(
            [0.0, port_gap_width / 2.0, sub_h],
            upper_arm.name,
            self.length_unit,
        )
        lower_edge_id = self._app.modeler.get_edgeid_from_position(
            [0.0, -port_gap_width / 2.0, sub_h],
            lower_arm.name,
            self.length_unit,
        )

        if upper_edge_id and lower_edge_id:
            upper_edge = self._app.modeler.create_object_from_edge(upper_edge_id)
            lower_edge = self._app.modeler.create_object_from_edge(lower_edge_id)
            self._app.modeler.connect([upper_edge.name, lower_edge.name])
            port = self._app.modeler[upper_edge.name]
            port.name = "port_lump_" + antenna_name
        else:
            port = self._app.modeler.create_rectangle(
                orientation=Plane.XY,
                origin=[-port_width, f"-{port_gap_width}/2", sub_h],
                sizes=[f"2*({port_width})", port_gap_width],
                name="port_lump_" + antenna_name,
                material="vacuum",
                is_covered=True,
                new_properties={"Coordinate System": coordinate_system},
            )

        port.color = (128, 0, 0)
        port.transparency = 0.25
        return port

    def _finalize_planar_model(
        self,
        antenna_name,
        coordinate_system,
        sub_h,
        sub_x,
        sub_y,
        upper_arm,
        port_width,
        port_gap_width,
        pos_x,
        pos_y,
        pos_z,
    ):
        upper_arm.color = (255, 128, 65)
        upper_arm.transparency = 0.1

        lower_name = upper_arm.duplicate_around_axis(Axis.Z, 180, 2)[0]
        lower_arm = self._app.modeler[lower_name]
        lower_arm.name = upper_arm.name.replace("upper", "lower")
        lower_arm.color = (255, 128, 65)
        lower_arm.transparency = 0.1

        port = self._create_feed_bridge_port(
            antenna_name,
            upper_arm,
            lower_arm,
            sub_h,
            port_gap_width,
            port_width,
            coordinate_system,
        )

        try:
            upper_bbox = upper_arm.bounding_box
            lower_bbox = lower_arm.bounding_box
            x_margin = max(float(port_width), float(sub_h))
            y_margin = max(float(port_gap_width) / 2.0, float(sub_h))
            min_x = min(upper_bbox[0], lower_bbox[0]) - x_margin
            min_y = min(upper_bbox[1], lower_bbox[1]) - y_margin
            max_x = max(upper_bbox[3], lower_bbox[3]) + x_margin
            max_y = max(upper_bbox[4], lower_bbox[4]) + y_margin
            sub_origin = [min_x, min_y, 0.0]
            sub_sizes = [max_x - min_x, max_y - min_y, sub_h]
        except Exception:
            sub_origin = [f"-{sub_x}/2", f"-{sub_y}/2", "0"]
            sub_sizes = [sub_x, sub_y, sub_h]

        sub = self._app.modeler.create_box(
            origin=sub_origin,
            sizes=sub_sizes,
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        for obj in [sub, upper_arm, lower_arm, port]:
            obj.group_name = antenna_name
            self.object_list[obj.name] = obj

        self._app.modeler.move(
            list(self.object_list.keys()),
            [pos_x, pos_y, pos_z],
        )
        self._app.modeler.fit_all()
        return True


class LogPeriodicToothed(CommonPrintedLogPeriodic):
    """Manage a toothed printed log periodic antenna.

    Parameters
    ----------
    start_frequency : float, optional
        Lower edge of the operating band. The default is ``4.0``.
    stop_frequency : float, optional
        Upper edge of the operating band. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. The default is ``"Duroid (tm)"``.
    material_properties : dict, optional
        Material properties for the substrate. The default is
        ``{"permittivity": 2.2}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    substrate_height : float, optional
        Substrate height. The default is ``1.5748``.
    tau_ratio : float, optional
        Successive element scaling ratio. The default is ``0.65``.
    sigma_ratio : float, optional
        Successive spacing ratio. The default is ``0.81``.
    delta_angle : float, optional
        Tooth taper angle in degrees. The default is ``45.0``.
    beta_angle : float, optional
        Main flare angle in degrees. The default is ``45.0``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.log_periodic.LogPeriodicToothed`
        Antenna object.

    Notes
    -----
     .. [1] C. Balanis, "Frequency Independent Antennas:
         Spirals and Log Periodics," in *Modern Antenna Handbook*,
         New York, Wiley, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend import antenna_models
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = antenna_models.log_periodic.LogPeriodicToothed(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        **CommonPrintedLogPeriodic._default_input_parameters,
        "delta_angle": 45.0,
        "beta_angle": 45.0,
    }

    def __init__(self, *args, **kwargs):
        CommonPrintedLogPeriodic.__init__(
            self,
            self._default_input_parameters,
            *args,
            **kwargs,
        )
        self.antenna_type = "LogPeriodicToothed"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        permittivity = self._get_material_permittivity()
        if permittivity is None:
            return parameters

        start_frequency = min(self.start_frequency, self.stop_frequency)
        stop_frequency = max(self.start_frequency, self.stop_frequency)
        freq_low_hz = constants.unit_converter(
            start_frequency,
            "Freq",
            self.frequency_unit,
            "Hz",
        )
        freq_high_hz = constants.unit_converter(
            stop_frequency,
            "Freq",
            self.frequency_unit,
            "Hz",
        )
        wl_low_meters = constants.SpeedOfLight / freq_low_hz
        wl_high_meters = constants.SpeedOfLight / freq_high_hz
        sub_meters = constants.unit_converter(
            self.substrate_height,
            "Length",
            self.length_unit,
            "meter",
        )

        eff_permittivity = self._effective_permittivity(
            wl_high_meters,
            sub_meters,
            permittivity,
        )
        correction_factor = 0.92
        wl_low_meters = correction_factor * constants.SpeedOfLight / freq_low_hz / math.sqrt(eff_permittivity)
        wl_high_meters = correction_factor * constants.SpeedOfLight / freq_high_hz / math.sqrt(eff_permittivity)

        outer_radius = constants.unit_converter(
            wl_low_meters / math.pi,
            "Length",
            "meter",
            self.length_unit,
        )
        inner_radius = constants.unit_converter(
            wl_high_meters / math.pi,
            "Length",
            "meter",
            self.length_unit,
        )
        port_gap_width = inner_radius
        port_width = port_gap_width / 2.0 * math.tan(math.radians(self._input_parameters.beta_angle / 2.0))

        parameters["outer_radius"] = outer_radius
        parameters["inner_radius"] = inner_radius
        parameters["port_gap_width"] = port_gap_width
        parameters["port_width"] = port_width
        parameters["sub_x"] = outer_radius * 2.3
        parameters["sub_y"] = outer_radius * 2.3
        parameters["sub_h"] = self.substrate_height
        parameters["tau_ratio"] = self._input_parameters.tau_ratio
        parameters["sigma_ratio"] = self._input_parameters.sigma_ratio
        parameters["delta_angle"] = self._input_parameters.delta_angle
        parameters["beta_angle"] = self._input_parameters.beta_angle
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
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

        antenna_name = self.name
        coordinate_system = self.coordinate_system
        self._app.modeler.set_working_coordinate_system(coordinate_system)
        sub_h = self.synthesis_parameters.sub_h.value
        sub_x = self.synthesis_parameters.sub_x.value
        sub_y = self.synthesis_parameters.sub_y.value
        outer_radius = self.synthesis_parameters.outer_radius.value
        tau_ratio = self.synthesis_parameters.tau_ratio.value
        sigma_ratio = self.synthesis_parameters.sigma_ratio.value
        delta_angle = self.synthesis_parameters.delta_angle.value
        beta_angle = self.synthesis_parameters.beta_angle.value
        port_gap_width = self.synthesis_parameters.port_gap_width.value
        port_width = self.synthesis_parameters.port_width.value
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        base_rotation = 90.0 - beta_angle / 2.0
        upper_arm = self._create_swept_radial_sheet(
            "ant_toothed_upper_" + antenna_name,
            0.0,
            outer_radius,
            beta_angle,
            base_rotation,
            sub_h,
            coordinate_system,
        )

        port_cutout = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=[-port_width, 0.0, sub_h],
            sizes=[2.0 * port_width, port_gap_width / 2.0],
            name="tool_port_cutout_" + antenna_name,
            is_covered=True,
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.subtract(upper_arm, port_cutout, keep_originals=False)
        upper_arm = self._app.modeler[upper_arm.name]

        port_opening = port_gap_width / 2.0
        port_extent = math.hypot(port_opening, port_width)
        current_outer = outer_radius
        current_inner = outer_radius * sigma_ratio
        tooth_index = 1

        while current_inner > port_extent and tooth_index <= 20:
            if tooth_index % 2:
                sweep_angle = delta_angle
                rotation_angle = base_rotation - delta_angle
                next_outer = current_inner
                next_inner = current_outer * tau_ratio
            else:
                sweep_angle = beta_angle + delta_angle
                rotation_angle = base_rotation
                next_outer = current_inner
                next_inner = current_inner * sigma_ratio

            tooth = self._create_swept_radial_sheet(
                f"ant_tooth_{tooth_index}_{antenna_name}",
                current_inner,
                current_outer,
                sweep_angle,
                rotation_angle,
                sub_h,
                coordinate_system,
            )
            self._app.modeler.unite([upper_arm.name, tooth.name])
            upper_arm = self._app.modeler[upper_arm.name]
            current_outer = next_outer
            current_inner = next_inner
            tooth_index += 1

        return self._finalize_planar_model(
            antenna_name,
            coordinate_system,
            sub_h,
            sub_x,
            sub_y,
            upper_arm,
            port_width,
            port_gap_width,
            pos_x,
            pos_y,
            pos_z,
        )


class LogPeriodicTrapezoidal(CommonPrintedLogPeriodic):
    """Manage a trapezoidal printed log periodic antenna.

    Parameters
    ----------
    start_frequency : float, optional
        Lower edge of the operating band. The default is ``4.0``.
    stop_frequency : float, optional
        Upper edge of the operating band. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. The default is ``"Duroid (tm)"``.
    material_properties : dict, optional
        Material properties for the substrate. The default is
        ``{"permittivity": 2.2}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    substrate_height : float, optional
        Substrate height. The default is ``1.5748``.
    tau_ratio : float, optional
        Successive element scaling ratio. The default is ``0.7``.
    sigma_ratio : float, optional
        Successive spacing ratio. The default is ``0.84``.
    delta_angle : float, optional
        Trapezoid tooth taper angle in degrees.
        The default is ``30.0``.
    beta_angle : float, optional
        Main flare angle in degrees. The default is ``60.0``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.log_periodic.LogPeriodicTrapezoidal`
        Antenna object.

    Notes
    -----
     .. [1] C. Balanis, "Frequency Independent Antennas:
         Spirals and Log Periodics," in *Modern Antenna Handbook*,
         New York, Wiley, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend import antenna_models
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = antenna_models.log_periodic.LogPeriodicTrapezoidal(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        **CommonPrintedLogPeriodic._default_input_parameters,
        "delta_angle": 30.0,
        "beta_angle": 60.0,
        "tau_ratio": 0.7,
        "sigma_ratio": 0.84,
    }

    def __init__(self, *args, **kwargs):
        CommonPrintedLogPeriodic.__init__(
            self,
            self._default_input_parameters,
            *args,
            **kwargs,
        )
        self.antenna_type = "LogPeriodicTrapezoidal"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        permittivity = self._get_material_permittivity()
        if permittivity is None:
            return parameters

        start_frequency = min(self.start_frequency, self.stop_frequency)
        stop_frequency = max(self.start_frequency, self.stop_frequency)
        freq_low_hz = constants.unit_converter(
            start_frequency,
            "Freq",
            self.frequency_unit,
            "Hz",
        )
        freq_high_hz = constants.unit_converter(
            stop_frequency,
            "Freq",
            self.frequency_unit,
            "Hz",
        )
        wl_low_meters = constants.SpeedOfLight / freq_low_hz
        wl_high_meters = constants.SpeedOfLight / freq_high_hz
        sub_meters = constants.unit_converter(
            self.substrate_height,
            "Length",
            self.length_unit,
            "meter",
        )

        eff_permittivity = self._effective_permittivity(
            wl_high_meters,
            sub_meters,
            permittivity,
        )
        correction_factor = 0.92
        wl_low_meters = correction_factor * constants.SpeedOfLight / freq_low_hz / math.sqrt(eff_permittivity)
        wl_high_meters = correction_factor * constants.SpeedOfLight / freq_high_hz / math.sqrt(eff_permittivity)

        beta_half = math.radians(self._input_parameters.beta_angle / 2.0)
        delta_angle = math.radians(self._input_parameters.delta_angle)
        taper_divisor = math.tan(beta_half) + math.tan(beta_half + delta_angle)
        outer_length = constants.unit_converter(
            wl_low_meters / 2.0 / taper_divisor,
            "Length",
            "meter",
            self.length_unit,
        )
        inner_length = constants.unit_converter(
            wl_high_meters / 2.0 / taper_divisor,
            "Length",
            "meter",
            self.length_unit,
        )
        port_gap_width = inner_length
        port_width = port_gap_width / 2.0 / math.tan(beta_half)

        parameters["outer_length"] = outer_length
        parameters["inner_length"] = inner_length
        parameters["port_gap_width"] = port_gap_width
        parameters["port_width"] = port_width
        parameters["sub_x"] = outer_length * 2.3
        parameters["sub_y"] = outer_length * 2.3
        parameters["sub_h"] = self.substrate_height
        parameters["tau_ratio"] = self._input_parameters.tau_ratio
        parameters["sigma_ratio"] = self._input_parameters.sigma_ratio
        parameters["delta_angle"] = self._input_parameters.delta_angle
        parameters["beta_angle"] = self._input_parameters.beta_angle
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
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

        antenna_name = self.name
        coordinate_system = self.coordinate_system
        self._app.modeler.set_working_coordinate_system(coordinate_system)
        sub_h = self.synthesis_parameters.sub_h.value
        sub_x = self.synthesis_parameters.sub_x.value
        sub_y = self.synthesis_parameters.sub_y.value
        outer_length = self.synthesis_parameters.outer_length.value
        tau_ratio = self.synthesis_parameters.tau_ratio.value
        sigma_ratio = self.synthesis_parameters.sigma_ratio.value
        delta_angle = self.synthesis_parameters.delta_angle.value
        beta_angle = self.synthesis_parameters.beta_angle.value
        port_gap_width = self.synthesis_parameters.port_gap_width.value
        port_width = self.synthesis_parameters.port_width.value
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        beta_tan = math.tan(math.radians(beta_angle / 2.0))
        center_points = [
            [port_width, port_gap_width / 2.0, sub_h],
            [outer_length / beta_tan, outer_length, sub_h],
            [-(outer_length / beta_tan), outer_length, sub_h],
            [-port_width, port_gap_width / 2.0, sub_h],
        ]
        upper_arm = self._create_polygon(
            "ant_trapezoidal_upper_" + antenna_name,
            center_points,
            coordinate_system,
        )

        current_outer = outer_length
        current_inner = outer_length * sigma_ratio
        tooth_index = 1
        max_teeth = 20

        while tooth_index <= max_teeth and current_inner > port_gap_width / 2.0:
            side_sign = "1" if tooth_index % 2 else "-1"
            tooth_angle_tan = math.tan(math.radians(90.0 - (beta_angle / 2.0 + delta_angle)))
            tooth_points = [
                [0.0, current_inner, sub_h],
                [0.0, current_outer, sub_h],
                [
                    float(side_sign) * current_outer / tooth_angle_tan,
                    current_outer,
                    sub_h,
                ],
                [
                    float(side_sign) * current_inner / tooth_angle_tan,
                    current_inner,
                    sub_h,
                ],
            ]
            tooth = self._create_polygon(
                f"ant_trapezoid_{tooth_index}_{antenna_name}",
                tooth_points,
                coordinate_system,
            )
            self._app.modeler.unite([upper_arm.name, tooth.name])
            upper_arm = self._app.modeler[upper_arm.name]

            if tooth_index % 2:
                next_outer = current_inner
                next_inner = current_outer * tau_ratio
            else:
                next_outer = current_inner
                next_inner = current_inner * sigma_ratio

            current_outer = next_outer
            current_inner = next_inner
            tooth_index += 1

        return self._finalize_planar_model(
            antenna_name,
            coordinate_system,
            sub_h,
            sub_x,
            sub_y,
            upper_arm,
            port_width,
            port_gap_width,
            pos_x,
            pos_y,
            pos_z,
        )


class LogPeriodicArray(CommonLogPeriodic):
    """Manage a log periodic dipole array antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency used for synthesis. The default is ``5.05``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Conductor material. The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    gain : float, optional
        Expected directivity in dBi. The default is ``10.0``.
    input_resistance : float, optional
        Feed resistance in ohms. The default is ``100.0``.
    load_impedance : float, optional
        Termination resistance in ohms. The default is ``118.7921``.
    boom_spacing : float, optional
        Spacing between booms. The default is ``0.22693``.
    tau_ratio : float, optional
        Successive element scaling ratio. The default is ``0.9265``.
    sigma_ratio : float, optional
        Successive spacing ratio. The default is ``0.198``.
    base_element_length : float, optional
        Length of the largest dipole element. The default is ``32.98``.
    base_element_radius : float, optional
        Radius of each dipole element. The default is ``0.093165``.
    number_of_elements : int, optional
        Number of dipole elements. The default is ``8``.
    num_sides : int, optional
        Number of sides used for cylindrical sections. The default is ``6``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.log_periodic.LogPeriodicArray`
        Antenna object.

    Notes
    -----
     .. [1] C. A. Balanis, "Horn Antennas," in
         *Antenna Theory: Analysis and Design*, 3rd ed., Hoboken,
         Wiley, 2005, sec. 11.4, pp. 619-637.
     .. [2] R. H. DuHamel and E. G. Berry,
         "Logarithmically Periodic Antenna Arrays,"
         *IRE Wescon Convention Record*, Part 1, 1958,
         pp. 161-177.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend import antenna_models
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = antenna_models.log_periodic.LogPeriodicArray(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

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
        "num_sides": 6,
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
        num_sides = max(int(round(self.num_sides)), 0)

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
        parameters["num_sides"] = num_sides
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
        num_sides = self.synthesis_parameters.num_sides.hfss_variable

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
            num_sides=num_sides,
        )
        lower_boom = self._app.modeler.create_cylinder(
            orientation=Axis.X,
            origin=["-" + base_element_radius, "-" + boom_spacing + "/2", "0"],
            radius=r_wire,
            height=s_feed + "+" + base_element_radius,
            name="lower_boom_" + antenna_name,
            material=self.material,
            num_sides=num_sides,
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
                num_sides=num_sides,
            )
            lower_element = self._app.modeler.create_cylinder(
                orientation=Axis.Z,
                origin=[total_x_position, "-" + boom_spacing + "/2", "0"],
                radius=base_element_radius,
                height=lower_height,
                name="lower_element_{}_{}".format(idx, antenna_name),
                material=self.material,
                num_sides=num_sides,
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
