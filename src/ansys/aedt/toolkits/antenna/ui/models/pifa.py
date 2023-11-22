import os

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger
from ansys.aedt.toolkits.antenna.ui.common.properties import be_properties
from ansys.aedt.toolkits.antenna.ui.models.frontend_api import ToolkitFrontend


class PIFA(ToolkitFrontend):
    """Manages UI PIFA antenna."""

    def __init__(self):
        ToolkitFrontend.__init__(self)
        self.antenna_template = None
        pass

    def draw_shorting_pin_ui(self):
        """Create a shorting pin PIFA antenna."""
        if self.is_backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.get_properties()

        if be_properties.antenna_created:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        # Update antenna type
        self.antenna_template = "ShortingPin"

        self._add_header("ShortingPin", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "ShortingPin.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_shorting_plate_ui(self):
        """Create a shorting plate PIFA antenna."""
        if self.is_backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.get_properties()

        if be_properties.antenna_created:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        # Update antenna type
        self.antenna_template = "ShortingPlate"

        self._add_header("ShortingPlate", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "ShortingPlate.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_planar_inverted_ui(self):
        """Create a planar inverted PIFA antenna."""
        if self.is_backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.get_properties()

        if be_properties.antenna_created:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        # Update antenna type
        self.antenna_template = "PlanarInverted"

        self._add_header("PlanarInverted", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "PlanarInvertedF.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)
