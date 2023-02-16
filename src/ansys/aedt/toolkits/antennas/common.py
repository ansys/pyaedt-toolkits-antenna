import copy
import os

from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import pyaedt_function_handler

from ansys.aedt.toolkits.antennas.parameters import InputParameters
from ansys.aedt.toolkits.antennas.parameters import Property
from ansys.aedt.toolkits.antennas.parameters import SynthesisParameters


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
        for k, v in new_params.items():
            if hasattr(self.synthesis_parameters, k):
                param = getattr(self.synthesis_parameters, k)
                param.value = v
            else:
                self.synthesis_parameters.add_parameter(k, v)

    @pyaedt_function_handler()
    def set_variables_in_hfss(self):
        for p in self.synthesis_parameters.__dict__.values():
            if isinstance(p, Property):
                self._app[p.hfss_variable] = str(p.value) + self.length_unit

    @pyaedt_function_handler()
    def init_model(self):
        # Create radiation boundary
        if self._input_parameters.outer_boundary:
            self._app.create_open_region(
                str(self.frequency) + self.frequency_unit, self.outer_boundary
            )
