import os

import requests

from ansys.aedt.toolkits.antennas.ui.common.logger_handler import logger


class Patch(object):
    """Manages UI patch antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_elliptical_edge_ui(self):
        """Create an elliptical patch antenna with edge probe."""
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
        self.antenna_template = "EllipticalPatchEdge"

        self._add_header("Elliptical_Patch_Edge", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "EllipticalEdge.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        # self.write_log_line("Elliptical template loaded")
        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_elliptical_inset_ui(self):
        """Create a elliptical patch antenna with inset fed."""
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
        self.antenna_template = "EllipticalPatchInset"

        self._add_header("Elliptical_Patch_Inset", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "EllipticalInset.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        # self.write_log_line("Elliptical template loaded")
        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_elliptical_probe_ui(self):
        """Create a elliptical patch antenna with probe."""
        if self.backend_busy():
            msg = "Toolkit running"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        self.property_table.clear()
        self.property_table.setRowCount(0)

        properties_request = requests.get(self.url + "/get_properties")
        properties = properties_request.json()
        if properties["antenna_created"]:
            msg = "Antenna is already created, please open the antenna wizard again to create a new antenna"
            logger.debug(msg)
            self.write_log_line(msg)
            return

        # Update antenna type
        self.antenna_template = "EllipticalPatchProbe"

        self._add_header("Elliptical_Patch_Probe", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "EllipticalProbe.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        # self.write_log_line("Elliptical template loaded")
        msg = "Antenna not implemented"
        logger.debug(msg)
        self.write_log_line(msg)

    def draw_rectangular_edge_ui(self):
        """Create a rectangular patch antenna with edge probe."""
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
        self.antenna_template = "RectangularPatchEdge"

        self._add_header("Rectangular_Patch_Edge", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "RectEdge.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Rectangular patch edge template loaded")

    def draw_rectangular_inset_ui(self):
        """Create a rectangular patch antenna with edge probe."""
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
        self.antenna_template = "RectangularPatchInset"

        self._add_header("Rectangular_Patch_Inset", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "RectInset.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Rectangular patch inset template loaded")

    def draw_rectangular_probe_ui(self):
        """Create a rectangular patch antenna with edge probe."""
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
        self.antenna_template = "RectangularPatchProbe"

        self._add_header("Rectangular_Patch_Probe", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 6, 0, 1, 1)

        self._add_footer(self.get_antenna)

        # Add image
        image = self._add_image(os.path.join(self.images_path, "RectProbe.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Rectangular patch inset template loaded")
