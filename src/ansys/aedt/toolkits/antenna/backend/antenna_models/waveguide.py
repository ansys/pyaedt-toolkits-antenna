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
import re

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import StandardWaveguide
from ansys.aedt.toolkits.antenna.backend.antenna_models.parameters import Property
from ansys.aedt.toolkits.antenna.backend.models import properties
from ansys.aedt.toolkits.common.backend.logger_handler import logger

_DIMENSIONLESS_PARAMETER_RE = re.compile("|".join(["ratio", "coefficient", "points", "number"]))


class CommonWaveguide(CommonAntenna):
    """Provides base methods common to waveguide antenna models."""

    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Waveguide"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)

    @property
    def material(self):
        """Waveguide material."""
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
            if value != self.material and self.object_list:
                for antenna_obj, antenna_part in self.object_list.items():
                    if (
                        antenna_part.material_name == self.material.lower()
                        and "port" not in antenna_obj
                        and "inner" not in antenna_obj
                    ):
                        antenna_part.material_name = value
                self._input_parameters.material = value
                parameters = self.synthesis()
                self.update_synthesis_parameters(parameters)
                self.set_variables_in_hfss()
            else:
                self._input_parameters.material = value
        else:
            self._input_parameters.material = value

    @property
    def material_properties(self):
        """Waveguide material properties."""
        return self._input_parameters.material_properties

    @pyaedt_function_handler()
    def set_variables_in_hfss(self, not_used=None):
        """Create HFSS design variables."""
        if not not_used:
            not_used = []
        for parameter in self.synthesis_parameters.__dict__.values():
            if isinstance(parameter, Property) and parameter.hfss_variable not in not_used:
                properties.antenna.parameters_hfss[parameter.name] = parameter.hfss_variable
                if "angle" in parameter.hfss_variable:
                    self._app[parameter.hfss_variable] = str(parameter.value) + "deg"
                elif _DIMENSIONLESS_PARAMETER_RE.search(parameter.hfss_variable):
                    self._app[parameter.hfss_variable] = str(int(parameter.value))
                else:
                    self._app[parameter.hfss_variable] = str(parameter.value) + self.length_unit


