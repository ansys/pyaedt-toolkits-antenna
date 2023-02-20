from collections import OrderedDict
import math

import pyaedt.generic.constants as constants
from pyaedt.generic.general_methods import pyaedt_function_handler

import ansys.aedt.toolkits.antennas.common_ui
from ansys.aedt.toolkits.antennas.models.common import CommonAntenna


class CommonHelix(CommonAntenna):
    """Base methods common to Horn antennas."""

    def __init__(self, _default_input_parameters, *args, **kwargs):
        CommonAntenna.antenna_type = "Helix"
        CommonAntenna.__init__(self, _default_input_parameters, *args, **kwargs)

    @property
    def gain_value(self):
        """Helix expected gain.

        Returns
        -------
        float
        """
        return self._input_parameters.gain_value

    @gain_value.setter
    def gain_value(self, value):
        self._input_parameters.gain_value = value
        if value != self.gain_value and self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def direction(self):
        """Helix direction. `0` for Left `1` for right.

        Returns
        -------
        int
        """
        return self._input_parameters.direction

    @direction.setter
    def direction(self, value):
        self._input_parameters.direction = value
        if value != self.direction and self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @property
    def feeder_length(self):
        """Helix Feeder Length.

        Returns
        -------
        float
        """
        return self._input_parameters.feeder_length

    @feeder_length.setter
    def feeder_length(self, value):
        self._input_parameters.feeder_length = value
        if value != self.feeder_length and self.object_list:
            parameters = self._synthesis()
            self.update_synthesis_parameters(parameters)
            self.set_variables_in_hfss()

    @pyaedt_function_handler()
    def _synthesis(self):
        pass


