from collections import OrderedDict

import pyaedt.generic.constants as constants
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antennas.common import CommonAntenna


class CommonHorn(CommonAntenna):
    """Base methods common to Horn antennas."""

    def __init__(self, *args, **kwargs):
        CommonAntenna.__init__(self, *args, **kwargs)
        self._old_material = None
        self.material = kwargs["material"]
        self.object_list = {}
        self.parameters = []

    @property
    def material(self):
        """Substrate material.

        Returns
        -------
        str
        """
        return self._material

    @material.setter
    def material(self, value):
        if (
            value
            and value not in self._app._materials.mat_names_aedt
            and value not in self._app._materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create new material before assign")
        else:
            self._material = value
            old_material = None
            if value != self._old_material:
                old_material = self._old_material
                self._old_material = self._material

            if old_material and self.object_list:
                parameters = self._synthesis()
                parameters_map = {}
                cont = 0
                for param in parameters:
                    parameters_map[self.parameters[cont]] = parameters[param]
                    cont += 1
                self._update_parameters(parameters_map, self.length_unit)
                for antenna_obj in self.object_list:
                    if self.object_list[antenna_obj].material_name == old_material.lower():
                        self.object_list[antenna_obj].material_name = value

    @pyaedt_function_handler()
    def _synthesis(self):
        pass


class ConicalHorn(CommonHorn):
    """Manages conical horn antenna.

    This class is accessible through the app hfss object.

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
    :class:`aedt.toolkits.antennas.ConicalHorn`
            Conical horn object.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> from ansys.aedt.toolkits.antennas.horn import ConicalHorn
    >>> hfss = Hfss()
    >>> horn = hfss.add_from_toolkit(ConicalHorn, frequency=20.0, frequency_unit="GHz",
    ...                              outer_boundary=None, huygens_box=True, substrate_height=0.16,
    ...                              length_unit="cm", coordinate_system="CS1",
    ...                              antenna_name="PatchAntenna", origin=[1, 100, 50])
    """

    def __init__(self, *args, **kwargs):
        if "frequency" not in kwargs.keys():
            kwargs["frequency"] = 10.0
        if "frequency_unit" not in kwargs.keys():
            kwargs["frequency_unit"] = "GHz"
        if "material" not in kwargs.keys():
            kwargs["material"] = "pec"
        if "outer_boundary" not in kwargs.keys():
            kwargs["outer_boundary"] = None
        if "huygens_box" not in kwargs.keys():
            kwargs["huygens_box"] = False
        if "coordinate_system" not in kwargs.keys():
            kwargs["coordinate_system"] = "Global"
        if "antenna_name" not in kwargs.keys():
            kwargs["antenna_name"] = None
        if "origin" not in kwargs.keys():
            kwargs["origin"] = [0, 0, 0]

        CommonHorn.__init__(self, *args, **kwargs)

        self.antenna_name = self._check_antenna_name(self.antenna_name)
        self._parameters = self._synthesis()
        self.parameters = []

    @pyaedt_function_handler()
    def draw(self):
        """Draw conical horn antenna. Once the antenna is created, this method will not be used."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists")
            return False

        for param in self._parameters:
            new_name = param + "_" + self.antenna_name
            if new_name not in self._app.variable_manager.variables:
                self._app[new_name] = str(self._parameters[param]) + self.length_unit
                self.parameters.append(new_name)

        self.parameters = sorted(self.parameters)

        # Map parameter list to understand code
        horn_length = self.parameters[0]
        horn_radius = self.parameters[1]
        pos_x = self.parameters[2]
        pos_y = self.parameters[3]
        pos_z = self.parameters[4]
        wall_thickness = self.parameters[5]
        wg_length = self.parameters[6]
        wg_radius = self.parameters[7]

        # Negative air
        neg_air = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius,
            height="-" + wg_length,
            matname="vacuum",
        )
        neg_air.history.props["Coordinate System"] = self.coordinate_system

        # Wall
        wall = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wg_length,
            name="wg_outer_" + self.antenna_name,
            matname=self.material,
        )
        wall.history.props["Coordinate System"] = self.coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(
            tool_list=[neg_air.name], blank_list=[wall.name], keep_originals=False
        )

        # Input
        wg_in = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius,
            height="-" + wg_length,
            name="wg_inner_" + self.antenna_name,
            matname="vacuum",
        )
        wg_in.history.props["Coordinate System"] = self.coordinate_system

        # Cap
        cap = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z + "-" + wg_length],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + self.antenna_name,
            matname="pec",
        )
        cap.history.props["Coordinate System"] = self.coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "-" + wg_length],
            radius=wg_radius,
            name="port_" + self.antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = self.coordinate_system

        # Horn wall
        base = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius,
        )
        base.history.props["Coordinate System"] = self.coordinate_system

        base_wall = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius + "+" + wall_thickness,
        )
        base_wall.history.props["Coordinate System"] = self.coordinate_system

        horn_top = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "+" + horn_length],
            radius=horn_radius,
        )
        horn_top.history.props["Coordinate System"] = self.coordinate_system

        horn_sheet = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "+" + horn_length],
            radius=horn_radius + "+" + wall_thickness,
        )
        horn_sheet.history.props["Coordinate System"] = self.coordinate_system

        self._app.modeler.connect([horn_sheet.name, base_wall.name])
        self._app.modeler.connect([base.name, horn_top.name])

        # Horn
        self._app.modeler.subtract(
            blank_list=[horn_sheet.name], tool_list=[base.name], keep_originals=False
        )
        self._app.modeler.unite([horn_sheet.name, wall.name])

        air_base = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius,
        )
        air_base.history.props["Coordinate System"] = self.coordinate_system

        air_top = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "+" + horn_length],
            radius=horn_radius,
        )
        air_top.history.props["Coordinate System"] = self.coordinate_system

        self._app.modeler.connect([air_base, air_top])

        self._app.modeler.unite([wg_in, air_base])

        wg_in.name = "internal_" + self.antenna_name
        wg_in.color = (128, 255, 255)

        horn_sheet.name = "metal_" + self.antenna_name
        horn_sheet.material_name = self.material
        horn_sheet.color = (255, 128, 65)

        cap.color = (132, 132, 192)
        p1.color = (128, 0, 0)

        # Create Huygens box
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
                    pos_x + "-" + horn_radius + "-" + huygens_dist + self.length_unit,
                    pos_y + "-" + horn_radius + "-" + huygens_dist + self.length_unit,
                    pos_z + "-" + wg_length,
                ],
                dimensions_list=[
                    "2*" + horn_radius + "+" + "2*" + huygens_dist + self.length_unit,
                    "2*" + horn_radius + "+" + "2*" + huygens_dist + self.length_unit,
                    huygens_dist + self.length_unit + "+" + wg_length + "+" + horn_length,
                ],
                name="huygens_" + self.antenna_name,
                matname="air",
            )
            huygens.display_wireframe = True
            huygens.color = (0, 0, 255)
            huygens.history.props["Coordinate System"] = self.coordinate_system

            mesh_op = self._app.mesh.assign_length_mesh(
                [huygens.name],
                maxlength=huygens_dist + self.length_unit,
                maxel=None,
                meshop_name="HuygensBox_Seed_" + self.antenna_name,
            )

            self.object_list[huygens.name] = huygens
            huygens.group_name = self.antenna_name
            self.mesh_operations[mesh_op.name] = mesh_op

        wg_in.group_name = self.antenna_name
        horn_sheet.group_name = self.antenna_name
        cap.group_name = self.antenna_name
        p1.group_name = self.antenna_name

        self.object_list[wg_in.name] = wg_in
        self.object_list[horn_sheet.name] = horn_sheet
        self.object_list[cap.name] = cap
        self.object_list[p1.name] = p1

        # Create radiation boundary
        if self.outer_boundary:
            self._app.create_open_region(
                str(self.frequency) + self.frequency_unit, self.outer_boundary
            )

        # Excitation
        if self._app.solution_type != "Modal":
            self._app.logger.warning("Solution type must be Modal to define the excitation")

        terminal_references = None
        if self._app.solution_type == "Terminal":
            terminal_references = cap.name
        port1 = self._app.create_wave_port_from_sheet(
            sheet=p1, portname="port_" + self.antenna_name, terminal_references=terminal_references
        )
        self.excitations[port1.name] = port1
        return True

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz
        wavelength_in = constants.unit_converter(wavelength, "Length", "meter", "in")
        if (
            self.material not in self._app._materials.mat_names_aedt
            or self.material not in self._app._materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create new material before assign.")
            return parameters

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
        wall_thickness = constants.unit_converter(
            wall_thickness_in, "Length", "in", self.length_unit
        )
        parameters["wall_thickness"] = wall_thickness

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

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
            antenna_name = generate_unique_name("Horn")
            while len(list(self._app.modeler.oeditor.GetObjectsInGroup(antenna_name))) > 0:
                antenna_name = generate_unique_name("Horn")
        return antenna_name
