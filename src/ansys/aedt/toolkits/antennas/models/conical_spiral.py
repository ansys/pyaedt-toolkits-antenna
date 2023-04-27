from collections import OrderedDict
import math

import pyaedt.generic.constants as constants
from pyaedt.generic.general_methods import pyaedt_function_handler

import ansys.aedt.toolkits.antennas.common_ui
from ansys.aedt.toolkits.antennas.models.common import CommonAntenna


class CommonConicalSpiral(CommonAntenna):
    """Provides base methods common to conical spiral antennas."""

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
        if (
            value
            and value not in self._app.materials.mat_names_aedt
            and value not in self._app.materials.mat_names_aedt_lower
        ):
            ansys.aedt.toolkits.antennas.common_ui.logger.warning(
                "Material is not found. Create the material before assigning it"
            )
        else:
            if value != self.material and self.object_list:
                for antenna_obj in self.object_list:
                    if (
                        self.object_list[antenna_obj].material_name == self.material.lower()
                        and "port_cap" not in antenna_obj
                    ):
                        self.object_list[antenna_obj].material_name = value

                self._input_parameters.material = value
                parameters = self._synthesis()
                self.update_synthesis_parameters(parameters)
                self.set_variables_in_hfss()

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
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
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
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @pyaedt_function_handler()
    def _synthesis(self):
        pass


class Archimedean(CommonConicalSpiral):
    """Manages conical archimedeal spiral antenna.

    This class is accessible through the app hfss object [1]_.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``GHz``.
    material : str, optional
        Horn material. If material is not defined a new material parametrized will be defined.
        The default is ``"pec"``.
    outer_boundary : str, optional
        Boundary type to use. Options are ``"Radiation"``,
        ``"FEBI"``, and ``"PML"`` or None. The default is ``None``.
    huygens_box : bool, optional
        Create a Huygens box. The default is ``False``.
    length_unit : str, optional
        Length units. The default is ``"cm"``.
    parametrized : bool, optional
        Create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antennas.Archimedean`
        Conical archimedean spiral object.

    Notes
    -----
    .. [1] R. Johnson, "Frequency Independent Antennas," Antenna Engineering Handbook,
        3rd ed. New York, McGraw-Hill, 1993.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> from ansys.aedt.toolkits.antennas.conical_spiral import Archimedean
    >>> hfss = Hfss()
    >>> horn = hfss.add_from_toolkit(Archimedean, draw=True, start_frequency=20.0,
    ...                              stop_frequency=50.0, frequency_unit="GHz",
    ...                              outer_boundary=None, huygens_box=True, length_unit="cm",
    ...                              coordinate_system="CS1", antenna_name="HornAntenna",
    ...                              origin=[1, 100, 50])

    """

    _default_input_parameters = {
        "antenna_name": None,
        "antenna_material": "pec",
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "start_frequency": 4.0,
        "stop_frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
        "huygens_box": False,
    }

    def __init__(self, *args, **kwargs):
        CommonConicalSpiral.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight
        start_freq_hz = constants.unit_converter(
            self.start_frequency, "Freq", self.frequency_unit, "Hz"
        )
        stop_freq_hz = constants.unit_converter(
            self.stop_frequency, "Freq", self.frequency_unit, "Hz"
        )
        if (
            self.material not in self._app.materials.mat_names_aedt
            or self.material not in self._app.materials.mat_names_aedt_lower
        ):
            ansys.aedt.toolkits.antennas.common_ui.logger.warning(
                "Material is not found. Create the material before assigning it."
            )
            return parameters

        expansion_coefficient = 1.0
        offset_angle = 90.0
        spiral_coefficient = 1.0
        points = 200
        arms = 2
        port_extension = 0.1

        outer_rad_calc = lightSpeed / (2 * math.pi * start_freq_hz)
        outer_rad_calc = constants.unit_converter(
            outer_rad_calc, "Length", "meter", self.length_unit
        )
        outer_rad_calc_cm = constants.unit_converter(
            outer_rad_calc, "Length", self.length_unit, "cm"
        )
        inner_rad_calc = lightSpeed / (2 * math.pi * stop_freq_hz)
        inner_rad = constants.unit_converter(inner_rad_calc, "Length", "meter", self.length_unit)
        inner_rad_cm = constants.unit_converter(inner_rad, "Length", self.length_unit, "cm")

        parameters["expansion_coefficient"] = expansion_coefficient
        parameters["offset_angle"] = offset_angle
        parameters["spiral_coefficient"] = spiral_coefficient
        parameters["inner_rad"] = round(inner_rad, 2)
        parameters["turns_number"] = round(
            (outer_rad_calc_cm - inner_rad_cm) / 2.0 / math.pi / 0.1, 2
        )
        parameters["cone_height"] = round(
            (outer_rad_calc - inner_rad) * math.tan(math.radians(66.66)), 2
        )
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

        Once the antenna is created, this method is not used anymore."""
        if self.object_list:
            ansys.aedt.toolkits.antennas.common_ui.logger.warning("This antenna already exists")
            return False

        self.set_variables_in_hfss()

        # Map parameters
        expansion_coefficient = self.synthesis_parameters.expansion_coefficient.hfss_variable
        self._app[expansion_coefficient] = str(
            self.synthesis_parameters.expansion_coefficient.value
        )
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
        self._app[port_extension] = str(self.synthesis_parameters.port_extension.value)

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.antenna_name
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
            comp.history().props["Coordinate System"] = coordinate_system
            if "AntennaArm" in comp.name:
                comp.name = "ant_" + comp.name + antenna_name
            else:
                comp.name = "port_lump_" + antenna_name

            self.object_list[comp.name] = comp

        obj_udm.move([pos_x, pos_y, pos_z])

        obj_udm.group_name = antenna_name

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDisco. To be implemenented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Setup in PyDisco. To be implemenented."""
        pass
