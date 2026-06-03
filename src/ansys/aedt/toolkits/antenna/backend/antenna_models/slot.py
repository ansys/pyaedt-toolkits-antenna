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
from ansys.aedt.toolkits.common.backend.logger_handler import logger


def _ordered_parameters(parameters):
    return OrderedDict((key, parameters[key]) for key in sorted(parameters))


def _set_group_and_move(antenna, *objects):
    pos_x = antenna.synthesis_parameters.pos_x.hfss_variable
    pos_y = antenna.synthesis_parameters.pos_y.hfss_variable
    pos_z = antenna.synthesis_parameters.pos_z.hfss_variable

    antenna._app.modeler.move([obj.name for obj in objects], [pos_x, pos_y, pos_z])
    for obj in objects:
        obj.group_name = antenna.name


class CommonSlot(CommonAntenna):
    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Slot"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)


class CommonPrintedSlot(CommonSlot):
    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonSlot.__init__(self, default_input_parameters, *args, **kwargs)
        if "substrate_height" not in kwargs:
            self.substrate_height = constants.unit_converter(
                self.substrate_height, "Length", default_input_parameters["length_unit"], self.length_unit
            )
        self._transmission_line_calculator = TransmissionLine(self.frequency, self.frequency_unit)

    @property
    def material(self):
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
                self._input_parameters.material = value
                parameters = self.synthesis()
                self.update_synthesis_parameters(parameters)
                if self.object_list:
                    self.set_variables_in_hfss()
        else:
            self._input_parameters.material = value

    @property
    def material_properties(self):
        return self._input_parameters.material_properties

    @property
    def substrate_height(self):
        return self._input_parameters.substrate_height

    @substrate_height.setter
    def substrate_height(self, value):
        self._input_parameters.substrate_height = value
        if self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    def _substrate_permittivity(self):
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
        return None

    @staticmethod
    def _suspended_microstrip_permittivity(wavelength, trace_width, substrate_height, permittivity):
        ratio = trace_width / substrate_height if substrate_height else 0.0
        effective = (permittivity + 1.0) / 2.0 + (permittivity - 1.0) / 2.0 * math.pow(1.0 + 12.0 / ratio, -0.5)
        if ratio < 1.0:
            effective += 0.04 * math.pow(1.0 - ratio, 2.0)
        suspended = 1.0 + (effective - 1.0) * (1.0 - math.exp(-2.0 * math.pi * substrate_height / wavelength))
        return max(suspended, 1.0)