class CircularWaveguide(CommonWaveguide):
    """Manage a circular waveguide section.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Waveguide material. The default is ``"pec"``.
    material_properties : dict, optional
        Material properties for the waveguide material. The default is ``{}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is determined by the common antenna base
        class when not explicitly provided.
    wg_radius : float, optional
        Waveguide inner radius. When ``None``, it is synthesized from the
        operating frequency.
    wg_length : float, optional
        Waveguide length. When ``None``, it is synthesized from the operating
        frequency.
    wall_thickness : float, optional
        Waveguide wall thickness. When ``None``, it is synthesized from the
        operating frequency.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.waveguide.CircularWaveguide`
        Antenna object.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.waveguide import CircularWaveguide
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = CircularWaveguide(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "material_properties": {},
        "outer_boundary": "",
        "wg_radius": None,
        "wg_length": None,
        "wall_thickness": None,
    }

    def __init__(self, *args, **kwargs):
        CommonWaveguide.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "CircularWaveguide"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        frequency_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        parameters["wg_length"] = self._input_parameters.wg_length or constants.unit_converter(
            2.0 * (10.0 / frequency_ghz), "Length", "in", self.length_unit
        )
        parameters["wg_radius"] = self._input_parameters.wg_radius or constants.unit_converter(
            0.45 * (10.0 / frequency_ghz), "Length", "in", self.length_unit
        )
        parameters["wall_thickness"] = self._input_parameters.wall_thickness or constants.unit_converter(
            0.02 * (10.0 / frequency_ghz), "Length", "in", self.length_unit
        )
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return OrderedDict((key, parameters[key]) for key in sorted(parameters))

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a circular waveguide."""
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
        self._app.solution_type = "Modal"

        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wg_radius = self.synthesis_parameters.wg_radius.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        air_cut = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            material="vacuum",
            new_properties={"Coordinate System": coordinate_system},
        )
        metal = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wg_length,
            name="metal_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        metal.color = (255, 128, 65)
        self._app.modeler.subtract(blank_list=[metal.name], tool_list=[air_cut.name], keep_originals=False)

        inner = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            name="inner_" + antenna_name,
            material="vacuum",
            new_properties={"Coordinate System": coordinate_system},
        )
        inner.transparency = 0.7
        port_cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (132, 132, 193)
        port = self._app.modeler.create_circle(
            orientation=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius,
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        self.object_list[metal.name] = metal
        self.object_list[inner.name] = inner
        self.object_list[port_cap.name] = port_cap
        self.object_list[port.name] = port
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        return self.object_list


class RectangularWaveguide(CommonWaveguide):
    """Manage a rectangular waveguide section.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Waveguide material. The default is ``"pec"``.
    material_properties : dict, optional
        Material properties for the waveguide material. The default is ``{}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is determined by the common antenna base
        class when not explicitly provided.
    wg_standard : str, optional
        Standard waveguide name. The default is ``"auto"``, which selects a
        size from frequency.
    wg_width : float, optional
        Waveguide inner width. When ``None``, it is synthesized from the
        selected standard.
    wg_height : float, optional
        Waveguide inner height. When ``None``, it is synthesized from the
        selected standard.
    wg_length : float, optional
        Waveguide length. When ``None``, it is synthesized from the operating
        frequency.
    wall_thickness : float, optional
        Waveguide wall thickness. When ``None``, it is synthesized from the
        selected standard.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.waveguide.RectangularWaveguide`
        Antenna object.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.waveguide import RectangularWaveguide
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = RectangularWaveguide(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "material_properties": {},
        "outer_boundary": "",
        "wg_standard": "auto",
        "wg_width": None,
        "wg_height": None,
        "wg_length": None,
        "wall_thickness": None,
    }

    def __init__(self, *args, **kwargs):
        CommonWaveguide.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "RectangularWaveguide"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        frequency_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        waveguide = StandardWaveguide()
        wg_name = self._input_parameters.wg_standard
        if not wg_name or str(wg_name).lower() == "auto":
            wg_name = waveguide.find_waveguide(self.frequency, self.frequency_unit)
        dimensions = waveguide.get_waveguide_dimensions(wg_name, self.length_unit)

        parameters["wg_width"] = self._input_parameters.wg_width or dimensions[0]
        parameters["wg_height"] = self._input_parameters.wg_height or dimensions[1]
        parameters["wall_thickness"] = self._input_parameters.wall_thickness or dimensions[2]
        parameters["wg_length"] = self._input_parameters.wg_length or constants.unit_converter(
            2.0 * (10.0 / frequency_ghz), "Length", "in", self.length_unit
        )
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return OrderedDict((key, parameters[key]) for key in sorted(parameters))

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a rectangular waveguide."""
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
        self._app.solution_type = "Modal"

        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_height = self.synthesis_parameters.wg_height.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        air_cut = self._app.modeler.create_box(
            origin=["-" + wg_width + "/2", "-" + wg_height + "/2", "-" + wg_length],
            sizes=[wg_width, wg_height, wg_length],
            material="vacuum",
            new_properties={"Coordinate System": coordinate_system},
        )
        metal = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2-" + wall_thickness,
                "-" + wg_height + "/2-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[wg_width + "+2*" + wall_thickness, wg_height + "+2*" + wall_thickness, wg_length],
            name="metal_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        metal.color = (255, 128, 65)
        self._app.modeler.subtract(blank_list=[metal.name], tool_list=[air_cut.name], keep_originals=False)

        inner = self._app.modeler.create_box(
            origin=["-" + wg_width + "/2", "-" + wg_height + "/2", "-" + wg_length],
            sizes=[wg_width, wg_height, wg_length],
            name="inner_" + antenna_name,
            material="vacuum",
            new_properties={"Coordinate System": coordinate_system},
        )
        inner.transparency = 0.7
        port_cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2-" + wall_thickness,
                "-" + wg_height + "/2-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (132, 132, 193)
        port = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + wg_width + "/2", "-" + wg_height + "/2", "-" + wg_length],
            sizes=[wg_width, wg_height],
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        self.object_list[metal.name] = metal
        self.object_list[inner.name] = inner
        self.object_list[port_cap.name] = port_cap
        self.object_list[port.name] = port
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        return self.object_list


