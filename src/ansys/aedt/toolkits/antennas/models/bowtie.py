from collections import OrderedDict
import math

import pyaedt.generic.constants as constants
from pyaedt.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antennas.models.common import TransmissionLine
from ansys.aedt.toolkits.antennas.models.patch import CommonPatch


class BowTie(CommonPatch):
    """Manages a bowtie antenna.

    This class is accessible through the ``Hfss`` object.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``GHz``.
    material : str, optional
        Substrate material. If the material is not defined, a new
        material ``parametrized`` is defined. The default is ``"FR4_epoxy"``.
    outer_boundary : str, optional
        Boundary type to use. Options are ``"Radiation"``,
        ``"FEBI"``, ``"PML"`` and ``None``. The default is ``None``.
    huygens_box : bool, optional
        Whether to create a Huygens box. The default is ``False``.
    length_unit : str, optional
        Length units. The default is ``"cm"``.
    substrate_height : float, optional
        Substrate height. The default is ``0.1575``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antennas.RectangularPatchProbe`
        Patch antenna object.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> from ansys.aedt.toolkits.antennas.models.bowtie import BowTie
    >>> hfss = Hfss()
    >>> patch = hfss.add_from_toolkit(BowTie, draw=True, frequency=20.0,
    ...                               frequency_unit="GHz")

    """

    _default_input_parameters = {
        "antenna_name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "outer_boundary": None,
        "huygens_box": False,
        "substrate_height": 0.1575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz

        if (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            mat_props = self._app.materials[self.material]
        else:
            self._app.logger.warning(
                "Material is not found. Create the material before assigning it."
            )
            return parameters

        subPermittivity = float(mat_props.permittivity.value)

        sub_meters = constants.unit_converter(
            self.substrate_height, "Length", self.length_unit, "meter"
        )

        tl = TransmissionLine()
        eff_Permittivity = tl.suspended_strip_calculator(
            wavelength, wavelength / 80.0, sub_meters, subPermittivity
        )

        eff_wl_meters = wavelength / math.sqrt(eff_Permittivity)
        eff_wl_working_units = constants.unit_converter(
            eff_wl_meters, output_units=self.length_unit
        )
        correction_factor = 0.65
        arm_length = round(
            correction_factor
            * math.sqrt(
                math.pow(eff_wl_working_units / 4.0, 2)
                - math.pow(eff_wl_working_units / 80.0 / 2.0, 2)
            ),
            2,
        )
        inner_width = round(correction_factor * eff_wl_working_units / 80.0, 2)
        outer_width = round(correction_factor * eff_wl_working_units / 80.0 * 18.0, 2)
        port_gap = round(correction_factor * eff_wl_working_units / 80.0, 2)
        sub_x = round(correction_factor * eff_wl_working_units, 0)
        sub_y = round(correction_factor * eff_wl_working_units, 0)
        parameters["inner_width"] = inner_width
        parameters["outer_width"] = outer_width
        parameters["arm_length"] = arm_length
        parameters["port_gap"] = port_gap
        parameters["sub_x"] = sub_x
        parameters["sub_y"] = sub_y
        parameters["sub_h"] = self.substrate_height

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a rectangular patch antenna with a coaxial probe.

        Once the antenna is created, this method is not used anymore.
        """
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        self.set_variables_in_hfss()

        # Map parameters
        arm_length = self.synthesis_parameters.arm_length.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        inner_width = self.synthesis_parameters.inner_width.hfss_variable
        outer_width = self.synthesis_parameters.outer_width.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.antenna_name
        coordinate_system = self.coordinate_system

        # Substrate
        sub = self._app.modeler.create_box(
            position=["-" + sub_x + "/2", "-" + sub_y + "/2", 0.0],
            dimensions_list=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            matname=self.material,
        )
        sub.color = (0, 128, 0)
        sub.history.props["Coordinate System"] = coordinate_system
        array_points = [["{}/2".format(inner_width), "{}/2".format(port_gap), 0]]
        array_points.append(["-{}/2".format(inner_width), "{}/2".format(port_gap), 0])
        array_points.append(
            ["-{}/2".format(outer_width), "{}/2.0+{}".format(port_gap, arm_length), 0.0]
        )
        array_points.append(
            ["{}/2".format(outer_width), "{}/2.0+{}".format(port_gap, arm_length), 0.0]
        )
        array_points.append(["{}/2".format(inner_width), "{}/2".format(port_gap), 0])
        ant = self._app.modeler.create_polyline(array_points, cover_surface=True, name="ant_arm")
        ant.color = (255, 128, 65)
        ant.transparency = 0.1
        ant.history.props["Coordinate System"] = coordinate_system
        ant2_name = ant.duplicate_around_axis(
            self._app.AXIS.Z,
            180,
            2,
        )[0]
        ant2 = self._app.modeler[ant2_name]

        p1 = self._app.modeler.create_rectangle(
            csPlane=self._app.PLANE.XY,
            position=["-{}/2".format(inner_width), "-{}/2".format(port_gap), 0.0],
            dimension_list=[inner_width, port_gap],
            name="port_lump_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = coordinate_system

        self._app.modeler.move([p1.name, ant2_name, ant.name], [0, 0, sub_h])

        if self.huygens_box:
            lightSpeed = constants.SpeedOfLight  # m/s
            freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
            huygens_dist = str(
                constants.unit_converter(
                    lightSpeed / (10 * freq_hz), "Length", "meter", self.length_unit
                )
            )
            huygens = self._app.modeler.create_box(
                position=[
                    "-{}/2-{}{}".format(sub_x, huygens_dist, self.length_unit),
                    "-{}/2-{}{}".format(sub_y, huygens_dist, self.length_unit),
                    "-{}{}".format(huygens_dist, self.length_unit),
                ],
                dimensions_list=[
                    "{}+2*{}{}".format(sub_x, huygens_dist, self.length_unit),
                    "{}+2*{}{}".format(sub_y, huygens_dist, self.length_unit),
                    "{}+2*{}{}".format(sub_h, huygens_dist, self.length_unit),
                ],
                name="huygens_" + antenna_name,
                matname="air",
            )
            huygens.display_wireframe = True
            huygens.color = (0, 0, 255)
            huygens.history.props["Coordinate System"] = coordinate_system
            huygens.group_name = antenna_name
            self.object_list[huygens.name] = huygens

        sub.group_name = antenna_name
        ant.group_name = antenna_name
        ant2.group_name = antenna_name
        p1.group_name = antenna_name

        self.object_list[sub.name] = sub
        self.object_list[ant.name] = ant
        self.object_list[ant2.name] = ant2
        self.object_list[p1.name] = p1
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

    @pyaedt_function_handler()
    def model_disco(self):
        """Model the bowtie antenna in PyDiscovery. To be implemenented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemenented."""
        pass


class BowTieRounded(CommonPatch):
    """Manages a bowtie rounded antenna.

    This class is accessible through the ``Hfss`` object.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``GHz``.
    material : str, optional
        Substrate material. If material is not defined, a new
        material, ``parametrized``is defined.
        The default is ``"FR4_epoxy"``.
    outer_boundary : str, optional
        Boundary type to use. Options are ``"Radiation"``,
        ``"FEBI"``, ``"PML"``, and ``None``. The default is ``None``.
    huygens_box : bool, optional
        Whether to create a Huygens box. The default is ``False``.
    length_unit : str, optional
        Length units. The default is ``"cm"``.
    substrate_height : float, optional
        Substrate height. The default is ``0.1575``.
    parametrized : bool, optional
        Whether to create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antennas.RectangularPatchProbe`
        Patch antenna object.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> from ansys.aedt.toolkits.antennas.models.bowtie import BowTie
    >>> hfss = Hfss()
    >>> patch = hfss.add_from_toolkit(BowTie, draw=True, frequency=20.0,
    ...                               frequency_unit="GHz")

    """

    _default_input_parameters = {
        "antenna_name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "FR4_epoxy",
        "outer_boundary": None,
        "huygens_box": False,
        "substrate_height": 0.1575,
    }

    def __init__(self, *args, **kwargs):
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz

        if (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            mat_props = self._app.materials[self.material]
        else:
            self._app.logger.warning(
                "Material is not found. Create the material before assigning it."
            )
            return parameters

        subPermittivity = float(mat_props.permittivity.value)

        sub_meters = constants.unit_converter(
            self.substrate_height, "Length", self.length_unit, "meter"
        )

        tl = TransmissionLine()
        eff_Permittivity = tl.suspended_strip_calculator(
            wavelength, wavelength / 80.0, sub_meters, subPermittivity
        )

        eff_wl_meters = wavelength / math.sqrt(eff_Permittivity)
        eff_wl_working_units = constants.unit_converter(
            eff_wl_meters, output_units=self.length_unit
        )
        correction_factor = 0.58
        arm_length = round(
            correction_factor
            * math.sqrt(
                math.pow(eff_wl_working_units / 4.0, 2)
                - math.pow(eff_wl_working_units / 80.0 / 2.0, 2)
            ),
            2,
        )
        inner_width = round(correction_factor * eff_wl_working_units / 80.0, 2)
        outer_width = round(correction_factor * eff_wl_working_units / 80.0 * 24.0, 2)
        outer_radius = round(correction_factor * eff_wl_working_units / 80.0 * 24.0 / 2.0 * 1.1, 2)
        port_gap = round(correction_factor * eff_wl_working_units / 80.0, 2)
        sub_x = round(correction_factor * eff_wl_working_units, 0)
        sub_y = round(correction_factor * eff_wl_working_units, 0)
        parameters["inner_width"] = inner_width
        parameters["outer_width"] = outer_width
        parameters["outer_radius"] = outer_radius
        parameters["arm_length"] = arm_length
        parameters["port_gap"] = port_gap
        parameters["sub_x"] = sub_x
        parameters["sub_y"] = sub_y
        parameters["sub_h"] = self.substrate_height

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw a rectangular patch antenna with a coaxial probe.

        Once the antenna is created, this method is not used anymore.
        """
        if self.object_list:
            self._app.logger.warning("This antenna already exists.")
            return False

        self.set_variables_in_hfss()

        # Map parameters
        arm_length = self.synthesis_parameters.arm_length.hfss_variable
        port_gap = self.synthesis_parameters.port_gap.hfss_variable
        inner_width = self.synthesis_parameters.inner_width.hfss_variable
        outer_width = self.synthesis_parameters.outer_width.hfss_variable
        outer_radius = self.synthesis_parameters.outer_radius.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.antenna_name
        coordinate_system = self.coordinate_system

        # Substrate
        sub = self._app.modeler.create_box(
            position=["-" + sub_x + "/2", "-" + sub_y + "/2", 0.0],
            dimensions_list=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            matname=self.material,
        )
        sub.color = (0, 128, 0)
        sub.history.props["Coordinate System"] = coordinate_system
        array_points = [["{}/2".format(inner_width), "{}/2".format(port_gap), 0]]
        array_points.append(["-{}/2".format(inner_width), "{}/2".format(port_gap), 0])
        array_points.append(
            ["-{}/2".format(outer_width), "{}/2.0+{}".format(port_gap, arm_length), 0.0]
        )
        array_points.append(
            ["{}/2".format(outer_width), "{}/2.0+{}".format(port_gap, arm_length), 0.0]
        )
        array_points.append(["{}/2".format(inner_width), "{}/2".format(port_gap), 0])
        ant = self._app.modeler.create_polyline(array_points, cover_surface=True, name="ant_arm")
        y_val = "if({0}>={1}/2,{2}-{1}/2/tan(asin({1}/2/{0}))+{3}/2 ,{2})".format(
            outer_radius, outer_width, arm_length, port_gap
        )
        round = self._app.modeler.create_circle(self._app.PLANE.XY, [0.0, y_val, 0.0], outer_radius)
        round.move([0, "-{}-({}/2)".format(arm_length, port_gap), 0])
        round.split(self._app.PLANE.ZX, "PositiveOnly")
        round.move([0, "{}+({}/2)".format(arm_length, port_gap), 0])
        ant.unite(round)
        ant.color = (255, 128, 65)
        ant.transparency = 0.1
        ant.history.props["Coordinate System"] = coordinate_system
        ant2_name = ant.duplicate_around_axis(
            self._app.AXIS.Z,
            180,
            2,
        )[0]
        ant2 = self._app.modeler[ant2_name]

        p1 = self._app.modeler.create_rectangle(
            csPlane=self._app.PLANE.XY,
            position=["-{}/2".format(inner_width), "-{}/2".format(port_gap), 0.0],
            dimension_list=[inner_width, port_gap],
            name="port_lump_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = coordinate_system

        self._app.modeler.move([p1.name, ant2_name, ant.name], [0, 0, sub_h])

        if self.huygens_box:
            lightSpeed = constants.SpeedOfLight  # m/s
            freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
            huygens_dist = str(
                constants.unit_converter(
                    lightSpeed / (10 * freq_hz), "Length", "meter", self.length_unit
                )
            )
            huygens = self._app.modeler.create_box(
                position=[
                    "-{}/2-{}{}".format(sub_x, huygens_dist, self.length_unit),
                    "-{}/2-{}{}".format(sub_y, huygens_dist, self.length_unit),
                    "-{}{}".format(huygens_dist, self.length_unit),
                ],
                dimensions_list=[
                    "{}+2*{}{}".format(sub_x, huygens_dist, self.length_unit),
                    "{}+2*{}{}".format(sub_y, huygens_dist, self.length_unit),
                    "{}+2*{}{}".format(sub_h, huygens_dist, self.length_unit),
                ],
                name="huygens_" + antenna_name,
                matname="air",
            )
            huygens.display_wireframe = True
            huygens.color = (0, 0, 255)
            huygens.history.props["Coordinate System"] = coordinate_system
            huygens.group_name = antenna_name
            self.object_list[huygens.name] = huygens

        sub.group_name = antenna_name
        ant.group_name = antenna_name
        ant2.group_name = antenna_name
        p1.group_name = antenna_name

        self.object_list[sub.name] = sub
        self.object_list[ant.name] = ant
        self.object_list[ant2.name] = ant2
        self.object_list[p1.name] = p1
        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDiscovery. To be implemenented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the model in PyDiscovery. To be implemenented."""
        pass