class SlotGap(CommonPrintedSlot):
    """Manage a gap-fed printed slot antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``1.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. The default is ``"FR4_epoxy"``.
    material_properties : dict, optional
        Material properties for the substrate. The default is
        ``{"permittivity": 4.4}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"cm"``.
    substrate_height : float, optional
        Substrate height. The default is ``0.15748``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.slot.SlotGap`
        Antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Linear Wire Antennas," in *Antenna Theory*,
       2nd ed., New York, Wiley, 1997.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.slot import SlotGap
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = SlotGap(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "cm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 0.15748,
    }

    def __init__(self, *args, **kwargs):
        CommonPrintedSlot.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "SlotGap"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        permittivity = self._substrate_permittivity()
        if permittivity is None:
            return parameters

        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = constants.SpeedOfLight / freq_hz
        substrate_height = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        eff_permittivity = self._suspended_microstrip_permittivity(
            wavelength, wavelength / 80.0, substrate_height, permittivity
        )
        eff_wavelength = wavelength / math.sqrt(eff_permittivity)
        correction_factor = 1.15

        parameters["slot_length"] = constants.unit_converter(
            correction_factor * eff_wavelength / 2.0, "Length", "meter", self.length_unit
        )
        parameters["slot_width"] = constants.unit_converter(
            correction_factor * eff_wavelength / 40.0, "Length", "meter", self.length_unit
        )
        parameters["feed_offset"] = constants.unit_converter(
            correction_factor * eff_wavelength * (1.0 / 4.0 - 1.0 / 9.0), "Length", "meter", self.length_unit
        )
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            correction_factor * 0.75 * eff_wavelength, "Length", "meter", self.length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            correction_factor * eff_wavelength, "Length", "meter", self.length_unit
        )
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return _ordered_parameters(parameters)

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

        slot_length = self.synthesis_parameters.slot_length.hfss_variable
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        feed_offset = self.synthesis_parameters.feed_offset.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "-" + sub_h],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + self.name,
            material=self.material,
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + self.name,
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        slot = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + slot_width + "/2", "-" + slot_length + "/2", "0"],
            sizes=[slot_width, slot_length],
            name="slot_" + self.name,
        )
        self._app.modeler.subtract(gnd, slot, False)

        # Split in half the ground plane to let HFSS assign a terminal
        split = gnd.split(constants.Plane.YZ)
        split_gnd = self._app.modeler.get_object_from_name(split[1])
        split_gnd.name = "PerfE_split"

        port = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + slot_width + "/2", feed_offset + "-" + slot_width + "/2", "0"],
            sizes=[slot_width, slot_width],
            name="port_lump_" + self.name,
        )
        port.color = (128, 0, 0)
        port.transparency = 0.4

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[split_gnd.name] = split_gnd
        self.object_list[port.name] = port

        _set_group_and_move(self, sub, gnd, port)
        return True


class SlotMicrostrip(CommonPrintedSlot):
    """Manage a microstrip-fed printed slot antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``1.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. The default is ``"FR4_epoxy"``.
    material_properties : dict, optional
        Material properties for the substrate. The default is
        ``{"permittivity": 4.4}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"cm"``.
    substrate_height : float, optional
        Substrate height. The default is ``0.15748``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.slot.SlotMicrostrip`
        Antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Linear Wire Antennas," in *Antenna Theory*,
       2nd ed., New York, Wiley, 1997.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.slot import SlotMicrostrip
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = SlotMicrostrip(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "cm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "material_properties": {"permittivity": 4.4},
        "outer_boundary": "",
        "substrate_height": 0.15748,
    }

    def __init__(self, *args, **kwargs):
        CommonPrintedSlot.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "SlotMicrostrip"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        permittivity = self._substrate_permittivity()
        if permittivity is None:
            return parameters

        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = constants.SpeedOfLight / freq_hz
        substrate_height = constants.unit_converter(self.substrate_height, "Length", self.length_unit, "meter")
        eff_permittivity = self._suspended_microstrip_permittivity(
            wavelength, wavelength / 80.0, substrate_height, permittivity
        )
        eff_wavelength = wavelength / math.sqrt(eff_permittivity)
        microstrip_width, microstrip_length = self._transmission_line_calculator.microstrip_calculator(
            substrate_height, permittivity, 50.0, 90.0
        )
        correction_factor = 1.15

        parameters["slot_length"] = constants.unit_converter(
            correction_factor * eff_wavelength / 2.0, "Length", "meter", self.length_unit
        )
        parameters["slot_width"] = constants.unit_converter(
            correction_factor * eff_wavelength / 40.0, "Length", "meter", self.length_unit
        )
        parameters["feed_offset"] = constants.unit_converter(
            correction_factor * eff_wavelength * (1.0 / 4.0 - 1.0 / 9.0), "Length", "meter", self.length_unit
        )
        parameters["microstrip_width"] = constants.unit_converter(microstrip_width, "Length", "meter", self.length_unit)
        parameters["microstrip_offset"] = constants.unit_converter(
            microstrip_length, "Length", "meter", self.length_unit
        )
        parameters["sub_h"] = self.substrate_height
        parameters["sub_x"] = constants.unit_converter(
            correction_factor * 0.75 * eff_wavelength, "Length", "meter", self.length_unit
        )
        parameters["sub_y"] = constants.unit_converter(
            correction_factor * eff_wavelength, "Length", "meter", self.length_unit
        )
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return _ordered_parameters(parameters)

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

        slot_length = self.synthesis_parameters.slot_length.hfss_variable
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        feed_offset = self.synthesis_parameters.feed_offset.hfss_variable
        microstrip_width = self.synthesis_parameters.microstrip_width.hfss_variable
        microstrip_offset = self.synthesis_parameters.microstrip_offset.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "-" + sub_h],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + self.name,
            material=self.material,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y],
            name="gnd_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        slot = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + slot_width + "/2", "-" + slot_length + "/2", "0"],
            sizes=[slot_width, slot_length],
            name="slot_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        self._app.modeler.subtract(gnd, slot, False)

        microstrip = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + sub_x + "/2", feed_offset + "-" + microstrip_width + "/2", "-" + sub_h],
            sizes=[sub_x + "/2+" + slot_width + "/2+" + microstrip_offset, microstrip_width],
            name="ant_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        microstrip.color = (255, 128, 65)
        microstrip.transparency = 0.1

        port = self._app.modeler.create_rectangle(
            orientation=1,
            origin=["-" + sub_x + "/2", feed_offset + "-" + microstrip_width + "/2", "-" + sub_h],
            sizes=[sub_h, microstrip_width],
            name="port_lump_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        port.color = (128, 0, 0)
        port.transparency = 0.4

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[microstrip.name] = microstrip
        self.object_list[port.name] = port

        _set_group_and_move(self, sub, gnd, microstrip, port)
        return True


class SlotTBar(CommonSlot):
    """Manage a T-bar-fed cavity-backed slot antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``1.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.slot.SlotTBar`
        Antenna object.

    Notes
    -----
    .. [1] E. Newman and G. Thiele, "Some important parameters in the design
       of T-bar fed slot antennas," *IEEE Transactions on Antennas and
       Propagation*, vol. 23, no. 1, pp. 97-100, Jan. 1975.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.slot import SlotTBar
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = SlotTBar(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonSlot.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "SlotTBar"

    @pyaedt_function_handler()
    def synthesis(self):
        design_frequency = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        scale = 1.0 / design_frequency
        parameters = {
            "antenna_length": 400.0 * scale,
            "antenna_width": 200.0 * scale,
            "slot_length": 234.6 * scale,
            "slot_width": 78.21 * scale,
            "cavity_depth": 105.1 * scale,
            "feed_bar_diameter": 26.89 * scale,
            "feed_bar_length": 6.11 * scale,
            "feed_pin_diameter": 6.721 * scale,
            "feed_gap": 0.4 * scale,
            "bar_offset": 0.0,
            "bar_depth": 43.16 * scale,
            "t_bar_diameter": 26.89 * scale,
            "transition_length": 7.332 * scale,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return _ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        self.set_variables_in_hfss()

        antenna_length = self.synthesis_parameters.antenna_length.hfss_variable
        antenna_width = self.synthesis_parameters.antenna_width.hfss_variable
        slot_length = self.synthesis_parameters.slot_length.hfss_variable
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        cavity_depth = self.synthesis_parameters.cavity_depth.hfss_variable
        feed_bar_diameter = self.synthesis_parameters.feed_bar_diameter.hfss_variable
        feed_bar_length = self.synthesis_parameters.feed_bar_length.hfss_variable
        feed_pin_diameter = self.synthesis_parameters.feed_pin_diameter.hfss_variable
        feed_gap = self.synthesis_parameters.feed_gap.hfss_variable
        bar_offset = self.synthesis_parameters.bar_offset.hfss_variable
        bar_depth = self.synthesis_parameters.bar_depth.hfss_variable
        t_bar_diameter = self.synthesis_parameters.t_bar_diameter.hfss_variable
        transition_length = self.synthesis_parameters.transition_length.hfss_variable

        cavity = self._app.modeler.create_box(
            origin=["-" + antenna_width + "/2", "-" + antenna_length + "/2", "-1.2*" + cavity_depth],
            sizes=[antenna_width, antenna_length, "1.2*" + cavity_depth],
            name="cavity_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        cavity_void = self._app.modeler.create_box(
            origin=["-" + slot_width + "/2", "-" + slot_length + "/2", "-" + cavity_depth],
            sizes=[slot_width, slot_length, cavity_depth],
            name="void_" + self.name,
            material="vacuum",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        self._app.modeler.subtract(cavity, cavity_void, False)
        cavity.color = (255, 128, 65)
        cavity.transparency = 0.15

        bar = self._app.modeler.create_cylinder(
            orientation=1,
            origin=[bar_offset, "-" + slot_length + "/2", "-" + bar_depth],
            radius=t_bar_diameter + "/2",
            height=slot_length,
            name="bar_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        feed_bar = self._app.modeler.create_cylinder(
            orientation=0,
            origin=[bar_offset, "0", "-" + bar_depth],
            radius=feed_bar_diameter + "/2",
            height=t_bar_diameter + "/2+" + feed_bar_length,
            name="feed_bar_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        feed_pin = self._app.modeler.create_cylinder(
            orientation=0,
            origin=[slot_width + "/2-" + feed_gap, "0", "-" + bar_depth],
            radius=feed_pin_diameter + "/2",
            height="-" + slot_width + "/2+" + feed_gap + "+" + bar_offset,
            name="feed_pin_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        transition = self._app.modeler.create_cone(
            orientation=0,
            origin=[bar_offset + "+" + t_bar_diameter + "/2+" + feed_bar_length, "0", "-" + bar_depth],
            bottom_radius=feed_bar_diameter + "/2",
            top_radius=feed_pin_diameter + "/2",
            height=transition_length,
            name="transition_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        signal = self._app.modeler.unite([bar, feed_bar, feed_pin, transition])
        signal = self._app.modeler.get_objects_by_name(signal)[0]
        signal.name = "feed_" + self.name

        port = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[slot_width + "/2-" + feed_gap, "-" + feed_pin_diameter + "/2", "-" + bar_depth],
            sizes=[feed_gap, feed_pin_diameter],
            name="port_lump_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        port.color = (128, 0, 0)
        port.transparency = 0.4

        self.object_list[cavity.name] = cavity
        self.object_list[signal.name] = signal
        self.object_list[port.name] = port

        _set_group_and_move(self, cavity, signal, port)
        return True


class SlotCavityBackedArray(CommonSlot):
    """Manage a cavity-backed slot antenna array.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``3.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.slot.SlotCavityBackedArray`
        Antenna object.

    Notes
    -----
    .. [1] C. A. Balanis, *Antenna Theory, Analysis and Design*,
       3rd ed., Wiley, chapters 6 and 12.
    .. [2] Byungje Lee et al., "Cavity-backed slot antenna array for the
       repeater system of a satellite digital multimedia broadcasting
       service," *IEEE Antennas and Wireless Propagation Letters*, vol. 4,
       pp. 389-392, 2005.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.slot import SlotCavityBackedArray
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = SlotCavityBackedArray(app)
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
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonSlot.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "SlotCavityBackedArray"

    @pyaedt_function_handler()
    def synthesis(self):
        design_frequency = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        scale = 3.0 / design_frequency
        parameters = {
            "reflector_length": 332.4 * scale,
            "reflector_width": 215.5 * scale,
            "reflector_height": 42.21 * scale,
            "cavity_length": 274.8 * scale,
            "cavity_width": 123.4 * scale,
            "cavity_height": 28.78 * scale,
            "wall_width": 0.5 * scale,
            "slot_length": 22.54 * scale,
            "slot_width": 45.09 * scale,
            "width_spacing_1": 68.11 * scale,
            "width_spacing_2": 84.42 * scale,
            "length_spacing": 62.93 * scale,
            "waveguide_length": 37.65 * scale,
            "waveguide_width": 75.31 * scale,
            "waveguide_height": 59.07 * scale,
            "pin_gap": 0.5 * scale,
            "pin_height": 21.19 * scale,
            "pin_diameter": 1.919 * scale,
            "pin_inset": 19.69 * scale,
            "pos_x": self.origin[0],
            "pos_y": self.origin[1],
            "pos_z": self.origin[2],
        }
        return _ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        self.set_variables_in_hfss()

        reflector_length = self.synthesis_parameters.reflector_length.hfss_variable
        reflector_width = self.synthesis_parameters.reflector_width.hfss_variable
        reflector_height = self.synthesis_parameters.reflector_height.hfss_variable
        cavity_length = self.synthesis_parameters.cavity_length.hfss_variable
        cavity_width = self.synthesis_parameters.cavity_width.hfss_variable
        cavity_height = self.synthesis_parameters.cavity_height.hfss_variable
        wall_width = self.synthesis_parameters.wall_width.hfss_variable
        slot_length = self.synthesis_parameters.slot_length.hfss_variable
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        width_spacing_1 = self.synthesis_parameters.width_spacing_1.hfss_variable
        width_spacing_2 = self.synthesis_parameters.width_spacing_2.hfss_variable
        length_spacing = self.synthesis_parameters.length_spacing.hfss_variable
        waveguide_length = self.synthesis_parameters.waveguide_length.hfss_variable
        waveguide_width = self.synthesis_parameters.waveguide_width.hfss_variable
        waveguide_height = self.synthesis_parameters.waveguide_height.hfss_variable
        pin_gap = self.synthesis_parameters.pin_gap.hfss_variable
        pin_height = self.synthesis_parameters.pin_height.hfss_variable
        pin_diameter = self.synthesis_parameters.pin_diameter.hfss_variable
        pin_inset = self.synthesis_parameters.pin_inset.hfss_variable

        cavity = self._app.modeler.create_box(
            origin=[
                "-" + reflector_length + "/2-" + wall_width + "/2",
                "-" + reflector_width + "/2-" + wall_width + "/2",
                "-" + cavity_height + "-" + waveguide_height + "-" + wall_width,
            ],
            sizes=[
                reflector_length + "+" + wall_width,
                reflector_width + "+" + wall_width,
                reflector_height + "+" + cavity_height + "+" + waveguide_height + "+" + wall_width,
            ],
            name="cavity_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        reflector = self._app.modeler.create_box(
            origin=["-" + reflector_length + "/2", "-" + reflector_width + "/2", "0"],
            sizes=[reflector_length, reflector_width, reflector_height],
            name="reflector_" + self.name,
            material="vacuum",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        cavity_void = self._app.modeler.create_box(
            origin=["-" + cavity_length + "/2", "-" + cavity_width + "/2", "-" + cavity_height],
            sizes=[cavity_length, cavity_width, cavity_height],
            name="cavity_void_" + self.name,
            material="vacuum",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        waveguide = self._app.modeler.create_box(
            origin=[
                "-" + waveguide_length + "/2",
                "-" + waveguide_width + "/2",
                "-" + cavity_height + "-" + waveguide_height,
            ],
            sizes=[waveguide_length, waveguide_width, waveguide_height],
            name="waveguide_" + self.name,
            material="vacuum",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        self._app.modeler.subtract(cavity, [reflector, cavity_void, waveguide], False)
        cavity.color = (90, 96, 110)
        cavity.transparency = 0.55

        cavity_face = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + reflector_length + "/2", "-" + reflector_width + "/2", "0"],
            sizes=[reflector_length, reflector_width],
            name="ant_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        cavity_face.color = (180, 205, 230)
        cavity_face.transparency = 0.35

        x_centers = [
            "-" + width_spacing_1 + "/2-" + width_spacing_2,
            "-" + width_spacing_1 + "/2",
            width_spacing_1 + "/2",
            width_spacing_1 + "/2+" + width_spacing_2,
        ]
        y_centers = ["-" + length_spacing + "/2", length_spacing + "/2"]
        slot_cuts = []
        slot_index = 0
        for y_center in y_centers:
            for x_center in x_centers:
                slot = self._app.modeler.create_rectangle(
                    orientation=2,
                    origin=[x_center + "-" + slot_length + "/2", y_center + "-" + slot_width + "/2", "0"],
                    sizes=[slot_length, slot_width],
                    name=f"slot_{self.name}_{slot_index}",
                    new_properties={"Coordinate System": self.coordinate_system},
                )
                slot_cuts.append(slot)
                slot_index += 1
        self._app.modeler.subtract(cavity_face, slot_cuts, False)

        pin = self._app.modeler.create_cylinder(
            orientation=0,
            origin=[
                "-" + waveguide_length + "/2+" + pin_gap,
                "0",
                "-" + cavity_height + "-" + waveguide_height + "+" + pin_inset,
            ],
            radius=pin_diameter + "/2",
            height=pin_height + "-" + pin_gap,
            name="pin_" + self.name,
            material="pec",
            new_properties={"Coordinate System": self.coordinate_system},
        )
        pin.color = (214, 145, 32)
        pin.transparency = 0.15

        port = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + waveguide_length + "/2",
                "-" + pin_diameter + "/2",
                "-" + cavity_height + "-" + waveguide_height + "+" + pin_inset,
            ],
            sizes=[pin_gap, pin_diameter],
            name="port_lump_" + self.name,
            new_properties={"Coordinate System": self.coordinate_system},
        )
        port.color = (196, 34, 51)
        port.transparency = 0.15

        self.object_list[cavity.name] = cavity
        self.object_list[cavity_face.name] = cavity_face
        self.object_list[pin.name] = pin
        self.object_list[port.name] = port

        _set_group_and_move(self, cavity, cavity_face, pin, port)
        return True
