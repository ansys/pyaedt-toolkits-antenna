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
import math

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.common.backend.logger_handler import logger

from ansys.aedt.toolkits.antenna.backend.antenna_models.common import CommonAntenna


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
    >>> antenna = Archimedean(hfss, start_frequency=20.0,
    ...                              stop_frequency=50.0, frequency_unit="GHz",
    ...                              outer_boundary='Radiation', length_unit="mm",
    ...                              antenna_name="Archimedean", origin=[1, 100, 50])
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
        lightSpeed = constants.SpeedOfLight
        start_freq_hz = constants.unit_converter(self.start_frequency, "Freq", self.frequency_unit, "Hz")
        stop_freq_hz = constants.unit_converter(self.stop_frequency, "Freq", self.frequency_unit, "Hz")

        expansion_coefficient = 1.0
        offset_angle = 90.0
        spiral_coefficient = 1.0
        points = 200
        arms = 2
        port_extension = 0.1

        outer_rad_calc = lightSpeed / (2 * math.pi * start_freq_hz)
        outer_rad_calc = constants.unit_converter(outer_rad_calc, "Length", "meter", self.length_unit)
        outer_rad_calc_cm = constants.unit_converter(outer_rad_calc, "Length", self.length_unit, "cm")
        inner_rad_calc = lightSpeed / (2 * math.pi * stop_freq_hz)
        inner_rad = constants.unit_converter(inner_rad_calc, "Length", "meter", self.length_unit)
        inner_rad_cm = constants.unit_converter(inner_rad, "Length", self.length_unit, "cm")
        port_extension = constants.unit_converter(port_extension, "Length", "cm", self.length_unit)

        parameters["expansion_coefficient"] = expansion_coefficient
        parameters["offset_angle"] = offset_angle
        parameters["spiral_coefficient"] = spiral_coefficient
        parameters["inner_rad"] = round(inner_rad, 2)
        parameters["turns_number"] = round((outer_rad_calc_cm - inner_rad_cm) / 2.0 / math.pi / 0.1, 2)
        parameters["cone_height"] = round((outer_rad_calc - inner_rad) * math.tan(math.radians(66.66)), 2)
        parameters["points"] = points
        parameters["arms_number"] = arms
        parameters["port_extension"] = port_extension

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical archimidean spiral antenna.

        This method uses the user-defined model from the AEDT installation.

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
        expansion_coefficient = self.synthesis_parameters.expansion_coefficient.hfss_variable
        self._app[expansion_coefficient] = str(self.synthesis_parameters.expansion_coefficient.value)
        offset_angle = self.synthesis_parameters.offset_angle.hfss_variable
        self._app[offset_angle] = str(self.synthesis_parameters.offset_angle.value) + "deg"
        spiral_coefficient = self.synthesis_parameters.spiral_coefficient.hfss_variable
        self._app[spiral_coefficient] = str(self.synthesis_parameters.spiral_coefficient.value)
        inner_rad = self.synthesis_parameters.inner_rad.hfss_variable
        turns = self.synthesis_parameters.turns_number.hfss_variable
        self._app[turns] = str(self.synthesis_parameters.turns_number.value)
        cone_height = self.synthesis_parameters.cone_height.hfss_variable
        arms = self.synthesis_parameters.arms_number.hfss_variable
        self._app[arms] = str(self.synthesis_parameters.arms_number.value)
        points = self.synthesis_parameters.points.hfss_variable
        self._app[points] = str(self.synthesis_parameters.points.value)
        port_extension = self.synthesis_parameters.port_extension.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        my_udmPairs = []
        mypair = ["NumberOfPoints", points]
        my_udmPairs.append(mypair)
        mypair = ["NumberOfArms", arms]
        my_udmPairs.append(mypair)
        mypair = ["InnerRadius", inner_rad]
        my_udmPairs.append(mypair)
        mypair = ["NumberOfTurns", turns]
        my_udmPairs.append(mypair)
        mypair = ["Offset", offset_angle]
        my_udmPairs.append(mypair)
        mypair = ["ConeHeight", cone_height]
        my_udmPairs.append(mypair)
        mypair = ["ExpansionCoefficient", expansion_coefficient]
        my_udmPairs.append(mypair)
        mypair = ["SpiralCoefficient", spiral_coefficient]
        my_udmPairs.append(mypair)
        mypair = ["Port_Extension", port_extension]
        my_udmPairs.append(mypair)
        obj_udm = self._app.modeler.create_udm(
            udmfullname="HFSS/Antenna Toolkit/Spiral/Archimedean.py",
            udm_params_list=my_udmPairs,
            udm_library="syslib",
            name="archimidean",
        )
        for part in obj_udm.parts:
            comp = obj_udm.parts[part]
            comp.history().properties["Coordinate System"] = coordinate_system
            if "AntennaArm" in comp.name:
                comp.name = "ant_" + comp.name + antenna_name
            else:
                comp.name = "port_lump_" + antenna_name

            self.object_list[comp.name] = comp

        obj_udm.move([pos_x, pos_y, pos_z])

        obj_udm.group_name = antenna_name

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
    >>> antenna = Log(hfss, start_frequency=20.0,
    ...                              stop_frequency=50.0, frequency_unit="GHz",
    ...                              outer_boundary='Radiation', length_unit="mm",
    ...                              antenna_name="Log", origin=[1, 100, 50])
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

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a conical log spiral antenna. This method uses the User Defined Model from AEDT installation.

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

        # Map parameters
        expansion_coefficient = self.synthesis_parameters.expansion_coefficient.hfss_variable
        self._app[expansion_coefficient] = str(self.synthesis_parameters.expansion_coefficient.value)
        offset_angle = self.synthesis_parameters.offset_angle.hfss_variable
        self._app[offset_angle] = str(self.synthesis_parameters.offset_angle.value) + "deg"
        spiral_coefficient = self.synthesis_parameters.spiral_coefficient.hfss_variable
        self._app[spiral_coefficient] = str(self.synthesis_parameters.spiral_coefficient.value)
        inner_rad = self.synthesis_parameters.inner_rad.hfss_variable
        turns = self.synthesis_parameters.turns_number.hfss_variable
        self._app[turns] = str(self.synthesis_parameters.turns_number.value)
        cone_height = self.synthesis_parameters.cone_height.hfss_variable
        arms = self.synthesis_parameters.arms_number.hfss_variable
        self._app[arms] = str(self.synthesis_parameters.arms_number.value)
        points = self.synthesis_parameters.points.hfss_variable
        self._app[points] = str(self.synthesis_parameters.points.value)

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.name
        coordinate_system = self.coordinate_system

        my_udmPairs = []
        mypair = ["NumberOfPoints", points]
        my_udmPairs.append(mypair)
        mypair = ["NumberOfArms", arms]
        my_udmPairs.append(mypair)
        mypair = ["InnerRadius", inner_rad]
        my_udmPairs.append(mypair)
        mypair = ["NumberOfTurns", turns]
        my_udmPairs.append(mypair)
        mypair = ["Offset", offset_angle]
        my_udmPairs.append(mypair)
        mypair = ["ConeHeight", cone_height]
        my_udmPairs.append(mypair)
        mypair = ["ExpansionCoefficient", expansion_coefficient]
        my_udmPairs.append(mypair)
        obj_udm = self._app.modeler.create_udm(
            udmfullname="HFSS/Antenna Toolkit/Spiral/Log.py",
            udm_params_list=my_udmPairs,
            udm_library="syslib",
            name="log",
        )
        for part in obj_udm.parts:
            comp = obj_udm.parts[part]
            comp.history().properties["Coordinate System"] = coordinate_system
            if "AntennaArm" in comp.name:
                comp.name = "ant_" + comp.name + antenna_name
            else:
                comp.name = "port_lump_" + antenna_name

            self.object_list[comp.name] = comp

        obj_udm.move([pos_x, pos_y, pos_z])

        obj_udm.group_name = antenna_name

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
    >>> antenna = Archimedean(hfss, start_frequency=20.0,
    ...                              stop_frequency=50.0, frequency_unit="GHz",
    ...                              outer_boundary='Radiation', length_unit="cm",
    ...                              antenna_name="Sinuous", origin=[1, 100, 50])
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
        lightSpeed = constants.SpeedOfLight
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
            scale_factor * lightSpeed / start_freq_hz / 4.0 / (math.radians(alpha_angle) + math.radians(delta_angle))
        )
        outer_rad = constants.unit_converter(outer_rad_calc, "Length", "meter", self.length_unit)
        inner_rad_calc = (
            scale_factor
            * lightSpeed
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

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a sinuous log spiral antenna. This method uses the User Defined Model from AEDT installation.

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

        my_udmPairs = []
        mypair = ["NumberOfPoints", points]
        my_udmPairs.append(mypair)
        mypair = ["NumberOfCells", cell_number]
        my_udmPairs.append(mypair)
        mypair = ["Alpha", alpha_angle]
        my_udmPairs.append(mypair)
        mypair = ["GrowRate", growth_rate]
        my_udmPairs.append(mypair)
        mypair = ["OuterRadius", outer_rad]
        my_udmPairs.append(mypair)
        mypair = ["Delta", delta_angle]
        my_udmPairs.append(mypair)
        mypair = ["NumberOfArms", arms]
        my_udmPairs.append(mypair)
        mypair = ["ConeHeight", cone_height]
        my_udmPairs.append(mypair)
        mypair = ["Port_Extension", port_extension]
        my_udmPairs.append(mypair)
        obj_udm = self._app.modeler.create_udm(
            udmfullname="HFSS/Antenna Toolkit/Spiral/Sinuous.py",
            udm_params_list=my_udmPairs,
            udm_library="syslib",
            name="log",
        )
        port_cont = 1
        gnd_cont = 1
        for part in obj_udm.parts:
            comp = obj_udm.parts[part]
            comp.history().properties["Coordinate System"] = coordinate_system
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

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up in PyDiscovery. To be implemented."""
        pass