class RectangularWaveguideSlotArray(CommonWaveguide):
    """Manage a rectangular waveguide slot array.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.3``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Waveguide material. The default is ``"pec"``.
    material_properties : dict, optional
        Material properties for the waveguide material. The default is ``{}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is determined by the common antenna base
        class when not explicitly provided.
    wg_standard : str, optional
        Standard waveguide name. The default is ``"auto"``, which selects a
        size from frequency.
    wg_width : float, optional
        Waveguide inner width. When ``None``, it is synthesized from the
        selected standard.
    wg_height : float, optional
        Waveguide inner height. When ``None``, it is synthesized from the
        selected standard.
    wg_length : float, optional
        Waveguide length. When ``None``, it is synthesized from slot-array
        defaults and adjusted to satisfy spacing constraints.
    wall_thickness : float, optional
        Waveguide wall thickness. When ``None``, it is synthesized from the
        selected standard.
    inset_from_feed : float, optional
        Distance from the feed plane to the first slot. When ``None``, it is
        synthesized from the reference design.
    inset_from_termination : float, optional
        Distance from the last slot to the terminated end. When ``None``, it
        is synthesized from the reference design.
    slot_spacing : float, optional
        Center-to-center spacing between adjacent slots. When ``None``, it is
        synthesized from the reference design.
    slot_width : float, optional
        Slot width. When ``None``, it is synthesized from the reference design.
    slot_length : float, optional
        Slot length. When ``None``, it is synthesized from the reference
        design.
    slot_offset : float, optional
        Alternating lateral slot offset from the waveguide centerline. When
        ``None``, it is synthesized from the reference design.
    slots_number : int, optional
        Number of radiating slots. The default is ``13``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.waveguide.RectangularWaveguideSlotArray`
        Antenna object.

    Notes
    -----
    .. [1] R. Elliott and I. Kurtz, "The design of small slot arrays," in
       *IEEE Transactions on Antennas and Propagation*, vol. 26, no. 2,
       pp. 214-219, Mar. 1978.
    .. [2] D. Y. Kim and R. S. Elliott, "A design procedure for slot arrays
       fed by single-ridge waveguide," in *IEEE Transactions on Antennas and
       Propagation*, vol. 36, no. 11, pp. 1531-1536, Nov. 1988.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.waveguide import RectangularWaveguideSlotArray
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = RectangularWaveguideSlotArray(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.3,
        "frequency_unit": "GHz",
        "material": "pec",
        "material_properties": {},
        "outer_boundary": "",
        "wg_standard": "auto",
        "wg_width": None,
        "wg_height": None,
        "wg_length": None,
        "wall_thickness": None,
        "inset_from_feed": None,
        "inset_from_termination": None,
        "slot_spacing": None,
        "slot_width": None,
        "slot_length": None,
        "slot_offset": None,
        "slots_number": 13,
    }

    def __init__(self, *args, **kwargs):
        CommonWaveguide.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "RectangularWaveguideSlotArray"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        frequency_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        scale = 10.3 / frequency_ghz
        waveguide = StandardWaveguide()
        wg_name = self._input_parameters.wg_standard
        if not wg_name or str(wg_name).lower() == "auto":
            wg_name = waveguide.find_waveguide(self.frequency, self.frequency_unit)
        dimensions = waveguide.get_waveguide_dimensions(wg_name, self.length_unit)

        def scaled(default_mm):
            return constants.unit_converter(default_mm * scale, "Length", "mm", self.length_unit)

        slots_number = max(2, int(self._input_parameters.slots_number))
        parameters["wg_width"] = self._input_parameters.wg_width or dimensions[0]
        parameters["wg_height"] = self._input_parameters.wg_height or dimensions[1]
        parameters["wall_thickness"] = self._input_parameters.wall_thickness or dimensions[2]
        parameters["inset_from_feed"] = self._input_parameters.inset_from_feed or scaled(9.4356)
        parameters["inset_from_termination"] = self._input_parameters.inset_from_termination or scaled(28.3067)
        parameters["slot_spacing"] = self._input_parameters.slot_spacing or scaled(18.8711)
        parameters["slot_width"] = self._input_parameters.slot_width or scaled(1.5875)
        parameters["slot_length"] = self._input_parameters.slot_length or scaled(14.1393)
        parameters["slot_offset"] = self._input_parameters.slot_offset or scaled(2.5646)
        parameters["slots_number"] = slots_number

        minimum_length = (
            parameters["inset_from_feed"]
            + (slots_number - 1) * parameters["slot_spacing"]
            + parameters["slot_length"]
            + parameters["inset_from_termination"]
        )
        auto_length = scaled(278.335)
        requested_length = self._input_parameters.wg_length or auto_length
        if requested_length < minimum_length:
            logger.debug("Waveguide length updated to satisfy slot-array spacing.")
            requested_length = minimum_length
        parameters["wg_length"] = requested_length
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return OrderedDict((key, parameters[key]) for key in sorted(parameters))

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a rectangular waveguide slot array."""
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
        self._app.solution_type = "Modal"

        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_height = self.synthesis_parameters.wg_height.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        inset_from_termination = self.synthesis_parameters.inset_from_termination.hfss_variable
        slot_spacing = self.synthesis_parameters.slot_spacing.hfss_variable
        slot_width = self.synthesis_parameters.slot_width.hfss_variable
        slot_length = self.synthesis_parameters.slot_length.hfss_variable
        slot_offset = self.synthesis_parameters.slot_offset.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        air_cut = self._app.modeler.create_box(
            origin=["-" + wg_width + "/2", "0", "-" + wg_height + "/2"],
            sizes=[wg_width, wg_length, wg_height],
            material="vacuum",
            new_properties={"Coordinate System": coordinate_system},
        )

        slot_names = []
        slots_number = int(round(self.synthesis_parameters.slots_number.value))
        for slot_index in range(slots_number):
            x_offset = slot_offset if slot_index % 2 == 0 else "-(" + slot_offset + ")"
            slot = self._app.modeler.create_box(
                origin=[
                    "-(" + slot_width + ")/2+" + x_offset,
                    wg_length + "-" + inset_from_termination + "-" + slot_length + f"-{slot_index}*{slot_spacing}",
                    wg_height + "/2",
                ],
                sizes=[slot_width, slot_length, wall_thickness],
                name=f"slot_cutout_{antenna_name}_{slot_index + 1}",
                material="vacuum",
                new_properties={"Coordinate System": coordinate_system},
            )
            slot_names.append(slot.name)

        metal = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2-" + wall_thickness,
                "0",
                "-" + wg_height + "/2-" + wall_thickness,
            ],
            sizes=[wg_width + "+2*" + wall_thickness, wg_length, wg_height + "+2*" + wall_thickness],
            name="metal_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        metal.color = (255, 128, 65)
        self._app.modeler.subtract(blank_list=[metal.name], tool_list=[air_cut.name] + slot_names, keep_originals=False)

        inner = self._app.modeler.create_box(
            origin=["-" + wg_width + "/2", "0", "-" + wg_height + "/2"],
            sizes=[wg_width, wg_length, wg_height],
            name="inner_" + antenna_name,
            material="vacuum",
            new_properties={"Coordinate System": coordinate_system},
        )
        inner.transparency = 0.75
        feed_cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2-" + wall_thickness,
                "0",
                "-" + wg_height + "/2-" + wall_thickness,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                "-" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_cap.color = (132, 132, 193)
        end_cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2-" + wall_thickness,
                wg_length,
                "-" + wg_height + "/2-" + wall_thickness,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="end_cap_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        end_cap.color = (132, 132, 193)
        port = self._app.modeler.create_rectangle(
            orientation=1,
            origin=["-" + wg_width + "/2", "0", "-" + wg_height + "/2"],
            sizes=[wg_height, wg_width],
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        self.object_list[metal.name] = metal
        self.object_list[inner.name] = inner
        self.object_list[feed_cap.name] = feed_cap
        self.object_list[end_cap.name] = end_cap
        self.object_list[port.name] = port
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        return self.object_list
