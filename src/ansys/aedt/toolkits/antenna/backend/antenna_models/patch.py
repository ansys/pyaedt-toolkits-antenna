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
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import TransmissionLine
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import properties
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonPatch(CommonAntenna):
    """Provides base methods common to patch antenna."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        default_input_parameters = properties.antenna.synthesis.model_dump()
        default_input_parameters.update(_default_input_parameters)
        CommonAntenna.antenna_type = "Patch"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)
        if "substrate_height" not in kwargs:
            self.substrate_height = constants.unit_converter(
                self.substrate_height, "Length", default_input_parameters["length_unit"], self.length_unit
            )
        self._transmission_line_calculator = TransmissionLine(self.frequency, self.frequency_unit)

    @property
    def material(self):
        """Substrate material.

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
                            and "coax" not in antenna_obj
                        ):
                            self.object_list[antenna_obj].material_name = value

                self._input_parameters.material = value
                parameters = self.synthesis()
                self.update_synthesis_parameters(parameters)
                self.set_variables_in_hfss()
        else:
            self._input_parameters.material = value

    @property
    def material_properties(self):
        """Substrate material properties.

        Returns
        -------
        str
        """
        return self._input_parameters.material_properties

    @property
    def substrate_height(self):
        """Substrate height.

        Returns
        -------
        float
        """
        return self._input_parameters.substrate_height

    @substrate_height.setter
    def substrate_height(self, value):
        self._input_parameters.substrate_height = value

        if self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    def _set_patch_property(self, parameter_name, value, requires_remodel=False):
        self._input_parameters.__setattr__(parameter_name, value)
        if self.object_list:
            if requires_remodel:
                logger.warning("%s updates require remodelling the antenna.", parameter_name)
                return
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def number_of_patches_x(self):
        return self._input_parameters.number_of_patches_x

    @number_of_patches_x.setter
    def number_of_patches_x(self, value):
        self._set_patch_property("number_of_patches_x", value, requires_remodel=True)

    @property
    def number_of_patches_y(self):
        return self._input_parameters.number_of_patches_y

    @number_of_patches_y.setter
    def number_of_patches_y(self, value):
        self._set_patch_property("number_of_patches_y", value, requires_remodel=True)

    @property
    def feed_rotation_angle(self):
        return self._input_parameters.feed_rotation_angle

    @feed_rotation_angle.setter
    def feed_rotation_angle(self, value):
        self._set_patch_property("feed_rotation_angle", value, requires_remodel=True)

    @property
    def element_1_rotation_angle(self):
        return self._input_parameters.element_1_rotation_angle

    @element_1_rotation_angle.setter
    def element_1_rotation_angle(self, value):
        self._set_patch_property("element_1_rotation_angle", value, requires_remodel=True)

    @property
    def element_2_rotation_angle(self):
        return self._input_parameters.element_2_rotation_angle

    @element_2_rotation_angle.setter
    def element_2_rotation_angle(self, value):
        self._set_patch_property("element_2_rotation_angle", value, requires_remodel=True)

    @property
    def element_3_rotation_angle(self):
        return self._input_parameters.element_3_rotation_angle

    @element_3_rotation_angle.setter
    def element_3_rotation_angle(self, value):
        self._set_patch_property("element_3_rotation_angle", value, requires_remodel=True)

    @property
    def element_4_rotation_angle(self):
        return self._input_parameters.element_4_rotation_angle

    @element_4_rotation_angle.setter
    def element_4_rotation_angle(self, value):
        self._set_patch_property("element_4_rotation_angle", value, requires_remodel=True)

    @property
    def element_1_port_phase(self):
        return self._input_parameters.element_1_port_phase

    @element_1_port_phase.setter
    def element_1_port_phase(self, value):
        self._set_patch_property("element_1_port_phase", value)

    @property
    def element_2_port_phase(self):
        return self._input_parameters.element_2_port_phase

    @element_2_port_phase.setter
    def element_2_port_phase(self, value):
        self._set_patch_property("element_2_port_phase", value)

    @property
    def element_3_port_phase(self):
        return self._input_parameters.element_3_port_phase

    @element_3_port_phase.setter
    def element_3_port_phase(self, value):
        self._set_patch_property("element_3_port_phase", value)

    @property
    def element_4_port_phase(self):
        return self._input_parameters.element_4_port_phase

    @element_4_port_phase.setter
    def element_4_port_phase(self, value):
        self._set_patch_property("element_4_port_phase", value)

    def _material_permittivity(self):
        if self._app and (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            mat_props = self._app.materials[self.material]
            permittivity = mat_props.permittivity.value
            self._input_parameters.material_properties["permittivity"] = permittivity
            return permittivity
        if self.material_properties:
            return self.material_properties["permittivity"]
        if self._app:
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
        return None

    def _patch_synthesis_base(self):
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = constants.SpeedOfLight / freq_hz
        permittivity = self._material_permittivity()
        if permittivity is None:
            return {}
        sub_permittivity = float(permittivity)
        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((sub_permittivity + 1.0) / 2.0))
        eff_permittivity = (sub_permittivity + 1.0) / 2.0 + (sub_permittivity - 1.0) / 2.0 * math.pow(
            1.0 + 12.0 * sub_meters / patch_width, -0.5
        )
        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_permittivity))
        top = (eff_permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_permittivity - 0.258) * (patch_width / sub_meters + 0.8)
        delta_length = 0.412 * sub_meters * top / bottom
        patch_length = effective_length - 2.0 * delta_length
        k = 2.0 * math.pi / eff_permittivity
        g = math.pi * patch_width / (120.0 * math.pi * wavelength) * (1.0 - math.pow(k * sub_meters, 2) / 24)
        res = 1.0 / (2.0 * g)
        offset_pin_pos = patch_length / math.pi * math.asin(math.sqrt(50.0 / res))
        return {
            "freq_hz": freq_hz,
            "patch_width": patch_width,
            "patch_length": patch_length,
            "resistance": res,
            "sub_meters": sub_meters,
            "sub_permittivity": sub_permittivity,
            "wavelength": wavelength,
            "offset_pin_pos": offset_pin_pos,
        }

    def _ordered_parameters(self, parameters):
        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Set up a patch antenna in HFSS."""
        for obj_name in self.object_list.keys():
            if obj_name.startswith("PerfE") or obj_name.startswith("gnd_") or obj_name.startswith("ant_"):
                bound = self._app.assign_perfecte_to_sheets(obj_name)
                bound.name = "PerfE_" + obj_name
                self.boundaries[bound.name] = bound
            elif obj_name.startswith("coax_"):
                obj = self.object_list[obj_name]
                face_id = obj.faces[0].edges[0].id
                for face in obj.faces:
                    if len(face.edges) == 2:
                        face_id = face.id
                        break
                coax_bound = self._app.assign_perfecte_to_sheets(face_id)
                coax_bound.name = "PerfE_" + obj_name
                self.boundaries[coax_bound.name] = coax_bound

        port_count = 1
        for item in list(self.object_list.keys()):
            terminal_references = []
            port_lump = port = port_cap = None
            if f"port_lump_{self.name}" in item:
                port_lump = self.object_list[item]
                terminal_references = [
                    i
                    for i in port_lump.touching_objects
                    if self._app.modeler[i]
                    and (
                        self._app.modeler[i].object_type == "Sheet"
                        or self._app.materials[self._app.modeler[i].material_name].is_conductor()
                    )
                ]
                if len(terminal_references) > 1:
                    terminal_references = terminal_references[1:]
            elif f"port_{self.name}" in item and not item.startswith("port_cap_"):
                port = self.object_list[item]
                port_suffix = item.replace(f"port_{self.name}", "", 1)
                matching_port_cap = f"port_cap_{self.name}{port_suffix}"
                if matching_port_cap in self.object_list:
                    port_cap = self.object_list[matching_port_cap]

            if port_lump:
                port1 = self._app.lumped_port(
                    assignment=item,
                    reference=terminal_references,
                    impedance=50,
                    name="port_" + self.name + "_" + str(port_count),
                    renormalize=True,
                    deembed=False,
                )
                self.excitations[port1.name] = port1
                port_count += 1

                if self._app.solution_type == "Terminal":
                    self._CommonAntenna__excitation_type = "Terminal_Lumped"
                else:
                    self._app.solution_type = "Modal_Lumped"
            elif port:
                if self._app.solution_type == "Terminal" and port_cap:
                    terminal_references = port_cap.name
                port1 = self._app.wave_port(
                    assignment=port,
                    reference=terminal_references,
                    name="port_" + self.name + "_" + str(port_count),
                )
                self.excitations[port1.name] = port1
                port_count += 1

                if self._app.solution_type == "Terminal":
                    self._CommonAntenna__excitation_type = "Terminal_Waveport"
                else:
                    self._app.solution_type = "Modal_Waveport"

        self._update_port_sources()
        return True

    def _update_port_sources(self):
        return None

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class RectangularPatchProbe(CommonPatch):
    """Manages a rectangular patch antenna with a coaxial probe.

    This class is accessible through the ``Hfss`` object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material.
        If the material is not defined, a new material, ``parametrized``, is created.
        The default is ``"FR4_epoxy"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    substrate_height : float, optional
        Substrate height. The default is ``1.575``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.RectangularPatchProbe`
        Patch antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Microstrip Antennas," *Antenna Theory*, 2nd Ed. New York: Wiley, 1997.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import RectangularPatchProbe
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = RectangularPatchProbe(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "RectangularPatchProbe"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        length_unit = self.length_unit
        light_speed = constants.SpeedOfLight  # m/s
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

        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((sub_permittivity + 1.0) / 2.0))

        eff_permittivity = (sub_permittivity + 1.0) / 2.0 + (sub_permittivity - 1.0) / 2.0 * math.pow(
            1.0 + 12.0 * sub_meters / patch_width, -0.5
        )

        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_permittivity))

        top = (eff_permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_permittivity - 0.258) * (patch_width / sub_meters + 0.8)

        delta_length = 0.412 * sub_meters * top / bottom

        patch_length = effective_length - 2.0 * delta_length

        # eff_WL_meters = wavelength / math.sqrt(eff_permittivity)

        k = 2.0 * math.pi / eff_permittivity
        g = math.pi * patch_width / (120.0 * math.pi * wavelength) * (1.0 - math.pow(k * sub_meters, 2) / 24)

        # impedance at edge of patch
        res = 1.0 / (2.0 * g)
        offset_pin_pos = patch_length / math.pi * math.asin(math.sqrt(50.0 / res))

        patch_x = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["patch_x"] = patch_x

        patch_y = constants.unit_converter(patch_length, "Length", "meter", length_unit)
        parameters["patch_y"] = patch_y

        feed_x = 0.0
        parameters["feed_x"] = feed_x

        feed_y = constants.unit_converter(offset_pin_pos, "Length", "meter", length_unit)
        parameters["feed_y"] = feed_y

        sub_h = self.substrate_height
        parameters["sub_h"] = sub_h

        sub_x = constants.unit_converter(1.5 * patch_width + 6.0 * sub_meters, "Length", "meter", length_unit)

        parameters["sub_x"] = sub_x

        sub_y = constants.unit_converter(1.5 * patch_length + 6.0 * sub_meters, "Length", "meter", length_unit)
        parameters["sub_y"] = sub_y

        coax_inner_rad = constants.unit_converter(0.025 * (1e8 / freq_hz), "Length", "meter", length_unit)

        parameters["coax_inner_rad"] = coax_inner_rad

        coax_outer_rad = constants.unit_converter(0.085 * (1e8 / freq_hz), "Length", "meter", length_unit)
        parameters["coax_outer_rad"] = coax_outer_rad

        feed_length = constants.unit_converter(wavelength / 6.0, "Length", "meter", length_unit)
        parameters["feed_length"] = feed_length

        gnd_x = sub_x
        gnd_y = sub_y

        parameters["gnd_x"] = gnd_x
        parameters["gnd_y"] = gnd_y

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """
        Draw rectangular patch antenna with coaxial probe.

        Once the antenna is created, this method will not be used anymore.
        """
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Map parameters
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        feed_x = self.synthesis_parameters.feed_x.hfss_variable
        feed_y = self.synthesis_parameters.feed_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        coax_inner_rad = self.synthesis_parameters.coax_inner_rad.hfss_variable
        coax_outer_rad = self.synthesis_parameters.coax_outer_rad.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        gnd_x = self.synthesis_parameters.gnd_x.hfss_variable
        gnd_y = self.synthesis_parameters.gnd_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Substrate
        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        # Ground
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + gnd_x + "/2", "-" + gnd_y + "/2", "0"],
            sizes=[gnd_x, gnd_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        # Antenna
        ant = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + patch_x + "/2",
                "-" + patch_y + "/2",
                sub_h,
            ],
            sizes=[patch_x, patch_y],
            name="ant_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1

        void = self._app.modeler.create_circle(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_outer_rad,
            name="void_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )

        self._app.modeler.subtract(gnd, void, False)

        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_inner_rad,
            height=sub_h,
            name="feed_pin_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_pin.color = (255, 128, 65)

        feed_coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_inner_rad,
            height="-" + feed_length,
            name="feed_coax_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_coax.color = (255, 128, 65)

        coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_outer_rad,
            height="-" + feed_length,
            name="coax_" + antenna_name,
            material="Teflon (tm)",
            new_properties={"Coordinate System": coordinate_system},
        )
        coax.color = (128, 255, 255)

        port_cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "-" + feed_length],
            radius=coax_outer_rad,
            height="-" + sub_h + "/" + str(10),
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (132, 132, 193)

        p1 = self._app.modeler.create_circle(
            orientation=2,
            origin=[feed_x, feed_y, "-" + feed_length],
            radius=coax_outer_rad,
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (128, 0, 0)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[feed_pin.name] = feed_pin
        self.object_list[feed_coax.name] = feed_coax
        self.object_list[coax.name] = coax
        self.object_list[port_cap.name] = port_cap
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        sub.group_name = antenna_name
        gnd.group_name = antenna_name
        ant.group_name = antenna_name
        feed_pin.group_name = antenna_name
        feed_coax.group_name = antenna_name
        coax.group_name = antenna_name
        port_cap.group_name = antenna_name
        p1.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemented."""
        pass


class EllipticalPatchMixin:
    def _create_patch_ellipse(self, patch_x, patch_y, sub_h, antenna_name, coordinate_system):
        ant = self._app.modeler.create_ellipse(
            orientation=2,
            origin=[0, 0, sub_h],
            major_radius=patch_x + "/2",
            ratio=patch_y + "/" + patch_x,
            name="ant_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1
        return ant


class EllipticalEdge(EllipticalPatchMixin, CommonPatch):
    """Manages an elliptical patch antenna with an edge feed."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "EllipticalEdge"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        base = self._patch_synthesis_base()
        if not base:
            return parameters

        length_unit = self.length_unit
        quarterwave_imped = math.sqrt(50.0 * base["resistance"])
        u_strip1 = self._transmission_line_calculator.microstrip_calculator(
            base["sub_meters"], base["sub_permittivity"], quarterwave_imped, 90.0
        )
        u_strip2 = self._transmission_line_calculator.microstrip_calculator(
            base["sub_meters"], base["sub_permittivity"], 50.0, 150.0
        )

        parameters["patch_x"] = constants.unit_converter(base["patch_width"], "Length", "meter", length_unit)
        parameters["patch_y"] = constants.unit_converter(base["patch_length"], "Length", "meter", length_unit)
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            1.5 * base["patch_width"] + 6.0 * base["sub_meters"], "Length", "meter", length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            2.1 * (u_strip2[1] + u_strip1[1] + base["patch_length"] / 2), "Length", "meter", length_unit
        )
        parameters["edge_feed_width"] = constants.unit_converter(u_strip1[0], "Length", "meter", length_unit)
        parameters["edge_feed_length"] = constants.unit_converter(u_strip1[1], "Length", "meter", length_unit)
        parameters["feed_width"] = constants.unit_converter(u_strip2[0], "Length", "meter", length_unit)
        parameters["feed_length"] = constants.unit_converter(u_strip2[1], "Length", "meter", length_unit)
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
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        edge_feed_width = self.synthesis_parameters.edge_feed_width.hfss_variable
        edge_feed_length = self.synthesis_parameters.edge_feed_length.hfss_variable
        feed_width = self.synthesis_parameters.feed_width.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1
        ant = self._create_patch_ellipse(patch_x, patch_y, sub_h, antenna_name, coordinate_system)
        edge_feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + edge_feed_width + "/2", "0", sub_h],
            sizes=[edge_feed_width, patch_y + "/2+" + edge_feed_length],
            name="edge_feed_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        edge_feed.color = (255, 128, 65)
        feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + feed_width + "/2", patch_y + "/2+" + edge_feed_length, sub_h],
            sizes=[feed_width, feed_length],
            name="feed_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        feed.color = (255, 128, 65)
        self._app.modeler.unite([ant, edge_feed, feed])
        p1 = self._app.modeler.create_rectangle(
            orientation=1,
            origin=["-" + feed_width + "/2", patch_y + "/2+" + edge_feed_length + "+" + feed_length, "0"],
            sizes=[sub_h, feed_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (255, 128, 65)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[p1.name] = p1
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        for obj in self.object_list.values():
            obj.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class EllipticalInset(EllipticalPatchMixin, CommonPatch):
    """Manages an elliptical patch antenna with an inset feed."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "EllipticalInset"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        base = self._patch_synthesis_base()
        if not base:
            return parameters

        length_unit = self.length_unit
        u_strip = self._transmission_line_calculator.microstrip_calculator(
            base["sub_meters"], base["sub_permittivity"], 50.0, 150.0
        )
        microstrip_width = u_strip[0]
        microstrip_length = u_strip[1]

        parameters["patch_x"] = constants.unit_converter(base["patch_width"], "Length", "meter", length_unit)
        parameters["patch_y"] = constants.unit_converter(base["patch_length"], "Length", "meter", length_unit)
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            1.5 * base["patch_width"] + 6.0 * base["sub_meters"], "Length", "meter", length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            2.1 * (microstrip_length + base["patch_length"] / 2), "Length", "meter", length_unit
        )
        parameters["inset_distance"] = constants.unit_converter(
            base["patch_length"] / 2 - base["offset_pin_pos"], "Length", "meter", length_unit
        )
        microstrip_width = constants.unit_converter(microstrip_width, "Length", "meter", length_unit)
        microstrip_length = constants.unit_converter(microstrip_length, "Length", "meter", length_unit)
        parameters["inset_gap"] = round(microstrip_width / 2, 3)
        parameters["feed_width"] = round(microstrip_width, 3)
        parameters["feed_length"] = round(microstrip_length, 3)
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
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        inset_distance = self.synthesis_parameters.inset_distance.hfss_variable
        inset_gap = self.synthesis_parameters.inset_gap.hfss_variable
        feed_width = self.synthesis_parameters.feed_width.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1
        ant = self._create_patch_ellipse(patch_x, patch_y, sub_h, antenna_name, coordinate_system)
        cutout = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + feed_width + "/2-" + inset_gap, patch_y + "/2-" + inset_distance, sub_h],
            sizes=[feed_width + "+2*" + inset_gap, feed_length],
            name="cutout_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.subtract(ant, cutout, False)
        feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + feed_width + "/2", patch_y + "/2-" + inset_distance, sub_h],
            sizes=[feed_width, feed_length + "+" + inset_distance],
            name="feed_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        feed.color = (255, 128, 65)
        self._app.modeler.unite([ant, feed])
        p1 = self._app.modeler.create_rectangle(
            orientation=1,
            origin=["-" + feed_width + "/2", patch_y + "/2+" + feed_length, "0"],
            sizes=[sub_h, feed_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (255, 128, 65)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[p1.name] = p1
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        for obj in self.object_list.values():
            obj.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class EllipticalProbe(EllipticalPatchMixin, CommonPatch):
    """Manages an elliptical patch antenna with a coaxial probe."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "EllipticalProbe"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        base = self._patch_synthesis_base()
        if not base:
            return parameters

        length_unit = self.length_unit
        patch_size = constants.unit_converter(base["patch_length"], "Length", "meter", length_unit)
        parameters["patch_x"] = patch_size
        parameters["patch_y"] = patch_size
        parameters["feed_x"] = constants.unit_converter(base["offset_pin_pos"], "Length", "meter", length_unit)
        parameters["feed_y"] = 0.0
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            base["patch_length"] + 6.0 * base["sub_meters"], "Length", "meter", length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            base["patch_length"] + 6.0 * base["sub_meters"], "Length", "meter", length_unit
        )
        parameters["coax_inner_rad"] = constants.unit_converter(
            0.025 * (1e8 / base["freq_hz"]), "Length", "meter", length_unit
        )
        parameters["coax_outer_rad"] = constants.unit_converter(
            0.085 * (1e8 / base["freq_hz"]), "Length", "meter", length_unit
        )
        parameters["feed_length"] = constants.unit_converter(base["wavelength"] / 6.0, "Length", "meter", length_unit)
        parameters["gnd_x"] = parameters["sub_x"]
        parameters["gnd_y"] = parameters["sub_y"]
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]
        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False
        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material is not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        feed_x = self.synthesis_parameters.feed_x.hfss_variable
        feed_y = self.synthesis_parameters.feed_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        coax_inner_rad = self.synthesis_parameters.coax_inner_rad.hfss_variable
        coax_outer_rad = self.synthesis_parameters.coax_outer_rad.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        gnd_x = self.synthesis_parameters.gnd_x.hfss_variable
        gnd_y = self.synthesis_parameters.gnd_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + gnd_x + "/2", "-" + gnd_y + "/2", "0"],
            sizes=[gnd_x, gnd_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1
        ant = self._create_patch_ellipse(patch_x, patch_y, sub_h, antenna_name, coordinate_system)
        void = self._app.modeler.create_circle(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_outer_rad,
            name="void_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.subtract(gnd, void, False)
        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_inner_rad,
            height=sub_h,
            name="feed_pin_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_pin.color = (255, 128, 65)
        feed_coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_inner_rad,
            height="-" + feed_length,
            name="feed_coax_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_coax.color = (255, 128, 65)
        coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_outer_rad,
            height="-" + feed_length,
            name="coax_" + antenna_name,
            material="Teflon (tm)",
            new_properties={"Coordinate System": coordinate_system},
        )
        coax.color = (128, 255, 255)
        port_cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "-" + feed_length],
            radius=coax_outer_rad,
            height="-" + sub_h + "/10",
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (132, 132, 193)
        p1 = self._app.modeler.create_circle(
            orientation=2,
            origin=[feed_x, feed_y, "-" + feed_length],
            radius=coax_outer_rad,
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (128, 0, 0)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[feed_pin.name] = feed_pin
        self.object_list[feed_coax.name] = feed_coax
        self.object_list[coax.name] = coax
        self.object_list[port_cap.name] = port_cap
        self.object_list[p1.name] = p1
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        for obj in self.object_list.values():
            obj.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class MbyNPatchArray(CommonPatch):
    """Manages an M-by-N rectangular patch array."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "material": "Teflon (tm)",
        "material_properties": {"permittivity": 2.1},
        "outer_boundary": "",
        "substrate_height": 1.272,
        "number_of_patches_x": 2,
        "number_of_patches_y": 3,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "MbyNPatchArray"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        base = self._patch_synthesis_base()
        if not base:
            return parameters

        length_unit = self.length_unit
        patch_count_x = int(self.number_of_patches_x)
        patch_count_y = int(self.number_of_patches_y)
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        parameters["patch_count_x"] = patch_count_x
        parameters["patch_count_y"] = patch_count_y
        parameters["patch_x"] = constants.unit_converter(base["patch_width"], "Length", "meter", length_unit)
        parameters["patch_y"] = constants.unit_converter(base["patch_length"], "Length", "meter", length_unit)
        parameters["feed_x"] = 0.0
        parameters["feed_y"] = constants.unit_converter(base["offset_pin_pos"], "Length", "meter", length_unit)
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            (patch_count_x - 1) * (1.5 * base["patch_width"] + 6.0 * base["sub_meters"]) + 2.0 * base["patch_width"],
            "Length",
            "meter",
            length_unit,
        )
        parameters["sub_y"] = constants.unit_converter(
            (patch_count_y - 1) * (1.5 * base["patch_length"] + 6.0 * base["sub_meters"]) + 2.0 * base["patch_length"],
            "Length",
            "meter",
            length_unit,
        )
        parameters["patch_spacing_x"] = constants.unit_converter(
            1.5 * base["patch_width"] + 6.0 * base["sub_meters"], "Length", "meter", length_unit
        )
        parameters["patch_spacing_y"] = constants.unit_converter(
            1.5 * base["patch_length"] + 6.0 * base["sub_meters"], "Length", "meter", length_unit
        )
        parameters["coax_inner_rad"] = constants.unit_converter(0.25 * (10.0 / freq_ghz), "Length", "mm", length_unit)
        parameters["coax_outer_rad"] = constants.unit_converter(0.85 * (10.0 / freq_ghz), "Length", "mm", length_unit)
        parameters["feed_length"] = constants.unit_converter(base["wavelength"] / 6.0, "Length", "meter", length_unit)
        parameters["gnd_x"] = parameters["sub_x"]
        parameters["gnd_y"] = parameters["sub_y"]
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
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        patch_spacing_x = self.synthesis_parameters.patch_spacing_x.hfss_variable
        patch_spacing_y = self.synthesis_parameters.patch_spacing_y.hfss_variable
        feed_x = self.synthesis_parameters.feed_x.hfss_variable
        feed_y = self.synthesis_parameters.feed_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        coax_inner_rad = self.synthesis_parameters.coax_inner_rad.hfss_variable
        coax_outer_rad = self.synthesis_parameters.coax_outer_rad.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        gnd_x = self.synthesis_parameters.gnd_x.hfss_variable
        gnd_y = self.synthesis_parameters.gnd_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system
        patch_count_x = int(self.number_of_patches_x)
        patch_count_y = int(self.number_of_patches_y)

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + gnd_x + "/2", "-" + gnd_y + "/2", "0"],
            sizes=[gnd_x, gnd_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1
        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd

        for i in range(patch_count_x):
            for j in range(patch_count_y):
                x_index = i - (patch_count_x - 1) / 2
                y_index = j - (patch_count_y - 1) / 2
                patch_center_x = f"({x_index})*{patch_spacing_x}"
                patch_center_y = f"({y_index})*{patch_spacing_y}"
                feed_origin = [patch_center_x + "+" + feed_x, patch_center_y + "+" + feed_y, "0"]

                ant = self._app.modeler.create_rectangle(
                    orientation=2,
                    origin=[patch_center_x + "-" + patch_x + "/2", patch_center_y + "-" + patch_y + "/2", sub_h],
                    sizes=[patch_x, patch_y],
                    name=f"ant_{antenna_name}_{i}_{j}",
                    new_properties={"Coordinate System": coordinate_system},
                )
                ant.color = (255, 128, 65)
                ant.transparency = 0.1
                void = self._app.modeler.create_circle(
                    orientation=2,
                    origin=feed_origin,
                    radius=coax_outer_rad,
                    name=f"void_{antenna_name}_{i}_{j}",
                    new_properties={"Coordinate System": coordinate_system},
                )
                self._app.modeler.subtract(gnd, void, False)
                feed_pin = self._app.modeler.create_cylinder(
                    orientation=2,
                    origin=feed_origin,
                    radius=coax_inner_rad,
                    height=sub_h,
                    name=f"feed_pin_{antenna_name}_{i}_{j}",
                    material="pec",
                    new_properties={"Coordinate System": coordinate_system},
                )
                feed_pin.color = (255, 128, 65)
                feed_coax = self._app.modeler.create_cylinder(
                    orientation=2,
                    origin=feed_origin,
                    radius=coax_inner_rad,
                    height="-" + feed_length,
                    name=f"feed_coax_{antenna_name}_{i}_{j}",
                    material="pec",
                    new_properties={"Coordinate System": coordinate_system},
                )
                feed_coax.color = (255, 128, 65)
                coax = self._app.modeler.create_cylinder(
                    orientation=2,
                    origin=feed_origin,
                    radius=coax_outer_rad,
                    height="-" + feed_length,
                    name=f"coax_{antenna_name}_{i}_{j}",
                    material="Teflon (tm)",
                    new_properties={"Coordinate System": coordinate_system},
                )
                coax.color = (128, 255, 255)
                port_cap = self._app.modeler.create_cylinder(
                    orientation=2,
                    origin=[patch_center_x + "+" + feed_x, patch_center_y + "+" + feed_y, "-" + feed_length],
                    radius=coax_outer_rad,
                    height="-" + sub_h + "/10",
                    name=f"port_cap_{antenna_name}_{i}_{j}",
                    material="pec",
                    new_properties={"Coordinate System": coordinate_system},
                )
                port_cap.color = (132, 132, 193)
                port = self._app.modeler.create_circle(
                    orientation=2,
                    origin=[patch_center_x + "+" + feed_x, patch_center_y + "+" + feed_y, "-" + feed_length],
                    radius=coax_outer_rad,
                    name=f"port_{antenna_name}_{i}_{j}",
                    new_properties={"Coordinate System": coordinate_system},
                )
                port.color = (128, 0, 0)

                for obj in [ant, feed_pin, feed_coax, coax, port_cap, port]:
                    self.object_list[obj.name] = obj

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        for obj in self.object_list.values():
            obj.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class SeqRotated2Patch(CommonPatch):
    """Manages a sequentially rotated four-patch array."""

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 5.0,
        "frequency_unit": "GHz",
        "material": "Teflon (tm)",
        "material_properties": {"permittivity": 2.1},
        "outer_boundary": "",
        "substrate_height": 1.272,
        "feed_rotation_angle": 45.0,
        "element_1_rotation_angle": 0.0,
        "element_2_rotation_angle": -90.0,
        "element_3_rotation_angle": -180.0,
        "element_4_rotation_angle": -270.0,
        "element_1_port_phase": 0.0,
        "element_2_port_phase": 90.0,
        "element_3_port_phase": 180.0,
        "element_4_port_phase": 270.0,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "SeqRotated2Patch"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        scale = 5.0 / freq_ghz
        length_unit = self.length_unit

        def scaled(value):
            return constants.unit_converter(scale * value, "Length", "mm", length_unit)

        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = scaled(80.0)
        parameters["sub_y"] = scaled(80.0)
        parameters["patch_diameter"] = scaled(23.53)
        parameters["patch_spacing_x"] = scaled(35.29)
        parameters["patch_spacing_y"] = scaled(35.29)
        parameters["notch_length"] = scaled(1.502)
        parameters["notch_width"] = scaled(3.004)
        parameters["feed_pin_offset"] = scaled(3.663)
        parameters["coax_inner_rad"] = constants.unit_converter(0.25, "Length", "mm", length_unit)
        parameters["coax_outer_rad"] = constants.unit_converter(0.85, "Length", "mm", length_unit)
        parameters["feed_length"] = constants.unit_converter(2.5, "Length", "mm", length_unit)
        parameters["feed_rotation_angle"] = self.feed_rotation_angle
        parameters["element_1_rotation_angle"] = self.element_1_rotation_angle
        parameters["element_2_rotation_angle"] = self.element_2_rotation_angle
        parameters["element_3_rotation_angle"] = self.element_3_rotation_angle
        parameters["element_4_rotation_angle"] = self.element_4_rotation_angle
        parameters["element_1_port_phase"] = self.element_1_port_phase
        parameters["element_2_port_phase"] = self.element_2_port_phase
        parameters["element_3_port_phase"] = self.element_3_port_phase
        parameters["element_4_port_phase"] = self.element_4_port_phase
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
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        patch_diameter = self.synthesis_parameters.patch_diameter.hfss_variable
        patch_spacing_x = self.synthesis_parameters.patch_spacing_x.hfss_variable
        patch_spacing_y = self.synthesis_parameters.patch_spacing_y.hfss_variable
        notch_length = self.synthesis_parameters.notch_length.hfss_variable
        notch_width = self.synthesis_parameters.notch_width.hfss_variable
        feed_pin_offset = self.synthesis_parameters.feed_pin_offset.hfss_variable
        coax_inner_rad = self.synthesis_parameters.coax_inner_rad.hfss_variable
        coax_outer_rad = self.synthesis_parameters.coax_outer_rad.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        feed_rotation_angle = self.synthesis_parameters.feed_rotation_angle.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        rotations = [
            self.synthesis_parameters.element_1_rotation_angle.hfss_variable,
            self.synthesis_parameters.element_2_rotation_angle.hfss_variable,
            self.synthesis_parameters.element_3_rotation_angle.hfss_variable,
            self.synthesis_parameters.element_4_rotation_angle.hfss_variable,
        ]
        centers = [
            [patch_spacing_x + "/2", patch_spacing_y + "/2", "0"],
            ["-" + patch_spacing_x + "/2", patch_spacing_y + "/2", "0"],
            ["-" + patch_spacing_x + "/2", "-" + patch_spacing_y + "/2", "0"],
            [patch_spacing_x + "/2", "-" + patch_spacing_y + "/2", "0"],
        ]
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1
        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd

        for idx, (center, rotation_angle) in enumerate(zip(centers, rotations)):
            ant = self._app.modeler.create_circle(
                orientation=2,
                origin=[0, 0, sub_h],
                radius=patch_diameter + "/2",
                name=f"ant_{antenna_name}_{idx}",
                new_properties={"Coordinate System": coordinate_system},
            )
            notch1 = self._app.modeler.create_rectangle(
                orientation=2,
                origin=[patch_diameter + "/2", "-" + notch_width + "/2", sub_h],
                sizes=["-" + notch_length, notch_width],
                name=f"notch_1_{antenna_name}_{idx}",
                new_properties={"Coordinate System": coordinate_system},
            )
            notch2 = self._app.modeler.create_rectangle(
                orientation=2,
                origin=["-" + patch_diameter + "/2", "-" + notch_width + "/2", sub_h],
                sizes=[notch_length, notch_width],
                name=f"notch_2_{antenna_name}_{idx}",
                new_properties={"Coordinate System": coordinate_system},
            )
            self._app.modeler.subtract(ant, [notch1, notch2], False)
            self._app.modeler.rotate(ant, "Z", rotation_angle)
            self._app.modeler.move(ant, center)
            ant.color = (255, 128, 65)
            ant.transparency = 0.1

            rotation_expr = feed_rotation_angle + "+" + rotation_angle
            feed_x = feed_pin_offset + "*cos((" + rotation_expr + ")*pi/180)"
            feed_y = feed_pin_offset + "*sin((" + rotation_expr + ")*pi/180)"
            feed_origin = [feed_x, feed_y, "0"]

            feed_pin = self._app.modeler.create_cylinder(
                orientation=2,
                origin=feed_origin,
                radius=coax_inner_rad,
                height=sub_h,
                name=f"feed_pin_{antenna_name}_{idx}",
                material="pec",
                new_properties={"Coordinate System": coordinate_system},
            )
            feed_pin.color = (255, 128, 65)
            feed_coax = self._app.modeler.create_cylinder(
                orientation=2,
                origin=feed_origin,
                radius=coax_inner_rad,
                height="-" + feed_length,
                name=f"feed_coax_{antenna_name}_{idx}",
                material="pec",
                new_properties={"Coordinate System": coordinate_system},
            )
            feed_coax.color = (255, 128, 65)
            coax = self._app.modeler.create_cylinder(
                orientation=2,
                origin=feed_origin,
                radius=coax_outer_rad,
                height="-" + feed_length,
                name=f"coax_{antenna_name}_{idx}",
                material="Teflon (tm)",
                new_properties={"Coordinate System": coordinate_system},
            )
            coax.color = (128, 255, 255)
            port_cap = self._app.modeler.create_cylinder(
                orientation=2,
                origin=[feed_x, feed_y, "-" + feed_length],
                radius=coax_outer_rad,
                height="-" + sub_h + "/10",
                name=f"port_cap_{antenna_name}_{idx}",
                material="pec",
                new_properties={"Coordinate System": coordinate_system},
            )
            port_cap.color = (132, 132, 193)
            port = self._app.modeler.create_circle(
                orientation=2,
                origin=[feed_x, feed_y, "-" + feed_length],
                radius=coax_outer_rad,
                name=f"port_{antenna_name}_{idx}",
                new_properties={"Coordinate System": coordinate_system},
            )
            port.color = (128, 0, 0)
            void = self._app.modeler.create_circle(
                orientation=2,
                origin=feed_origin,
                radius=coax_outer_rad,
                name=f"void_{antenna_name}_{idx}",
                new_properties={"Coordinate System": coordinate_system},
            )
            self._app.modeler.move(
                [feed_pin.name, feed_coax.name, coax.name, port_cap.name, port.name, void.name],
                center,
            )
            self._app.modeler.subtract(gnd, void, False)

            for obj in [ant, feed_pin, feed_coax, coax, port_cap, port]:
                self.object_list[obj.name] = obj

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        for obj in self.object_list.values():
            obj.group_name = antenna_name
        return True

    def _update_port_sources(self):
        if len(self.excitations) != 4:
            return None
        phases = [
            self.element_1_port_phase,
            self.element_2_port_phase,
            self.element_3_port_phase,
            self.element_4_port_phase,
        ]
        assignments = {
            port_name: (1, f"{phase}deg") for port_name, phase in zip(sorted(self.excitations.keys()), phases)
        }
        self._app.edit_sources(assignments)
        return None

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class RectangularPatchInset(CommonPatch):
    """Manages a rectangular patch antenna inset fed.

    This class is accessible through the ``Hfss`` object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. If the material is not defined, a new
        material, ``parametrized``, is created. The default is ``"FR4_epoxy"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    substrate_height : float, optional
        Substrate height. The default is ``1.575``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.RectangularPatchInset`
        Patch antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Microstrip Antennas," *Antenna Theory*, 2nd Ed. New York: Wiley, 1997.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import RectangularPatchInset
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = RectangularPatchInset(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "RectangularPatchInset"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        length_unit = self.length_unit
        light_speed = constants.SpeedOfLight  # m/s
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

        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((sub_permittivity + 1.0) / 2.0))

        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")

        eff_permittivity = (sub_permittivity + 1.0) / 2.0 + (sub_permittivity - 1.0) / 2.0 * math.pow(
            1.0 + 12.0 * sub_meters / patch_width, -0.5
        )

        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_permittivity))

        top = (eff_permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_permittivity - 0.258) * (patch_width / sub_meters + 0.8)

        delta_length = 0.412 * sub_meters * top / bottom

        patch_length = effective_length - 2.0 * delta_length

        # eff_WL_meters = wavelength / math.sqrt(eff_permittivity)

        k = 2.0 * math.pi / eff_permittivity
        g = math.pi * patch_width / (120.0 * math.pi * wavelength) * (1.0 - math.pow(k * sub_meters, 2) / 24)

        # impedance at edge of patch
        res = 1.0 / (2.0 * g)
        inset_distance_meter = patch_length / math.pi * math.asin(math.sqrt(50.0 / res))

        # quarterwave_imped = math.sqrt(50.0 * res)

        u_strip = self._transmission_line_calculator.microstrip_calculator(sub_meters, sub_permittivity, 50.0, 150.0)

        microstrip_width = u_strip[0]
        microstrip_length = u_strip[1]

        patch_x = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["patch_x"] = patch_x

        patch_y = constants.unit_converter(patch_length, "Length", "meter", length_unit)
        parameters["patch_y"] = patch_y

        sub_h = self.substrate_height
        parameters["sub_h"] = sub_h

        sub_x = constants.unit_converter(1.5 * patch_width + 6.0 * sub_meters, "Length", "meter", length_unit)
        parameters["sub_x"] = sub_x

        sub_y = constants.unit_converter(2.1 * (microstrip_length + patch_length / 2), "Length", "meter", length_unit)

        parameters["sub_y"] = sub_y

        inset_distance = constants.unit_converter(
            patch_length / 2 - inset_distance_meter, "Length", "meter", length_unit
        )

        parameters["inset_distance"] = inset_distance

        microstrip_length = constants.unit_converter(microstrip_length, "Length", "meter", length_unit)
        microstrip_width = constants.unit_converter(microstrip_width, "Length", "meter", length_unit)

        inset_gap = round(microstrip_width / 2, 3)
        parameters["inset_gap"] = inset_gap

        feed_width = round(microstrip_width, 3)
        parameters["feed_width"] = feed_width

        feed_length = round(microstrip_length, 3)
        parameters["feed_length"] = feed_length

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a rectangular patch antenna inset fed.

        Once the antenna is created, this method is not used anymore.
        """
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

        # Map parameters
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        inset_distance = self.synthesis_parameters.inset_distance.hfss_variable
        inset_gap = self.synthesis_parameters.inset_gap.hfss_variable
        feed_width = self.synthesis_parameters.feed_width.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Substrate
        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        # Ground
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        # Antenna
        ant = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + patch_x + "/2",
                "-" + patch_y + "/2",
                sub_h,
            ],
            sizes=[patch_x, patch_y],
            name="ant_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1

        cutout = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + feed_width + "/2" + "-" + inset_gap,
                patch_y + "/2" + "-" + inset_distance,
                sub_h,
            ],
            sizes=[feed_width + "+2*" + inset_gap, feed_length],
            name="cutout_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        cutout.color = (255, 128, 65)

        self._app.modeler.subtract(ant, cutout, False)

        feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + feed_width + "/2",
                patch_y + "/2-" + inset_distance,
                sub_h,
            ],
            sizes=[feed_width, feed_length + "+" + inset_distance],
            name="feed_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        feed.color = (255, 128, 65)

        self._app.modeler.unite([ant, feed])

        p1 = self._app.modeler.create_rectangle(
            orientation=1,
            origin=[
                "-" + feed_width + "/2",
                patch_y + "/2" + "+" + feed_length,
                "0",
            ],
            sizes=[sub_h, feed_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (255, 128, 65)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        sub.group_name = antenna_name
        gnd.group_name = antenna_name
        ant.group_name = antenna_name
        p1.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemented."""
        pass


