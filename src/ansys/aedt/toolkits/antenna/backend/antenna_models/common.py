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

import copy
import math
import os

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antenna.backend.antenna_models.parameters import InputParameters
from ansys.aedt.toolkits.antenna.backend.antenna_models.parameters import Property
from ansys.aedt.toolkits.antenna.backend.antenna_models.parameters import SynthesisParameters
from ansys.aedt.toolkits.antenna.backend.models import properties


class CommonAntenna(object):
    """Provides base methods common to the antenna toolkit."""

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
            self._input_parameters.length_unit = properties.antenna.synthesis.length_unit

        if self._app:
            self._input_parameters.name = self._check_antenna_name(self._input_parameters.name)

        self.synthesis_parameters = SynthesisParameters()
        self.synthesis_parameters.name = self._input_parameters.name

        self.object_list = {}
        self.boundaries = {}
        self.excitations = {}
        self.mesh_operations = {}

    @property
    def material(self):
        """Material assigned.

        Returns
        -------
        str
        """
        return self._input_parameters.material

    @material.setter
    def material(self, value):
        self._input_parameters.material = value
        if self.object_list:
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def frequency(self):
        """Center frequency.

        Returns
        -------
        float
        """
        return self._input_parameters.frequency

    @frequency.setter
    def frequency(self, value):
        self._input_parameters.frequency = value
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
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
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
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
                str(self.frequency) + self.frequency_unit,
                value,
            )

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
        self._input_parameters.length_unit = value
        parameters = self.synthesis()
        self.update_synthesis_parameters(parameters)
        if self.object_list:
            self.set_variables_in_hfss()

    @property
    def coordinate_system(self):
        """Reference coordinate system.

        Returns
        -------
        str
        """
        return self._input_parameters.coordinate_system

    @coordinate_system.setter
    def coordinate_system(self, value):
        self._input_parameters.coordinate_system = value
        for antenna_obj in self.object_list:
            self.object_list[antenna_obj].history().properties[
                "Coordinate System"
            ] = self._input_parameters.coordinate_system

    @property
    def name(self):
        """Antenna name.

        Returns
        -------
        str
        """
        return self._input_parameters.name

    @name.setter
    def name(self, value):
        if value != self.name and self.object_list:
            for antenna_obj in self.object_list:
                self.object_list[antenna_obj].group_name = value
            if len(list(self._app.modeler.oeditor.GetObjectsInGroup(self.name))) == 0:
                self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.name])
        self._input_parameters.name = value

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
            parameters = self.synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @pyaedt_function_handler()
    def create_lattice_pair(self, lattice_height=None, bottom_extend=False):
        """Create a lattice pair box.

        Parameters
        ----------
        lattice_height : str, optional
            Height of the lattice pair box.
        bottom_extend : bool, optional
            Whether to extend the lattice pair in the bottom side. The default is ``False``.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.object3d.Object3d`
            3D object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical
        >>> hfss = Hfss()
        >>> horn = hfss.add_from_toolkit(Conical, draw=True)
        >>> horn = horn.create_lattice_pair(lattice_height="20mm")
        """
        if not lattice_height:
            lightSpeed = constants.SpeedOfLight  # m/s
            freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
            wavelength = lightSpeed / freq_hz
            lattice_height = str(wavelength / 10.0) + "meter"

        self.synthesis_parameters.add_parameter("lattice_height", lattice_height)

        hfss_parameter = self.synthesis_parameters.lattice_height.hfss_variable
        self._app[hfss_parameter] = self.synthesis_parameters.lattice_height.value

        bounding_box = self._app.modeler.get_group_bounding_box(self.name)
        bounding_dim = [
            abs(bounding_box[0] - bounding_box[3]),
            abs(bounding_box[1] - bounding_box[4]),
            abs(bounding_box[2] - bounding_box[5]),
        ]

        if bottom_extend:
            lattice_box = self._app.modeler.create_box(
                origin=[
                    str(bounding_box[0]) + self._app.modeler.model_units,
                    str(bounding_box[1]) + self._app.modeler.model_units,
                    str(bounding_box[2]) + self._app.modeler.model_units + "-" + hfss_parameter,
                ],
                sizes=[
                    str(bounding_dim[0]) + self._app.modeler.model_units,
                    str(bounding_dim[1]) + self._app.modeler.model_units,
                    str(bounding_dim[2]) + self._app.modeler.model_units + "+2*" + hfss_parameter,
                ],
                material="vacuum",
            )
        else:
            lattice_box = self._app.modeler.create_box(
                origin=[
                    str(bounding_box[0]) + self._app.modeler.model_units,
                    str(bounding_box[1]) + self._app.modeler.model_units,
                    str(bounding_box[2]) + self._app.modeler.model_units,
                ],
                sizes=[
                    str(bounding_dim[0]) + self._app.modeler.model_units,
                    str(bounding_dim[1]) + self._app.modeler.model_units,
                    str(bounding_dim[2]) + self._app.modeler.model_units + "+" + hfss_parameter,
                ],
                material="vacuum",
            )

        lattice1 = self._app.assign_lattice_pair(face_couple=[lattice_box.bottom_face_x.id, lattice_box.top_face_x.id])
        self.boundaries[lattice1.name] = lattice1
        lattice2 = self._app.assign_lattice_pair(face_couple=[lattice_box.bottom_face_y.id, lattice_box.top_face_y.id])
        self.boundaries[lattice2.name] = lattice2

        self.object_list[lattice_box.name] = lattice_box

        return lattice_box

    @pyaedt_function_handler()
    def create_3dcomponent(self, component_file=None, component_name=None, replace=False):
        """Create a 3D component of the antenna.

        Parameters
        ----------
        component_file : str, optional
            Full path to the A3DCOMP file. The default is the ``ansys.aedt.core`` folder.
        component_name : str, optional
            Name of the component. The default is the antenna name.
        replace : bool, optional
            Whether to eplace the antenna with a 3D component. The default is ``False``.

        Returns
        -------
        str
            Path of the 3D component file or
            :class:`ansys.aedt.core.modeler.components_3d.UserDefinedComponent`.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical
        >>> hfss = Hfss()
        >>> horn = hfss.add_from_toolkit(Conical, draw=True)
        >>> horn = horn.create_3dcomponent()
        """
        if not component_file:
            component_file = os.path.join(self._app.working_directory, self.name + ".a3dcomp")
        if not component_name:
            component_name = self.name

        parameters = []
        for p in self.synthesis_parameters.__dict__.values():
            if isinstance(p, Property):
                parameters.append(p.hfss_variable)

        boundaries = list(self.boundaries.keys())
        if not boundaries:
            boundaries = [""]

        self._app.modeler.create_3dcomponent(
            input_file=component_file,
            name=component_name,
            variables_to_include=parameters,
            assignment=list(self.object_list.keys()),
            boundaries=boundaries,
            excitations=list(self.excitations.keys()),
            coordinate_systems=[self.coordinate_system],
            reference_coordinate_system=self.coordinate_system,
            component_outline="None",
        )

        if replace:
            user_defined_component = self._app.modeler.replace_3dcomponent(
                name=component_name,
                variables_to_include=parameters,
                assignment=list(self.object_list.keys()),
                boundaries=boundaries,
                excitations=list(self.excitations.keys()),
                coordinate_systems=[self.coordinate_system],
                reference_coordinate_system=self.coordinate_system,
            )
            if self._app.modeler.oeditor.GetObjectsInGroup(self.name).count == 0:
                self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.name])
            return user_defined_component
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
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical
        >>> hfss = Hfss()
        >>> horn = hfss.add_from_toolkit(Conical, draw=True)
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
    def synthesis(self):
        pass

    @pyaedt_function_handler()
    def _check_antenna_name(self, antenna_name=None):
        """Check if antenna name is repeated or assign a random antenna name."""
        if (
            not antenna_name
            or len(list(self._app.modeler.oeditor.GetObjectsInGroup(antenna_name))) > 0
            or any(antenna_name in variables for variables in list(self._app.variable_manager.variables.keys()))
        ):
            antenna_name = generate_unique_name(self.antenna_type)
            if self._app:
                while len(list(self._app.modeler.oeditor.GetObjectsInGroup(antenna_name))) > 0:
                    antenna_name = generate_unique_name(self.antenna_type)
        return antenna_name

    @pyaedt_function_handler()
    def update_synthesis_parameters(self, new_params):
        """Update the synthesis parameter from the antenna list."""
        for k, v in new_params.items():
            if hasattr(self.synthesis_parameters, k):
                param = getattr(self.synthesis_parameters, k)
                param.value = float(round(v, 6))
            else:
                self.synthesis_parameters.add_parameter(k, v)

    @pyaedt_function_handler()
    def set_variables_in_hfss(self, not_used=None):
        """Create HFSS design variables."""
        if not not_used:
            not_used = []
        for p in self.synthesis_parameters.__dict__.values():
            if isinstance(p, Property) and p.hfss_variable not in not_used:
                properties.antenna.parameters_hfss[p.name] = p.hfss_variable
                if "angle" in p.hfss_variable:
                    self._app[p.hfss_variable] = str(p.value) + "deg"
                elif "ratio" in p.hfss_variable:
                    self._app[p.hfss_variable] = str(p.value)
                else:
                    self._app[p.hfss_variable] = str(p.value) + self.length_unit

    @pyaedt_function_handler()
    def init_model(self):
        """Create a radiation boundary."""
        if self._input_parameters.outer_boundary:
            self._app.create_open_region(str(self.frequency) + self.frequency_unit, self.outer_boundary)

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Set up an antenna in HFSS."""

        for obj_name in self.object_list.keys():
            if obj_name.startswith("PerfE") or obj_name.startswith("gnd_") or obj_name.startswith("ant_"):
                bound = self._app.assign_perfecte_to_sheets(obj_name)
                bound.name = "PerfE_" + obj_name
                self.boundaries[bound.name] = bound
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

        port_count = 1
        for item in list(self.object_list.keys()):
            terminal_references = []
            port_lump = port = port_cap = None
            if "port_lump_{}".format(self.name) in item:
                port_lump = self.object_list[item]
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
                        if terminal_references[1] in self._app.modeler.get_bodynames_from_position(edge.midpoint):
                            axis_dir[1] = edge.midpoint
                        elif terminal_references[0] in self._app.modeler.get_bodynames_from_position(edge.midpoint):
                            axis_dir[0] = edge.midpoint
                    terminal_references = terminal_references[1:]

            elif "port_{}".format(self.name) in item:
                port = self.object_list[item]
                for item_cap in list(self.object_list.keys()):
                    if "port_cap_{}".format(self.name) in item_cap:
                        port_cap = self.object_list[item_cap]

            if port_lump:
                port1 = self._app.lumped_port(
                    assignment=item,
                    reference=terminal_references,
                    impedance=50,
                    name="port_" + self.name + "_" + str(port_count),
                    renormalize=True,
                    deembed=False,
                )

                self.excitations[port1.name] = port1
                port_count += 1
            elif port:
                if self._app.solution_type == "Terminal" and port_cap:
                    terminal_references = port_cap.name
                port1 = self._app.wave_port(
                    assignment=port,
                    reference=terminal_references,
                    name="port_" + self.name + "_" + str(port_count),
                )
                self.excitations[port1.name] = port1
                port_count += 1

        return True


class TransmissionLine(object):
    """Provides base methods common to transmission line calculations.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.common.TransmissionLine`
        Transmission line calculator object.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.common import TransmissionLine
    >>> tl_calc = TransmissionLine(frequency=2)
    >>> tl_calc.stripline_calculator(substrate_height=10, permittivity=2.2, impedance=60)
    """

    def __init__(self, frequency=10, frequency_unit="GHz"):
        self.frequency = frequency
        self.frequency_unit = frequency_unit

    @pyaedt_function_handler()
    def microstrip_calculator(self, substrate_height, permittivity, impedance=50.0, electrical_length=150.0):
        """Use the micro strip line calculator to calculate line width and length.

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

        A_us = z0 / 60.0 * math.sqrt((e0 + 1.0) / 2.0) + (e0 - 1.0) / (e0 + 1.0) * (0.23 + 0.11 / e0)
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

        er_eff = (e0 + 1.0) / 2.0 + (e0 - 1.0) / 2.0 * 1.0 / (math.sqrt(1.0 + 12.0 * h0 / ustrip_width))
        f = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")

        k0 = 2.0 * math.pi * f / 3.0e8

        ustrip_length = math.radians(electrical_length) / (math.sqrt(er_eff) * k0)

        return ustrip_width, ustrip_length

    @pyaedt_function_handler()
    def stripline_calculator(self, substrate_height, permittivity, impedance=50.0):
        """Use the strip line calculator to calculate line width.

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
        """Use the suspended strip line calculator to calculate effective permittivity.

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
            Effective permittivity.
        """
        Hfrac = 16.0  # H_as_fraction_of_wavelength 1/H
        H = (wavelength / math.sqrt(permittivity) + substrate_height * Hfrac) / Hfrac
        heigth_ratio = substrate_height / (H - substrate_height)
        a = math.pow(0.8621 - 0.125 * math.log(heigth_ratio), 4.0)
        b = math.pow(0.4986 - 0.1397 * math.log(heigth_ratio), 4.0)

        Width_to_height_ratio = w1 / (H - substrate_height)
        sqrt_er_eff = math.pow(
            1.0 + heigth_ratio * (a - b * math.log(Width_to_height_ratio)) * (1.0 / math.sqrt(permittivity) - 1.0),
            -1.0,
        )
        effective_permittivity = math.pow(sqrt_er_eff, 2.0)

        if (permittivity >= 6.0) and (permittivity <= 10.0):
            effective_permittivity = effective_permittivity * 1.15  # about 15% larger than calculated
        if permittivity > 10:
            effective_permittivity = effective_permittivity * 1.25  # about 25% lager then calculated

        if effective_permittivity >= (permittivity + 1.0) / 2.0:
            effective_permittivity = (permittivity + 1.0) / 2.0

        return effective_permittivity


class StandardWaveguide(object):
    """Provides base methods common to standard waveguides.

    Parameters
    ----------
    frequency : float, optional
        Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
        Frequency units. The default is ``"GHz"``.

    Returns
    -------
    :class:`aedt.toolkits.antenna.common.StandardWaveguide`
        Standard waveguide object.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.common import StandardWaveguide
    >>> wg_calc = StandardWaveguide()
    >>> wg_dim = wg_calc.get_waveguide_dimensions("WR-75")
    """

    wg = {}
    wg["WR-2300"] = [23.0, 11.5, 0.15]
    wg["WR-2100"] = [21.0, 10.5, 0.125]
    wg["WR-1800"] = [18.0, 9.0, 0.125]
    wg["WR-1500"] = [15.0, 7.5, 0.125]
    wg["WR-1150"] = [11.5, 5.75, 0.125]
    wg["WR-975"] = [9.75, 4.875, 0.125]
    wg["WR-770"] = [7.7, 3.850, 0.125]
    wg["WR-650"] = [6.5, 3.25, 0.08]
    wg["WR-510"] = [5.1, 2.55, 0.08]
    wg["WR-430"] = [4.3, 2.15, 0.08]
    wg["WR-340"] = [3.4, 1.7, 0.08]
    wg["WR-284"] = [2.84, 1.34, 0.08]
    wg["WR-229"] = [2.29, 1.145, 0.064]
    wg["WR-187"] = [1.872, 0.872, 0.064]
    wg["WR-159"] = [1.53, 0.795, 0.064]
    wg["WR-137"] = [1.372, 0.622, 0.064]
    wg["WR-112"] = [1.122, 0.497, 0.064]
    wg["WR-102"] = [1.02, 0.51, 0.064]
    wg["WR-90"] = [0.9, 0.4, 0.05]
    wg["WR-75"] = [0.75, 0.375, 0.05]
    wg["WR-62"] = [0.622, 0.311, 0.04]
    wg["WR-51"] = [0.51, 0.255, 0.04]
    wg["WR-42"] = [0.42, 0.17, 0.04]
    wg["WR-34"] = [0.34, 0.17, 0.04]
    wg["WR-28"] = [0.28, 0.14, 0.04]
    wg["WR-22"] = [0.224, 0.112, 0.04]
    wg["WR-19"] = [0.188, 0.094, 0.04]
    wg["WR-15"] = [0.148, 0.074, 0.04]
    wg["WR-12"] = [0.122, 0.061, 0.04]
    wg["WR-10"] = [0.1, 0.05, 0.04]
    wg["WR-8"] = [0.08, 0.04, 0.02]
    wg["WR-7"] = [0.065, 0.0325, 0.02]
    wg["WR-5"] = [0.0510, 0.0255, 0.02]

    def __init__(self, frequency=10, frequency_unit="GHz"):
        self.frequency = frequency
        self.frequency_unit = frequency_unit

    @property
    def waveguide_list(self):
        """Standard waveguide list."""
        return self.wg.keys()

    @pyaedt_function_handler()
    def get_waveguide_dimensions(self, name, units="mm"):
        """Get waveguide dimensions.

        Parameters
        ----------
        name : str
            Waveguide name.
        units : str
           Dimension units. The default is ``mm``.

        Returns
        -------
        list
            Waveguide dimensions.
        """

        if name in self.wg:
            wg_dim = []
            for dbl in self.wg[name]:
                wg_dim.append(constants.unit_converter(dbl, "Length", "in", units))
            return wg_dim
        else:
            return False

    @pyaedt_function_handler()
    def find_waveguide(self, freq, units="GHz"):  # pragma: no cover
        """Find the closest standard waveguide for the operational frequency.

        Parameters
        ----------
        freq : float
            Operational frequency.
        units : str
           Input frequency units. The default is ``"GHz"``.

        Returns
        -------
        str
            Waveguide name.
        """

        freq = constants.unit_converter(freq, "Frequency", units, "GHz")
        op_freq = freq * 0.8

        if op_freq >= 140:
            wg_name = "WR-5"
        elif op_freq >= 110:
            wg_name = "WR-7"
        elif op_freq >= 90:
            wg_name = "WR-8"
        elif op_freq >= 75:
            wg_name = "WR-10"
        elif op_freq >= 60:
            wg_name = "WR-12"
        elif op_freq >= 50:
            wg_name = "WR-15"
        elif op_freq >= 40:
            wg_name = "WR-19"
        elif op_freq >= 33:
            wg_name = "WR-22"
        elif op_freq >= 26.50:
            wg_name = "WR-28"
        elif op_freq >= 22:
            wg_name = "WR-34"
        elif op_freq >= 18:
            wg_name = "WR-42"
        elif op_freq >= 15:
            wg_name = "WR-51"
        elif op_freq >= 12.4:
            wg_name = "WR-62"
        elif op_freq >= 10:
            wg_name = "WR-75"
        elif op_freq >= 8.2:
            wg_name = "WR-90"
        elif op_freq >= 6.95:
            wg_name = "WR-102"
        elif op_freq >= 7.05:
            wg_name = "WR-112"
        elif op_freq >= 5.85:
            wg_name = "WR-137"
        elif op_freq >= 4.9:
            wg_name = "WR-159"
        elif op_freq >= 3.95:
            wg_name = "WR-187"
        elif op_freq >= 3.3:
            wg_name = "WR-229"
        elif op_freq >= 2.6:
            wg_name = "WR-284"
        elif op_freq >= 2.2:
            wg_name = "WR-340"
        elif op_freq >= 1.70:
            wg_name = "WR-430"
        elif op_freq >= 1.45:
            wg_name = "WR-510"
        elif op_freq >= 1.12:
            wg_name = "WR-650"
        elif op_freq >= 0.96:
            wg_name = "WR-770"
        elif op_freq >= 0.75:
            wg_name = "WR-975"
        elif op_freq >= 0.64:
            wg_name = "WR-1150"
        elif op_freq >= 0.49:
            wg_name = "WR-1500"
        elif op_freq >= 0.41:
            wg_name = "WR-1800"
        elif op_freq >= 0.35:
            wg_name = "WR-2100"
        elif op_freq > 0:
            wg_name = "WR-2300"
        else:
            wg_name = None
        return wg_name
