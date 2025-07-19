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

import gc
import os.path
from pathlib import Path
import re
import sys

# isort: off
sys.path.append(str(Path(__file__).parent))
from ansys.aedt.toolkits.antenna.backend.models import properties

# isort: on

from ansys.aedt.core import generate_unique_name
from ansys.aedt.core.visualization.advanced.touchstone_parser import find_touchstone_files
from ansys.aedt.toolkits.common.backend.api import AEDTCommon
from ansys.aedt.toolkits.common.backend.logger_handler import logger

from ansys.aedt.toolkits.antenna.backend import antenna_models


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
        self.oantenna = None
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
        >>> from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
        >>> import time
        >>> toolkit = ToolkitBackend()
        >>> msg1 = toolkit_api.launch_thread(toolkit.launch_aedt)
        >>> idle = toolkit_api.wait_to_be_idle()
        >>> toolkit.get_antenna("BowTie")
        """

        if self.oantenna:
            logger.debug("Antenna is already created.")
            return False

        if antenna not in antenna_models.__dir__():
            logger.debug("Antenna is not implemented.")
            return False

        if not synth_only and not self.aedtapp:
            if not self.properties.active_design:
                logger.debug("Not active design.")
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
        self.oantenna = antenna_module(
            self.aedtapp,
            frequency_unit=freq_units,
            length_unit=self.properties.antenna.synthesis.length_unit,
        )

        # Update antenna properties
        for antenna_prop in self.properties.antenna.synthesis.model_fields:
            if (
                antenna_prop == "frequency"
                and "start_frequency" in self.oantenna.__dir__()
                and "stop_frequency" in self.oantenna.__dir__()
            ):
                pass
            elif antenna_prop == "material_properties":
                if self.properties.antenna.synthesis.material_properties:
                    self.oantenna.material_properties["permittivity"] = (
                        self.properties.antenna.synthesis.material_properties["permittivity"]
                    )
            elif getattr(self.properties.antenna.synthesis, antenna_prop):
                setattr(self.oantenna, antenna_prop, getattr(self.properties.antenna.synthesis, antenna_prop))

        self.oantenna._parameters = self.oantenna.synthesis()
        self.oantenna.update_synthesis_parameters(self.oantenna._parameters)

        antenna_parameters = {}

        oantenna_public_parameters = (
            name for name in self.oantenna.synthesis_parameters.__dict__ if not name.startswith("_")
        )
        for param in oantenna_public_parameters:
            antenna_parameters[param] = self.oantenna.synthesis_parameters.__getattribute__(param).value
        if not synth_only and not self.properties.antenna.is_created:
            if not self.oantenna.object_list:
                if not self.oantenna.name:
                    self.oantenna.name = generate_unique_name(self.antenna_type)
                    self.set_properties({"name": self.oantenna.name})
                self.oantenna.init_model()
                self.oantenna.model_hfss()
                self.oantenna.setup_hfss()
                self.properties.antenna.is_created = True
            if self.properties.antenna.setup.lattice_pair:
                self.oantenna.create_lattice_pair()
            if self.properties.antenna.setup.component_3d:
                self.oantenna.create_3dcomponent(replace=True)
            if self.properties.antenna.setup.create_setup:
                freq = float(self.oantenna.frequency)
                setup = self.aedtapp.create_setup()
                setup.props["Frequency"] = str(freq) + freq_units
                if int(self.properties.antenna.setup.sweep) > 0:
                    sweep1 = setup.add_sweep()
                    perc_sweep = (int(self.properties.antenna.setup.sweep)) / 100
                    sweep1.props["RangeStart"] = str(freq * (1 - perc_sweep)) + freq_units
                    sweep1.props["RangeEnd"] = str(freq * (1 + perc_sweep)) + freq_units
                    sweep1.update()
        elif synth_only:
            self.oantenna = None

        if self.aedtapp:
            self.aedtapp.save_project()

        self.properties.antenna.parameters = antenna_parameters
        self.release_aedt(False, False)
        return antenna_parameters

    def update_hfss_parameters(self, key: str, val: str) -> bool:
        """Update parameters in HFSS.

        Parameters
        ----------
        key : str
            Key.
        val : str
            Value.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
        >>> import time
        >>> toolkit = ToolkitBackend()
        >>> msg1 = toolkit_api.launch_thread(toolkit.launch_aedt)
        >>> idle = toolkit_api.wait_to_be_idle()
        >>> toolkit.get_antenna("BowTie")
        >>> msg3 = toolkit.update_hfss_parameters()
        """
        if not self.properties.antenna.parameters_hfss:  # pragma: no cover
            logger.debug("Antenna was not created in HFSS.")
            return True

        if not self.aedtapp:
            # Connect to AEDT design
            self.connect_design()
            if not self.aedtapp:  # pragma: no cover
                logger.debug("HFSS design is not connected.")
                return False

        if (
            self.aedtapp
            and key in self.properties.antenna.parameters_hfss
            and self.properties.antenna.parameters_hfss[key] in self.aedtapp.variable_manager.independent_variable_names
        ):
            ratio_re = re.compile("|".join(["ratio", "coefficient", "points", "number"]))
            if "angle" in key:  # pragma: no cover
                if "deg" not in val:
                    val = val + "deg"
            elif ratio_re.search(key):  # pragma: no cover
                val = val
            else:
                if self.properties.antenna.synthesis.length_unit not in val:
                    val = val + self.properties.antenna.synthesis.length_unit
            hfss_parameter = self.properties.antenna.parameters_hfss[key]
            self.aedtapp[hfss_parameter] = val

            new_value = self.properties.antenna.parameters
            new_value[key] = val
            self.release_aedt(False, False)
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
        >>> from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
        >>> toolkit = ToolkitBackend()
        >>> msg1 = toolkit_api.launch_thread(toolkit.launch_aedt)
        >>> idle = toolkit_api.wait_to_be_idle()
        >>> toolkit.get_antenna("BowTie")
        >>> toolkit.analyze()
        """
        if not self.aedtapp:
            # Connect to AEDT design
            self.connect_design()
            if not self.aedtapp:  # pragma: no cover
                logger.debug("HFSS design is not connected.")
                return False

        num_cores = properties.antenna.setup.num_cores

        self.aedtapp.save_project()

        self.aedtapp.analyze(cores=num_cores)

        gc.collect()
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
            # Connect to AEDT design
            self.connect_design()
            if not self.aedtapp:  # pragma: no cover
                logger.debug("HFSS design is not connected.")
                return False

        sol_data = self.aedtapp.post.get_solution_data()

        self.release_aedt(False, False)

        if not sol_data:  # pragma: no cover
            return
        return sol_data.primary_sweep_values, sol_data.data_db20()

    def export_farfield(self, frequencies=None, setup=None, sphere=None, variations=None, encode=True):
        """Export far field data and then encode the file if the ``encode`` parameter is enabled.

        Parameters
        ----------
        frequencies : float, list
            Frequency value or list of frequencies to compute far field data. The default is ``None,`` in which case
            all available frequencies are computed.
        setup : str, optional
            Name of the setup to use. The default is ``None,`` in which case ``nominal_adaptive`` is used.
        sphere : str, optional
            Infinite sphere to use. The default is ``None``, in which case an existing sphere is used or a new
            one is created.
        variations : dict, optional
            Variation dictionary.
        encode : bool, optional
            Whether to encode the file. The default is ``True``.

        Returns
        -------
        list or dict
            List of eep files or encoded data.
        """
        if not self.aedtapp:
            self.connect_design()

        if self.aedtapp:
            self.aedtapp.save_project()

            farfield_exporter = self.aedtapp.get_antenna_data(
                frequencies=frequencies, setup=setup, sphere=sphere, variations=variations
            )

            if encode:
                encoded_json_file = None
                encoded_geometry_files = []
                encoded_ffd_files = []
                encoded_scattering_file = None

                metadata_file = farfield_exporter.metadata_file
                metadata_dir = os.path.dirname(metadata_file)

                if os.path.isfile(metadata_file):
                    serialized_file = self.serialize_obj_base64(metadata_file)
                    encoded_json_file = serialized_file.decode("utf-8")

                geometry_path = os.path.abspath(os.path.join(metadata_dir, "geometry"))
                if os.path.exists(geometry_path):
                    for root, _, files in os.walk(geometry_path):
                        for file in files:
                            if file.lower().endswith(".obj"):
                                geometry_file = os.path.abspath(os.path.join(root, file))
                                serialized_file = self.serialize_obj_base64(geometry_file)
                                encoded_geometry_files.append(serialized_file.decode("utf-8"))

                    for root, _, files in os.walk(metadata_dir):
                        for file in files:
                            if file.lower().endswith(".ffd"):
                                ffd_file = os.path.abspath(os.path.join(root, file))
                                serialized_file = self.serialize_obj_base64(ffd_file)
                                encoded_ffd_files.append(serialized_file.decode("utf-8"))

                    sNp_files = find_touchstone_files(metadata_dir)

                    if sNp_files:
                        snP_file = list(sNp_files.keys())[0]
                        serialized_file = self.serialize_obj_base64(sNp_files[snP_file])
                        encoded_scattering_file = serialized_file.decode("utf-8")

                    self.release_aedt(False, False)

                    return encoded_json_file, encoded_geometry_files, encoded_ffd_files, encoded_scattering_file

            self.release_aedt(False, False)
            return farfield_exporter.metadata_file, farfield_exporter.frequencies