class RectangularPatchEdge(CommonPatch):
    """Manages a rectangular patch edge antenna.

    This class is accessible through the ``Hfss`` object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. If the material is not defined,
        a new material, ``parametrized``, is created.
        The default is ``"FR4_epoxy"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    substrate_height : float, optional
        Substrate height. The default is ``1.575``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.RectangularPatchEdge`
        Patch antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Microstrip Antennas," *Antenna Theory*, 2nd Ed. New York: Wiley, 1997.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import RectangularPatchEdge
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = RectangularPatchEdge(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 1.575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "RectangularPatchEdge"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        length_unit = self.length_unit
        light_speed = constants.SpeedOfLight  # m/s
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

        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((sub_permittivity + 1.0) / 2.0))

        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")

        eff_permittivity = (sub_permittivity + 1.0) / 2.0 + (sub_permittivity - 1.0) / 2.0 * math.pow(
            1.0 + 12.0 * sub_meters / patch_width, -0.5
        )

        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_permittivity))

        top = (eff_permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_permittivity - 0.258) * (patch_width / sub_meters + 0.8)

        delta_length = 0.412 * sub_meters * top / bottom

        patch_length = effective_length - 2.0 * delta_length

        # eff_WL_meters = wavelength / math.sqrt(eff_permittivity)

        k = 2.0 * math.pi / eff_permittivity
        g = math.pi * patch_width / (120.0 * math.pi * wavelength) * (1.0 - math.pow(k * sub_meters, 2) / 24)

        # impedance at edge of patch
        res = 1.0 / (2.0 * g)
        # offset_pin_pos = patch_length / math.pi * math.asin(math.sqrt(50.0 / res))

        quarterwave_imped = math.sqrt(50.0 * res)

        u_strip1 = self._transmission_line_calculator.microstrip_calculator(
            sub_meters, sub_permittivity, quarterwave_imped, 90.0
        )

        microstrip_edge_width = u_strip1[0]
        microstrip_edge_length = u_strip1[1]

        u_strip2 = self._transmission_line_calculator.microstrip_calculator(sub_meters, sub_permittivity, 50.0, 150.0)

        microstrip_width = u_strip2[0]
        microstrip_length = u_strip2[1]

        patch_x = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["patch_x"] = patch_x

        patch_y = constants.unit_converter(patch_length, "Length", "meter", length_unit)
        parameters["patch_y"] = patch_y

        sub_h = self.substrate_height
        parameters["sub_h"] = sub_h

        sub_x = constants.unit_converter(1.5 * patch_width + 6.0 * sub_meters, "Length", "meter", length_unit)
        parameters["sub_x"] = sub_x

        sub_y = constants.unit_converter(
            2.1 * (microstrip_length + microstrip_edge_length + patch_length / 2),
            "Length",
            "meter",
            length_unit,
        )
        parameters["sub_y"] = sub_y

        edge_feed_width = constants.unit_converter(microstrip_edge_width, "Length", "meter", length_unit)

        parameters["edge_feed_width"] = edge_feed_width

        edge_feed_length = constants.unit_converter(microstrip_edge_length, "Length", "meter", length_unit)
        parameters["edge_feed_length"] = edge_feed_length

        feed_width = constants.unit_converter(microstrip_width, "Length", "meter", length_unit)

        parameters["feed_width"] = feed_width

        feed_length = constants.unit_converter(microstrip_length, "Length", "meter", length_unit)
        parameters["feed_length"] = feed_length

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a rectangular patch edge antenna inset fed.

        Once the antenna is created, this method is not used anymore.
        """
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

        # Map parameters
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        edge_feed_width = self.synthesis_parameters.edge_feed_width.hfss_variable
        edge_feed_length = self.synthesis_parameters.edge_feed_length.hfss_variable
        feed_width = self.synthesis_parameters.feed_width.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Substrate
        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        # Ground
        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        # Antenna
        ant = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + patch_x + "/2",
                "-" + patch_y + "/2",
                sub_h,
            ],
            sizes=[patch_x, patch_y],
            name="ant_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1

        edge_feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + edge_feed_width + "/2",
                "0",
                sub_h,
            ],
            sizes=[edge_feed_width, patch_y + "/2" + "+" + edge_feed_length],
            name="cutout_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        edge_feed.color = (255, 128, 65)

        feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + feed_width + "/2",
                patch_y + "/2" + "+" + edge_feed_length,
                sub_h,
            ],
            sizes=[feed_width, feed_length],
            name="feed_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        feed.color = (255, 128, 65)

        self._app.modeler.unite([ant, edge_feed, feed])

        p1 = self._app.modeler.create_rectangle(
            orientation=1,
            origin=[
                "-" + feed_width + "/2",
                patch_y + "/2" + "+" + edge_feed_length + "+" + feed_length,
                "0",
            ],
            sizes=[sub_h, feed_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (255, 128, 65)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        sub.group_name = antenna_name
        gnd.group_name = antenna_name
        ant.group_name = antenna_name
        p1.group_name = antenna_name
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemented."""
        pass
