import os

import requests

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger


class Slot(object):
    """Manages UI Slot antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_backed_array_ui(self):
        """Create a backed array antenna."""
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
        self.antenna_template = "SlotBackedArray"

        self._add_header("BackedArray", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "SlotCavityBackedArray.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_backed_t_bar_ui(self):
        """Create a backed T-bar antenna."""
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
        self.antenna_template = "SlotTBar"

        self._add_header("SlotTBar", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "SlotTBar.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_gap_fed_ui(self):
        """Create a gap fed antenna."""
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
        self.antenna_template = "SlotGapFed"

        self._add_header("SlotGapFed", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "SlotGap.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_microstrip_feed_ui(self):
        """Create a microstrip feed slot antenna."""
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
        self.antenna_template = "SlotMicrostrip"

        self._add_header("SlotMicrostrip", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "SlotMicrostrip.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)
