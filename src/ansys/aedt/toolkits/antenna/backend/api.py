# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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

import re
import time

from ansys.aedt.toolkits.common.backend.api import AEDTCommon
from ansys.aedt.toolkits.common.backend.logger_handler import logger
import pyaedt

from ansys.aedt.toolkits.antenna.backend import antenna_models
from ansys.aedt.toolkits.antenna.backend.models import properties


class ToolkitBackend(AEDTCommon):
    """Provides methods for controlling the toolkit workflow.

    This class provides methods for creating an AEDT session, connecting to an existing
    AEDT session, and synthesizing and creating an antenna in HFSS.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
    >>> import time
    >>> toolkit = ToolkitBackend()
    >>> msg1 = toolkit.launch_aedt()
    >>> toolkit.wait_to_be_idle()
    >>> toolkit.get_antenna("BowTie")
    """

    def __init__(self):
        AEDTCommon.__init__(self, properties)
        self.properties = properties
        self._oantenna = None
        self.antenna_type = None
        self.available_antennas = []
        for name, var in vars(antenna_models).items():
            # If the variable is a module, print the module's name
            if isinstance(var, type):
                self.available_antennas.append(name)

    def get_antenna(self, antenna, synth_only=False):
        """Synthesize and create an antenna in HFSS.

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
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
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
            logger.debug("Antenna is already created.")
            return False

        if antenna not in antenna_models.__dir__():
            logger.debug("Antenna is not implemented.")
            return False

        if not synth_only and not self.aedtapp:
            if self.properties.active_design and list(self.properties.active_design.keys())[0].lower() != "hfss":
                logger.debug("Selected design must be HFSS.")
                return False
            # Connect to AEDT design
            self.connect_design("HFSS")
            if not self.aedtapp:
                logger.debug("HFSS design is not connected.")
                return False

        # Get antenna properties
        freq_units = self.properties.antenna.synthesis.frequency_unit
        antenna_module = getattr(antenna_models, antenna)
        self.properties.antenna.model = antenna
        self.antenna_type = antenna

        # Create antenna object with default values
        self._oantenna = antenna_module(
            self.aedtapp,
            frequency_unit=freq_units,
            length_unit=self.properties.antenna.synthesis.length_unit,
        )

        # Update antenna properties
        oantenna_public_props = (name for name in self._oantenna.__dir__() if not name.startswith("_"))
        for antenna_prop in oantenna_public_props:
            if antenna_prop in self.properties.antenna.synthesis.__dir__():
                if (
                    antenna_prop == "frequency"
                    and "start_frequency" in self._oantenna.__dir__()
                    and "stop_frequency" in self._oantenna.__dir__()
                ):
                    pass
                elif antenna_prop == "material_properties":
                    if self.properties.antenna.synthesis.material_properties:
                        self._oantenna.material_properties["permittivity"] = (
                            self.properties.antenna.synthesis.material_properties["permittivity"]
                        )
                else:
                    setattr(self._oantenna, antenna_prop, getattr(self.properties.antenna.synthesis, antenna_prop))

        self._oantenna._parameters = self._oantenna._synthesis()
        self._oantenna.update_synthesis_parameters(self._oantenna._parameters)

        antenna_parameters = {}

        oantenna_public_parameters = (
            name for name in self._oantenna.synthesis_parameters.__dict__ if not name.startswith("_")
        )
        for param in oantenna_public_parameters:
            antenna_parameters[param] = self._oantenna.synthesis_parameters.__getattribute__(param).value
        if not synth_only and not self.properties.antenna.is_created:
            if not self._oantenna.object_list:
                if not self._oantenna.name:
                    self._oantenna.name = pyaedt.generate_unique_name(self.antenna_type)
                    self.set_properties({"name": self._oantenna.name})
                self._oantenna.init_model()
                self._oantenna.model_hfss()
                self._oantenna.setup_hfss()
                self.properties.antenna.is_created = True
            if self.properties.antenna.setup.lattice_pair:
                self._oantenna.create_lattice_pair()
            if self.properties.antenna.setup.component_3d:
                self._oantenna.create_3dcomponent(replace=True)
            if self.properties.create_setup:
                freq = float(self._oantenna.frequency)
                setup = self.aedtapp.create_setup()
                setup.props["Frequency"] = str(freq) + freq_units
                if int(self.properties.sweep) > 0:
                    sweep1 = setup.add_sweep()
                    perc_sweep = (int(self.properties.sweep)) / 100
                    sweep1.props["RangeStart"] = str(freq * (1 - perc_sweep)) + freq_units
                    sweep1.props["RangeEnd"] = str(freq * (1 + perc_sweep)) + freq_units
                    sweep1.update()
        elif synth_only:
            self._oantenna = None

        if self.aedtapp:
            self.aedtapp.save_project()

        self.properties.antenna.parameters = antenna_parameters
        self.release_aedt(False, False)
        return antenna_parameters

    def export_hfss_model(self):
        """Export model in the OBJ format.

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
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> import time
        >>> toolkit = Toolkit()
        >>> msg1 = toolkit.launch_aedt()
        >>> response = toolkit.get_thread_status()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> msg3 = toolkit.get_antenna("BowTie")
        """

        if not self._oantenna:
            logger.debug("No antenna is available.")
            return False

        # PyVista check
        # model = ModelPlotter()
        # for file in files:
        #     model.add_object(file[0], file[1],file[2])

        # Export different solid
        files = self.aedtapp.post.export_model_obj(export_as_single_objects=True)

        return files

    def update_parameters(self, key, val):
        """Update parameters in HFSS.

        Parameters
        ----------
        key : str
            Key.
        val : float
            Value.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
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
        if not self.properties.antenna.parameters_hfss:
            logger.debug("Antenna was not created in HFSS.")
            return True

        if not self.aedtapp:
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design is not connected.")
                return False

        if (
            self.aedtapp
            and key in self.properties.antenna.parameters_hfss
            and self.properties.antenna.parameters_hfss[key] in self.aedtapp.variable_manager.independent_variable_names
        ):
            ratio_re = re.compile("|".join(["ratio", "coefficient", "points", "number"]))
            if "angle" in key:
                if "deg" not in val:
                    val = val + "deg"
            elif ratio_re.search(key):
                val = val
            else:
                if self.properties.antenna.synthesis.length_unit not in val:
                    val = val + self.properties.antenna.synthesis.length_unit
            hfss_parameter = self.properties.antenna.parameters_hfss[key]
            self.aedtapp[hfss_parameter] = val

            new_value = self.properties.antenna.parameters
            new_value[key] = val
            # self.set_properties({"parameters": new_value})

            return True
        else:
            logger.debug("Parameter does not exist.")
            return False

    def analyze(self):
        """Analyze the design.

        Launch analysis in batch. AEDT is released once it is opened.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
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
                logger.debug("Selected design must be HFSS.")
                return False
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design is not connected.")
                return False

        num_cores = properties.core_number

        self.aedtapp.save_project()
        time.sleep(1)
        self.aedtapp.solve_in_batch(run_in_thread=True, machine="localhost", num_cores=num_cores)
        self.release_aedt(False, False)
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
                logger.debug("Selected design must be HFSS.")
                return False
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design is not connected.")
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
                logger.debug("Selected design must be HFSS.")
                return False
            # Connect to AEDT design
            self.connect_design("Hfss")
            if not self.aedtapp:
                logger.debug("HFSS design is not connected.")
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
