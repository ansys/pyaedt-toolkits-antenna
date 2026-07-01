# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.common.backend.logger_handler import logger

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna


class CommonMisc(CommonAntenna):
    """Provides base methods common to the miscellaneous antenna family."""

    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Misc"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)

    @property
    def material(self):
        """Metal material."""
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
                            and "port_lump" not in antenna_obj
                        ):
                            self.object_list[antenna_obj].material_name = value
                self._input_parameters.material = value
        else:
            self._input_parameters.material = value


class Bicone(CommonMisc):
    """Manage a bicone antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Metal material. The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.misc.Bicone`
        Antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.misc import Bicone
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = Bicone(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMisc.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Bicone"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        frequency_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        length_unit = self.length_unit

        inner_radius = constants.unit_converter(round(0.125 * (0.8 / frequency_ghz), 3), "Length", "cm", length_unit)
        outer_radius = constants.unit_converter(round(3.0 * (0.8 / frequency_ghz), 2), "Length", "cm", length_unit)
        cone_height = constants.unit_converter(round(5.0 * (0.8 / frequency_ghz), 2), "Length", "cm", length_unit)
        port_gap = constants.unit_converter(round(0.25 * (0.8 / frequency_ghz), 3), "Length", "cm", length_unit)
        port_width = constants.unit_converter(round(0.25 * (0.8 / frequency_ghz), 3), "Length", "cm", length_unit)

        parameters = OrderedDict(
            [
                ("cone_height", cone_height),
                ("inner_radius", inner_radius),
                ("outer_radius", outer_radius),
                ("port_gap", port_gap),
                ("port_width", port_width),
                ("pos_x", self.origin[0]),
                ("pos_y", self.origin[1]),
                ("pos_z", self.origin[2]),
            ]
        )
        return parameters

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a bicone antenna."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        self.set_variables_in_hfss()

        coordinate_system = self.coordinate_system
        antenna_name = self.name

        inner_radius = self.synthesis_parameters.inner_radius.hfss_variable
        outer_radius = self.synthesis_parameters.outer_radius.hfss_variable
        cone_height = self.synthesis_parameters.cone_height.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        port_width = self.synthesis_parameters.port_width.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        top_profile = self._app.modeler.create_polyline(
            points=[[inner_radius, 0, f"{port_gap}/2"], [outer_radius, 0, f"{port_gap}/2+{cone_height}"]],
            name=f"ant_{antenna_name}",
            material=self.material,
        )

        # Set coordinate system of polyline
        top_profile_obj = self._app.get_oo_object(self._app.oeditor, top_profile.name)
        self._app.set_oo_property_value(
            aedt_object=top_profile_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        top_cone = top_profile.sweep_around_axis(2)
        top_cap = self._app.modeler.create_circle(
            orientation=Plane.XY,
            origin=[0, 0, f"{port_gap}/2"],
            radius=inner_radius,
            name=f"ant_cap_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.unite([top_cone.name, top_cap.name])
        top_cone = self._app.modeler[top_cone.name]
        top_cone.color = (255, 128, 65)
        top_cone.transparency = 0.1

        bottom_profile = self._app.modeler.create_polyline(
            points=[[inner_radius, 0, f"-{port_gap}/2"], [outer_radius, 0, f"-{port_gap}/2-{cone_height}"]],
            name=f"ant_{antenna_name}_1",
            material=self.material,
        )

        # Set coordinate system of polyline
        bottom_profile_obj = self._app.get_oo_object(self._app.oeditor, bottom_profile.name)
        self._app.set_oo_property_value(
            aedt_object=bottom_profile_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        bottom_cone = bottom_profile.sweep_around_axis(2)
        bottom_cap = self._app.modeler.create_circle(
            orientation=Plane.XY,
            origin=[0, 0, f"-{port_gap}/2"],
            radius=inner_radius,
            name=f"ant_cap_{antenna_name}_1",
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.unite([bottom_cone.name, bottom_cap.name])
        bottom_cone = self._app.modeler[bottom_cone.name]
        bottom_cone.color = (255, 128, 65)
        bottom_cone.transparency = 0.1

        port_lump = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"-{port_width}/2", f"-{port_gap}/2"],
            sizes=[port_width, port_gap],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_lump.color = (128, 0, 0)

        top_cone.group_name = antenna_name
        bottom_cone.group_name = antenna_name
        port_lump.group_name = antenna_name

        self.object_list[top_cone.name] = top_cone
        self.object_list[bottom_cone.name] = bottom_cone
        self.object_list[port_lump.name] = port_lump

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True


class Discone(CommonMisc):
    """Manage a discone antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Metal material. The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.misc.Discone`
        Antenna object.

    Notes
    -----
    .. [1] C. Balanis, "Wideband and Travelling-Wave Antennas,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.misc import Discone
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = Discone(app)
    >>> antenna.model_hfss()
    >>> antenna.setup_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonMisc.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Discone"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        frequency_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        length_unit = self.length_unit

        inner_radius = constants.unit_converter(round(0.125 * (1.0 / frequency_ghz), 3), "Length", "cm", length_unit)
        outer_radius = constants.unit_converter(round(6.0 * (1.0 / frequency_ghz), 2), "Length", "cm", length_unit)
        cone_height = constants.unit_converter(round(10.0 * (1.0 / frequency_ghz), 2), "Length", "cm", length_unit)
        disk_radius = constants.unit_converter(round(3.5 * (1.0 / frequency_ghz), 3), "Length", "cm", length_unit)
        port_gap = constants.unit_converter(round(0.25 * (1.0 / frequency_ghz), 3), "Length", "cm", length_unit)
        port_width = constants.unit_converter(round(0.25 * (1.0 / frequency_ghz), 3), "Length", "cm", length_unit)

        parameters = OrderedDict(
            [
                ("cone_height", cone_height),
                ("disk_radius", disk_radius),
                ("inner_radius", inner_radius),
                ("outer_radius", outer_radius),
                ("port_gap", port_gap),
                ("port_width", port_width),
                ("pos_x", self.origin[0]),
                ("pos_y", self.origin[1]),
                ("pos_z", self.origin[2]),
            ]
        )
        return parameters

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a discone antenna."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        self.set_variables_in_hfss()

        coordinate_system = self.coordinate_system
        antenna_name = self.name

        inner_radius = self.synthesis_parameters.inner_radius.hfss_variable
        outer_radius = self.synthesis_parameters.outer_radius.hfss_variable
        cone_height = self.synthesis_parameters.cone_height.hfss_variable
        disk_radius = self.synthesis_parameters.disk_radius.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        port_width = self.synthesis_parameters.port_width.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        ground_disk = self._app.modeler.create_circle(
            orientation=Plane.XY,
            origin=[0, 0, 0],
            radius=disk_radius,
            name=f"gnd_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        ground_disk.color = (230, 230, 230)
        ground_disk.transparency = 0.2

        cone_profile = self._app.modeler.create_polyline(
            points=[[inner_radius, 0, f"{port_gap}/2"], [outer_radius, 0, f"{port_gap}/2+{cone_height}"]],
            name=f"ant_{antenna_name}",
            material=self.material,
        )

        # Set coordinate system of polyline
        cone_profile_obj = self._app.get_oo_object(self._app.oeditor, cone_profile.name)
        self._app.set_oo_property_value(
            aedt_object=cone_profile_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        cone = cone_profile.sweep_around_axis(2)
        cone_cap = self._app.modeler.create_circle(
            orientation=Plane.XY,
            origin=[0, 0, f"{port_gap}/2"],
            radius=inner_radius,
            name=f"ant_cap_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.unite([cone.name, cone_cap.name])
        cone = self._app.modeler[cone.name]
        cone.color = (255, 128, 65)
        cone.transparency = 0.1

        port_lump = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0, f"-{port_width}/2", f"-{port_gap}/2"],
            sizes=[port_width, port_gap],
            name=f"port_lump_{antenna_name}",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_lump.color = (128, 0, 0)

        ground_disk.group_name = antenna_name
        cone.group_name = antenna_name
        port_lump.group_name = antenna_name

        self.object_list[ground_disk.name] = ground_disk
        self.object_list[cone.name] = cone
        self.object_list[port_lump.name] = port_lump

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        self._app.modeler.fit_all()
        return True
