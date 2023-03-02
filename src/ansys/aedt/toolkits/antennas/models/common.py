import copy
import math
import os

import pyaedt.generic.constants as constants
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antennas.models.parameters import InputParameters
from ansys.aedt.toolkits.antennas.models.parameters import Property
from ansys.aedt.toolkits.antennas.models.parameters import SynthesisParameters


class CommonAntenna(object):
    """Base methods common to antennas toolkit."""

    antenna_type = ""

    def __init__(self, default_input_parameters, *args, **kwargs):
        self._app = args[0]
        self._input_parameters = InputParameters(default_input_parameters)

        for k, v in kwargs.items():
            if k in default_input_parameters:
                setattr(self._input_parameters, k, copy.deepcopy(v))
            else:
                raise AttributeError(
                    f"{k} is not a valid parameter for this antenna. \n"
                    f"Accepted parameters are {str(list(default_input_parameters.keys()))}"
                )

        if self._input_parameters.length_unit is None:
            self._input_parameters.length_unit = self._app.modeler.model_units

        self._input_parameters.antenna_name = self._check_antenna_name(
            self._input_parameters.antenna_name
        )

        self.synthesis_parameters = SynthesisParameters()
        self.synthesis_parameters.antenna_name = self._input_parameters.antenna_name

        self.object_list = {}
        self.boundaries = {}
        self.excitations = {}
        self.mesh_operations = {}

    @property
    def antenna_material(self):
        """Metal to be assigned to material Frequency.

        Returns
        -------
        float
        """
        return self._input_parameters.antenna_material

    @antenna_material.setter
    def antenna_material(self, value):
        self._input_parameters.antenna_material = value
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def frequency(self):
        """Center Frequency.

        Returns
        -------
        float
        """
        return self._input_parameters.frequency

    @frequency.setter
    def frequency(self, value):
        self._input_parameters.frequency = value
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def frequency_unit(self):
        """Frequency units.

        Returns
        -------
        str
        """
        return self._input_parameters.frequency_unit

    @frequency_unit.setter
    def frequency_unit(self, value):
        self._input_parameters.frequency_unit = value
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def outer_boundary(self):
        """Outer boundary.

        Returns
        -------
        str
        """
        return self._input_parameters.outer_boundary

    @outer_boundary.setter
    def outer_boundary(self, value):
        self._input_parameters.outer_boundary = value
        if self.object_list:
            self._app.create_open_region(
                str(self._input_parameters.frequency) + self._input_parameters.frequency_unit,
                self._input_parameters.outer_boundary,
            )

    @property
    def huygens_box(self):
        """Enable Huygens box.

        Returns
        -------
        bool
        """
        return self._input_parameters.huygens_box

    @huygens_box.setter
    def huygens_box(self, value):
        # No effect for now
        self._huygens_box = value

    @property
    def length_unit(self):
        """Length unit.

        Returns
        -------
        str
        """
        return self._input_parameters.length_unit

    @length_unit.setter
    def length_unit(self, value):
        self._length_unit = value
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def coordinate_system(self):
        """Reference Coordinate system.

        Returns
        -------
        str
        """
        return self._input_parameters.coordinate_system

    @coordinate_system.setter
    def coordinate_system(self, value):
        self._input_parameters.coordinate_system = value
        for antenna_obj in self.object_list:
            self.object_list[antenna_obj].history.props[
                "Coordinate System"
            ] = self._input_parameters.coordinate_system

    @property
    def antenna_name(self):
        """Antenna name.

        Returns
        -------
        str
        """
        return self._input_parameters.antenna_name

    @antenna_name.setter
    def antenna_name(self, value):
        if value != self.antenna_name and self.object_list:
            for antenna_obj in self.object_list:
                self.object_list[antenna_obj].group_name = value
            if len(list(self._app.modeler.oeditor.GetObjectsInGroup(self.antenna_name))) == 0:
                self._app.modeler.oeditor.Delete(
                    ["NAME:Selections", "Selections:=", self.antenna_name]
                )
            self._input_parameters.antenna_name = value

    @property
    def origin(self):
        """Antenna origin.

        Returns
        -------
        list
        """
        return self._input_parameters.origin

    @origin.setter
    def origin(self, value):
        self._input_parameters.origin = value
        if self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @pyaedt_function_handler()
    def create_3dcomponent(self, component_file=None, component_name=None, replace=False):
        """Create 3DComponent of the antenna.

        Parameters
        ----------
        component_file : str, optional
            Full path to the A3DCOMP file. The default is the pyaedt folder.
        component_name : str, optional
            Name of the component. The default is the antenna name.
        replace : bool, optional
            Whether to replace antenna with a 3DComponent. The default is ``False``.

        Returns
        -------
        str.
            Path of the 3DComponent file or 3DComponent name.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> from ansys.aedt.toolkits.antennas.horn import ConicalHorn
        >>> hfss = Hfss()
        >>> horn = hfss.add_from_toolkit(ConicalHorn, draw=True)
        >>> horn = horn.create_3dcomponent()
        """
        if not component_file:
            component_file = os.path.join(
                self._app.working_directory, self.antenna_name + ".a3dcomp"
            )
        if not component_name:
            component_name = self.antenna_name

        parameters = []
        for p in self.synthesis_parameters.__dict__.values():
            if isinstance(p, Property):
                parameters.append(p.hfss_variable)

        boundaries = list(self.boundaries.keys())
        if not boundaries:
            boundaries = [""]

        self._app.modeler.create_3dcomponent(
            component_file=component_file,
            component_name=component_name,
            variables_to_include=parameters,
            object_list=list(self.object_list.keys()),
            boundaries_list=boundaries,
            excitation_list=list(self.excitations.keys()),
            included_cs=[self.coordinate_system],
            reference_cs=self.coordinate_system,
            component_outline="None",
        )

        if replace:
            self._app.modeler.replace_3dcomponent(
                component_name=component_name,
                variables_to_include=parameters,
                object_list=list(self.object_list.keys()),
                boundaries_list=boundaries,
                excitation_list=list(self.excitations.keys()),
                included_cs=[self.coordinate_system],
                reference_cs=self.coordinate_system,
            )
            if self._app.modeler.oeditor.GetObjectsInGroup(self.antenna_name).count == 0:
                self._app.modeler.oeditor.Delete(
                    ["NAME:Selections", "Selections:=", self.antenna_name]
                )

            user_defined_component = self._app.modeler.add_new_user_defined_component()
            self._app.modeler.refresh_all_ids()
            return user_defined_component[0]
        return component_file

    @pyaedt_function_handler()
    def duplicate_along_line(self, vector, num_clones=2):
        """Duplicate the object along a line.

        Parameters
        ----------
        vector : list
            List of ``[x1 ,y1, z1]`` coordinates for the vector.
        num_clones : int, optional
            Number of clones. The default is ``2``.

        Returns
        -------
        dict
            Dictionary with the list of new objects.

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> from ansys.aedt.toolkits.antennas.horn import ConicalHorn
        >>> hfss = Hfss()
        >>> horn = hfss.add_from_toolkit(ConicalHorn, draw=True)
        >>> new_horn = horn.duplicate_along_line([10, 0, 0], 2)
        """
        new_objects = {}
        for i in range(0, num_clones - 1):
            new_objects["antenna" + str(i)] = []
        for component in self.object_list:
            _, output = self._app.modeler.duplicate_along_line(component, vector, num_clones)
            for i in range(0, num_clones - 1):
                new_objects["antenna" + str(i)].append(output[i])

        return new_objects

    @pyaedt_function_handler()
    def _update_parameters(self, parameters, length_unit):
        for param in parameters:
            self._app[param] = str(parameters[param]) + length_unit
        return True

    @pyaedt_function_handler()
    def _synthesis(self):
        pass

    @pyaedt_function_handler()
    def _check_antenna_name(self, antenna_name=None):
        """Check if antenna name is repeated or assign a random antenna name."""
        if (
            not antenna_name
            or len(list(self._app.modeler.oeditor.GetObjectsInGroup(antenna_name))) > 0
            or any(
                antenna_name in variables
                for variables in list(self._app.variable_manager.variables.keys())
            )
        ):
            antenna_name = generate_unique_name(self.antenna_type)
            while len(list(self._app.modeler.oeditor.GetObjectsInGroup(antenna_name))) > 0:
                antenna_name = generate_unique_name(self.antenna_type)
        return antenna_name

    @pyaedt_function_handler()
    def update_synthesis_parameters(self, new_params):
        """Update syntesys variable from antenna list."""
        for k, v in new_params.items():
            if hasattr(self.synthesis_parameters, k):
                param = getattr(self.synthesis_parameters, k)
                param.value = float(round(v, 3))
            else:
                self.synthesis_parameters.add_parameter(k, v)

    @pyaedt_function_handler()
    def set_variables_in_hfss(self):
        """Create Hfss design variables."""
        for p in self.synthesis_parameters.__dict__.values():
            if isinstance(p, Property):
                self._app[p.hfss_variable] = str(p.value) + self.length_unit

    @pyaedt_function_handler()
    def init_model(self):
        """Create radiation boundary."""
        if self._input_parameters.outer_boundary:
            self._app.create_open_region(
                str(self.frequency) + self.frequency_unit, self.outer_boundary
            )

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Antenna HFSS setup."""
        terminal_references = []
        port_lump = port = port_cap = None
        if "port_lump_{}".format(self.antenna_name) in self.object_list:
            port_lump = self.object_list["port_lump_{}".format(self.antenna_name)]
            terminal_references = [
                i
                for i in port_lump.touching_objects
                if self._app.modeler[i]
                and (
                    self._app.modeler[i].object_type == "Sheet"
                    or self._app.materials[self._app.modeler[i].material_name].is_conductor()
                )
            ]
            if len(terminal_references) > 1:
                axis_dir = [[], []]
                for edge in port_lump.edges:
                    if terminal_references[1] in self._app.modeler.get_bodynames_from_position(
                        edge.midpoint
                    ):
                        axis_dir[1] = edge.midpoint
                    elif terminal_references[0] in self._app.modeler.get_bodynames_from_position(
                        edge.midpoint
                    ):
                        axis_dir[0] = edge.midpoint
                terminal_references = terminal_references[1:]

        elif "port_{}".format(self.antenna_name) in self.object_list:
            port = self.object_list["port_{}".format(self.antenna_name)]
            if "port_cap_{}".format(self.antenna_name) in self.object_list:
                port_cap = self.object_list["port_cap_{}".format(self.antenna_name)]
        if port_lump:
            port1 = self._app.create_lumped_port_to_sheet(
                "port_lump_{}".format(self.antenna_name),
                axisdir=axis_dir,
                impedance=50,
                portname="port_" + self.antenna_name,
                renorm=True,
                deemb=False,
                reference_object_list=terminal_references,
            )
            self.excitations[port1.name] = port1
        elif port:
            if self._app.solution_type == "Terminal" and port_cap:
                terminal_references = port_cap.name
            port1 = self._app.create_wave_port_from_sheet(
                sheet=port,
                portname="port_" + self.antenna_name,
                terminal_references=terminal_references,
            )
            self.excitations[port1.name] = port1
        for obj_name in self.object_list.keys():
            if (
                obj_name.startswith("PerfE")
                or obj_name.startswith("gnd_")
                or obj_name.startswith("ant_")
            ):
                self._app.assign_perfecte_to_sheets(obj_name)
            elif obj_name.startswith("coax"):
                obj = self.object_list[obj_name]
                face_id = obj.faces[0].edges[0].id
                for face in obj.faces:
                    if len(face.edges) == 2:
                        face_id = face.id
                        break
                coax_bound = self._app.assign_perfecte_to_sheets(face_id)
                coax_bound.name = "PerfE_" + obj_name
                self.boundaries[coax_bound.name] = coax_bound
                break
            elif obj_name.startswith("huygens_"):
                if self.huygens_box:
                    lightSpeed = constants.SpeedOfLight  # m/s
                    freq_hz = constants.unit_converter(
                        self.frequency, "Freq", self.frequency_unit, "Hz"
                    )
                    huygens_dist = str(
                        constants.unit_converter(
                            lightSpeed / (10 * freq_hz), "Length", "meter", self.length_unit
                        )
                    )
                    mesh_op = self._app.mesh.assign_length_mesh(
                        [obj_name],
                        maxlength=huygens_dist + self.length_unit,
                        maxel=None,
                        meshop_name="HuygensBox_Seed_" + self.antenna_name,
                    )
                    self.mesh_operations[mesh_op.name] = mesh_op

        return True


class TransmissionLine(object):
    """Base methods common to transmission line calculation.

    Parameters
    ----------
    frequency : float, optional
            Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
            Frequency units. The default is ``GHz``.

    Returns
    -------
    :class:`aedt.toolkits.antennas.common.TransmissionLine`
            Transmission line calculator object.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antennas.common import TransmissionLine
    >>> tl_calc = TransmissionLine(frequency=2)
    >>> tl_calc.stripline_calculator(substrate_height=10, permittivity=2.2, impedance=60)
    """

    antenna_type = ""

    def __init__(self, frequency=10, frequency_unit="GHz"):
        self.frequency = frequency
        self.frequency_unit = frequency_unit

    @pyaedt_function_handler()
    def microstrip_calculator(
        self, substrate_height, permittivity, impedance=50.0, electrical_length=150.0
    ):
        """Strip line calculator.

        Parameters
        ----------
        substrate_height : float
                Substrate height.
        permittivity : float
                Substrate permittivity.
        impedance : str, optional
                Impedance. The default is ``50.0``.
        electrical_length : str, optional
                Electrical length in degrees. The default is ``150.0``.

        Returns
        -------
        tuple
            Line width and length.
        """

        z0 = impedance
        e0 = permittivity
        h0 = substrate_height

        A_us = z0 / 60.0 * math.sqrt((e0 + 1.0) / 2.0) + (e0 - 1.0) / (e0 + 1.0) * (
            0.23 + 0.11 / e0
        )
        B_us = 377.0 * math.pi / (2.0 * z0 * math.sqrt(e0))

        w_over_subH_1 = 8.0 * math.exp(A_us) / (math.exp(2.0 * A_us) - 2.0)
        w_over_subH_2 = (
            2.0
            / math.pi
            * (
                B_us
                - 1.0
                - math.log(2.0 * B_us - 1.0)
                + (e0 - 1.0) / (2.0 * e0) * (math.log(B_us - 1.0) + 0.39 - 0.61 / e0)
            )
        )

        ustrip_width = w_over_subH_1 * h0
        if w_over_subH_1 < 2.0:
            ustrip_width = w_over_subH_1 * h0

        if w_over_subH_2 >= 2:
            ustrip_width = w_over_subH_2 * h0

        er_eff = (e0 + 1.0) / 2.0 + (e0 - 1.0) / 2.0 * 1.0 / (
            math.sqrt(1.0 + 12.0 * h0 / ustrip_width)
        )
        f = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")

        k0 = 2.0 * math.pi * f / 3.0e8

        ustrip_length = math.radians(electrical_length) / (math.sqrt(er_eff) * k0)

        return ustrip_width, ustrip_length

    @pyaedt_function_handler()
    def stripline_calculator(self, substrate_height, permittivity, impedance=50.0):
        """Strip line calculator.

        Parameters
        ----------
        substrate_height : float
                Substrate height.
        permittivity : float
                Substrate permittivity.
        impedance : str, optional
                Impedance. The default is ``50.0``.

        Returns
        -------
        float
            Line width.
        """

        x = 30.0 * math.pi / (math.sqrt(permittivity) * impedance) - 0.441

        if math.sqrt(permittivity) * impedance <= 120:
            w_over_h = x
        else:
            w_over_h = 0.85 - math.sqrt(0.6 - x)

        width = w_over_h * substrate_height
        return width

    @pyaedt_function_handler()
    def suspended_strip_calculator(self, wavelength, w1, substrate_height, permittivity):
        """Suspended stripline calculator.

        Parameters
        ----------
        wavelength : float
        w1 : float
        substrate_height : float
            Substrate in meter.
        permittivity : float
            Dielectric permittivity

        Returns
        -------
        float
            Effective Permittivity.
        """
        Hfrac = 16.0  # H_as_fraction_of_wavelength 1/H
        H = (wavelength / math.sqrt(permittivity) + substrate_height * Hfrac) / Hfrac
        heigth_ratio = substrate_height / (H - substrate_height)
        a = math.pow(0.8621 - 0.125 * math.log(heigth_ratio), 4.0)
        b = math.pow(0.4986 - 0.1397 * math.log(heigth_ratio), 4.0)

        Width_to_height_ratio = w1 / (H - substrate_height)
        sqrt_er_eff = math.pow(
            1.0
            + heigth_ratio
            * (a - b * math.log(Width_to_height_ratio))
            * (1.0 / math.sqrt(permittivity) - 1.0),
            -1.0,
        )
        eff_perm = math.pow(sqrt_er_eff, 2.0)

        if (permittivity >= 6.0) and (permittivity <= 10.0):
            eff_perm = eff_perm * 1.15  # about 15% larger than calculated
        if permittivity > 10:
            eff_perm = eff_perm * 1.25  # about 25% lager then calculated

        if eff_perm >= (permittivity + 1.0) / 2.0:
            eff_perm = (permittivity + 1.0) / 2.0

        return eff_perm