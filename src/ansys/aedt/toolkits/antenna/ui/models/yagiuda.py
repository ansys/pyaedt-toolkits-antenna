import os

import requests

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger


class YagiUda(object):
    """Manages UI Yagi-Uda antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_quasi_yagi_ui(self):
        """Create a quasi yagi uda antenna."""
        if self.backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        properties_request = requests.get(self.url + "/get_properties")
        properties = properties_request.json()
        if properties["antenna_created"]:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        # Update antenna type
        self.antenna_template = "QuasiYagiUda"

        self._add_header("QuasiYagiUda", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "Quasi_Yagi.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_wire_ui(self):
        """Create a wire yagi uda antenna."""
        if self.backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        properties_request = requests.get(self.url + "/get_properties")
        properties = properties_request.json()
        if properties["antenna_created"]:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        # Update antenna type
        self.antenna_template = "WireYagiUda"

        self._add_header("WireYagiUda", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "WireYagiUda.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)
