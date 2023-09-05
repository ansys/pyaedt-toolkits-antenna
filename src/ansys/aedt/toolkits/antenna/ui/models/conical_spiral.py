import os

import requests

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger


class ConicalSpiral(object):
    """Manages UI patch antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_archimidean_conical_ui(self):
        """Create a conical archimidean spiral antenna."""
        if self.backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        if "frequency" in self.__dir__():
            self.frequency.setText("0")

        properties_request = requests.get(self.url + "/get_properties")
        properties = properties_request.json()
        if properties["antenna_created"]:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        # Update antenna type
        self.antenna_template = "Archimedean"

        self._add_header("Conical_Archimedean_Spiral", ["4", "10"])

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "ConicalArchimedean.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Conical Archimidean spiral template loaded")

    def draw_log_conical_ui(self):
        """Create a conical log spiral antenna."""
        if self.backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        if "frequency" in self.__dir__():
            self.frequency.setText("0")

        properties_request = requests.get(self.url + "/get_properties")
        properties = properties_request.json()
        if properties["antenna_created"]:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        # Update antenna type
        self.antenna_template = "Log"

        self._add_header("Conical_Log_Spiral", ["4", "10"])

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "ConicalLog.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Conical Log spiral template loaded")

    def draw_sinuous_conical_ui(self):
        """Create a conical sinuous spiral antenna."""
        if self.backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        if "frequency" in self.__dir__():
            self.frequency.setText("0")

        properties_request = requests.get(self.url + "/get_properties")
        properties = properties_request.json()
        if properties["antenna_created"]:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        # Update antenna type
        self.antenna_template = "Sinuous"

        self._add_header("Conical_Sinuous_Spiral", ["4", "10"])

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "ConicalSinuous.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Conical Sinuous spiral template loaded")