class AxialMode(CommonHelix):
    """Manages Axial mode Helix antenna.

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
    :class:`aedt.toolkits.antennas.AxialMode`
            Antenna object.

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
        "gain_value": 10,
        "direction": 0,
        "feeder_length": 10,
        "outer_boundary": None,
        "huygens_box": False,
    }

    def __init__(self, *args, **kwargs):
        CommonHelix.__init__(self, self._default_input_parameters, *args, **kwargs)

        self._parameters = self._synthesis()
        self.update_synthesis_parameters(self._parameters)

    @pyaedt_function_handler()
    def _synthesis(self):
        parameters = {}
        lightSpeed = constants.SpeedOfLight  # m/s
        freq_hz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "Hz")
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        wl_meters = lightSpeed / freq_hz
        gain_value_dB = self.gain_value
        gain_value_mag = math.pow(10.0, gain_value_dB / 10.0)

        groundx = constants.unit_converter(4.0 * (3.33 / freq_ghz), "Length", "in", "mm")
        groundy = constants.unit_converter(4.0 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_diameter = constants.unit_converter(1.128 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_spacing = constants.unit_converter(0.786 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_wiredia = constants.unit_converter(0.2 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_coax_inner_radius = constants.unit_converter(
            0.082 * (3.33 / freq_ghz) / 2, "Length", "in", "mm"
        )
        helix_coax_outer_radius = constants.unit_converter(
            0.275 * (3.33 / freq_ghz) / 2, "Length", "in", "mm"
        )
        helix_feed_pinL = constants.unit_converter(0.05 * (3.33 / freq_ghz), "Length", "in", "mm")
        helix_feed_pinD = constants.unit_converter(0.082 * (3.33 / freq_ghz), "Length", "in", "mm")

        helix_diameter_syn = wl_meters / math.pi * 0.9
        helix_spacing_syn = math.pi * helix_diameter_syn * math.tan(math.radians(12.5))
        helix_turns_syn = gain_value_mag * wl_meters / 15.0 / helix_spacing_syn

        parameters["groundx"] = groundx
        parameters["groundy"] = groundy
        parameters["diameter"] = helix_diameter
        parameters["spacing"] = helix_spacing
        parameters["wire_diameter"] = helix_wiredia
        parameters["coax_inner_radius"] = helix_coax_inner_radius
        parameters["coax_outer_radius"] = helix_coax_outer_radius
        parameters["feed_pinL"] = helix_feed_pinL
        parameters["feed_pinD"] = helix_feed_pinD
        parameters["number_of_turns"] = helix_turns_syn
        parameters["feeder_length"] = self.feeder_length

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
        self._app
        # Map parameters
        groundx = self.synthesis_parameters.groundx.hfss_variable
        groundy = self.synthesis_parameters.groundy.hfss_variable
        diameter = self.synthesis_parameters.diameter.hfss_variable
        wire_diameter = self.synthesis_parameters.wire_diameter.hfss_variable
        spacing = self.synthesis_parameters.spacing.hfss_variable
        coax_inner_radius = self.synthesis_parameters.coax_inner_radius.hfss_variable
        coax_outer_radius = self.synthesis_parameters.coax_outer_radius.hfss_variable
        feed_pinL = self.synthesis_parameters.feed_pinL.hfss_variable
        feed_pinD = self.synthesis_parameters.feed_pinD.hfss_variable
        feeder_length = self.synthesis_parameters.feeder_length.hfss_variable
        number_of_turns = self.synthesis_parameters.number_of_turns.hfss_variable
        self._app[number_of_turns] = str(self.synthesis_parameters.number_of_turns.value)

        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable
        antenna_name = self.antenna_name
        coordinate_system = self.coordinate_system
        my_udmPairs = []
        mypair = ["PolygonSegments", "8"]
        my_udmPairs.append(mypair)
        mypair = ["PolygonRadius", "{}/2".format(wire_diameter)]
        my_udmPairs.append(mypair)
        mypair = ["StartHelixRadius", "{}/2".format(diameter)]
        my_udmPairs.append(mypair)
        mypair = ["RadiusChange", "0"]
        my_udmPairs.append(mypair)
        mypair = ["Pitch", spacing]
        my_udmPairs.append(mypair)
        mypair = ["Turns", str(number_of_turns)]
        my_udmPairs.append(mypair)
        mypair = ["SegmentsPerTurn", "16"]
        my_udmPairs.append(mypair)
        mypair = ["RightHanded", self.direction]
        my_udmPairs.append(mypair)
        udm = self._app.modeler.create_udp(
            udp_dll_name="SegmentedHelix/PolygonHelix.dll",
            udp_parameters_list=my_udmPairs,
            upd_library="syslib",
            name="helix",
        )
        udm.history.props["Coordinate System"] = coordinate_system
        udm.material_name = "pec"
        self._app.modeler.split(udm, "XY", "PositiveOnly")
        gnd = self._app.modeler.create_rectangle(
            self._app.PLANE.XY,
            [
                "-{}/2".format(groundx),
                "-{}/2".format(groundy),
                "-{}-{}/2".format(feed_pinL, wire_diameter),
            ],
            [groundx, groundy],
            name="gnd_" + antenna_name,
        )
        gnd.history.props["Coordinate System"] = coordinate_system

        cutout = self._app.modeler.create_circle(
            cs_plane=2,
            position=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pinD),
                "-{}-{}/2".format(feed_pinL, wire_diameter),
            ],
            radius=coax_outer_radius,
        )
        cutout.history.props["Coordinate System"] = coordinate_system
        gnd.subtract(cutout, keep_originals=False)

        # Negative air
        feedPin = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pinD),
                "-{}-{}/2".format(feed_pinL, wire_diameter),
            ],
            radius=feed_pinD + "/2",
            height=feed_pinL + "+" + wire_diameter + "/2",
            name="Feed_{}".format(antenna_name),
            matname="pec",
        )
        feedPin.history.props["Coordinate System"] = coordinate_system

        feedCoax = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pinD),
                "-{}-{}/2".format(feed_pinL, wire_diameter),
            ],
            radius=coax_inner_radius,
            height="-{}".format(feeder_length),
            name="Feed1_{}".format(antenna_name),
            matname="pec",
        )
        feedCoax.history.props["Coordinate System"] = coordinate_system

        Coax = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pinD),
                "-{}-{}/2".format(feed_pinL, wire_diameter),
            ],
            radius=coax_outer_radius,
            height="-{}".format(feeder_length),
            name="coax_{}".format(antenna_name),
            matname="Teflon (tm)",
        )
        Coax.history.props["Coordinate System"] = coordinate_system
        # faceId = self._app.modeler.get_faceid_from_position(
        #     obj_name=Coax.name,
        #     position=[
        #         "{}/2+{}".format(diameter, coax_outer_radius),
        #         "-{}/2".format(feed_pinD),
        #         "-{}-{}/2-{}/2".format(feed_pinL, wire_diameter, feed_pinD),
        #     ],
        # )

        # f_perf = [i for i in Coax.faces if i.id not in
        # [Coax.bottom_face_z.id, Coax.top_face_z.id]]
        # o1 = self._app.modeler.create_object_from_face(faceId)
        # o1.name = "PerfE_Coax_{}".format(antenna_name)
        # Cap
        cap = self._app.modeler.create_cylinder(
            cs_axis=2,
            position=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pinD),
                "-{}-{}/2-{}".format(feed_pinL, wire_diameter, feeder_length),
            ],
            radius=coax_outer_radius,
            height="-{}/2".format(feed_pinL),
            name="port_cap_" + antenna_name,
            matname="pec",
        )
        cap.history.props["Coordinate System"] = coordinate_system

        # P1
        p1 = self._app.modeler.create_circle(
            cs_plane=2,
            position=[
                "{}/2".format(diameter),
                "-{}/2".format(feed_pinD),
                "-{}-{}/2-{}".format(feed_pinL, wire_diameter, feeder_length),
            ],
            radius=coax_outer_radius,
            name="port_" + antenna_name,
        )
        p1.color = (128, 0, 0)
        p1.history.props["Coordinate System"] = coordinate_system

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
                    pos_x + "-{}/2".format(groundx) + "-" + huygens_dist + self.length_unit,
                    pos_y + "-{}/2".format(groundy) + "-" + huygens_dist + self.length_unit,
                    pos_z + "-{}-{}/2-{}".format(feed_pinL, wire_diameter, feeder_length),
                ],
                dimensions_list=[
                    groundx + "+" + "2*" + huygens_dist + self.length_unit,
                    groundy + "+" + "2*" + huygens_dist + self.length_unit,
                    number_of_turns
                    + "*"
                    + spacing
                    + "+"
                    + feeder_length
                    + "+.5*"
                    + feed_pinL
                    + "+"
                    + wire_diameter
                    + "/2+"
                    + huygens_dist
                    + self.length_unit,
                ],
                name="huygens_" + antenna_name,
                matname="air",
            )
            huygens.display_wireframe = True
            huygens.color = (0, 0, 255)
            huygens.history.props["Coordinate System"] = coordinate_system
            huygens.group_name = antenna_name

        udm.group_name = antenna_name
        feedCoax.group_name = antenna_name
        feedPin.group_name = antenna_name
        cap.group_name = antenna_name
        gnd.group_name = antenna_name
        p1.group_name = antenna_name
        # o1.group_name = antenna_name
        self._app.modeler.translate(
            [udm, feedCoax, feedPin, cap, gnd, p1, o1], [pos_x, pos_y, pos_z]
        )
        self.object_list[udm.name] = udm
        self.object_list[feedCoax.name] = feedCoax
        self.object_list[feedPin.name] = feedPin
        self.object_list[cap.name] = cap
        self.object_list[gnd.name] = gnd
        self.object_list[p1.name] = p1

    @pyaedt_function_handler()
    def model_disco(self):
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        pass
