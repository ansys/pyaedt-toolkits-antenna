import os

import requests

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger


class Monopole(object):
    """Manages UI misc antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_blade_ui(self):
        """Create a blade antenna."""
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
        self.antenna_template = "Blade"

        self._add_header("Blade", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "Blade_Antenna.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_circular_disc_ui(self):
        """Create circular disc antenna."""
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
        self.antenna_template = "CircularDisc"

        self._add_header("CircularDisc", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "CircularDiscMonopole.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_elliptical_strip_ui(self):
        """Create elliptical strip antenna."""
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
        self.antenna_template = "EllipticalBaseStrip"

        self._add_header("EllipticalBaseStrip", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "EllipticalBaseStripMonopole.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_vertical_trapezoidal_ui(self):
        """Create vertical trapezoidal antenna."""
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
        self.antenna_template = "VerticalTrapezoidal"

        self._add_header("VerticalTrapezoidal", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "VerticalTrapezoidalMonopole.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_wire_ui(self):
        """Create wire monopole antenna."""
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
        self.antenna_template = "WireMonopole"

        self._add_header("WireMonopole", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "WireMonopole.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_wire_infinite_ui(self):
        """Create wire monopole with infinite ground antenna."""
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
        self.antenna_template = "WireMonopoleInfGnd"

        self._add_header("WireMonopole", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "WireMonopole_InfGnd.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)
