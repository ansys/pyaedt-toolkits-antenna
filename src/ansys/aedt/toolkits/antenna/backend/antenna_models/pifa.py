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
from ansys.aedt.toolkits.common.backend.logger_handler import logger

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna


class CommonPIFA(CommonAntenna):
    """Provides base methods common to PIFA antennas."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "PIFA"
        CommonAntenna.__init__(self, _default_input_parameters, *args, **kwargs)
        if "substrate_height" not in kwargs:
            self.substrate_height = constants.unit_converter(
                self.substrate_height, "Length", _default_input_parameters["length_unit"], self.length_unit
            )

    @property
    def material(self):
        """Substrate material."""
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
                    for antenna_obj in self.object_list.values():
                        if antenna_obj.material_name == self.material.lower() and "coax" not in antenna_obj.name:
                            antenna_obj.material_name = value

                self._input_parameters.material = value
                parameters = self.synthesis()
                self.update_synthesis_parameters(parameters)
                if self.object_list:
                    self.set_variables_in_hfss()
        else:
            self._input_parameters.material = value

    @property
    def material_properties(self):
        """Substrate material properties."""
        return self._input_parameters.material_properties

    @property
    def substrate_height(self):
        """Substrate height."""
        return self._input_parameters.substrate_height

    @substrate_height.setter
    def substrate_height(self, value):
        self._input_parameters.substrate_height = value

        if self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    def _get_permittivity(self):
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

    @staticmethod
    def _effective_permittivity(trace_width, substrate_height, permittivity):
        return (permittivity + 1.0) / 2.0 + (permittivity - 1.0) / 2.0 * math.pow(
            1.0 + 12.0 * substrate_height / trace_width, -0.5
        )

    def _ordered_parameters(self, parameters):
        return OrderedDict((key, parameters[key]) for key in sorted(parameters.keys()))

    def _map_probe_feed_parameters(self):
        return {
            "patch_x": self.synthesis_parameters.patch_x.hfss_variable,
            "patch_y": self.synthesis_parameters.patch_y.hfss_variable,
            "short_x": self.synthesis_parameters.short_x.hfss_variable,
            "short_y": self.synthesis_parameters.short_y.hfss_variable,
            "sub_h": self.synthesis_parameters.sub_h.hfss_variable,
            "sub_x": self.synthesis_parameters.sub_x.hfss_variable,
            "sub_y": self.synthesis_parameters.sub_y.hfss_variable,
            "feed_x": self.synthesis_parameters.feed_x.hfss_variable,
            "feed_y": self.synthesis_parameters.feed_y.hfss_variable,
            "coax_inner_rad": self.synthesis_parameters.coax_inner_rad.hfss_variable,
            "coax_outer_rad": self.synthesis_parameters.coax_outer_rad.hfss_variable,
            "feed_length": self.synthesis_parameters.feed_length.hfss_variable,
            "gnd_x": self.synthesis_parameters.gnd_x.hfss_variable,
            "gnd_y": self.synthesis_parameters.gnd_y.hfss_variable,
            "pos_x": self.synthesis_parameters.pos_x.hfss_variable,
            "pos_y": self.synthesis_parameters.pos_y.hfss_variable,
            "pos_z": self.synthesis_parameters.pos_z.hfss_variable,
        }

    def _create_probe_feed_objects(self):
        parameters = self._map_probe_feed_parameters()
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + parameters["sub_x"] + "/2", "-" + parameters["sub_y"] + "/2", "0"],
            sizes=[parameters["sub_x"], parameters["sub_y"], parameters["sub_h"]],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + parameters["gnd_x"] + "/2", "-" + parameters["gnd_y"] + "/2", "0"],
            sizes=[parameters["gnd_x"], parameters["gnd_y"]],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        ant = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + parameters["patch_x"] + "/2", "-" + parameters["patch_y"] + "/2", parameters["sub_h"]],
            sizes=[parameters["patch_x"], parameters["patch_y"]],
            name="ant_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1

        void = self._app.modeler.create_circle(
            orientation=2,
            origin=[parameters["feed_x"], parameters["feed_y"], "0"],
            radius=parameters["coax_outer_rad"],
            name="void_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.subtract(gnd, void, False)

        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[parameters["feed_x"], parameters["feed_y"], "0"],
            radius=parameters["coax_inner_rad"],
            height=parameters["sub_h"],
            name="feed_pin_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_pin.color = (255, 128, 65)

        feed_coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[parameters["feed_x"], parameters["feed_y"], "0"],
            radius=parameters["coax_inner_rad"],
            height="-" + parameters["feed_length"],
            name="feed_coax_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_coax.color = (255, 128, 65)

        coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[parameters["feed_x"], parameters["feed_y"], "0"],
            radius=parameters["coax_outer_rad"],
            height="-" + parameters["feed_length"],
            name="coax_" + antenna_name,
            material="Teflon (tm)",
            new_properties={"Coordinate System": coordinate_system},
        )
        coax.color = (128, 255, 255)

        port_cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[parameters["feed_x"], parameters["feed_y"], "-" + parameters["feed_length"]],
            radius=parameters["coax_outer_rad"],
            height="-" + parameters["sub_h"] + "/10",
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (132, 132, 193)

        port = self._app.modeler.create_circle(
            orientation=2,
            origin=[parameters["feed_x"], parameters["feed_y"], "-" + parameters["feed_length"]],
            radius=parameters["coax_outer_rad"],
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        objects = {
            sub.name: sub,
            gnd.name: gnd,
            ant.name: ant,
            feed_pin.name: feed_pin,
            feed_coax.name: feed_coax,
            coax.name: coax,
            port_cap.name: port_cap,
            port.name: port,
        }
        return parameters, objects

    def _finalize_model(self, objects, position_parameters):
        self.object_list.update(objects)
        self._app.modeler.move(
            list(objects.keys()),
            [position_parameters["pos_x"], position_parameters["pos_y"], position_parameters["pos_z"]],
        )

        for obj in objects.values():
            obj.group_name = self.name
        return True

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class PlanarInvertedF(CommonPIFA):
    """Manage a planar inverted-F antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``2.4``.
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

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.pifa.PlanarInvertedF`
        Antenna object.

    Notes
    -----
    .. [1] W. Kin-Lu, "PIFAs for Internal Mobile Phone Antennas," in
       *Planar Antennas for Wireless Communications*, New York, 2003.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.pifa import PlanarInvertedF
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = PlanarInvertedF(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 2.4,
        "frequency_unit": "GHz",
        "material": "Duroid (tm)",
        "material_properties": {"permittivity": 2.2},
        "outer_boundary": "",
        "substrate_height": 1.5748,
    }

    def __init__(self, *args, **kwargs):
        CommonPIFA.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "PlanarInvertedF"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wavelength = light_speed / freq_hz
        permittivity = self._get_permittivity()
        if permittivity is None:
            return parameters

        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        eff_permittivity = self._effective_permittivity(wavelength / 80.0, sub_meters, permittivity)
        scale = (2.4 / freq_ghz / math.sqrt(eff_permittivity)) * 1.13

        parameters["length1"] = constants.unit_converter(2.49 * scale, "Length", "cm", self.length_unit)
        parameters["length2"] = constants.unit_converter(0.8 * scale, "Length", "cm", self.length_unit)
        parameters["trace_width"] = constants.unit_converter(0.15 * scale, "Length", "cm", self.length_unit)
        parameters["antenna_offset"] = constants.unit_converter(0.45 * scale, "Length", "cm", self.length_unit)
        parameters["feed_offset"] = constants.unit_converter(-0.5 * scale, "Length", "cm", self.length_unit)
        parameters["feed_length"] = constants.unit_converter(0.015 * scale, "Length", "cm", self.length_unit)
        parameters["feed_width"] = constants.unit_converter(0.15 * scale, "Length", "cm", self.length_unit)
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(5.0 * scale, "Length", "cm", self.length_unit)
        parameters["sub_y"] = constants.unit_converter(10.0 * scale, "Length", "cm", self.length_unit)
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

        length1 = self.synthesis_parameters.length1.hfss_variable
        length2 = self.synthesis_parameters.length2.hfss_variable
        trace_width = self.synthesis_parameters.trace_width.hfss_variable
        antenna_offset = self.synthesis_parameters.antenna_offset.hfss_variable
        feed_offset = self.synthesis_parameters.feed_offset.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        feed_width = self.synthesis_parameters.feed_width.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system
        sub_origin_y = f"-{sub_y}+{length2}+{trace_width}"

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", sub_origin_y, "-" + sub_h],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", sub_origin_y, "-" + sub_h],
            sizes=[sub_x, f"{sub_y}-{length2}-{trace_width}"],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        ant_feed = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[f"-{trace_width}/2+{feed_offset}", "0", "0"],
            sizes=[trace_width, length2],
            name="ant_feed_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant_feed.color = (255, 128, 65)

        short_x_origin = f"-{trace_width}/2-{antenna_offset}+{feed_offset}-{trace_width}"

        ant_short_arm = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[short_x_origin, "0", "0"],
            sizes=[trace_width, length2],
            name="ant_short_arm_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant_short_arm.color = (255, 128, 65)

        ant_short_wall = self._app.modeler.create_rectangle(
            orientation=1,
            origin=[short_x_origin, "0", "-" + sub_h],
            sizes=[sub_h, trace_width],
            name="ant_short_wall_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant_short_wall.color = (255, 128, 65)

        ant_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[short_x_origin, f"{length2}-{trace_width}", "0"],
            sizes=[length1, trace_width],
            name="ant_top_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant_top.color = (255, 128, 65)

        ant_microstrip = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[f"-{feed_width}/2+{feed_offset}", "-" + feed_length, "0"],
            sizes=[feed_width, feed_length],
            name="ant_microstrip_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant_microstrip.color = (255, 128, 65)

        self._app.modeler.unite([ant_feed, ant_short_arm, ant_top, ant_microstrip])
        antenna = self._app.modeler[ant_feed.name]
        antenna.name = "ant_" + antenna_name
        antenna.color = (255, 128, 65)

        port_lump = self._app.modeler.create_rectangle(
            orientation=1,
            origin=[f"-{feed_width}/2+{feed_offset}", "-" + feed_length, "-" + sub_h],
            sizes=[sub_h, feed_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port_lump.color = (255, 128, 65)

        objects = {
            sub.name: sub,
            gnd.name: gnd,
            antenna.name: antenna,
            ant_short_wall.name: ant_short_wall,
            port_lump.name: port_lump,
        }
        return self._finalize_model(objects, {"pos_x": pos_x, "pos_y": pos_y, "pos_z": pos_z})

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class ShortingPin(CommonPIFA):
    """Manage a shorting-pin planar inverted-F antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``2.45``.
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

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.pifa.ShortingPin`
        Antenna object.

    Notes
    -----
    .. [1] W. Kin-Lu, "PIFAs for Internal Mobile Phone Antennas," in
       *Planar Antennas for Wireless Communications*, New York, 2003.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.pifa import ShortingPin
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = ShortingPin(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 2.45,
        "frequency_unit": "GHz",
        "material": "Duroid (tm)",
        "material_properties": {"permittivity": 2.2},
        "outer_boundary": "",
        "substrate_height": 1.5748,
    }

    def __init__(self, *args, **kwargs):
        CommonPIFA.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "ShortingPin"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        length_unit = self.length_unit
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wavelength = light_speed / freq_hz
        permittivity = self._get_permittivity()
        if permittivity is None:
            return parameters

        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((permittivity + 1.0) / 2.0))
        eff_permittivity = self._effective_permittivity(patch_width, sub_meters, permittivity)
        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_permittivity))
        top = (eff_permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_permittivity - 0.258) * (patch_width / sub_meters + 0.8)
        delta_length = 0.412 * sub_meters * top / bottom
        patch_length = effective_length - 2.0 * delta_length

        k = 2.0 * math.pi / eff_permittivity
        g = math.pi * patch_width / (120.0 * math.pi * wavelength) * (1.0 - math.pow(k * sub_meters, 2) / 24.0)
        res = 1.0 / (2.0 * g)
        offset_pin_pos = patch_length / math.pi * math.asin(math.sqrt(50.0 / res))
        offset_pin_pos *= 0.78
        patch_length /= 2.63
        offset_pin_pos -= patch_length / 2.0

        parameters["patch_x"] = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["patch_y"] = constants.unit_converter(patch_length, "Length", "meter", length_unit)
        parameters["short_x"] = 0.0
        parameters["short_y"] = constants.unit_converter(-patch_length / 2.0, "Length", "meter", length_unit)
        parameters["feed_x"] = 0.0
        parameters["feed_y"] = constants.unit_converter(offset_pin_pos, "Length", "meter", length_unit)
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            2.0 * patch_width + 6.0 * sub_meters, "Length", "meter", length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            2.0 * patch_length + 6.0 * sub_meters, "Length", "meter", length_unit
        )
        parameters["coax_inner_rad"] = constants.unit_converter(0.13 * (3.0 / freq_ghz), "Length", "cm", length_unit)
        parameters["coax_outer_rad"] = constants.unit_converter(0.44 * (3.0 / freq_ghz), "Length", "cm", length_unit)
        parameters["feed_length"] = constants.unit_converter(wavelength / 6.0, "Length", "meter", length_unit)
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
        parameters, objects = self._create_probe_feed_objects()

        short_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[parameters["short_x"], parameters["short_y"], "0"],
            radius=parameters["coax_inner_rad"] + "/3",
            height=parameters["sub_h"],
            name="short_pin_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        short_pin.color = (255, 128, 65)
        objects[short_pin.name] = short_pin

        return self._finalize_model(objects, parameters)

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass


