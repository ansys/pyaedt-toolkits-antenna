from collections import OrderedDict
import math

import pyaedt.generic.constants as constants
# from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antennas.common import CommonAntenna


class CommonPatch(CommonAntenna):
    """Base methods common to Patch antennas."""

    def __init__(self, default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Patchhh"
        CommonAntenna.__init__(self, default_input_parameters, *args, **kwargs)


        self._old_material = None
        # self.material = kwargs["material"]
        # self.substrate_height = kwargs["substrate_height"]
        # self.object_list = {}
        # self.parameters = []

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
                    if (
                        self.object_list[antenna_obj].material_name == old_material.lower()
                        and "coax" not in antenna_obj
                    ):
                        self.object_list[antenna_obj].material_name = value

    @property
    def substrate_height(self):
        """Substrate height.

        Returns
        -------
        float
        """
        return self._substrate_height

    @substrate_height.setter
    def substrate_height(self, value):
        self._substrate_height = value
        parameters = self._synthesis()
        if self.object_list:
            parameters_map = {}
            cont = 0
            for param in parameters:
                parameters_map[self.parameters[cont]] = parameters[param]
                cont += 1
            self._update_parameters(parameters_map, self.length_unit)

    @pyaedt_function_handler()
    def _synthesis(self):
        pass


class RectangularPatchProbe(CommonPatch):
    """Manages rectangular patch antenna with coaxial probe.

    This class is accessible through the app hfss object.

    Parameters
    ----------
    frequency : float, optional
            Center frequency. The default is ``10.0``.
    frequency_unit : str, optional
            Frequency units. The default is ``GHz``.
    material : str, optional
            Substrate material.
            If material is not defined a new material parametrized will be defined.
            The default is ``"FR4_epoxy"``.
    outer_boundary : str, optional
            Boundary type to use. Options are ``"Radiation"``,
            ``"FEBI"``, and ``"PML"`` or None. The default is ``None``.
    huygens_box : bool, optional
            Create a Huygens box. The default is ``False``.
    length_unit : str, optional
            Length units. The default is ``"cm"``.
    substrate_height : float, optional
            Substrate height. The default is ``0.1575``.
    parametrized : bool, optional
            Create a parametrized antenna. The default is ``True``.

    Returns
    -------
    :class:`aedt.toolkits.antennas.RectangularPatchProbe`
            Patch antenna object.

    Examples
    --------
    >>> from pyaedt import Hfss
    >>> from ansys.aedt.toolkits.antennas.patch import RectangularPatchProbe
    >>> hfss = Hfss()
    >>> patch = hfss.add_from_toolkit(RectangularPatchProbe, frequency=20.0, frequency_unit="GHz")
    """

    default_input_parameters = {
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
        # if "frequency" not in kwargs.keys():
        #     kwargs["frequency"] = 10.0
        # if "frequency_unit" not in kwargs.keys():
        #     kwargs["frequency_unit"] = "GHz"
        # if "material" not in kwargs.keys():
        #     kwargs["material"] = "FR4_epoxy"
        # if "outer_boundary" not in kwargs.keys():
        #     kwargs["outer_boundary"] = None
        # if "huygens_box" not in kwargs.keys():
        #     kwargs["huygens_box"] = False
        # if "substrate_height" not in kwargs.keys():
        #     kwargs["substrate_height"] = 0.1575
        # if "coordinate_system" not in kwargs.keys():
        #     kwargs["coordinate_system"] = "Global"
        # if "antenna_name" not in kwargs.keys():
        #     kwargs["antenna_name"] = None
        # if "origin" not in kwargs.keys():
        #     kwargs["origin"] = [0, 0, 0]

        CommonPatch.__init__(self, self.default_input_parameters, *args, **kwargs)

        # self.antenna_name = self._check_antenna_name(self.antenna_name)
        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

        res=-1
        # self.parameters = []

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        length_unit = self.input_parameters.length_unit
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(
            self.input_parameters.frequency, "Freq", self.input_parameters.frequency_unit, "Hz"
        )
        wavelength = lightSpeed / freq_hz

        if (
            self.input_parameters.material in self._app._materials.mat_names_aedt
            or self.input_parameters.material in self._app._materials.mat_names_aedt_lower
        ):
            mat_props = self._app._materials[self.input_parameters.material]
        else:
            self._app.logger.warning("Material not found. Create the material before assignment.")
            return parameters

        subPermittivity = float(mat_props.permittivity.value)

        sub_meters = constants.unit_converter(
            self.input_parameters.substrate_height, "Length", self.input_parameters.length_unit, "meter"
        )

        patch_width = 3.0e8 / ((2.0 * freq_hz) * math.sqrt((subPermittivity + 1.0) / 2.0))

        eff_Permittivity = (subPermittivity + 1.0) / 2.0 + (subPermittivity - 1.0) / 2.0 * math.pow(
            1.0 + 12.0 * sub_meters / patch_width, -0.5
        )

        effective_length = 3.0e8 / (2.0 * freq_hz * math.sqrt(eff_Permittivity))

        top = (eff_Permittivity + 0.3) * (patch_width / sub_meters + 0.264)
        bottom = (eff_Permittivity - 0.258) * (patch_width / sub_meters + 0.8)

        delta_length = 0.412 * sub_meters * top / bottom

        patch_length = effective_length - 2.0 * delta_length

        # eff_WL_meters = wavelength / math.sqrt(eff_Permittivity)

        k = 2.0 * math.pi / eff_Permittivity
        G = (
            math.pi
            * patch_width
            / (120.0 * math.pi * wavelength)
            * (1.0 - math.pow(k * sub_meters, 2) / 24)
        )

        # impedance at edge of patch
        Res = 1.0 / (2.0 * G)
        offset_pin_pos = patch_length / math.pi * math.asin(math.sqrt(50.0 / Res))

        patch_x = constants.unit_converter(patch_width, "Length", "meter", length_unit)
        parameters["patch_x"] = patch_x

        patch_y = constants.unit_converter(patch_length, "Length", "meter", length_unit)
        parameters["patch_y"] = patch_y

        feed_x = 0.0
        parameters["feed_x"] = feed_x

        feed_y = round(constants.unit_converter(offset_pin_pos, "Length", "meter", length_unit), 2)
        parameters["feed_y"] = feed_y

        sub_h = self.input_parameters.substrate_height
        parameters["sub_h"] = sub_h

        sub_x = round(
            constants.unit_converter(
                1.5 * patch_width + 6.0 * sub_meters, "Length", "meter", length_unit
            ),
            1,
        )
        parameters["sub_x"] = sub_x

        sub_y = round(
            constants.unit_converter(
                1.5 * patch_length + 6.0 * sub_meters, "Length", "meter", length_unit
            ),
            1,
        )
        parameters["sub_y"] = sub_y

        coax_inner_rad = round(
            constants.unit_converter(0.025 * (1e8 / freq_hz), "Length", "meter", length_unit),
            3,
        )
        parameters["coax_inner_rad"] = coax_inner_rad

        coax_outer_rad = round(
            constants.unit_converter(0.085 * (1e8 / freq_hz), "Length", "meter", length_unit),
            3,
        )
        parameters["coax_outer_rad"] = coax_outer_rad

        feed_length = round(
            constants.unit_converter(wavelength / 6.0, "Length", "meter", length_unit), 2
        )
        parameters["feed_length"] = feed_length

        if self.input_parameters.huygens_box:
            gnd_x = constants.unit_converter((299792458 / freq_hz / 4), "Length", "meter", length_unit) + sub_x
            gnd_y = constants.unit_converter((299792458 / freq_hz / 4), "Length", "meter", length_unit) + sub_y
        else:
            gnd_x = sub_x
            gnd_y = sub_y

        parameters["gnd_x"] = gnd_x
        parameters["gnd_y"] = gnd_y

        parameters["pos_x"] = self.input_parameters.origin[0]
        parameters["pos_y"] = self.input_parameters.origin[1]
        parameters["pos_z"] = self.input_parameters.origin[2]

        myKeys = list(parameters.keys())
        myKeys.sort()
        parameters_out = OrderedDict([(i, parameters[i]) for i in myKeys])

        return parameters_out

    @pyaedt_function_handler()
    # def draw(self):
    #     """Draw rectangular patch antenna.
    #     Once the antenna is created, this method will not be used."""
    #     if self.object_list:
    #         self._app.logger.warning("This antenna already exists")
    #         return False
    #
    #     for param in self._parameters:
    #         new_name = param + "_" + self.antenna_name
    #         if new_name not in self._app.variable_manager.variables:
    #             self._app[new_name] = str(self._parameters[param]) + self.length_unit
    #             self.parameters.append(new_name)
    #
    #     self.parameters = sorted(self.parameters)
    #     # Map parameter list to understand code
    #     patch_x = self.parameters[7]
    #     patch_y = self.parameters[8]
    #     feed_x = self.parameters[3]
    #     feed_y = self.parameters[4]
    #     sub_h = self.parameters[12]
    #     sub_x = self.parameters[13]
    #     sub_y = self.parameters[14]
    #
    #     coax_inner_rad = self.parameters[0]
    #     coax_outer_rad = self.parameters[1]
    #     feed_length = self.parameters[2]
    #     gnd_x = self.parameters[5]
    #     gnd_y = self.parameters[6]
    #     pos_x = self.parameters[9]
    #     pos_y = self.parameters[10]
    #     pos_z = self.parameters[11]
    #
    #     # Substrate
    #     sub = self._app.modeler.create_box(
    #         position=["-" + sub_x + "/2" "+" + pos_x, "-" + sub_y + "/2" "+" + pos_y, pos_z],
    #         dimensions_list=[sub_x, sub_y, sub_h],
    #         name="sub_" + self.antenna_name,
    #         matname=self.material,
    #     )
    #     sub.color = (0, 128, 0)
    #     sub.history.props["Coordinate System"] = self.coordinate_system
    #
    #     # Ground
    #     gnd = self._app.modeler.create_rectangle(
    #         csPlane=2,
    #         position=["-" + gnd_x + "/2" "+" + pos_x, "-" + gnd_y + "/2" "+" + pos_y, pos_z],
    #         dimension_list=[gnd_x, gnd_y],
    #         name="gnd_" + self.antenna_name,
    #     )
    #     gnd.color = (255, 128, 65)
    #     gnd.history.props["Coordinate System"] = self.coordinate_system
    #
    #     # Antenna
    #     ant = self._app.modeler.create_rectangle(
    #         csPlane=2,
    #         position=[
    #             "-" + patch_x + "/2" "+" + pos_x,
    #             "-" + patch_y + "/2" "+" + pos_y,
    #             sub_h + "+" + pos_z,
    #         ],
    #         dimension_list=[patch_x, patch_y],
    #         name="ant" + self.antenna_name,
    #     )
    #     ant.color = (255, 128, 65)
    #     ant.transparency = 0.1
    #     ant.history.props["Coordinate System"] = self.coordinate_system
    #
    #     void = self._app.modeler.create_circle(
    #         cs_plane=2,
    #         position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
    #         radius=coax_outer_rad,
    #         name="void_" + self.antenna_name,
    #     )
    #
    #     self._app.modeler.subtract(gnd, void, False)
    #
    #     feed_pin = self._app.modeler.create_cylinder(
    #         cs_axis=2,
    #         position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
    #         radius=coax_inner_rad,
    #         height=sub_h,
    #         name="feed_pin_" + self.antenna_name,
    #         matname="pec",
    #     )
    #     feed_pin.color = (255, 128, 65)
    #     feed_pin.history.props["Coordinate System"] = self.coordinate_system
    #
    #     feed_coax = self._app.modeler.create_cylinder(
    #         cs_axis=2,
    #         position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
    #         radius=coax_inner_rad,
    #         height="-" + feed_length,
    #         name="feed_coax_" + self.antenna_name,
    #         matname="pec",
    #     )
    #     feed_coax.color = (255, 128, 65)
    #     feed_coax.history.props["Coordinate System"] = self.coordinate_system
    #
    #     coax = self._app.modeler.create_cylinder(
    #         cs_axis=2,
    #         position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
    #         radius=coax_outer_rad,
    #         height="-" + feed_length,
    #         name="coax_" + self.antenna_name,
    #         matname="Teflon (tm)",
    #     )
    #     coax.color = (128, 255, 255)
    #     coax.history.props["Coordinate System"] = self.coordinate_system
    #
    #     port_cap = self._app.modeler.create_cylinder(
    #         cs_axis=2,
    #         position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z + "-" + feed_length],
    #         radius=coax_outer_rad,
    #         height="-" + sub_h + "/" + str(10),
    #         name="port_cap_" + self.antenna_name,
    #         matname="pec",
    #     )
    #     port_cap.color = (132, 132, 193)
    #     port_cap.history.props["Coordinate System"] = self.coordinate_system
    #
    #     p1 = self._app.modeler.create_circle(
    #         cs_plane=2,
    #         position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z + "-" + feed_length],
    #         radius=coax_outer_rad,
    #         name="port_" + self.antenna_name,
    #     )
    #     p1.color = (128, 0, 0)
    #     p1.history.props["Coordinate System"] = self.coordinate_system
    #
    #     # Create Huygens box
    #     if self.huygens_box:
    #         lightSpeed = constants.SpeedOfLight  # m/s
    #         freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
    #         huygens_dist = str(
    #             constants.unit_converter(
    #                 lightSpeed / (10 * freq_hz), "Length", "meter", self.length_unit
    #             )
    #         )
    #         huygens = self._app.modeler.create_box(
    #             position=[
    #                 "-" + gnd_x + "/2.1" "+" + pos_x,
    #                 "-" + gnd_y + "/2.1" "+" + pos_y,
    #                 pos_z,
    #             ],
    #             dimensions_list=[
    #                 "abs(-" + gnd_x + "/2.1" + "-" + gnd_x + "/2.1)",
    #                 "abs(-" + gnd_y + "/2.1" + "-" + gnd_y + "/2.1)",
    #                 "abs(-" + sub_h + ")+" + huygens_dist + self.length_unit,
    #             ],
    #             name="huygens_" + self.antenna_name,
    #             matname="air",
    #         )
    #         huygens.display_wireframe = True
    #         huygens.color = (0, 0, 255)
    #         huygens.history.props["Coordinate System"] = self.coordinate_system
    #
    #         mesh_op = self._app.mesh.assign_length_mesh(
    #             [huygens.name],
    #             maxlength=huygens_dist + self.length_unit,
    #             maxel=None,
    #             meshop_name="HuygensBox_Seed_" + self.antenna_name,
    #         )
    #
    #         self.object_list[huygens.name] = huygens
    #         huygens.group_name = self.antenna_name
    #         self.mesh_operations[mesh_op.name] = mesh_op
    #
    #     sub.group_name = self.antenna_name
    #     gnd.group_name = self.antenna_name
    #     ant.group_name = self.antenna_name
    #     feed_pin.group_name = self.antenna_name
    #     feed_coax.group_name = self.antenna_name
    #     coax.group_name = self.antenna_name
    #     port_cap.group_name = self.antenna_name
    #     p1.group_name = self.antenna_name
    #
    #     self.object_list[sub.name] = sub
    #     self.object_list[gnd.name] = gnd
    #     self.object_list[ant.name] = ant
    #     self.object_list[feed_pin.name] = feed_pin
    #     self.object_list[feed_coax.name] = feed_coax
    #     self.object_list[coax.name] = coax
    #     self.object_list[port_cap.name] = port_cap
    #     self.object_list[p1.name] = p1
    #
    #     # Assign coating
    #     ant_bound = self._app.assign_perfecte_to_sheets(ant.name)
    #     ant_bound.name = "PerfE_antenna_" + self.antenna_name
    #     self.boundaries[ant_bound.name] = ant_bound
    #     gnd_bound = self._app.assign_perfecte_to_sheets(gnd.name)
    #     gnd_bound.name = "PerfE_gnd_" + self.antenna_name
    #     self.boundaries[gnd_bound.name] = gnd_bound
    #
    #     face_id = coax.faces[0].edges[0].id
    #     for face in coax.faces:
    #         if len(face.edges) == 2:
    #             face_id = face.id
    #             break
    #
    #     coax_bound = self._app.assign_perfecte_to_sheets(face_id)
    #     coax_bound.name = "PerfE_coax_" + self.antenna_name
    #     self.boundaries[coax_bound.name] = coax_bound
    #
    #     # Excitation
    #     port1 = self._app.create_wave_port_from_sheet(
    #         sheet=p1, portname="port_" + self.antenna_name, terminal_references=port_cap.name
    #     )
    #     self.excitations[port1.name] = port1
    #     if self._app.solution_type == "Terminal":
    #         self.excitations[port1.name + "_T1"] = port1
    #
    #     # Create radiation boundary
    #     if self.outer_boundary:
    #         self._app.create_open_region(
    #             str(self.frequency) + self.frequency_unit, self.outer_boundary
    #         )
    #
    #     return True

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw rectangular patch antenna.
        Once the antenna is created, this method will not be used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists")
            return False

        # for param in self._parameters:
        #     new_name = param + "_" + self.antenna_name
        #     if new_name not in self._app.variable_manager.variables:
        #         self._app[new_name] = str(self._parameters[param]) + self.length_unit
        #         self.parameters.append(new_name)

        self.set_variables_in_hfss()

        # self.parameters = sorted(self.parameters)

        # Map parameters
        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        feed_x = self.synthesis_parameters.feed_x.hfss_variable
        feed_y = self.synthesis_parameters.feed_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable

        coax_inner_rad = self.synthesis_parameters.coax_inner_rad.hfss_variable
        coax_outer_rad = self.synthesis_parameters.coax_outer_rad.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        gnd_x = self.synthesis_parameters.gnd_x.hfss_variable
        gnd_y = self.synthesis_parameters.gnd_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.input_parameters.antenna_name
        coordinate_system = self.input_parameters.coordinate_system

        # Substrate
        sub = self._app.modeler.create_box(
            position=["-" + sub_x + "/2" "+" + pos_x, "-" + sub_y + "/2" "+" + pos_y, pos_z],
            dimensions_list=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            matname=self.input_parameters.material,
        )
        sub.color = (0, 128, 0)
        sub.history.props["Coordinate System"] = coordinate_system

        # Ground
        gnd = self._app.modeler.create_rectangle(
            csPlane=2,
            position=["-" + gnd_x + "/2" "+" + pos_x, "-" + gnd_y + "/2" "+" + pos_y, pos_z],
            dimension_list=[gnd_x, gnd_y],
            name="gnd_" + antenna_name,
        )
        gnd.color = (255, 128, 65)
        gnd.history.props["Coordinate System"] = coordinate_system

        # Antenna
        ant = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + patch_x + "/2" "+" + pos_x,
                "-" + patch_y + "/2" "+" + pos_y,
                sub_h + "+" + pos_z,
            ],
            dimension_list=[patch_x, patch_y],
            name="ant_" + antenna_name,
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1
        ant.history.props["Coordinate System"] = coordinate_system

        void = self._app.modeler.create_circle(
            cs_plane=2,
            position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
            radius=coax_outer_rad,
            name="void_" + antenna_name,
        )

        self._app.modeler.subtract(gnd, void, False)

        feed_pin = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
            radius=coax_inner_rad,
            height=sub_h,
            name="feed_pin_" + antenna_name,
            matname="pec",
        )
        feed_pin.color = (255, 128, 65)
        feed_pin.history.props["Coordinate System"] = coordinate_system

        feed_coax = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
            radius=coax_inner_rad,
            height="-" + feed_length,
            name="feed_coax_" + antenna_name,
            matname="pec",
        )
        feed_coax.color = (255, 128, 65)
        feed_coax.history.props["Coordinate System"] = coordinate_system

        coax = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z],
            radius=coax_outer_rad,
            height="-" + feed_length,
            name="coax_" + antenna_name,
            matname="Teflon (tm)",
        )
        coax.color = (128, 255, 255)
        coax.history.props["Coordinate System"] = coordinate_system

        port_cap = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z + "-" + feed_length],
            radius=coax_outer_rad,
            height="-" + sub_h + "/" + str(10),
            name="port_cap_" + antenna_name,
            matname="pec",
        )
        port_cap.color = (132, 132, 193)
        port_cap.history.props["Coordinate System"] = coordinate_system

        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            position=[feed_x + "+" + pos_x, feed_y + "+" + pos_y, pos_z + "-" + feed_length],
            radius=coax_outer_rad,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = coordinate_system

        sub.group_name = antenna_name
        gnd.group_name = antenna_name
        ant.group_name = antenna_name
        feed_pin.group_name = antenna_name
        feed_coax.group_name = antenna_name
        coax.group_name = antenna_name
        port_cap.group_name = antenna_name
        p1.group_name = antenna_name

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[feed_pin.name] = feed_pin
        self.object_list[feed_coax.name] = feed_coax
        self.object_list[coax.name] = coax
        self.object_list[port_cap.name] = port_cap
        self.object_list[p1.name] = p1

    @pyaedt_function_handler()
    def setup_hfss(self):

        # Map parameters
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        gnd_x = self.synthesis_parameters.gnd_x.hfss_variable
        gnd_y = self.synthesis_parameters.gnd_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.input_parameters.antenna_name
        coordinate_system = self.input_parameters.coordinate_system
        length_unit = self.input_parameters.length_unit

        # Create Huygens box
        if self.input_parameters.huygens_box:
            lightSpeed = constants.SpeedOfLight  # m/s
            freq_hz = constants.unit_converter(
                self.input_parameters.frequency, "Freq", self.input_parameters.frequency_unit, "Hz"
            )
            huygens_dist = str(
                constants.unit_converter(
                    lightSpeed / (10 * freq_hz), "Length", "meter", length_unit
                )
            )
            huygens = self._app.modeler.create_box(
                position=[
                    "-" + gnd_x + "/2.1" "+" + pos_x,
                    "-" + gnd_y + "/2.1" "+" + pos_y,
                    pos_z,
                ],
                dimensions_list=[
                    "abs(-" + gnd_x + "/2.1" + "-" + gnd_x + "/2.1)",
                    "abs(-" + gnd_y + "/2.1" + "-" + gnd_y + "/2.1)",
                    "abs(-" + sub_h + ")+" + huygens_dist + length_unit,
                ],
                name="huygens_" + antenna_name,
                matname="air",
            )
            huygens.display_wireframe = True
            huygens.color = (0, 0, 255)
            huygens.history.props["Coordinate System"] = coordinate_system

            mesh_op = self._app.mesh.assign_length_mesh(
                [huygens.name],
                maxlength=huygens_dist + length_unit,
                maxel=None,
                meshop_name="HuygensBox_Seed_" + antenna_name,
            )

            self.object_list[huygens.name] = huygens
            huygens.group_name = antenna_name
            self.mesh_operations[mesh_op.name] = mesh_op

        # sub.group_name = antenna_name
        # gnd.group_name = antenna_name
        # ant.group_name = antenna_name
        # feed_pin.group_name = antenna_name
        # feed_coax.group_name = antenna_name
        # coax.group_name = antenna_name
        # port_cap.group_name = antenna_name
        # p1.group_name = antenna_name
        #
        # self.object_list[sub.name] = sub
        # self.object_list[gnd.name] = gnd
        # self.object_list[ant.name] = ant
        # self.object_list[feed_pin.name] = feed_pin
        # self.object_list[feed_coax.name] = feed_coax
        # self.object_list[coax.name] = coax
        # self.object_list[port_cap.name] = port_cap
        # self.object_list[p1.name] = p1

        # Assign boundary conditions
        for obj_name in self.object_list:
            if obj_name.startswith("ant_"):
                ant_bound = self._app.assign_perfecte_to_sheets(obj_name)
                ant_bound.name = "PerfE_antenna_" + antenna_name
                self.boundaries[ant_bound.name] = ant_bound
                break

        for obj_name in self.object_list:
            if obj_name.startswith("gnd_"):
                gnd_bound = self._app.assign_perfecte_to_sheets(obj_name)
                gnd_bound.name = "PerfE_gnd_" + antenna_name
                self.boundaries[gnd_bound.name] = gnd_bound
                break

        for obj_name in self.object_list:
            if obj_name.startswith("coax_"):
                obj = self.object_list[obj_name]
                face_id = obj.faces[0].edges[0].id
                for face in obj.faces:
                    if len(face.edges) == 2:
                        face_id = face.id
                        break
                coax_bound = self._app.assign_perfecte_to_sheets(face_id)
                coax_bound.name = "PerfE_coax_" + antenna_name
                self.boundaries[coax_bound.name] = coax_bound
                break

        # Assign port and excitation
        port_cap = None
        port = None
        for obj_name in self.object_list:
            if obj_name.startswith("port_cap_"):
                port_cap = self.object_list[obj_name]
            elif obj_name.startswith("port_"):
                port = self.object_list[obj_name]

        # Excitation
        if port_cap and port:
            port1 = self._app.create_wave_port_from_sheet(
                sheet=port, portname="port_" + antenna_name, terminal_references=port_cap.name
            )
            self.excitations[port1.name] = port1
            if self._app.solution_type == "Terminal":
                self.excitations[port1.name + "_T1"] = port1

        # Create radiation boundary
        if self.input_parameters.outer_boundary:
            self._app.create_open_region(
                str(self.input_parameters.frequency) + self.input_parameters.frequency_unit, self.input_parameters.outer_boundary
            )

        return True

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass

