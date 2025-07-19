# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.common.backend.logger_handler import logger

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import StandardWaveguide


class CommonHorn(CommonAntenna):
    """Provides base methods common to horn antenna."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Horn"
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

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class Conical(CommonHorn):
    """Manages a conical horn antenna.

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
    :class:`aedt.toolkits.antenna.ConicalHorn`
        Conical horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical
    >>> import ansys.aedt.core
    >>> oantenna1 = Conical(None)
    >>> oantenna1.frequency = 12.0
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = Conical(app)
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = Conical(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
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
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Conical"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz
        wavelength_in = constants.unit_converter(wavelength, "Length", "meter", "in")

        wg_radius_in = 0.5 * wavelength_in
        wg_length_in = 0.4 * wavelength_in
        horn_radius_in = 1.4 * wavelength_in
        horn_length_in = 2 * wavelength_in
        wall_thickness_in = 0.02 * wavelength_in

        wg_radius = constants.unit_converter(wg_radius_in, "Length", "in", self.length_unit)
        parameters["wg_radius"] = wg_radius
        wg_length = constants.unit_converter(wg_length_in, "Length", "in", self.length_unit)
        parameters["wg_length"] = wg_length
        horn_radius = constants.unit_converter(horn_radius_in, "Length", "in", self.length_unit)
        parameters["horn_radius"] = horn_radius
        horn_length = constants.unit_converter(horn_length_in, "Length", "in", self.length_unit)
        parameters["horn_length"] = horn_length
        wall_thickness = constants.unit_converter(wall_thickness_in, "Length", "in", self.length_unit)
        parameters["wall_thickness"] = wall_thickness

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical horn antenna.

        Once the antenna is created, this method is not used anymore."""
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

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        horn_radius = self.synthesis_parameters.horn_radius.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wg_radius = self.synthesis_parameters.wg_radius.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Negative air
        neg_air = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            material="vacuum",
        )
        neg_air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wg_length,
            name="wg_outer_" + antenna_name,
            material=self.material,
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[neg_air.name], blank_list=[wall.name], keep_originals=False)

        # Input
        wg_in = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            name="wg_inner_" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system

        # Cap
        cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", horn_length],
            radius=horn_radius,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn_sheet = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", horn_length],
            radius=horn_radius + "+" + wall_thickness,
        )
        horn_sheet.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([horn_sheet.name, base_wall.name])
        self._app.modeler.connect([base.name, horn_top.name])

        # Horn
        self._app.modeler.subtract(blank_list=[horn_sheet.name], tool_list=[base.name], keep_originals=False)
        self._app.modeler.unite([horn_sheet.name, wall.name])

        air_base = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        air_top = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", horn_length],
            radius=horn_radius,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base, air_top])

        self._app.modeler.unite([wg_in, air_base])

        wg_in.name = "internal_" + antenna_name
        wg_in.color = (128, 255, 255)

        horn_sheet.name = "metal_" + antenna_name
        horn_sheet.material_name = self.material
        horn_sheet.color = (255, 128, 65)

        cap.color = (132, 132, 192)
        p1.color = (128, 0, 0)

        self.object_list[wg_in.name] = wg_in
        self.object_list[horn_sheet.name] = horn_sheet
        self.object_list[cap.name] = cap
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        wg_in.group_name = antenna_name
        horn_sheet.group_name = antenna_name
        cap.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass


class PyramidalRidged(CommonHorn):
    """Manages a pyramidal ridged horn antenna.

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
    :class:`aedt.toolkits.antenna.PyramidalRidged`
        Pyramidal ridged horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import PyramidalRidged
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = PyramidalRidged(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = PyramidalRidged(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
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
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "PyramidalRidged"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        scale = lambda x: (1.0 / freq_ghz) * x

        def scale_value(value, round_val=3, doScale=True):
            if doScale:
                value = scale(value)
            return round(value, round_val)

        aperture_height = scale_value(140.0)
        aperture_width = scale_value(200.0)
        flare_length = scale_value(160.0)
        wall_thickness = scale_value(5.0)
        wg_height = scale_value(28.4)
        wg_width = scale_value(44.85)
        wg_length = scale_value(15.6)
        ridge_width = scale_value(14.64)
        ridge_spacing = scale_value(2)

        aperture_height = constants.unit_converter(aperture_height, "Length", "mm", self.length_unit)
        parameters["aperture_height"] = aperture_height
        aperture_width = constants.unit_converter(aperture_width, "Length", "mm", self.length_unit)
        parameters["aperture_width"] = aperture_width
        flare_length = constants.unit_converter(flare_length, "Length", "mm", self.length_unit)
        parameters["flare_length"] = flare_length
        wall_thickness = constants.unit_converter(wall_thickness, "Length", "mm", self.length_unit)
        parameters["wall_thickness"] = wall_thickness
        wg_height = constants.unit_converter(wg_height, "Length", "mm", self.length_unit)
        parameters["wg_height"] = wg_height
        wg_width = constants.unit_converter(wg_width, "Length", "mm", self.length_unit)
        parameters["wg_width"] = wg_width
        wg_length = constants.unit_converter(wg_length, "Length", "mm", self.length_unit)
        parameters["wg_length"] = wg_length
        ridge_width = constants.unit_converter(ridge_width, "Length", "mm", self.length_unit)
        parameters["ridge_width"] = ridge_width
        ridge_spacing = constants.unit_converter(ridge_spacing, "Length", "mm", self.length_unit)
        parameters["ridge_spacing"] = ridge_spacing

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw conical horn antenna.
        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        aperture_height = self.synthesis_parameters.aperture_height.hfss_variable
        aperture_width = self.synthesis_parameters.aperture_width.hfss_variable
        flare_length = self.synthesis_parameters.flare_length.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_height = self.synthesis_parameters.wg_height.hfss_variable
        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        ridge_width = self.synthesis_parameters.ridge_width.hfss_variable
        ridge_spacing = self.synthesis_parameters.ridge_spacing.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Base of the horn
        # Air
        air = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            material="vacuum",
        )
        air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                wg_length,
            ],
            name="wall_" + antenna_name,
            material="vacuum",
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[air.name], blank_list=[wall.name], keep_originals=False)

        # Top of the horn
        # Input
        wg_in = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            name="wg_inner" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system
        wg_in.color = (128, 255, 255)

        # Cap
        cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system
        cap.color = (132, 132, 193)

        # P1
        p1 = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height],
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[wg_width, wg_height],
            name="base_" + antenna_name,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "0",
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="base_wall_" + antenna_name,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + aperture_width + "/2",
                "-" + aperture_height + "/2",
                flare_length,
            ],
            sizes=[aperture_width, aperture_height],
            name="horn_top_" + antenna_name,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + aperture_width + "/2" + "-" + wall_thickness,
                "-" + aperture_height + "/2" + "-" + wall_thickness,
                flare_length,
            ],
            sizes=[
                aperture_width + "+" + "2*" + wall_thickness,
                aperture_height + "+" + "2*" + wall_thickness,
            ],
            name="horn_" + antenna_name,
        )
        horn.history().properties["Coordinate System"] = coordinate_system

        # Ridge
        def ridge_position(sign="+"):
            position = []
            if sign == "+":
                sign = ""
            position.append(["0", sign + "(" + ridge_spacing + "/2)", "0"])
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.00417)",
                    flare_length + "*1/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.0179)",
                    flare_length + "*2/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.0439)",
                    flare_length + "*3/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.0858)",
                    flare_length + "*4/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.1502)",
                    flare_length + "*5/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.1942)",
                    flare_length + "*11/16",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.25)",
                    flare_length + "*6/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.2945)",
                    flare_length + "*19/24",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.3486)",
                    flare_length + "*5/6",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.4183)",
                    flare_length + "*7/8",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.4776)",
                    flare_length + "*29/32",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.5549)",
                    flare_length + "*15/16",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.6780)",
                    flare_length + "*31/32",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.7654)",
                    flare_length + "*63/64",
                ]
            )
            position.append(
                [
                    "0",
                    sign
                    + "("
                    + ridge_spacing
                    + "/2"
                    + "+"
                    + "("
                    + aperture_height
                    + "-"
                    + ridge_spacing
                    + ")/2*"
                    + "0.8627)",
                    flare_length + "*127/128",
                ]
            )
            position.append(["0", sign + aperture_height + "/2", flare_length])
            position.append(["0", sign + wg_height + "/2", "0"])
            return position

        ridge = self._app.modeler.create_polyline(
            position_list=ridge_position(),
            cover_surface=True,
            name="right_ridge" + antenna_name,
            material=self.material,
        )
        ridge = self._app.modeler.thicken_sheet(ridge, ridge_width, True)
        ridge.history().properties["Coordinate System"] = coordinate_system
        ridge.color = (132, 132, 193)

        mridge = self._app.modeler.create_polyline(
            position_list=ridge_position("-"),
            cover_surface=True,
            name="left_ridge" + antenna_name,
            material=self.material,
        )
        mridge = self._app.modeler.thicken_sheet(mridge, ridge_width, True)
        mridge.history().properties["Coordinate System"] = coordinate_system
        mridge.color = (132, 132, 193)

        # Connectors of the ridge
        # Connector
        connector = self._app.modeler.create_box(
            origin=[
                "-" + ridge_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[
                ridge_width,
                "(" + wg_height + "-" + ridge_spacing + ")/2",
                wg_length,
            ],
            name="connector_" + antenna_name,
            material="pec",
        )
        connector.history().properties["Coordinate System"] = coordinate_system
        connector.color = (132, 132, 193)

        # Bottom connector
        bconnector = self._app.modeler.create_box(
            origin=[
                "-" + ridge_width + "/2",
                wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[
                ridge_width,
                "-(" + wg_height + "-" + ridge_spacing + ")/2",
                wg_length,
            ],
            name="bconnector_" + antenna_name,
            material="pec",
        )
        bconnector.history().properties["Coordinate System"] = coordinate_system
        bconnector.color = (132, 132, 193)

        # Connect pieces
        self._app.modeler.connect([horn.name, base_wall.name])
        self._app.modeler.connect([base.name, horn_top.name])

        self._app.modeler.subtract(horn.name, base.name, False)
        self._app.modeler.unite([horn, wall, ridge, mridge, connector, bconnector])
        horn.color = (255, 128, 65)
        horn.material_name = self.material

        # Air base
        air_base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[
                wg_width,
                wg_height,
            ],
            name="air_base_" + antenna_name,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        # Air top
        air_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + aperture_width + "/2",
                "-" + aperture_height + "/2",
                flare_length,
            ],
            sizes=[
                aperture_width,
                aperture_height,
            ],
            name="air_top_" + antenna_name,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base.name, air_top.name])

        self._app.modeler.unite([wg_in, air_base])

        self.object_list[cap.name] = cap
        self.object_list[horn.name] = horn
        self.object_list[wg_in.name] = wg_in
        self.object_list[p1.name] = p1

        self._app.modeler.move([cap, horn, wg_in, p1], [pos_x, pos_y, pos_z])

        self._app.change_material_override(True)

        cap.group_name = antenna_name
        horn.group_name = antenna_name
        wg_in.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class Corrugated(CommonHorn):
    """Manages a corrugated horn antenna.

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
    :class:`aedt.toolkits.antenna.CorrugatedHorn`
        Corrugated horn object.

    Notes
    -----
    .. [1] C. Balanis, "Horn Antennas," Antenna Theory Analysis,
        3rd ed. Hoboken: Wiley, 2005, sec. 13.6, pp. 785-791.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Corrugated
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = Corrugated(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "meter",
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Corrugated"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        wg_radius_mm = round(11.7 * 10.4 / freq_ghz, 3)
        wg_length_mm = round(30.0 * 10.4 / freq_ghz, 3)
        wall_thickness_mm = round(2.0 * 10.4 / freq_ghz, 3)
        flare_angle = 20
        notches = 25.0
        notch_width_mm = round(2.0 * 10.4 / freq_ghz, 3)
        notch_depth_mm = round(7.5 * 10.4 / freq_ghz, 3)
        tooth_width_mm = round(2.0 * 10.4 / freq_ghz, 3)

        wg_radius = constants.unit_converter(wg_radius_mm, "Length", "mm", self.length_unit)
        parameters["wg_radius"] = wg_radius
        wg_length = constants.unit_converter(wg_length_mm, "Length", "mm", self.length_unit)
        parameters["wg_length"] = wg_length
        wall_thickness = constants.unit_converter(wall_thickness_mm, "Length", "mm", self.length_unit)
        parameters["wall_thickness"] = wall_thickness
        parameters["flare_angle"] = flare_angle
        parameters["notches"] = notches
        notch_width = constants.unit_converter(notch_width_mm, "Length", "mm", self.length_unit)
        parameters["notch_width"] = notch_width
        notch_depth = constants.unit_converter(notch_depth_mm, "Length", "mm", self.length_unit)
        parameters["notch_depth"] = notch_depth
        tooth_width = constants.unit_converter(tooth_width_mm, "Length", "mm", self.length_unit)
        parameters["tooth_width"] = tooth_width

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical horn antenna.

        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        # Not used parameters in HFSS
        notches = self.synthesis_parameters.notches.hfss_variable
        notches_value = self.synthesis_parameters.notches.value
        del self.synthesis_parameters.notches

        # Solution type: Modal
        self._app.solution_type = "Modal"

        self.set_variables_in_hfss([notches])

        # Map parameters
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wg_radius = self.synthesis_parameters.wg_radius.hfss_variable
        self._app[self.synthesis_parameters.flare_angle.hfss_variable] = (
            str(self.synthesis_parameters.flare_angle.value) + "deg"
        )
        flare_angle = self.synthesis_parameters.flare_angle.hfss_variable

        notch_width = self.synthesis_parameters.notch_width.hfss_variable
        notch_depth = self.synthesis_parameters.notch_depth.hfss_variable
        tooth_width = self.synthesis_parameters.tooth_width.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        l = self._app.variable_manager[wg_length].numeric_value
        n = notches_value
        Ka = "tan(" + flare_angle + ")"

        # Based on inputs calculate minimum feed length for geometry to work,
        # and loop until user inputs value above minimum required.
        pts = []
        zStart = "0.0"

        pts.append([wg_radius, "0.0", "0.0"])

        if l > 0.0:
            zStart = wg_length
            pts.append([wg_radius, 0, zStart])

        count = 1
        N = 1

        while count <= n:
            # Create constants K1 through K3, used in coordinate calculations.
            K1 = str((N - 1)) + "*" + "(" + notch_width + "+" + tooth_width + ")"
            K2 = "(" + str(N) + "*" + notch_width + ")+(" + str(N - 1) + ")*" + tooth_width
            K3 = str(N) + "*" + "(" + notch_width + "+" + tooth_width + ")"
            xdel1 = "(" + K1 + ")*" + Ka
            xdel2 = "(" + K2 + ")*" + Ka
            xdel3 = "(" + K3 + ")*" + Ka
            c1 = K1
            c2 = K2
            c3 = K3
            del1 = xdel1
            del2 = xdel2
            del3 = xdel3

            # Create individual components of necessary points
            c1x = wg_radius + "+" + notch_depth + "+" + del1
            c1z = zStart + "+" + c1
            c2x = wg_radius + "+" + notch_depth + "+" + del2
            c2z = zStart + "+" + c2
            c3x = wg_radius + "+" + del2
            c3z = zStart + "+" + c2
            c4x = wg_radius + "+" + del3
            c4z = zStart + "+" + c3

            # Begin drawing corrugations
            pts.append([c1x, 0, c1z])
            pts.append([c2x, 0, c2z])
            pts.append([c3x, 0, c3z])
            pts.append([c4x, 0, c4z])

            count2 = count + 1
            count = count2

            N = count

        # Draw end of horn and exterior outline.
        # This calculation is what required the minimum feed length test,
        # or calculated x-axis point for exterior could end up BEHIND port plane.

        temp1 = c4x + "+" + wall_thickness
        endx = temp1 + "+" + notch_depth
        pts.append([endx, 0, c4z])
        out1 = endx
        out2 = wg_radius + "+" + wall_thickness
        out3 = c4z
        zpart = out3 + "-" + "(((" + out1 + ")-(" + out2 + ")) /(" + Ka + "))"
        finx = out2
        finz = zpart
        pts.append([finx, 0, finz])
        pts.append([finx, 0, 0])

        pts.append([pts[0][0], pts[0][1], pts[0][2]])

        horn = self._app.modeler.create_polyline(
            position_list=pts,
            cover_surface=True,
            name="horn" + antenna_name,
            material=self.material,
        )
        horn = horn.sweep_around_axis(2)
        horn.history().properties["Coordinate System"] = coordinate_system
        horn.color = (132, 132, 193)

        # Cap
        cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        self.object_list[horn.name] = horn
        self.object_list[cap.name] = cap
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        horn.group_name = antenna_name
        cap.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass


class Elliptical(CommonHorn):
    """Manages an elliptical horn antenna.

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
    :class:`aedt.toolkits.antenna.EllipticalHorn`
        Elliptical horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import PyramidalRidged
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = Elliptical(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = Elliptical(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Elliptical"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz
        wavelength_in = constants.unit_converter(wavelength, "Length", "meter", "in")

        wg_radius_in = 0.5 * wavelength_in
        wg_length_in = wavelength_in
        horn_radius_in = 1.4 * wavelength_in
        horn_length_in = 2 * wavelength_in
        wall_thickness_in = 0.02 * wavelength_in
        ellipse_ratio = 0.6

        wg_radius = constants.unit_converter(wg_radius_in, "Length", "in", self.length_unit)
        parameters["wg_radius"] = wg_radius
        wg_length = constants.unit_converter(wg_length_in, "Length", "in", self.length_unit)
        parameters["wg_length"] = wg_length
        horn_radius = constants.unit_converter(horn_radius_in, "Length", "in", self.length_unit)
        parameters["horn_radius"] = horn_radius
        horn_length = constants.unit_converter(horn_length_in, "Length", "in", self.length_unit)
        parameters["horn_length"] = horn_length
        wall_thickness = constants.unit_converter(wall_thickness_in, "Length", "in", self.length_unit)
        parameters["wall_thickness"] = wall_thickness
        parameters["ellipse_ratio"] = ellipse_ratio

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw elliptical horn antenna.
        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        horn_radius = self.synthesis_parameters.horn_radius.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wg_radius = self.synthesis_parameters.wg_radius.hfss_variable
        ellipse_ratio = self.synthesis_parameters.ellipse_ratio.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Negative air
        neg_air = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            material="vacuum",
        )
        neg_air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wg_length,
            name="wg_outer_" + antenna_name,
            material=self.material,
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[neg_air.name], blank_list=[wall.name], keep_originals=False)

        # Input
        wg_in = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            name="wg_inner_" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system

        # Cap
        cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_ellipse(
            cs_plane=2,
            origin=["0", "0", horn_length],
            major_radius=horn_radius,
            ratio=ellipse_ratio,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn_sheet = self._app.modeler.create_ellipse(
            cs_plane=2,
            origin=["0", "0", horn_length],
            major_radius=horn_radius + "+" + wall_thickness,
            ratio=ellipse_ratio,
        )
        horn_sheet.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([horn_sheet.name, base_wall.name])
        self._app.modeler.connect([base.name, horn_top.name])

        # Horn
        self._app.modeler.subtract(blank_list=[horn_sheet.name], tool_list=[base.name], keep_originals=False)
        self._app.modeler.unite([horn_sheet.name, wall.name])

        air_base = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        air_top = self._app.modeler.create_ellipse(
            cs_plane=2,
            origin=["0", "0", horn_length],
            major_radius=horn_radius,
            ratio=ellipse_ratio,
        )

        self._app.modeler.connect([air_base, air_top])
        self._app.modeler.unite([wg_in, air_base])

        wg_in.name = "internal_" + antenna_name
        wg_in.color = (128, 255, 255)

        horn_sheet.name = "metal_" + antenna_name
        horn_sheet.material_name = self.material
        horn_sheet.color = (255, 128, 65)

        cap.color = (132, 132, 192)
        p1.color = (128, 0, 0)

        self.object_list[wg_in.name] = wg_in
        self.object_list[horn_sheet.name] = horn_sheet
        self.object_list[cap.name] = cap
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        wg_in.group_name = antenna_name
        horn_sheet.group_name = antenna_name
        cap.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass


class EPlane(CommonHorn):
    """Manages an E plane horn antenna.

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
    :class:`aedt.toolkits.antenna.EPlaneHorn`
        E plane horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import EPlane
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = EPlane(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = EPlane(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "material_properties": {},
        "outer_boundary": None,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "EPlane"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        if self._app and (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            mat_props = self._app.materials[self.material]
            permittivity = mat_props.permittivity.value
            self._input_parameters.material_properties["permittivity"] = permittivity

        elif isinstance(self.material_properties, dict):
            pass
        else:
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return parameters

        scale = lambda x: (10.0 / freq_ghz) * x

        def scale_value(value, round_val=3, doScale=True):
            if doScale:
                value = scale(value)
            return round(value, round_val)

        wg_length_in = scale_value(1.0)
        flare_in = scale_value(1.4)
        horn_length_in = scale_value(3.0)

        wg_obj = StandardWaveguide()
        wg_name = wg_obj.find_waveguide(freq_ghz)
        if wg_name:
            wg_dim_in = wg_obj.get_waveguide_dimensions(wg_name, self.length_unit)
            wg_a = wg_dim_in[0]
            wg_b = wg_dim_in[1]
            wall_thickness = wg_dim_in[2]
        else:
            wg_a_in = scale_value(0.9)
            wg_a = constants.unit_converter(wg_a_in, "Length", "in", self.length_unit)
            wg_b_in = scale_value(0.4)
            wg_b = constants.unit_converter(wg_b_in, "Length", "in", self.length_unit)
            wall_thickness_in = scale_value(0.02)
            wall_thickness = constants.unit_converter(wall_thickness_in, "Length", "in", self.length_unit)

        wg_length = constants.unit_converter(wg_length_in, "Length", "in", self.length_unit)
        parameters["wg_length"] = wg_length
        flare = constants.unit_converter(flare_in, "Length", "in", self.length_unit)
        parameters["flare"] = flare
        horn_length = constants.unit_converter(horn_length_in, "Length", "in", self.length_unit)
        parameters["horn_length"] = horn_length
        parameters["wg_width"] = wg_a
        parameters["wg_height"] = wg_b
        parameters["wall_thickness"] = wall_thickness

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw E plane horn antenna.
        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        flare = self.synthesis_parameters.flare.hfss_variable
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_height = self.synthesis_parameters.wg_height.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Base of the horn
        # Air
        air = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            material="vacuum",
        )
        air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                wg_length,
            ],
            name="wall_" + antenna_name,
            material="vacuum",
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[air.name], blank_list=[wall.name], keep_originals=False)

        # Top of the horn
        # Input
        wg_in = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            name="wg_inner" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system
        wg_in.color = (128, 255, 255)

        # Cap
        cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system
        cap.color = (132, 132, 193)

        # P1
        p1 = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height],
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[wg_width, wg_height],
            name="base_" + antenna_name,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "0",
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="base_wall_" + antenna_name,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + flare + "/2",
                horn_length,
            ],
            sizes=[wg_width, flare],
            name="horn_top_" + antenna_name,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + flare + "/2" + "-" + wall_thickness,
                horn_length,
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                flare + "+" + "2*" + wall_thickness,
            ],
            name="horn_" + antenna_name,
        )
        horn.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([horn, base_wall])
        self._app.modeler.connect([base, horn_top])

        new_wall = self._app.modeler.subtract(tool_list=[base.name], blank_list=[horn.name], keep_originals=False)

        new_horn = self._app.modeler.unite([horn.name, wall.name])

        horn.color = (132, 132, 193)
        horn.material_name = self.material

        # Air base
        air_base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[
                wg_width,
                wg_height,
            ],
            name="air_base_" + antenna_name,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        # Air top
        air_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + flare + "/2",
                horn_length,
            ],
            sizes=[
                wg_width,
                flare,
            ],
            name="air_top_" + antenna_name,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base.name, air_top.name])

        self._app.modeler.unite([wg_in, air_base])

        self.object_list[cap.name] = cap
        self.object_list[horn.name] = horn
        self.object_list[wg_in.name] = wg_in
        self.object_list[p1.name] = p1

        self._app.modeler.move([cap, horn, wg_in, p1], [pos_x, pos_y, pos_z])

        cap.group_name = antenna_name
        horn.group_name = antenna_name
        wg_in.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class HPlane(CommonHorn):
    """Manages an H plane horn antenna.

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
    :class:`aedt.toolkits.antenna.HPlaneHorn`
        H plane horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import HPlane
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = HPlane(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = HPlane(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "HPlane"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        scale = lambda x: (10.0 / freq_ghz) * x

        def scale_value(value, round_val=3, doScale=True):
            if doScale:
                value = scale(value)
            return round(value, round_val)

        wg_length_in = scale_value(2.0)
        flare_in = scale_value(1.8)
        horn_length_in = scale_value(3.0)

        wg_obj = StandardWaveguide()
        wg_name = wg_obj.find_waveguide(freq_ghz)
        if wg_name:
            wg_dim_in = wg_obj.get_waveguide_dimensions(wg_name, self.length_unit)
            wg_a = wg_dim_in[0]
            wg_b = wg_dim_in[1]
            wall_thickness = wg_dim_in[2]
        else:
            wg_a_in = scale_value(0.9)
            wg_a = constants.unit_converter(wg_a_in, "Length", "in", self.length_unit)
            wg_b_in = scale_value(0.4)
            wg_b = constants.unit_converter(wg_b_in, "Length", "in", self.length_unit)
            wall_thickness_in = scale_value(0.02)
            wall_thickness = constants.unit_converter(wall_thickness_in, "Length", "in", self.length_unit)

        wg_length = constants.unit_converter(wg_length_in, "Length", "in", self.length_unit)
        parameters["wg_length"] = wg_length
        flare = constants.unit_converter(flare_in, "Length", "in", self.length_unit)
        parameters["flare"] = flare
        horn_length = constants.unit_converter(horn_length_in, "Length", "in", self.length_unit)
        parameters["horn_length"] = horn_length
        parameters["wg_width"] = wg_a
        parameters["wg_height"] = wg_b
        parameters["wall_thickness"] = wall_thickness

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw H plane horn antenna.
        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")

            return False

        self.set_variables_in_hfss()

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        flare = self.synthesis_parameters.flare.hfss_variable
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_height = self.synthesis_parameters.wg_height.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Base of the horn
        # Air
        air = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            material="vacuum",
        )
        air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                wg_length,
            ],
            name="wall_" + antenna_name,
            material="vacuum",
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[air.name], blank_list=[wall.name], keep_originals=False)

        # Top of the horn
        # Input
        wg_in = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            name="wg_inner" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system
        wg_in.color = (128, 255, 255)

        # Cap
        cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system
        cap.color = (132, 132, 193)

        # P1
        p1 = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height],
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[wg_width, wg_height],
            name="base_" + antenna_name,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "0",
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="base_wall_" + antenna_name,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + flare + "/2",
                "-" + wg_height + "/2",
                horn_length,
            ],
            sizes=[flare, wg_height],
            name="horn_top_" + antenna_name,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + flare + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                horn_length,
            ],
            sizes=[
                flare + "+" + "2*" + wall_thickness,
                wg_height + "+" + "2*" + wall_thickness,
            ],
            name="horn_" + antenna_name,
        )
        horn.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([horn, base_wall])
        self._app.modeler.connect([base, horn_top])

        new_wall = self._app.modeler.subtract(tool_list=[base.name], blank_list=[horn.name], keep_originals=False)

        new_horn = self._app.modeler.unite([horn.name, wall.name])

        horn.color = (132, 132, 193)
        horn.material_name = self.material

        # Air base
        air_base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[
                wg_width,
                wg_height,
            ],
            name="air_base_" + antenna_name,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        # Air top
        air_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + flare + "/2",
                "-" + wg_height + "/2",
                horn_length,
            ],
            sizes=[
                flare,
                wg_height,
            ],
            name="air_top_" + antenna_name,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base.name, air_top.name])

        self._app.modeler.unite([wg_in, air_base])

        self.object_list[cap.name] = cap
        self.object_list[horn.name] = horn
        self.object_list[wg_in.name] = wg_in
        self.object_list[p1.name] = p1

        self._app.modeler.move([cap, horn, wg_in, p1], [pos_x, pos_y, pos_z])

        cap.group_name = antenna_name
        horn.group_name = antenna_name
        wg_in.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class Pyramidal(CommonHorn):
    """Manages a pyramidal horn antenna.

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
    :class:`aedt.toolkits.antenna.Pyramidal`
        Pyramidal horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Pyramidal
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = Pyramidal(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = Pyramidal(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Pyramidal"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        scale = lambda x: (10.0 / freq_ghz) * x

        def scale_value(value, round_val=3, doScale=True):
            if doScale:
                value = scale(value)
            return round(value, round_val)

        wg_length_in = scale_value(1.0)
        flare_a_in = scale_value(1.8)
        flare_b_in = scale_value(1.4)
        horn_length_in = scale_value(3.0)

        wg_obj = StandardWaveguide()
        wg_name = wg_obj.find_waveguide(freq_ghz)
        if wg_name:
            wg_dim_in = wg_obj.get_waveguide_dimensions(wg_name, self.length_unit)
            wg_a = wg_dim_in[0]
            wg_b = wg_dim_in[1]
            wall_thickness = wg_dim_in[2]
        else:
            wg_a_in = scale_value(0.9)
            wg_a = constants.unit_converter(wg_a_in, "Length", "in", self.length_unit)
            wg_b_in = scale_value(0.4)
            wg_b = constants.unit_converter(wg_b_in, "Length", "in", self.length_unit)
            wall_thickness_in = scale_value(0.02)
            wall_thickness = constants.unit_converter(wall_thickness_in, "Length", "in", self.length_unit)

        wg_length = constants.unit_converter(wg_length_in, "Length", "in", self.length_unit)
        parameters["wg_length"] = wg_length
        flare_a = constants.unit_converter(flare_a_in, "Length", "in", self.length_unit)
        parameters["flare_a"] = flare_a
        flare_b = constants.unit_converter(flare_b_in, "Length", "in", self.length_unit)
        parameters["flare_b"] = flare_b
        horn_length = constants.unit_converter(horn_length_in, "Length", "in", self.length_unit)
        parameters["horn_length"] = horn_length
        parameters["wg_width"] = wg_a
        parameters["wg_height"] = wg_b
        parameters["wall_thickness"] = wall_thickness

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw pyramidal horn antenna.
        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        flare_a = self.synthesis_parameters.flare_a.hfss_variable
        flare_b = self.synthesis_parameters.flare_b.hfss_variable
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_height = self.synthesis_parameters.wg_height.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Base of the horn
        # Air
        air = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            material="vacuum",
        )
        air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                wg_length,
            ],
            name="wall_" + antenna_name,
            material="vacuum",
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[air.name], blank_list=[wall.name], keep_originals=False)

        # Top of the horn
        # Input
        wg_in = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height, wg_length],
            name="wg_inner" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system
        wg_in.color = (128, 255, 255)

        # Cap
        cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system
        cap.color = (132, 132, 193)

        # P1
        p1 = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_height],
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[wg_width, wg_height],
            name="base_" + antenna_name,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "0",
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="base_wall_" + antenna_name,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + flare_a + "/2",
                "-" + flare_b + "/2",
                horn_length,
            ],
            sizes=[flare_a, flare_b],
            name="horn_top_" + antenna_name,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + flare_a + "/2" + "-" + wall_thickness,
                "-" + flare_b + "/2" + "-" + wall_thickness,
                horn_length,
            ],
            sizes=[
                flare_a + "+" + "2*" + wall_thickness,
                flare_b + "+" + "2*" + wall_thickness,
            ],
            name="horn_" + antenna_name,
        )
        horn.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([horn, base_wall])
        self._app.modeler.connect([base, horn_top])

        new_wall = self._app.modeler.subtract(tool_list=[base.name], blank_list=[horn.name], keep_originals=False)

        new_horn = self._app.modeler.unite([horn.name, wall.name])

        horn.color = (132, 132, 193)
        horn.material_name = self.material

        # Air base
        air_base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            sizes=[
                wg_width,
                wg_height,
            ],
            name="air_base_" + antenna_name,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        # Air top
        air_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + flare_a + "/2",
                "-" + flare_b + "/2",
                horn_length,
            ],
            sizes=[
                flare_a,
                flare_b,
            ],
            name="air_top_" + antenna_name,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base.name, air_top.name])

        self._app.modeler.unite([wg_in, air_base])

        self.object_list[cap.name] = cap
        self.object_list[horn.name] = horn
        self.object_list[wg_in.name] = wg_in
        self.object_list[p1.name] = p1

        self._app.modeler.move([cap, horn, wg_in, p1], [pos_x, pos_y, pos_z])

        cap.group_name = antenna_name
        horn.group_name = antenna_name
        wg_in.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class QuadRidged(CommonHorn):
    """Manages a quad-ridged horn antenna.

    This class is accessible through the app hfss object [1]_, [2]_, [3]_.

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
    :class:`aedt.toolkits.antenna.PyramidalRidged`
        Pyramidal ridged horn object.

    Notes
    -----
    .. [1] K. L. Walton and V. C. Sundberg, "Broadband ridged horn design,"
        Microwave J., vol. 4, pp. 96-101, Apr. 1964.
    .. [2] C. Bruns et al., "Analysis and Simulations of a 1-18 GHz
        Broadband Double-Ridged Horn Antenna,"
        IEEE Electromag. Compat., vol. 45, pp. 55-60, Feb 2003.
    .. [3] C. Balanis, "Horn Antennas," Antenna Theory Analysis,
        3rd ed. Hoboken: Wiley, 2005, ch. 13.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import QuadRidged
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = QuadRidged(app)
    >>> oantenna1.frequency = 12.0
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = QuadRidged(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
    >>> app.release_desktop(False, False)

    """

    _default_input_parameters = {
        "name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "QuadRidged"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        scale = lambda x: (5.0 / freq_ghz) * x

        def scale_value(value, round_val=3, doScale=True):
            if doScale:
                value = scale(value)
            return round(value, round_val)

        aperture_width = scale_value(89.6)
        flare_length = scale_value(64.0)
        wall_thickness = scale_value(5.0)
        wg_width = scale_value(25.6)
        wg_length = scale_value(64.0)
        ridge_width = scale_value(4.48)
        ridge_spacing = scale_value(4.8)
        ridge_height_1 = scale_value(10.4)
        ridge_height_2 = scale_value(12.96)
        ridge_height_3 = scale_value(14.56)
        ridge_height_4 = scale_value(16.0)
        ridge_height_5 = scale_value(16.96)
        ridge_height_6 = scale_value(16.48)
        ridge_height_7 = scale_value(16.0)
        ridge_height_8 = scale_value(14.56)
        ridge_height_9 = scale_value(12.64)
        ridge_height_10 = scale_value(9.92)

        parameters["aperture_width"] = aperture_width
        flare_length = constants.unit_converter(flare_length, "Length", "mm", self.length_unit)
        parameters["flare_length"] = flare_length
        wall_thickness = constants.unit_converter(wall_thickness, "Length", "mm", self.length_unit)
        parameters["wall_thickness"] = wall_thickness
        wg_width = constants.unit_converter(wg_width, "Length", "mm", self.length_unit)
        parameters["wg_width"] = wg_width
        wg_length = constants.unit_converter(wg_length, "Length", "mm", self.length_unit)
        parameters["wg_length"] = wg_length
        ridge_width = constants.unit_converter(ridge_width, "Length", "mm", self.length_unit)
        parameters["ridge_width"] = ridge_width
        ridge_spacing = constants.unit_converter(ridge_spacing, "Length", "mm", self.length_unit)
        parameters["ridge_spacing"] = ridge_spacing
        ridge_height_1 = constants.unit_converter(ridge_height_1, "Length", "mm", self.length_unit)
        parameters["ridge_height_1"] = ridge_height_1
        ridge_height_2 = constants.unit_converter(ridge_height_2, "Length", "mm", self.length_unit)
        parameters["ridge_height_2"] = ridge_height_2
        ridge_height_3 = constants.unit_converter(ridge_height_3, "Length", "mm", self.length_unit)
        parameters["ridge_height_3"] = ridge_height_3
        ridge_height_4 = constants.unit_converter(ridge_height_4, "Length", "mm", self.length_unit)
        parameters["ridge_height_4"] = ridge_height_4
        ridge_height_5 = constants.unit_converter(ridge_height_5, "Length", "mm", self.length_unit)
        parameters["ridge_height_5"] = ridge_height_5
        ridge_height_6 = constants.unit_converter(ridge_height_6, "Length", "mm", self.length_unit)
        parameters["ridge_height_6"] = ridge_height_6
        ridge_height_7 = constants.unit_converter(ridge_height_7, "Length", "mm", self.length_unit)
        parameters["ridge_height_7"] = ridge_height_7
        ridge_height_8 = constants.unit_converter(ridge_height_8, "Length", "mm", self.length_unit)
        parameters["ridge_height_8"] = ridge_height_8
        ridge_height_9 = constants.unit_converter(ridge_height_9, "Length", "mm", self.length_unit)
        parameters["ridge_height_9"] = ridge_height_9
        ridge_height_10 = constants.unit_converter(ridge_height_10, "Length", "mm", self.length_unit)
        parameters["ridge_height_10"] = ridge_height_10

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw conical horn antenna.
        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        if (
            self.material not in self._app.materials.mat_names_aedt
            and self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create the material before assigning it.")
            return False

        self.set_variables_in_hfss()

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        aperture_width = self.synthesis_parameters.aperture_width.hfss_variable
        flare_length = self.synthesis_parameters.flare_length.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_width = self.synthesis_parameters.wg_width.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        ridge_width = self.synthesis_parameters.ridge_width.hfss_variable
        ridge_spacing = self.synthesis_parameters.ridge_spacing.hfss_variable
        ridge_height_1 = self.synthesis_parameters.ridge_height_1.hfss_variable
        ridge_height_2 = self.synthesis_parameters.ridge_height_2.hfss_variable
        ridge_height_3 = self.synthesis_parameters.ridge_height_3.hfss_variable
        ridge_height_4 = self.synthesis_parameters.ridge_height_4.hfss_variable
        ridge_height_5 = self.synthesis_parameters.ridge_height_5.hfss_variable
        ridge_height_6 = self.synthesis_parameters.ridge_height_6.hfss_variable
        ridge_height_7 = self.synthesis_parameters.ridge_height_7.hfss_variable
        ridge_height_8 = self.synthesis_parameters.ridge_height_8.hfss_variable
        ridge_height_9 = self.synthesis_parameters.ridge_height_9.hfss_variable
        ridge_height_10 = self.synthesis_parameters.ridge_height_10.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Base of the horn
        # Air
        air = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_width + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_width, wg_length],
            material="vacuum",
        )
        air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+2*" + wall_thickness,
                wg_width + "+2*" + wall_thickness,
                wg_length,
            ],
            name="wall_" + antenna_name,
            material="vacuum",
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[air.name], blank_list=[wall.name], keep_originals=False)

        # Top of the horn
        # Input
        wg_in = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_width + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_width, wg_length],
            name="wg_inner" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system
        wg_in.color = (128, 255, 255)

        # Cap
        cap = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_width + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system
        cap.color = (132, 132, 193)

        # P1
        p1 = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_width + "/2",
                "-" + wg_length,
            ],
            sizes=[wg_width, wg_width],
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_width + "/2",
                "0",
            ],
            sizes=[wg_width, wg_width],
            name="base_" + antenna_name,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "0",
            ],
            sizes=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_width + "+2*" + wall_thickness,
            ],
            name="base_wall_" + antenna_name,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + aperture_width + "/2",
                "-" + aperture_width + "/2",
                flare_length,
            ],
            sizes=[aperture_width, aperture_width],
            name="horn_top_" + antenna_name,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + aperture_width + "/2" + "-" + wall_thickness,
                "-" + aperture_width + "/2" + "-" + wall_thickness,
                flare_length,
            ],
            sizes=[
                aperture_width + "+" + "2*" + wall_thickness,
                aperture_width + "+" + "2*" + wall_thickness,
            ],
            name="horn_" + antenna_name,
        )
        horn.history().properties["Coordinate System"] = coordinate_system

        # Ridge
        position_ridge_1 = []
        position_ridge_2 = []
        position_ridge_3 = []
        position_ridge_4 = []
        ridged_tapers = [
            ridge_height_1,
            ridge_height_2,
            ridge_height_3,
            ridge_height_4,
            ridge_height_5,
            ridge_height_6,
            ridge_height_7,
            ridge_height_8,
            ridge_height_9,
            ridge_height_10,
        ]
        x = "0"
        for i in range(10):
            y = (
                "("
                + wg_width
                + "/2+("
                + aperture_width
                + "-"
                + wg_width
                + ")/2*"
                + str(i)
                + "/10-"
                + str(ridged_tapers[i])
                + ")"
            )
            z = flare_length + "*" + str(i) + "/10"

            position_ridge_1.append([x, y, z])
            position_ridge_2.append([x, "-" + y, z])
            position_ridge_3.append([y, x, z])
            position_ridge_4.append(["-" + y, x, z])

        y = aperture_width + "/2"
        z = flare_length
        position_ridge_1.append([x, y, z])
        position_ridge_2.append([x, "-" + y, z])
        position_ridge_3.append([y, x, z])
        position_ridge_4.append(["-" + y, x, z])

        y = wg_width + "/2"
        z = "0"
        position_ridge_1.append([x, y, z])
        position_ridge_2.append([x, "-" + y, z])
        position_ridge_3.append([y, x, z])
        position_ridge_4.append(["-" + y, x, z])

        ridge1 = self._app.modeler.create_polyline(
            position_list=position_ridge_1,
            cover_surface=True,
            name="ridge_1" + antenna_name,
            material=self.material,
        )
        ridge1 = self._app.modeler.thicken_sheet(ridge1, ridge_width, True)
        ridge1.history().properties["Coordinate System"] = coordinate_system
        ridge1.color = (132, 132, 193)

        ridge2 = self._app.modeler.create_polyline(
            position_list=position_ridge_2,
            cover_surface=True,
            name="ridge_2" + antenna_name,
            material=self.material,
        )
        ridge2 = self._app.modeler.thicken_sheet(ridge2, ridge_width, True)
        ridge2.history().properties["Coordinate System"] = coordinate_system
        ridge2.color = (132, 132, 193)

        ridge3 = self._app.modeler.create_polyline(
            position_list=position_ridge_3,
            cover_surface=True,
            name="ridge_3" + antenna_name,
            material=self.material,
        )
        ridge3 = self._app.modeler.thicken_sheet(ridge3, ridge_width, True)
        ridge3.history().properties["Coordinate System"] = coordinate_system
        ridge3.color = (132, 132, 193)

        ridge4 = self._app.modeler.create_polyline(
            position_list=position_ridge_4,
            cover_surface=True,
            name="ridge_4" + antenna_name,
            material=self.material,
        )
        ridge4 = self._app.modeler.thicken_sheet(ridge4, ridge_width, True)
        ridge4.history().properties["Coordinate System"] = coordinate_system
        ridge4.color = (132, 132, 193)

        # Connectors of the ridge
        # Connector
        connector1 = self._app.modeler.create_box(
            origin=[
                "-" + ridge_width + "/2",
                "-" + wg_width + "/2",
                "-" + wg_length,
            ],
            sizes=[
                ridge_width,
                "(" + wg_width + "-" + ridge_spacing + ")/2",
                wg_length,
            ],
            name="connector_" + antenna_name,
            material="pec",
        )
        connector1.history().properties["Coordinate System"] = coordinate_system
        connector1.color = (132, 132, 193)

        connector2 = self._app.modeler.create_box(
            origin=[
                "-" + ridge_width + "/2",
                wg_width + "/2",
                "-" + wg_length,
            ],
            sizes=[
                ridge_width,
                "-(" + wg_width + "-" + ridge_spacing + ")/2",
                wg_length,
            ],
            name="connector_" + antenna_name,
            material="pec",
        )
        connector2.history().properties["Coordinate System"] = coordinate_system
        connector2.color = (132, 132, 193)

        connector3 = self._app.modeler.create_box(
            origin=[
                "-" + wg_width + "/2",
                "-" + ridge_width + "/2",
                "-" + wg_length,
            ],
            sizes=[
                "(" + wg_width + "-" + ridge_spacing + ")/2",
                ridge_width,
                wg_length,
            ],
            name="connector_" + antenna_name,
            material="pec",
        )
        connector3.history().properties["Coordinate System"] = coordinate_system
        connector3.color = (132, 132, 193)

        connector4 = self._app.modeler.create_box(
            origin=[
                wg_width + "/2",
                "-" + ridge_width + "/2",
                "-" + wg_length,
            ],
            sizes=[
                "-(" + wg_width + "-" + ridge_spacing + ")/2",
                ridge_width,
                wg_length,
            ],
            name="connector_" + antenna_name,
            material="pec",
        )
        connector4.history().properties["Coordinate System"] = coordinate_system
        connector4.color = (132, 132, 193)

        # Connect pieces
        self._app.modeler.connect([horn.name, base_wall.name])
        self._app.modeler.connect([base.name, horn_top.name])

        self._app.modeler.subtract(horn.name, base.name, False)
        self._app.modeler.unite(
            [
                horn,
                wall,
                ridge1,
                ridge2,
                ridge3,
                ridge4,
                connector1,
                connector2,
                connector3,
                connector4,
            ]
        )
        horn.color = (255, 128, 65)
        horn.material_name = self.material

        # Air base
        air_base = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + wg_width + "/2",
                "-" + wg_width + "/2",
                "0",
            ],
            sizes=[
                wg_width,
                wg_width,
            ],
            name="air_base_" + antenna_name,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        # Air top
        air_top = self._app.modeler.create_rectangle(
            orientation=2,
            origin=[
                "-" + aperture_width + "/2",
                "-" + aperture_width + "/2",
                flare_length,
            ],
            sizes=[
                aperture_width,
                aperture_width,
            ],
            name="air_top_" + antenna_name,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base.name, air_top.name])

        self._app.modeler.unite([wg_in, air_base])

        self.object_list[cap.name] = cap
        self.object_list[horn.name] = horn
        self.object_list[wg_in.name] = wg_in
        self.object_list[p1.name] = p1

        self._app.modeler.move([cap, horn, wg_in, p1], [pos_x, pos_y, pos_z])

        self._app.change_material_override(True)

        cap.group_name = antenna_name
        horn.group_name = antenna_name
        wg_in.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up model in PyDiscovery. To be implemented."""
        pass


class Conical_Special(CommonHorn):
    """Manages a conical horn antenna.

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
    :class:`aedt.toolkits.antenna.ConicalHorn`
        Conical horn object.

    Notes
    -----
    .. [1] C. Balanis, "Aperture Antennas: Analysis, Design, and Applications,"
        *Modern Antenna Handbook*, New York, 2008.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical
    >>> import ansys.aedt.core
    >>> oantenna1 = Conical()
    >>> oantenna1.frequency = 12.0
    >>> app = ansys.aedt.core.Hfss()
    >>> oantenna1 = Conical(app)
    >>> oantenna1.model_hfss()
    >>> oantenna1.setup_hfss()
    >>> oantenna2 = Conical(app, origin=[0.2, 0.5, 0])
    >>> oantenna2.model_hfss()
    >>> oantenna2.setup_hfss()
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
        "outer_boundary": "",
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "Conical"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis.

        Returns
        -------
        dict
            Analytical parameters.
        """
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz
        wavelength_in = constants.unit_converter(wavelength, "Length", "meter", "in")

        wg_radius_in = 0.5 * wavelength_in
        wg_length_in = 0.4 * wavelength_in
        horn_radius_in = 1.4 * wavelength_in
        horn_length_in = 2 * wavelength_in
        wall_thickness_in = 0.02 * wavelength_in

        wg_radius = constants.unit_converter(wg_radius_in, "Length", "in", self.length_unit)
        parameters["wg_radius"] = wg_radius
        wg_length = constants.unit_converter(wg_length_in, "Length", "in", self.length_unit)
        parameters["wg_length"] = wg_length
        horn_radius = constants.unit_converter(horn_radius_in, "Length", "in", self.length_unit)
        parameters["horn_radius"] = horn_radius
        horn_length = constants.unit_converter(horn_length_in, "Length", "in", self.length_unit)
        parameters["horn_length"] = horn_length
        wall_thickness = constants.unit_converter(wall_thickness_in, "Length", "in", self.length_unit)
        parameters["wall_thickness"] = wall_thickness

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical horn antenna.

        Once the antenna is created, this method is not used anymore."""
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

        # Solution type: Modal
        self._app.solution_type = "Modal"

        # Map parameters
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        horn_radius = self.synthesis_parameters.horn_radius.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wg_radius = self.synthesis_parameters.wg_radius.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        # Negative air
        neg_air = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            material="vacuum",
        )
        neg_air.history().properties["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wg_length,
            name="wg_outer_" + antenna_name,
            material=self.material,
        )
        wall.history().properties["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(tool_list=[neg_air.name], blank_list=[wall.name], keep_originals=False)

        # Input
        wg_in = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
            height="-" + wg_length,
            name="wg_inner_" + antenna_name,
            material="vacuum",
        )
        wg_in.history().properties["Coordinate System"] = coordinate_system

        # Cap
        cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + antenna_name,
            material="pec",
        )
        cap.history().properties["Coordinate System"] = coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "-" + wg_length],
            radius=wg_radius,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history().properties["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
        )
        base.history().properties["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius + "+" + wall_thickness,
        )
        base_wall.history().properties["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", horn_length],
            radius=horn_radius,
        )
        horn_top.history().properties["Coordinate System"] = coordinate_system

        horn_sheet = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", horn_length],
            radius=horn_radius + "+" + wall_thickness,
        )
        horn_sheet.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([horn_sheet.name, base_wall.name])
        self._app.modeler.connect([base.name, horn_top.name])

        # Horn
        self._app.modeler.subtract(blank_list=[horn_sheet.name], tool_list=[base.name], keep_originals=False)
        self._app.modeler.unite([horn_sheet.name, wall.name])

        air_base = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", "0"],
            radius=wg_radius,
        )
        air_base.history().properties["Coordinate System"] = coordinate_system

        air_top = self._app.modeler.create_circle(
            cs_plane=2,
            origin=["0", "0", horn_length],
            radius=horn_radius,
        )
        air_top.history().properties["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base, air_top])

        self._app.modeler.unite([wg_in, air_base])

        wg_in.name = "internal_" + antenna_name
        wg_in.color = (128, 255, 255)

        horn_sheet.name = "metal_" + antenna_name
        horn_sheet.material_name = self.material
        horn_sheet.color = (255, 128, 65)

        cap.color = (132, 132, 192)
        p1.color = (128, 0, 0)

        self.object_list[wg_in.name] = wg_in
        self.object_list[horn_sheet.name] = horn_sheet
        self.object_list[cap.name] = cap
        self.object_list[p1.name] = p1

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        wg_in.group_name = antenna_name
        horn_sheet.group_name = antenna_name
        cap.group_name = antenna_name
        p1.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass
