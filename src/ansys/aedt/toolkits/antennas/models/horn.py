from collections import OrderedDict

import pyaedt.generic.constants as constants
from pyaedt.generic.general_methods import pyaedt_function_handler

import ansys.aedt.toolkits.antennas.common_ui
from ansys.aedt.toolkits.antennas.models.common import CommonAntenna


class CommonHorn(CommonAntenna):
    """Base methods common to Horn antennas."""

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
        if (
            value
            and value not in self._app.materials.mat_names_aedt
            and value not in self._app.materials.mat_names_aedt_lower
        ):
            ansys.aedt.toolkits.antennas.common_ui.logger.warning(
                "Material not found. Create new material before assign"
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
    >>> horn = hfss.add_from_toolkit(ConicalHorn, draw=True, frequency=20.0, frequency_unit="GHz",
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
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
        "huygens_box": False,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        wavelength = lightSpeed / freq_hz
        wavelength_in = constants.unit_converter(wavelength, "Length", "meter", "in")
        if (
            self.material not in self._app.materials.mat_names_aedt
            or self.material not in self._app.materials.mat_names_aedt_lower
        ):
            ansys.aedt.toolkits.antennas.common_ui.logger.warning(
                "Material not found. Create new material before assign."
            )
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
    def model_hfss(self):
        """Draw conical horn antenna.
        Once the antenna is created, this method will not be used anymore."""
        if self.object_list:
            ansys.aedt.toolkits.antennas.common_ui.logger.warning("This antenna already exists")
            return False

        self.set_variables_in_hfss()

        # Map parameters
        horn_length = self.synthesis_parameters.horn_length.hfss_variable
        horn_radius = self.synthesis_parameters.horn_radius.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        wg_radius = self.synthesis_parameters.wg_radius.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.antenna_name
        coordinate_system = self.coordinate_system

        # Negative air
        neg_air = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius,
            height="-" + wg_length,
            matname="vacuum",
        )
        neg_air.history.props["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wg_length,
            name="wg_outer_" + antenna_name,
            matname=self.material,
        )
        wall.history.props["Coordinate System"] = coordinate_system

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
            name="wg_inner_" + antenna_name,
            matname="vacuum",
        )
        wg_in.history.props["Coordinate System"] = coordinate_system

        # Cap
        cap = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[pos_x, pos_y, pos_z + "-" + wg_length],
            radius=wg_radius + "+" + wall_thickness,
            height="-" + wall_thickness,
            name="port_cap_" + antenna_name,
            matname="pec",
        )
        cap.history.props["Coordinate System"] = coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "-" + wg_length],
            radius=wg_radius,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius,
        )
        base.history.props["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z],
            radius=wg_radius + "+" + wall_thickness,
        )
        base_wall.history.props["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "+" + horn_length],
            radius=horn_radius,
        )
        horn_top.history.props["Coordinate System"] = coordinate_system

        horn_sheet = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "+" + horn_length],
            radius=horn_radius + "+" + wall_thickness,
        )
        horn_sheet.history.props["Coordinate System"] = coordinate_system

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
        air_base.history.props["Coordinate System"] = coordinate_system

        air_top = self._app.modeler.create_circle(
            cs_plane=2,
            position=[pos_x, pos_y, pos_z + "+" + horn_length],
            radius=horn_radius,
        )
        air_top.history.props["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base, air_top])

        self._app.modeler.unite([wg_in, air_base])

        wg_in.name = "internal_" + antenna_name
        wg_in.color = (128, 255, 255)

        horn_sheet.name = "metal_" + antenna_name
        horn_sheet.material_name = self.material
        horn_sheet.color = (255, 128, 65)

        cap.color = (132, 132, 192)
        p1.color = (128, 0, 0)
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
                name="huygens_" + antenna_name,
                matname="air",
            )
            huygens.display_wireframe = True
            huygens.color = (0, 0, 255)
            huygens.history.props["Coordinate System"] = coordinate_system
            huygens.group_name = antenna_name
            self.object_list[huygens.name] = huygens

        wg_in.group_name = antenna_name
        horn_sheet.group_name = antenna_name
        cap.group_name = antenna_name
        p1.group_name = antenna_name

        self.object_list[wg_in.name] = wg_in
        self.object_list[horn_sheet.name] = horn_sheet
        self.object_list[cap.name] = cap
        self.object_list[p1.name] = p1

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDisco. To be implemenented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Setup in PyDisco. To be implemenented."""
        pass


class PyramidalRidged(CommonHorn):
    """Manages pyramidal ridged horn antenna.

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
    >>> from ansys.aedt.toolkits.antennas.horn import PyramidalRidged
    >>> hfss = Hfss()
    >>> horn = hfss.add_from_toolkit(PyramidalRidged, draw=True, frequency=20.0,
    ...                              outer_boundary=None, huygens_box=True, length_unit="cm",
    ...                              coordinate_system="CS1", antenna_name="HornAntenna",
    ...                              origin=[1, 100, 50])

    """

    _default_input_parameters = {
        "antenna_name": None,
        "origin": [0, 0, 0],
        "length_unit": None,
        "coordinate_system": "Global",
        "frequency": 10.0,
        "frequency_unit": "GHz",
        "material": "pec",
        "outer_boundary": None,
        "huygens_box": False,
    }

    def __init__(self, *args, **kwargs):
        CommonHorn.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")

        if (
            self.material not in self._app.materials.mat_names_aedt
            or self.material not in self._app.materials.mat_names_aedt_lower
        ):
            self._app.logger.warning("Material not found. Create new material before assign.")
            return parameters

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

        aperture_height = constants.unit_converter(
            aperture_height, "Length", "mm", self.length_unit
        )
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
        Once the antenna is created, this method will not be used anymore."""
        if self.object_list:
            self._app.logger.warning("This antenna already exists")
            return False

        self.set_variables_in_hfss()

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
        antenna_name = self.antenna_name
        coordinate_system = self.coordinate_system

        # Base of the horn
        # Air
        air = self._app.modeler.create_box(
            position=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            dimensions_list=[wg_width, wg_height, wg_length],
            matname="vacuum",
        )
        air.history.props["Coordinate System"] = coordinate_system

        # Wall
        wall = self._app.modeler.create_box(
            position=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            dimensions_list=[
                wg_width + "+2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                wg_length,
            ],
            name="wall_" + antenna_name,
            matname="vacuum",
        )
        wall.history.props["Coordinate System"] = coordinate_system

        # Subtract
        new_wall = self._app.modeler.subtract(
            tool_list=[air.name], blank_list=[wall.name], keep_originals=False
        )

        # Top of the horn
        # Input
        wg_in = self._app.modeler.create_box(
            position=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            dimensions_list=[wg_width, wg_height, wg_length],
            name="wg_inner" + antenna_name,
            matname="vacuum",
        )
        wg_in.history.props["Coordinate System"] = coordinate_system
        wg_in.color = (128, 255, 255)

        # Cap
        cap = self._app.modeler.create_box(
            position=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "-" + wg_length,
            ],
            dimensions_list=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
                "-" + wall_thickness,
            ],
            name="port_cap_" + antenna_name,
            matname="pec",
        )
        cap.history.props["Coordinate System"] = coordinate_system
        cap.color = (132, 132, 193)

        # P1
        p1 = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            dimension_list=[wg_width, wg_height],
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = coordinate_system

        # Horn wall
        base = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            dimension_list=[wg_width, wg_height],
            name="base_" + antenna_name,
        )
        base.history.props["Coordinate System"] = coordinate_system

        base_wall = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + wg_width + "/2" + "-" + wall_thickness,
                "-" + wg_height + "/2" + "-" + wall_thickness,
                "0",
            ],
            dimension_list=[
                wg_width + "+" + "2*" + wall_thickness,
                wg_height + "+2*" + wall_thickness,
            ],
            name="base_wall_" + antenna_name,
        )
        base_wall.history.props["Coordinate System"] = coordinate_system

        horn_top = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + aperture_width + "/2",
                "-" + aperture_height + "/2",
                flare_length,
            ],
            dimension_list=[aperture_width, aperture_height],
            name="horn_top_" + antenna_name,
        )
        horn_top.history.props["Coordinate System"] = coordinate_system

        horn = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + aperture_width + "/2" + "-" + wall_thickness,
                "-" + aperture_height + "/2" + "-" + wall_thickness,
                flare_length,
            ],
            dimension_list=[
                aperture_width + "+" + "2*" + wall_thickness,
                aperture_height + "+" + "2*" + wall_thickness,
            ],
            name="horn_" + antenna_name,
        )
        horn.history.props["Coordinate System"] = coordinate_system

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
            matname=self.material,
        )
        ridge = self._app.modeler.thicken_sheet(ridge, ridge_width, True)
        ridge.history.props["Coordinate System"] = coordinate_system
        ridge.color = (132, 132, 193)

        mridge = self._app.modeler.create_polyline(
            position_list=ridge_position("-"),
            cover_surface=True,
            name="left_ridge" + antenna_name,
            matname=self.material,
        )
        mridge = self._app.modeler.thicken_sheet(mridge, ridge_width, True)
        mridge.history.props["Coordinate System"] = coordinate_system
        mridge.color = (132, 132, 193)

        # Connectors of the ridge
        # Connector
        connector = self._app.modeler.create_box(
            position=[
                "-" + ridge_width + "/2",
                "-" + wg_height + "/2",
                "-" + wg_length,
            ],
            dimensions_list=[
                ridge_width,
                "(" + wg_height + "-" + ridge_spacing + ")/2",
                wg_length,
            ],
            name="connector_" + antenna_name,
            matname="pec",
        )
        connector.history.props["Coordinate System"] = coordinate_system
        connector.color = (132, 132, 193)

        # Bottom connector
        bconnector = self._app.modeler.create_box(
            position=[
                "-" + ridge_width + "/2",
                wg_height + "/2",
                "-" + wg_length,
            ],
            dimensions_list=[
                ridge_width,
                "-(" + wg_height + "-" + ridge_spacing + ")/2",
                wg_length,
            ],
            name="bconnector_" + antenna_name,
            matname="pec",
        )
        bconnector.history.props["Coordinate System"] = coordinate_system
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
            csPlane=2,
            position=[
                "-" + wg_width + "/2",
                "-" + wg_height + "/2",
                "0",
            ],
            dimension_list=[
                wg_width,
                wg_height,
            ],
            name="air_base_" + antenna_name,
        )
        air_base.history.props["Coordinate System"] = coordinate_system

        # Air top
        air_top = self._app.modeler.create_rectangle(
            csPlane=2,
            position=[
                "-" + aperture_width + "/2",
                "-" + aperture_height + "/2",
                flare_length,
            ],
            dimension_list=[
                aperture_width,
                aperture_height,
            ],
            name="air_top_" + antenna_name,
        )
        air_top.history.props["Coordinate System"] = coordinate_system

        self._app.modeler.connect([air_base.name, air_top.name])

        self._app.modeler.unite([wg_in, air_base])

        self._app.modeler.move([cap, horn, wg_in, p1], [pos_x, pos_y, pos_z])

        cap.group_name = antenna_name
        horn.group_name = antenna_name
        wg_in.group_name = antenna_name
        p1.group_name = antenna_name

        self.object_list[cap.name] = cap
        self.object_list[horn.name] = horn
        self.object_list[wg_in.name] = wg_in
        self.object_list[p1.name] = p1

    @pyaedt_function_handler()
    def setup_hfss(self):
        """Conical horn antenna HFSS setup."""
        aperture_height = self.synthesis_parameters.aperture_height.hfss_variable
        aperture_width = self.synthesis_parameters.aperture_width.hfss_variable
        wg_length = self.synthesis_parameters.wg_length.hfss_variable
        flare_length = self.synthesis_parameters.flare_length.hfss_variable
        wall_thickness = self.synthesis_parameters.wall_thickness.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.antenna_name
        coordinate_system = self.coordinate_system
        length_unit = self.length_unit

        # Create Huygens box
        if self.huygens_box:
            lightSpeed = constants.SpeedOfLight  # m/s
            freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
            huygens_dist = str(
                constants.unit_converter(
                    lightSpeed / (10 * freq_hz), "Length", "meter", length_unit
                )
            )
            huygens = self._app.modeler.create_box(
                position=[
                    pos_x
                    + "-"
                    + aperture_width
                    + "/2-"
                    + huygens_dist
                    + length_unit
                    + "-2*"
                    + wall_thickness,
                    pos_y
                    + "-"
                    + aperture_height
                    + "/2"
                    + "-"
                    + wall_thickness
                    + "-"
                    + huygens_dist
                    + length_unit,
                    pos_z + "-" + wg_length + "-" + wall_thickness,
                ],
                dimensions_list=[
                    aperture_width
                    + "+"
                    + "2*"
                    + huygens_dist
                    + length_unit
                    + "+2*"
                    + wall_thickness,
                    aperture_height + "+" + "2*" + huygens_dist + length_unit,
                    huygens_dist
                    + length_unit
                    + "+"
                    + wg_length
                    + "+"
                    + wall_thickness
                    + "+"
                    + flare_length,
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

        self._app.change_material_override(True)

        # Excitation
        if self._app.solution_type != "Modal" and int(self._app.aedt_version_id[-3:]) < 231:
            self._app.logger.warning("Solution type must be Modal to define the excitation")
            return True

        # Assign port and excitation
        port_cap = None
        port = None
        for obj_name in self.object_list:
            if obj_name.startswith("port_cap_"):
                port_cap = self.object_list[obj_name]
            elif obj_name.startswith("port_"):
                port = self.object_list[obj_name]

        if self._app.solution_type == "Terminal":
            port1 = self._app._create_waveport_driven(
                objectname=port.name,
                int_line_start=port.faces[0].edges[1].midpoint,
                int_line_stop=port.faces[0].edges[3].midpoint,
                portname="port_" + antenna_name,
            )
        else:
            if int(self._app.aedt_version_id[-3:]) < 231:
                port1 = self._app.create_wave_port(
                    port.faces[0].id,
                    port.faces[0].edges[0].midpoint,
                    port.faces[0].edges[2].midpoint,
                    portname="port_" + antenna_name,
                )
            else:
                port1 = self._app.create_wave_port(
                    port.faces[0].id,
                    port.faces[0].edges[1].midpoint,
                    port.faces[0].edges[3].midpoint,
                    portname="port_" + antenna_name,
                )

        self.excitations[port1.name] = port1

        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model in PyDisco. To be implemenented."""
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Setup in PyDisco. To be implemenented."""
        pass