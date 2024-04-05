import os

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger
from ansys.aedt.toolkits.antenna.ui.common.properties import be_properties
from ansys.aedt.toolkits.antenna.ui.models.frontend_api import ToolkitFrontend


class Horn(ToolkitFrontend):
    """Manages UI bowtie antenna."""

    def __init__(self):
        ToolkitFrontend.__init__(self)
        self.antenna_template = None
        pass

    def draw_conical_corrugated_ui(self):
        """Create a conical corrugated horn antenna."""
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
        self.antenna_template = "Corrugated"

        self._add_header("Corrugated", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornConicalCorrugated.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Conical Corrugated horn template loaded")

    def draw_conical_ui(self):
        """Create a conical horn antenna."""
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
        self.antenna_template = "Conical"

        self._add_header("Conical", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornConical.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Conical horn template loaded")

    def draw_eplane_ui(self):
        """Create a E-plane horn antenna."""
        if self.is_backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.get_properties()

        if properties.antenna_created:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        # Update antenna type
        self.antenna_template = "EPlane"

        self._add_header("EPlane", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornEPlane.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("E-Plane horn template loaded")

    def draw_elliptical_ui(self):
        """Create a Elliptical horn antenna."""
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
        self.antenna_template = "Elliptical"

        self._add_header("Elliptical", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornElliptical.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Elliptical horn template loaded")

    def draw_hplane_ui(self):
        """Create a H-plane horn antenna."""
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
        self.antenna_template = "HPlane"

        self._add_header("HPlane", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornHPlane.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("H-Plane horn template loaded")

    def draw_pyramidal_ui(self):
        """Create a Pyramidal horn antenna."""
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
        self.antenna_template = "Pyramidal"

        self._add_header("Pyramidal", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornPyramidal.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Pyramidal horn template loaded")

    def draw_pyramidal_ridged_ui(self):
        """Create a Pyramidal ridged horn antenna."""
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
        self.antenna_template = "PyramidalRidged"

        self._add_header("PyramidalRidged", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornPyramidalRidged.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Pyramidal Ridged horn template loaded")

    def draw_quad_ridged_ui(self):
        """Create a quad-ridged horn antenna."""
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
        self.antenna_template = "QuadRidged"

        self._add_header("QuadRidged", "10")

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "HornQuadRidged.png"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Quad-ridged horn template loaded")
