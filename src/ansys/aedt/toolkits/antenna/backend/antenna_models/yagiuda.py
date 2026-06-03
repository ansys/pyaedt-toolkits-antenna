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
from collections import namedtuple

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class CommonYagiUda(CommonAntenna):
    """Provides base methods common to Yagi-Uda antenna models."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "YagiUda"
        CommonAntenna.__init__(self, _default_input_parameters, *args, **kwargs)

    @property
    def material_properties(self):
        """Material properties."""
        return self._input_parameters.material_properties

    @property
    def gain(self):
        """Target gain in dBi."""
        return self._input_parameters.gain

    @gain.setter
    def gain(self, value):
        self._input_parameters.gain = value
        if self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

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

    def _resolve_material(self):
        """Return an AEDT material name for dielectric bodies."""
        if not self._app:
            return self.material

        if (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            return self.material

        material_name = self.material or f"{self.antenna_type}_material"
        if material_name in self._app.materials.mat_names_aedt_lower:
            return material_name

        mat = self._app.materials.add_material(material_name)
        if self.material_properties:
            if "permittivity" in self.material_properties:
                mat.permittivity = float(self.material_properties["permittivity"])
            if "conductivity" in self.material_properties:
                mat.conductivity = float(self.material_properties["conductivity"])
        self._input_parameters.material = material_name
        return material_name

    @pyaedt_function_handler()
    def synthesis(self):
        pass


class QuasiYagi(CommonYagiUda):
    """Manage a quasi-Yagi antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``2.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Substrate material. The default is ``"Rogers"``.
    material_properties : dict, optional
        Material properties for the substrate. The default is
        ``{"permittivity": 10.2}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"mm"``.
    substrate_height : float, optional
        Substrate height. The default is ``3.175``.
    gain : float, optional
        Target gain in dBi. The default is ``0.0``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda.QuasiYagi`
        Antenna object.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda import QuasiYagi
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = QuasiYagi(app)
    >>> antenna.model_hfss()
    >>> app.release_desktop(False, False)
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 2.0,
        "frequency_unit": "GHz",
        "material": "Rogers",
        "material_properties": {"permittivity": 10.2},
        "outer_boundary": "",
        "substrate_height": 3.175,
        "gain": 0.0,
    }

    _base_dimensions_mm = {
        "director_length": 16.5,
        "director_width": 3.0,
        "driver_length": 43.5,
        "driver_width": 3.0,
        "director_spacing": 15.0,
        "driver_spacing": 22.5,
        "ground_spacing": 42.0,
        "ground_length": 38.5,
        "feed_width": 3.0,
        "launcher_width": 6.0,
        "feed_gap": 3.175,
        "sub_width": 75.0,
    }
    _base_frequency = 2.0

    def __init__(self, *args, **kwargs):
        CommonYagiUda.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "QuasiYagi"

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        scale = self._base_frequency / freq_ghz

        if self._app and (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            self._input_parameters.material_properties["permittivity"] = self._app.materials[
                self.material
            ].permittivity.value

        for key, value in self._base_dimensions_mm.items():
            parameters[key] = constants.unit_converter(value * scale, "Length", "mm", self.length_unit)

        parameters["sub_h"] = self.substrate_height
        parameters["sub_length"] = (
            parameters["ground_spacing"] + parameters["ground_length"] + parameters["feed_width"] * 2.0
        )
        parameters["launcher_length"] = parameters["sub_length"] - (
            parameters["driver_spacing"] + parameters["driver_width"] / 2.0
        )
        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict((i, parameters[i]) for i in my_keys)

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a quasi-Yagi antenna."""
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        dielectric_material = self._resolve_material()
        self.set_variables_in_hfss()

        antenna_name = self.name
        coordinate_system = self.coordinate_system
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_width = self.synthesis_parameters.sub_width.hfss_variable
        sub_length = self.synthesis_parameters.sub_length.hfss_variable
        ground_length = self.synthesis_parameters.ground_length.hfss_variable
        director_length = self.synthesis_parameters.director_length.hfss_variable
        director_width = self.synthesis_parameters.director_width.hfss_variable
        director_spacing = self.synthesis_parameters.director_spacing.hfss_variable
        driver_length = self.synthesis_parameters.driver_length.hfss_variable
        driver_width = self.synthesis_parameters.driver_width.hfss_variable
        driver_spacing = self.synthesis_parameters.driver_spacing.hfss_variable
        launcher_length = self.synthesis_parameters.launcher_length.hfss_variable
        launcher_width = self.synthesis_parameters.launcher_width.hfss_variable
        feed_width = self.synthesis_parameters.feed_width.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        sub = self._app.modeler.create_box(
            origin=["-" + sub_h, "-" + sub_width + "/2", "-" + sub_length],
            sizes=[sub_h, sub_width, sub_length],
            name="sub_" + antenna_name,
            material=dielectric_material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        gnd = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=["-" + sub_h, "-" + sub_width + "/2", "-" + sub_length],
            sizes=[sub_width, ground_length],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)

        director = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0.0, "-" + director_length + "/2", "-" + director_spacing + "-" + director_width + "/2"],
            sizes=[director_length, director_width],
            name="ant_director_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        director.color = (255, 128, 65)

        driver = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0.0, "-" + driver_length + "/2", "-" + driver_spacing + "-" + driver_width + "/2"],
            sizes=[driver_length, driver_width],
            name="ant_driver_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        driver.color = (255, 128, 65)

        launcher = self._app.modeler.create_rectangle(
            orientation=Plane.YZ,
            origin=[0.0, "-" + launcher_width + "/2", "-" + sub_length],
            sizes=[launcher_width, launcher_length],
            name="ant_launcher_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        launcher.color = (255, 128, 65)

        port = self._app.modeler.create_rectangle(
            orientation=Plane.XY,
            origin=["-" + sub_h, "-" + feed_width + "/2", "-" + sub_length],
            sizes=[sub_h, feed_width],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)
        port.transparency = 0.2

        for obj in [sub, gnd, director, driver, launcher, port]:
            obj.group_name = antenna_name

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[director.name] = director
        self.object_list[driver.name] = driver
        self.object_list[launcher.name] = launcher
        self.object_list[port.name] = port
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        return True


class WireYagiUda(CommonYagiUda):
    """Manage a wire Yagi-Uda antenna.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``1.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.
    material : str, optional
        Conductor material. The default is ``"pec"``.
    material_properties : dict, optional
        Material properties for the conductor. The default is ``{}``.
    outer_boundary : str, optional
        Boundary type to use. The default is ``None``. Options are
        ``"FEBI"``, ``"PML"``, ``"Radiation"``, and ``None``.
    length_unit : str, optional
        Length units. The default is ``"cm"``.
    substrate_height : float, optional
        Reserved substrate-height input carried by the common family base.
        The default is ``0.0``.
    gain : float, optional
        Target gain in dBi used to select a Viezbicke design table entry.
        The default is ``9.26``.

    Returns
    -------
    :class:`ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda.WireYagiUda`
        Antenna object.

    Notes
    -----
    .. [1] P. P. Viezbicke, *Yagi Antenna Design*, National Bureau of
       Standards, U.S. Department of Commerce, Boulder, CO, NBS Technical
       Note 688, 1976.
    .. [2] C. A. Balanis, "Design of Yagi-Uda Antennas," in *Antenna Theory:
       Analysis and Design*, 3rd ed., Hoboken, Wiley, 2005, sec. 10.3,
       pp. 577-600.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda import WireYagiUda
    >>> import ansys.aedt.core
    >>> app = ansys.aedt.core.Hfss()
    >>> antenna = WireYagiUda(app)
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
        "material": "pec",
        "material_properties": {},
        "outer_boundary": "",
        "substrate_height": 0.0,
        "gain": 9.26,
    }
    _max_directors = 15

    def __init__(self, *args, **kwargs):
        CommonYagiUda.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "WireYagiUda"

    @staticmethod
    def _viezbicke_designs():
        yagi_design = namedtuple("ViezbickeYagi", ["reflector_length", "director_spacing", "director_lengths", "gain"])
        return [
            yagi_design(reflector_length=0.482, director_spacing=0.2, director_lengths=[0.424], gain=9.26),
            yagi_design(
                reflector_length=0.482,
                director_spacing=0.2,
                director_lengths=[0.428, 0.424, 0.428],
                gain=11.36,
            ),
            yagi_design(
                reflector_length=0.482,
                director_spacing=0.25,
                director_lengths=[0.428, 0.420, 0.420, 0.428],
                gain=12.36,
            ),
            yagi_design(
                reflector_length=0.482,
                director_spacing=0.20,
                director_lengths=[0.432, 0.415, 0.407, 0.398, 0.390, 0.390, 0.390, 0.390, 0.398, 0.407],
                gain=14.41,
            ),
            yagi_design(
                reflector_length=0.482,
                director_spacing=0.20,
                director_lengths=[
                    0.428,
                    0.420,
                    0.407,
                    0.398,
                    0.394,
                    0.390,
                    0.386,
                    0.386,
                    0.386,
                    0.386,
                    0.386,
                    0.386,
                    0.386,
                    0.386,
                    0.386,
                ],
                gain=15.56,
            ),
            yagi_design(
                reflector_length=0.475,
                director_spacing=0.308,
                director_lengths=[
                    0.424,
                    0.424,
                    0.420,
                    0.407,
                    0.403,
                    0.398,
                    0.394,
                    0.390,
                    0.390,
                    0.390,
                    0.390,
                    0.390,
                    0.390,
                ],
                gain=16.36,
            ),
        ]

    def _design_for_gain(self, gain):
        selected_design = self._viezbicke_designs()[-1]
        for design in self._viezbicke_designs():
            if design.gain >= gain - 0.01:
                selected_design = design
                break
        return selected_design

    @pyaedt_function_handler()
    def synthesis(self):
        """Antenna synthesis."""
        parameters = {}
        light_speed = constants.SpeedOfLight
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = light_speed / freq_hz
        wavelength_working = constants.unit_converter(wavelength, "Length", "meter", self.length_unit)

        design = self._design_for_gain(self.gain)
        parameters["element_diameter"] = 0.0085 * wavelength_working
        parameters["driven_element_length"] = 0.45 * wavelength_working
        parameters["feed_gap"] = 0.5 * parameters["element_diameter"]
        parameters["reflector_spacing"] = 0.2 * wavelength_working
        parameters["reflector_length"] = design.reflector_length * wavelength_working
        parameters["number_of_directors"] = len(design.director_lengths)
        parameters["director_spacing"] = design.director_spacing * wavelength_working
        for index in range(self._max_directors):
            key = f"director_{index + 1:02d}_length"
            parameters[key] = 0.0
            if index < len(design.director_lengths):
                parameters[key] = design.director_lengths[index] * wavelength_working

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict((i, parameters[i]) for i in my_keys)

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a wire Yagi-Uda antenna."""
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
        element_diameter = self.synthesis_parameters.element_diameter.hfss_variable
        driven_element_length = self.synthesis_parameters.driven_element_length.hfss_variable
        feed_gap = self.synthesis_parameters.feed_gap.hfss_variable
        reflector_spacing = self.synthesis_parameters.reflector_spacing.hfss_variable
        reflector_length = self.synthesis_parameters.reflector_length.hfss_variable
        director_spacing = self.synthesis_parameters.director_spacing.hfss_variable
        number_of_directors = int(self.synthesis_parameters.number_of_directors.value)
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        driven_top = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0.0, 0.0, feed_gap + "/2"],
            radius=element_diameter + "/2",
            height=driven_element_length + "/2-" + feed_gap + "/2",
            name="ant_driven_top_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        driven_top.color = (255, 128, 65)

        driven_bottom = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0.0, 0.0, "-" + driven_element_length + "/2"],
            radius=element_diameter + "/2",
            height=driven_element_length + "/2-" + feed_gap + "/2",
            name="ant_driven_bottom_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        driven_bottom.color = (255, 128, 65)

        reflector = self._app.modeler.create_cylinder(
            orientation=Axis.Z,
            origin=[0.0, "-" + reflector_spacing, "-" + reflector_length + "/2"],
            radius=element_diameter + "/2",
            height=reflector_length,
            name="ant_reflector_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        reflector.color = (255, 128, 65)

        port = self._app.modeler.create_rectangle(
            orientation=Plane.ZX,
            origin=["-" + element_diameter + "/2", 0.0, "-" + feed_gap + "/2"],
            sizes=[feed_gap, element_diameter],
            name="port_lump_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)
        port.transparency = 0.2

        self.object_list[driven_top.name] = driven_top
        self.object_list[driven_bottom.name] = driven_bottom
        self.object_list[reflector.name] = reflector
        self.object_list[port.name] = port

        for index in range(number_of_directors):
            length_variable = getattr(self.synthesis_parameters, f"director_{index + 1:02d}_length").hfss_variable
            director = self._app.modeler.create_cylinder(
                orientation=Axis.Z,
                origin=[0.0, f"({index + 1})*{director_spacing}", f"-{length_variable}/2"],
                radius=element_diameter + "/2",
                height=length_variable,
                name=f"ant_director_{index + 1:02d}_{antenna_name}",
                material=self.material,
                new_properties={"Coordinate System": coordinate_system},
            )
            director.color = (255, 128, 65)
            self.object_list[director.name] = director

        for obj in self.object_list.values():
            obj.group_name = antenna_name

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])
        return True
