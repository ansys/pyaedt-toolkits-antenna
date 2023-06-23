from ansys.aedt.toolkits.antennas.backend import models
from ansys.aedt.toolkits.antennas.backend.common.api_generic import ToolkitGeneric
from ansys.aedt.toolkits.antennas.backend.common.logger_handler import logger
from ansys.aedt.toolkits.antennas.backend.common.properties import properties


class Toolkit(ToolkitGeneric):
    """API to control the toolkit workflow.

    This class provides methods to synthesize and create antennas.

    Examples
    --------
    >>> from ansys.aedt.toolkits.antennas.backend.api import Toolkit
    >>> import time
    >>> service = Toolkit()
    >>> msg1 = service.launch_aedt()
    >>> response = service.get_thread_status()
    >>> while response[0] == 0:
    >>>     time.sleep(1)
    >>>     response = service.get_thread_status()
    >>> service.get_antenna("BowTie")
    """

    def __init__(self):
        ToolkitGeneric.__init__(self)
        self.oantenna = None
        self.antennas = []
        self.antenna_names = []

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
        >>> service = Toolkit()
        >>> msg1 = service.launch_aedt()
        >>> response = service.get_thread_status()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = service.get_thread_status()
        >>> msg3 = service.get_antenna("BowTie")
        """

        if not self.aedtapp:
            # Connect to AEDT design
            self.connect_design("Hfss")

        if not self.aedtapp:
            logger.debug("HFSS design not connected")
            return False

        if self.oantenna:
            logger.debug("Antenna is already created")
            return False

        freq_units = properties.frequency_unit

        antenna_module = getattr(models, antenna)

        self.oantenna = antenna_module(
            self.aedtapp,
            frequency_unit=freq_units,
            length_unit=properties.length_unit,
        )

        # Origin
        x_pos = float(properties.origin[0])
        y_pos = float(properties.origin[0])
        z_pos = float(properties.origin[0])
        self.oantenna.origin = [x_pos, y_pos, z_pos]

        if ["start_frequency", "stop_frequency"] in self.oantenna.__dir__():
            if self.oantenna.start_frequency != 0.0 and self.oantenna.stop_frequency != 0.0:
                properties.start_frequency = self.oantenna.start_frequency
                properties.stop_frequency = self.oantenna.stop_frequency
            else:
                properties.frequency = self.oantenna.frequency
        else:
            properties.frequency = self.oantenna.frequency

        self.oantenna.outer_boundary = properties.outer_boundary

        self.oantenna._parameters = self.oantenna._synthesis()

        # Update properties
        oantenna_public_props = (name for name in self.oantenna.__dir__() if not name.startswith("_"))
        for antenna_prop in oantenna_public_props:
            if antenna_prop in properties.__dir__():
                setattr(properties, antenna_prop, getattr(self.oantenna, antenna_prop))

        if not synth_only:
            if not self.oantenna.object_list:
                self.oantenna.init_model()
                self.oantenna.model_hfss()
                self.oantenna.setup_hfss()
            if properties.component_3d:
                self.oantenna.create_3dcomponent(replace=True)
            if properties.create_setup:
                freq = float(self.oantenna.frequency)
                setup = self.aedtapp.create_setup()
                setup.props["Frequency"] = str(freq) + freq_units
                if int(properties.sweep.value()) > 0:
                    sweep1 = setup.add_sweep()
                    perc_sweep = (int(properties.sweep.value())) / 100
                    sweep1.props["RangeStart"] = str(freq * (1 - perc_sweep)) + freq_units
                    sweep1.props["RangeEnd"] = str(freq * (1 + perc_sweep)) + freq_units
                    sweep1.update()

        return True
