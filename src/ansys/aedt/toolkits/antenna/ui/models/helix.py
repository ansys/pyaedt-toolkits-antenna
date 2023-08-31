import os

import requests

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger


class Helix(object):
    """Manages UI helix antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_axial_mode_ui(self):
        """Create an axial mode helix antenna."""
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
        self.antenna_template = "AxialMode"

        self._add_header("AxialMode", "10")

        line2 = self._add_line(
            "line_2",
            "gain_value",
            "Expected Gain (dB)",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line(
            "line_3",
            "feeder_length",
            "Feeder Length",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "AxialMode.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Axial Mode helix template loaded")

    def draw_axial_mode_continuous_ui(self):
        """Create an axial mode helix antenna."""
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
        self.antenna_template = "AxialModeContinuous"

        self._add_header("AxialModeContinuous", "10")

        line2 = self._add_line(
            "line_2",
            "gain_value",
            "Expected Gain (dB)",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line(
            "line_3",
            "feeder_length",
            "Feeder Length",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "AxialModeTaper.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_axial_normal_mode_ui(self):
        """Create an axial normal mode helix antenna."""
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
        self.antenna_template = "AxialNormalMode"

        self._add_header("AxialNormalMode", "10")

        line2 = self._add_line(
            "line_2",
            "gain_value",
            "Expected Gain (dB)",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line(
            "line_3",
            "feeder_length",
            "Feeder Length",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "NormalMode.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_quadrifilar_open_ui(self):
        """Create an axial normal mode helix antenna."""
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
        self.antenna_template = "QuadrifilarOpen"

        self._add_header("QuadrifilarOpen", "10")

        line2 = self._add_line(
            "line_2",
            "gain_value",
            "Expected Gain (dB)",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line(
            "line_3",
            "feeder_length",
            "Feeder Length",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "QuadrifilarOpen.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_quadrifilar_short_ui(self):
        """Create an axial normal mode helix antenna."""
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
        self.antenna_template = "QuadrifilarShort"

        self._add_header("QuadrifilarShort", "10")

        line2 = self._add_line(
            "line_2",
            "gain_value",
            "Expected Gain (dB)",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line(
            "line_3",
            "feeder_length",
            "Feeder Length",
            "edit",
            "10",
        )
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "QuadrifilarShort.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)