class ShortingPlate(CommonPIFA):
    """Manage a shorting-plate planar inverted-F antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``3.0``.
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

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.pifa.ShortingPlate`
        Antenna object.

    Notes
    -----
    .. [1] W. Kin-Lu, "PIFAs for Internal Mobile Phone Antennas," in
       *Planar Antennas for Wireless Communications*, New York, 2003.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.pifa import ShortingPlate
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = ShortingPlate(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 3.0,
        "frequency_unit": "GHz",
        "material": "Duroid (tm)",
        "material_properties": {"permittivity": 2.2},
        "outer_boundary": "",
        "substrate_height": 1.5748,
    }

    def __init__(self, *args, **kwargs):
        CommonPIFA.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "ShortingPlate"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        length_unit = self.length_unit
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wavelength = light_speed / freq_hz
        permittivity = self._get_permittivity()
        if permittivity is None:
            return parameters

        sub_meters = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((permittivity + 1.0) / 2.0))
        eff_permittivity = self._effective_permittivity(patch_width, sub_meters, permittivity)
        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_permittivity))
        top = (eff_permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_permittivity - 0.258) * (patch_width / sub_meters + 0.8)
        delta_length = 0.412 * sub_meters * top / bottom
        patch_length = effective_length - 2.0 * delta_length

        k = 2.0 * math.pi / eff_permittivity
        g = math.pi * patch_width / (120.0 * math.pi * wavelength) * (1.0 - math.pow(k * sub_meters, 2) / 24.0)
        res = 1.0 / (2.0 * g)
        offset_pin_pos = patch_length / math.pi * math.asin(math.sqrt(50.0 / res))
        offset_pin_pos *= 0.78
        patch_length = patch_length / 2.0 * 0.95
        offset_pin_pos -= patch_length / 2.0

        parameters["patch_x"] = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["patch_y"] = constants.unit_converter(patch_length, "Length", "meter", length_unit)
        parameters["plate_w"] = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["short_x"] = "-" + "patch_x"  # placeholder overwritten below
        parameters["feed_x"] = 0.0
        parameters["feed_y"] = constants.unit_converter(offset_pin_pos, "Length", "meter", length_unit)
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            2.0 * patch_width + 6.0 * sub_meters, "Length", "meter", length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            2.0 * patch_length + 6.0 * sub_meters, "Length", "meter", length_unit
        )
        parameters["coax_inner_rad"] = constants.unit_converter(0.13 * (3.0 / freq_ghz), "Length", "cm", length_unit)
        parameters["coax_outer_rad"] = constants.unit_converter(0.44 * (3.0 / freq_ghz), "Length", "cm", length_unit)
        parameters["feed_length"] = constants.unit_converter(wavelength / 6.0, "Length", "meter", length_unit)
        parameters["gnd_x"] = parameters["sub_x"]
        parameters["gnd_y"] = parameters["sub_y"]
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        parameters["short_x"] = -parameters["patch_x"] / 2.0
        parameters["short_y"] = -parameters["patch_y"] / 2.0
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
        parameters, objects = self._create_probe_feed_objects()

        shorting_plate = self._app.modeler.create_rectangle(
            orientation=1,
            origin=[parameters["short_x"], parameters["short_y"], "0"],
            sizes=[parameters["sub_h"], self.synthesis_parameters.plate_w.hfss_variable],
            name="shorting_plate_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        shorting_plate.color = (255, 128, 65)
        objects[shorting_plate.name] = shorting_plate

        return self._finalize_model(objects, parameters)

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass
