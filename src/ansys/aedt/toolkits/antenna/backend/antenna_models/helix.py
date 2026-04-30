# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonHelix(CommonAntenna):
    """Provides base methods common to horn antenna."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Helix"
        CommonAntenna.__init__(self, _default_input_parameters, *args, **kwargs)

    @property
    def material(self):
        """Helix material.

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

    @property
    def gain(self):
        """Helix expected gain.

        Returns
        -------
        float
        """
        return self._input_parameters.gain

    @gain.setter
    def gain(self, value):
        self._input_parameters.gain = value
        if value != self.gain and self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def direction(self):
        """Helix direction. ``0`` for left, and ``1`` for right.

        Returns
        -------
        int
        """
        return self._input_parameters.direction

    @direction.setter
    def direction(self, value):
        if isinstance(value, str) and value.lower() == "left":
            value = 0
        elif isinstance(value, str) and value.lower() == "right":
            value = 1

        self._input_parameters.direction = value
        if self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def feeder_length(self):
        """Helix feeder length.

        Returns
        -------
        float
        """
        return self._input_parameters.feeder_length

    @feeder_length.setter
    def feeder_length(self, value):
        self._input_parameters.feeder_length = value
        if value != self.feeder_length and self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @staticmethod
    def _ordered_parameters(parameters):
        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    def _validate_material(self):
        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False
        return True

    def _set_unitless_parameter(self, parameter_name):
        parameter = getattr(self.synthesis_parameters, parameter_name, None)
        if parameter:
            self._app[parameter.hfss_variable] = str(parameter.value)

    def _single_feed_model(self, radius_change="0"):
        if self.object_list:
            logger.debug("This antenna is already defined")
            return False

        if not self._validate_material():
            return False

        self.set_variables_in_hfss()

        groundx = self.synthesis_parameters.groundx.hfss_variable
        groundy = self.synthesis_parameters.groundy.hfss_variable
        diameter = self.synthesis_parameters.diameter.hfss_variable
        wire_diameter = self.synthesis_parameters.wire_diameter.hfss_variable
        spacing = self.synthesis_parameters.spacing.hfss_variable
        coax_inner_radius = self.synthesis_parameters.coax_inner_radius.hfss_variable
        coax_outer_radius = self.synthesis_parameters.coax_outer_radius.hfss_variable
        feed_pinl = self.synthesis_parameters.feed_pinL.hfss_variable
        feed_pind = self.synthesis_parameters.feed_pinD.hfss_variable
        feeder_length = self.synthesis_parameters.feeder_length.hfss_variable
        number_of_turns = self.synthesis_parameters.number_of_turns.hfss_variable
        self._set_unitless_parameter("number_of_turns")

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        my_udm_pairs = [
            ["PolygonSegments", "8"],
            ["PolygonRadius", "{}/2".format(wire_diameter)],
            ["StartHelixRadius", "{}/2".format(diameter)],
            ["RadiusChange", radius_change],
            ["Pitch", spacing],
            ["Turns", str(number_of_turns)],
            ["SegmentsPerTurn", "16"],
            ["RightHanded", self.direction],
        ]

        udm = self._app.modeler.create_udp(
            dll="SegmentedHelix/PolygonHelix.dll",
            parameters=my_udm_pairs,
            library="syslib",
            name="helix",
        )
        udm_obj = self._app.get_oo_object(self._app.oeditor, udm.name)
        # Set direction
        self._app.set_oo_property_value(
            aedt_object=udm_obj, object_name="CreateUserDefinedPart:1", prop_name="RightHanded", value=self.direction
        )

        # Set coordinate system of udm
        self._app.set_oo_property_value(
            aedt_object=udm_obj,
            object_name="CreateUserDefinedPart:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        udm.material_name = "pec"
        self._app.modeler.split(udm, "XY", "PositiveOnly")
        gnd = self._app.modeler.create_rectangle(
            Plane.XY,
            [
                "-{}/2".format(groundx),
                "-{}/2".format(groundy),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            [groundx, groundy],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )

        cutout = self._app.modeler.create_circle(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=coax_outer_radius,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.subtract(cutout, keep_originals=False)

        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=feed_pind + "/2",
            height=feed_pinl + "+" + wire_diameter + "/2",
            name="Feed_{}".format(antenna_name),
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )

        feed_coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=coax_inner_radius,
            height="-{}".format(feeder_length),
            name="Feed1_{}".format(antenna_name),
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )

        coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=coax_outer_radius,
            height="-{}".format(feeder_length),
            name="coax_{}".format(antenna_name),
            material="Teflon (tm)",
            new_properties={"Coordinate System": coordinate_system},
        )

        cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2-{}".format(feed_pinl, wire_diameter, feeder_length),
            ],
            radius=coax_outer_radius,
            height="-{}/2".format(feed_pinl),
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )

        p1 = self._app.modeler.create_circle(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2-{}".format(feed_pinl, wire_diameter, feeder_length),
            ],
            radius=coax_outer_radius,
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (128, 0, 0)

        objects = [udm, feed_coax, feed_pin, coax, cap, gnd, p1]
        for obj in objects:
            obj.group_name = antenna_name

        self._app.modeler.move(objects, [pos_x, pos_y, pos_z])

        for obj in objects:
            self.object_list[obj.name] = obj
        self._app.modeler.fit_all()
        return True

    def _quadrifilar_model(self, shorted=False):
        if self.object_list:
            logger.debug("This antenna is already defined")
            return False

        if not self._validate_material():
            return False

        self.set_variables_in_hfss()

        groundx = self.synthesis_parameters.groundx.hfss_variable
        groundy = self.synthesis_parameters.groundy.hfss_variable
        diameter = self.synthesis_parameters.diameter.hfss_variable
        wire_diameter = self.synthesis_parameters.wire_diameter.hfss_variable
        spacing = self.synthesis_parameters.spacing.hfss_variable
        port_height = self.synthesis_parameters.port_height.hfss_variable
        number_of_turns = self.synthesis_parameters.number_of_turns.hfss_variable
        self._set_unitless_parameter("number_of_turns")

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        objects = []
        gnd = self._app.modeler.create_rectangle(
            Plane.XY,
            [
                "-{}/2".format(groundx),
                "-{}/2".format(groundy),
                "-2*{}-{}/2".format(port_height, wire_diameter),
            ],
            [groundx, groundy],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        objects.append(gnd)

        udp_pairs = [
            ["PolygonSegments", "8"],
            ["PolygonRadius", "{}/2".format(wire_diameter)],
            ["StartHelixRadius", "{}/2".format(diameter)],
            ["RadiusChange", "0"],
            ["Pitch", spacing],
            ["Turns", str(number_of_turns)],
            ["SegmentsPerTurn", "16"],
            ["RightHanded", self.direction],
        ]

        helix = self._app.modeler.create_udp(
            dll="SegmentedHelix/PolygonHelix.dll",
            parameters=udp_pairs,
            library="syslib",
            name="helix_1",
        )
        # Set direction
        helix_obj = self._app.get_oo_object(self._app.oeditor, helix.name)
        # Set direction
        self._app.set_oo_property_value(
            aedt_object=helix_obj, object_name="CreateUserDefinedPart:1", prop_name="RightHanded", value=self.direction
        )

        # Set coordinate system of udm
        self._app.set_oo_property_value(
            aedt_object=helix_obj,
            object_name="CreateUserDefinedPart:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        helix.material_name = "pec"
        self._app.modeler.split(helix, "XY", "PositiveOnly")
        helix_names = [helix.name] + helix.duplicate_around_axis(Axis.Z, 90, 4)

        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["{}/2".format(diameter), "0", "-{}-{}/2".format(port_height, wire_diameter)],
            radius="{}/2".format(wire_diameter),
            height="{}+{}/2".format(port_height, wire_diameter),
            name="feed_1",
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_names = [feed_pin.name] + feed_pin.duplicate_around_axis(Axis.Z, 90, 4)

        port = self._app.modeler.create_rectangle(
            orientation=Plane.ZX,
            origin=[
                "{}/2-{}/2".format(diameter, wire_diameter),
                "0",
                "-{}-{}/2".format(port_height, wire_diameter),
            ],
            sizes=["-{}".format(port_height), wire_diameter],
            name="port_lump_{}_1".format(antenna_name),
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)
        port_names = [port.name] + port.duplicate_around_axis(Axis.Z, 90, 4)

        for index, object_name in enumerate(helix_names, start=1):
            obj = self._app.modeler[object_name]
            if index > 1:
                obj.name = "helix_{}".format(index)
                obj = self._app.modeler[obj.name]
                helix_names[index - 1] = obj.name
            objects.append(obj)

        for index, object_name in enumerate(feed_names, start=1):
            obj = self._app.modeler[object_name]
            if index > 1:
                obj.name = "feed_{}".format(index)
                obj = self._app.modeler[obj.name]
            objects.append(obj)

        for index, object_name in enumerate(port_names, start=1):
            obj = self._app.modeler[object_name]
            if index > 1:
                obj.name = "port_lump_{}_{}".format(antenna_name, index)
                obj = self._app.modeler[obj.name]
            obj.color = (128, 0, 0)
            objects.append(obj)

        if shorted:
            short_1 = self._app.modeler.create_cylinder(
                orientation=0,
                origin=["{}/2".format(diameter), 0.0, "{}*{}".format(number_of_turns, spacing)],
                radius="{}/2".format(wire_diameter),
                height="-{}".format(diameter),
                name="short_1",
                material="pec",
                new_properties={"Coordinate System": coordinate_system},
            )
            short_2 = self._app.modeler.create_cylinder(
                orientation=1,
                origin=[0.0, "{}/2".format(diameter), "{}*{}".format(number_of_turns, spacing)],
                radius="-{}/2".format(wire_diameter),
                height="-{}".format(diameter),
                name="short_2",
                material="pec",
                new_properties={"Coordinate System": coordinate_system},
            )
            objects.extend([short_1, short_2])

            # Unite all helix and short objects
            helix_and_short_objs = [self._app.modeler[name] for name in helix_names] + [short_1, short_2]
            self._app.modeler.unite(helix_and_short_objs)
            # _ = helix_and_short_objs[0]

            # Remove united objects from objects list and add the united one
            for obj in helix_and_short_objs[1:]:
                if obj in objects:
                    objects.remove(obj)

        for obj in objects:
            obj.group_name = antenna_name

        self._app.modeler.move(objects, [pos_x, pos_y, pos_z])

        for obj in objects:
            self.object_list[obj.name] = obj

        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class AxialMode(CommonHelix):
    """Manages an axial mode helix antenna.

    This class is accessible through the ``Hfss`` object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Helix material. If the material is not defined, a new material,
        ``parametrized``, is defined. The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are ``"FEBI"``, ``"PML"``,
        ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.AxialMode`
        Antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.helix import AxialMode
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = AxialMode(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = AxialMode(app, origin=[200, 50, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "gain": 10,
        "direction": 0,
        "feeder_length": 10,
        "outer_boundary": "",
        "material": "pec",
    }

    def __init__(self, *args, **kwargs):
        CommonHelix.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "AxialMode"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        light_speed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wl_meters = light_speed / freq_hz
        gain_value_db = self.gain
        gain_value_mag = math.pow(10.0, gain_value_db / 10.0)

        groundx = constants.unit_converter(4.0 * (3.33 / freq_ghz), "Length", "in", "mm")
        groundy = constants.unit_converter(4.0 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_diameter = constants.unit_converter(1.128 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_spacing = constants.unit_converter(0.786 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_wiredia = constants.unit_converter(0.2 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_coax_inner_radius = constants.unit_converter(0.082 * (3.33 / freq_ghz) / 2, "Length", "in", "mm")
        helix_coax_outer_radius = constants.unit_converter(0.275 * (3.33 / freq_ghz) / 2, "Length", "in", "mm")

        helix_feed_pinl = constants.unit_converter(0.05 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_feed_pind = constants.unit_converter(0.082 * (3.33 / freq_ghz), "Length", "in", "mm")

        helix_diameter_syn = wl_meters / math.pi * 0.9
        helix_spacing_syn = math.pi * helix_diameter_syn * math.tan(math.radians(12.5))
        helix_turns_syn = gain_value_mag * wl_meters / 15.0 / helix_spacing_syn

        parameters["groundx"] = groundx
        parameters["groundy"] = groundy
        parameters["diameter"] = helix_diameter
        parameters["spacing"] = helix_spacing
        parameters["wire_diameter"] = helix_wiredia
        parameters["coax_inner_radius"] = helix_coax_inner_radius
        parameters["coax_outer_radius"] = helix_coax_outer_radius
        parameters["feed_pinL"] = helix_feed_pinl
        parameters["feed_pinD"] = helix_feed_pind
        parameters["feed_pinL"] = helix_feed_pinl
        parameters["feed_pinD"] = helix_feed_pind
        parameters["number_of_turns"] = helix_turns_syn
        parameters["feeder_length"] = self.feeder_length

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in my_keys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw an axial mode antenna.

        Once the antenna is created, this method is not used anymore.
        """
        if self.object_list:
            logger.debug("This antenna is already defined")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Map parameters
        groundx = self.synthesis_parameters.groundx.hfss_variable
        groundy = self.synthesis_parameters.groundy.hfss_variable
        diameter = self.synthesis_parameters.diameter.hfss_variable
        wire_diameter = self.synthesis_parameters.wire_diameter.hfss_variable
        spacing = self.synthesis_parameters.spacing.hfss_variable
        coax_inner_radius = self.synthesis_parameters.coax_inner_radius.hfss_variable
        coax_outer_radius = self.synthesis_parameters.coax_outer_radius.hfss_variable
        feed_pinl = self.synthesis_parameters.feed_pinL.hfss_variable
        feed_pind = self.synthesis_parameters.feed_pinD.hfss_variable
        feeder_length = self.synthesis_parameters.feeder_length.hfss_variable
        number_of_turns = self.synthesis_parameters.number_of_turns.hfss_variable
        self._app[number_of_turns] = str(self.synthesis_parameters.number_of_turns.value)

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        my_udm_pairs = []
        mypair = ["PolygonSegments", "8"]
        my_udm_pairs.append(mypair)
        mypair = ["PolygonRadius", "{}/2".format(wire_diameter)]
        my_udm_pairs.append(mypair)
        mypair = ["StartHelixRadius", "{}/2".format(diameter)]
        my_udm_pairs.append(mypair)
        mypair = ["RadiusChange", "0"]
        my_udm_pairs.append(mypair)
        mypair = ["Pitch", spacing]
        my_udm_pairs.append(mypair)
        mypair = ["Turns", str(number_of_turns)]
        my_udm_pairs.append(mypair)
        mypair = ["SegmentsPerTurn", "16"]
        my_udm_pairs.append(mypair)

        # Parameter not working in native API call, it is modified later
        mypair = ["RightHanded", self.direction]
        my_udm_pairs.append(mypair)

        udm = self._app.modeler.create_udp(
            dll="SegmentedHelix/PolygonHelix.dll",
            parameters=my_udm_pairs,
            library="syslib",
            name="helix",
        )

        udm_obj = self._app.get_oo_object(self._app.oeditor, udm.name)
        # Set direction
        self._app.set_oo_property_value(
            aedt_object=udm_obj, object_name="CreateUserDefinedPart:1", prop_name="RightHanded", value=self.direction
        )

        # Set coordinate system of udm
        self._app.set_oo_property_value(
            aedt_object=udm_obj,
            object_name="CreateUserDefinedPart:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        udm.material_name = "pec"
        self._app.modeler.split(udm, "XY", "PositiveOnly")
        gnd = self._app.modeler.create_rectangle(
            Plane.XY,
            [
                "-{}/2".format(groundx),
                "-{}/2".format(groundy),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            [groundx, groundy],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )

        cutout = self._app.modeler.create_circle(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=coax_outer_radius,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.subtract(cutout, keep_originals=False)

        # Negative air
        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=feed_pind + "/2",
            height=feed_pinl + "+" + wire_diameter + "/2",
            name="Feed_{}".format(antenna_name),
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )

        feed_coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=coax_inner_radius,
            height="-{}".format(feeder_length),
            name="Feed1_{}".format(antenna_name),
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )

        coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2".format(feed_pinl, wire_diameter),
            ],
            radius=coax_outer_radius,
            height="-{}".format(feeder_length),
            name="coax_{}".format(antenna_name),
            material="Teflon (tm)",
            new_properties={"Coordinate System": coordinate_system},
        )

        # Cap
        cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2-{}".format(feed_pinl, wire_diameter, feeder_length),
            ],
            radius=coax_outer_radius,
            height="-{}/2".format(feed_pinl),
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )

        # P1
        p1 = self._app.modeler.create_circle(
            orientation=2,
            origin=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pind),
                "-{}-{}/2-{}".format(feed_pinl, wire_diameter, feeder_length),
            ],
            radius=coax_outer_radius,
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        p1.color = (128, 0, 0)

        udm.group_name = antenna_name
        feed_coax.group_name = antenna_name
        feed_pin.group_name = antenna_name
        cap.group_name = antenna_name
        gnd.group_name = antenna_name
        p1.group_name = antenna_name

        self._app.modeler.move([udm, feed_coax, feed_pin, coax, cap, gnd, p1], [pos_x, pos_y, pos_z])
        self.object_list[udm.name] = udm
        self.object_list[feed_coax.name] = feed_coax
        self.object_list[feed_pin.name] = feed_pin
        self.object_list[cap.name] = cap
        self.object_list[gnd.name] = gnd
        self.object_list[p1.name] = p1
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class AxialModeTaper(CommonHelix):
    """Manages a tapered axial mode helix antenna.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "gain": 10,
        "direction": 0,
        "feeder_length": None,
        "outer_boundary": "",
        "material": "pec",
    }

    def __init__(self, *args, **kwargs):
        CommonHelix.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "AxialModeTaper"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wl_meters = light_speed / freq_hz
        gain_value_mag = math.pow(10.0, self.gain / 10.0)

        groundx = constants.unit_converter(4.0 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        groundy = constants.unit_converter(4.0 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        helix_diameter = constants.unit_converter(1.128 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        helix_spacing = constants.unit_converter(0.786 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        helix_wiredia = constants.unit_converter(0.2 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        helix_coax_inner_radius = constants.unit_converter(
            0.082 * (3.33 / freq_ghz) / 2.0, "Length", "in", self.length_unit
        )
        helix_coax_outer_radius = constants.unit_converter(
            0.275 * (3.33 / freq_ghz) / 2.0, "Length", "in", self.length_unit
        )
        helix_feed_pinl = constants.unit_converter(0.05 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        helix_feed_pind = constants.unit_converter(0.082 * (3.33 / freq_ghz), "Length", "in", self.length_unit)
        default_feeder_length = constants.unit_converter(1.005 * (3.33 / freq_ghz), "Length", "in", self.length_unit)

        helix_diameter_syn = wl_meters / math.pi * 0.9
        helix_spacing_syn = math.pi * helix_diameter_syn * math.tan(math.radians(12.5))
        helix_turns_syn = gain_value_mag * wl_meters / 15.0 / helix_spacing_syn
        helix_radius_change_syn = helix_diameter_syn * 0.4 / 2.0 / helix_turns_syn

        parameters["groundx"] = groundx
        parameters["groundy"] = groundy
        parameters["diameter"] = helix_diameter
        parameters["spacing"] = helix_spacing
        parameters["wire_diameter"] = helix_wiredia
        parameters["coax_inner_radius"] = helix_coax_inner_radius
        parameters["coax_outer_radius"] = helix_coax_outer_radius
        parameters["feed_pinL"] = helix_feed_pinl
        parameters["feed_pinD"] = helix_feed_pind
        parameters["number_of_turns"] = helix_turns_syn
        parameters["radius_change"] = constants.unit_converter(
            helix_radius_change_syn, "Length", "meter", self.length_unit
        )
        parameters["feeder_length"] = self.feeder_length or default_feeder_length

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        return self._single_feed_model("-{}".format(self.synthesis_parameters.radius_change.hfss_variable))

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class NormalMode(CommonHelix):
    """Manages a normal mode helix antenna.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "gain": 1,
        "direction": 0,
        "feeder_length": None,
        "outer_boundary": "",
        "material": "pec",
    }

    def __init__(self, *args, **kwargs):
        CommonHelix.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "NormalMode"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wl_meters = light_speed / freq_hz

        groundx_syn = wl_meters
        groundy_syn = wl_meters
        helix_diameter_syn = wl_meters / 20.0
        helix_spacing_syn = wl_meters / 20.0
        helix_turns_syn = wl_meters / 8.0 / helix_spacing_syn / 1.375
        zin = 2.0 * math.pow(25.3 * helix_turns_syn * helix_spacing_syn / wl_meters, 2)

        helix_wiredia_syn = wl_meters * 0.01
        helix_coax_inner_radius_syn = helix_wiredia_syn / 2.0
        helix_coax_outer_radius_syn = helix_coax_inner_radius_syn * math.exp(zin * math.sqrt(2.2) / 60.0)
        while helix_coax_outer_radius_syn >= wl_meters / 8.0 / math.sqrt(2.2):
            helix_coax_inner_radius_syn *= 0.9
            helix_coax_outer_radius_syn = helix_coax_inner_radius_syn * math.exp(zin * math.sqrt(2.2) / 60.0)

        helix_feed_pinl_syn = wl_meters / 64.0
        helix_feed_pind_syn = helix_coax_inner_radius_syn * 2.0
        default_feeder_length = 5 * helix_feed_pind_syn

        parameters["groundx"] = constants.unit_converter(groundx_syn, "Length", "meter", self.length_unit)
        parameters["groundy"] = constants.unit_converter(groundy_syn, "Length", "meter", self.length_unit)
        parameters["diameter"] = constants.unit_converter(helix_diameter_syn, "Length", "meter", self.length_unit)
        parameters["spacing"] = constants.unit_converter(helix_spacing_syn, "Length", "meter", self.length_unit)
        parameters["wire_diameter"] = constants.unit_converter(helix_wiredia_syn, "Length", "meter", self.length_unit)
        parameters["coax_inner_radius"] = constants.unit_converter(
            helix_coax_inner_radius_syn, "Length", "meter", self.length_unit
        )
        parameters["coax_outer_radius"] = constants.unit_converter(
            helix_coax_outer_radius_syn, "Length", "meter", self.length_unit
        )
        parameters["feed_pinL"] = constants.unit_converter(helix_feed_pinl_syn, "Length", "meter", self.length_unit)
        parameters["feed_pinD"] = constants.unit_converter(helix_feed_pind_syn, "Length", "meter", self.length_unit)
        parameters["number_of_turns"] = helix_turns_syn
        parameters["feeder_length"] = self.feeder_length or constants.unit_converter(
            default_feeder_length, "Length", "meter", self.length_unit
        )

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        return self._single_feed_model()

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class QuadrifilarOpen(CommonHelix):
    """Manages an open quadrifilar helix antenna.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "gain": 10,
        "direction": 0,
        "feeder_length": 0.0,
        "outer_boundary": "",
        "material": "pec",
    }

    def __init__(self, *args, **kwargs):
        CommonHelix.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "QuadrifilarOpen"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        parameters["groundx"] = constants.unit_converter(60 * (1 / freq_ghz), "Length", "mm", self.length_unit)
        parameters["groundy"] = constants.unit_converter(60 * (1 / freq_ghz), "Length", "mm", self.length_unit)
        parameters["diameter"] = constants.unit_converter(43.2 * (1 / freq_ghz), "Length", "mm", self.length_unit)
        parameters["spacing"] = constants.unit_converter(139 * (1 / freq_ghz), "Length", "mm", self.length_unit)
        parameters["wire_diameter"] = constants.unit_converter(1.6 * (1 / freq_ghz), "Length", "mm", self.length_unit)
        parameters["port_height"] = constants.unit_converter(3.2 * (1 / freq_ghz), "Length", "mm", self.length_unit)
        parameters["number_of_turns"] = 1.1

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        return self._quadrifilar_model()

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class QuadrifilarShort(CommonHelix):
    """Manages a shorted quadrifilar helix antenna.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.0,
        "frequency_unit": "GHz",
        "gain": 10,
        "direction": 0,
        "feeder_length": 0.0,
        "outer_boundary": "",
        "material": "pec",
    }

    def __init__(self, *args, **kwargs):
        CommonHelix.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "QuadrifilarShort"

    @pyaedt_function_handler()
    def synthesis(self):
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        syn_resonant_freq = 0.9322
        scaling = syn_resonant_freq / freq_ghz

        parameters["groundx"] = constants.unit_converter(100 * scaling, "Length", "mm", self.length_unit)
        parameters["groundy"] = constants.unit_converter(100 * scaling, "Length", "mm", self.length_unit)
        parameters["diameter"] = constants.unit_converter(52.2 * scaling, "Length", "mm", self.length_unit)
        parameters["spacing"] = constants.unit_converter(255 * scaling, "Length", "mm", self.length_unit)
        parameters["wire_diameter"] = constants.unit_converter(15 * scaling, "Length", "mm", self.length_unit)
        parameters["port_height"] = constants.unit_converter(3.2 * scaling, "Length", "mm", self.length_unit)
        parameters["number_of_turns"] = 0.5

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        return self._ordered_parameters(parameters)

    @pyaedt_function_handler()
    def model_hfss(self):
        return self._quadrifilar_model(shorted=True)

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass
