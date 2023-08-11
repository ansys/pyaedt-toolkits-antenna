import re
import time

import pyaedt

from ansys.aedt.toolkits.antennas.backend import models
from ansys.aedt.toolkits.antennas.backend.common.api_generic import ToolkitGeneric
from ansys.aedt.toolkits.antennas.backend.common.logger_handler import logger
from ansys.aedt.toolkits.antennas.backend.common.properties import properties
from ansys.aedt.toolkits.antennas.backend.common.thread_manager import ThreadManager

thread = ThreadManager()


class Toolkit(ToolkitGeneric):
    """API to control the toolkit workflow.

    This class provides methods to synthesize and create antennas.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antennas.backend.api import Toolkit
    >>> import time
    >>> toolkit = Toolkit()
    >>> msg1 = toolkit.launch_aedt()
    >>> response = toolkit.get_thread_status()
    >>> while response[0] == 0:
    >>>     time.sleep(1)
    >>>     response = toolkit.get_thread_status()
    >>> toolkit.get_antenna("BowTie")
    """

    def __init__(self):
        ToolkitGeneric.__init__(self)
        self._oantenna = None
        self.antenna_type = None
        self.available_antennas = []
        for name, var in vars(models).items():
            # If the variable is a module, print the module's name
            if isinstance(var, type):
                self.available_antennas.append(name)

    def get_antenna(self, antenna, synth_only=False):
        """Synthesize and create the antenna in HFSS.

        Parameters
        ----------
        antenna : :class:
            Type of antenna to create.
        synth_only : bool, optional
            Whether to only synthesize the anttena. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antennas.backend.api import Toolkit
        >>> import time
        >>> toolkit = Toolkit()
        >>> msg1 = toolkit.launch_aedt()
        >>> response = toolkit.get_thread_status()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> msg3 = toolkit.get_antenna("BowTie")
        """

        if self._oantenna:
            logger.debug("Antenna is already created")
            return False

        if antenna not in models.__dir__():
            logger.debug("Antenna is not implemented")
            return False

        if not synth_only and not self.aedtapp:
            if properties.active_design and list(properties.active_design.keys())[0].lower() != "hfss":
                logger.debug("Selected design must be HFSS")
                return False
            # Connect to AEDT design
            self.connect_design("HFSS")
            if not self.aedtapp:
                logger.debug("HFSS design not connected")
                return False

        # Get antenna properties
        freq_units = properties.frequency_unit
        antenna_module = getattr(models, antenna)
        properties.antenna_type = antenna
        self.antenna_type = antenna

        # Create antenna object with default values
        self._oantenna = antenna_module(
            self.aedtapp,
            frequency_unit=freq_units,
            length_unit=properties.length_unit,
        )

        # Update antenna properties
        oantenna_public_props = (name for name in self._oantenna.__dir__() if not name.startswith("_"))
        for antenna_prop in oantenna_public_props:
            if antenna_prop in properties.__dir__():
                if (
                    antenna_prop == "frequency"
                    and "start_frequency" in self._oantenna.__dir__()
                    and "stop_frequency" in self._oantenna.__dir__()
                ):
                    pass
                elif antenna_prop == "material_properties":
                    if properties.material_properties:
                        self._oantenna.material_properties["permittivity"] = properties.material_properties[
                            "permittivity"
                        ]
                else:
                    setattr(self._oantenna, antenna_prop, getattr(properties, antenna_prop))

        self._oantenna._parameters = self._oantenna._synthesis()
        self._oantenna.update_synthesis_parameters(self._oantenna._parameters)

        antenna_parameters = {}

        oantenna_public_parameters = (
            name for name in self._oantenna.synthesis_parameters.__dict__ if not name.startswith("_")
        )
        for param in oantenna_public_parameters:
            antenna_parameters[param] = self._oantenna.synthesis_parameters.__getattribute__(param).value
        if not synth_only and not properties.antenna_created:
            if not self._oantenna.object_list:
                if not self._oantenna.antenna_name:
                    self._oantenna.antenna_name = pyaedt.generate_unique_name(self.antenna_type)
                    self.set_properties({"antenna_name": self._oantenna.antenna_name})
                self._oantenna.init_model()
                self._oantenna.model_hfss()
                self._oantenna.setup_hfss()
                properties.antenna_created = True
            if properties.lattice_pair:
                self._oantenna.create_lattice_pair()
            if properties.component_3d:
                self._oantenna.create_3dcomponent(replace=True)
            if properties.create_setup:
                freq = float(self._oantenna.frequency)
                setup = self.aedtapp.create_setup()
                setup.props["Frequency"] = str(freq) + freq_units
                if int(properties.sweep) > 0:
                    sweep1 = setup.add_sweep()
                    perc_sweep = (int(properties.sweep)) / 100
                    sweep1.props["RangeStart"] = str(freq * (1 - perc_sweep)) + freq_units
                    sweep1.props["RangeEnd"] = str(freq * (1 + perc_sweep)) + freq_units
                    sweep1.update()
        elif synth_only:
            self._oantenna = None

        if self.aedtapp:
            self.aedtapp.save_project()
            time.sleep(1)
        #     self.aedtapp.release_desktop(False, False)
        #     self.aedtapp = None

        properties.parameters = antenna_parameters
        return antenna_parameters

    def update_parameters(self, key, val):
        """Update parameters in HFSS.

        Parameters
        ----------
        key : str
        val : float

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antennas.backend.api import Toolkit
        >>> import time
        >>> toolkit = Toolkit()
        >>> msg1 = toolkit.launch_aedt()
        >>> response = toolkit.get_thread_status()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> msg3 = toolkit.get_antenna("BowTie")
        >>> msg3 = toolkit.update_parameters()
        """
        properties = self.get_properties()
        if not properties["parameters_hfss"]:
            logger.debug("Antenna not created in HFSS")
            return True

        if not self.aedtapp:
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design not connected")
                return False

        if (
            self.aedtapp
            and key in properties["parameters_hfss"]
            and properties["parameters_hfss"][key] in self.aedtapp.variable_manager.independent_variable_names
        ):
            ratio_re = re.compile("|".join(["ratio", "coefficient", "points", "number"]))
            if "angle" in key:
                if "deg" not in val:
                    val = val + "deg"
            elif ratio_re.search(key):
                val = val
            else:
                if properties["length_unit"] not in val:
                    val = val + properties["length_unit"]
            hfss_parameter = properties["parameters_hfss"][key]
            self.aedtapp[hfss_parameter] = val

            new_value = properties["parameters"]
            new_value[key] = val
            self.set_properties({"parameters": new_value})

            return True
        else:
            logger.debug("Parameter does not exist")
            return False

    @thread.launch_thread
    def analyze(self):
        """Analyze design.

        This method is launched in a thread if grpc is enabled. AEDT is released once it is opened.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antennas.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit_free = toolkit.get_thread_status()
        """
        # Check if the backend is already connected to an AEDT session
        connected, msg = self.aedt_connected()
        if not connected:
            if properties.active_design and list(properties.active_design.keys())[0].lower() != "hfss":
                logger.debug("Selected design must be HFSS")
                return False
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design not connected")
                return False

        num_cores = properties.core_number

        self.aedtapp.save_project()
        time.sleep(1)
        self.aedtapp.solve_in_batch(run_in_thread=True, machine="localhost", num_cores=num_cores)
        self.aedtapp.release_desktop(False, False)
        self.aedtapp = None
        return True

    def scattering_results(self):
        """Get antenna scattering results.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not self.aedtapp:
            if properties.active_design and list(properties.active_design.keys())[0].lower() != "hfss":
                logger.debug("Selected design must be HFSS")
                return False
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design not connected")
                return False

        sol_data = self.aedtapp.post.get_solution_data()

        self.aedtapp.release_desktop(False, False)
        self.aedtapp = None

        if not sol_data:
            return
        return sol_data.primary_sweep_values, sol_data.data_db20()

    def farfield_results(self):
        """Get antenna far field results.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not self.aedtapp:
            if properties.active_design and list(properties.active_design.keys())[0].lower() != "hfss":
                logger.debug("Selected design must be HFSS")
                return False
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design not connected")
                return False

        field_solution = self.aedtapp.post.get_solution_data(
            "GainTotal",
            self.aedtapp.nominal_adaptive,
            primary_sweep_variable="Theta",
            context="3D",
            report_category="Far Fields",
        )

        if not field_solution:
            return

        phi_cuts = field_solution.intrinsics["Phi"]
        theta = field_solution.primary_sweep_values
        val_theta = []
        for t in phi_cuts:
            field_solution.active_intrinsic["Phi"] = t
            val_theta.append(field_solution.data_db20())
        field_solution.active_intrinsic["Phi"] = phi_cuts[0]

        field_solution.primary_sweep = "Phi"
        theta_cuts = field_solution.intrinsics["Theta"]
        phi = field_solution.primary_sweep_values
        val_phi = []
        for t in theta_cuts:
            field_solution.active_intrinsic["Theta"] = t
            val_phi.append(field_solution.data_db20())
        field_solution.active_intrinsic["Theta"] = theta_cuts[0]

        self.aedtapp.release_desktop(False, False)
        self.aedtapp = None

        return [phi_cuts, theta, val_theta, theta_cuts, phi, val_phi]
