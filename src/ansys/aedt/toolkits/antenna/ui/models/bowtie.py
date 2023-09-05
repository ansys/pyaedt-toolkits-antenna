import os

import requests

from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger


class BowTie(object):
    """Manages UI bowtie antenna."""

    def __init__(self):
        self.antenna_template = None
        pass

    def draw_bowtie_normal_ui(self):
        """Create a normal bowtie antenna."""
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
        self.antenna_template = "BowTie"

        self._add_header("Bowtie", "10")

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
        image = self._add_image(os.path.join(self.images_path, "Bowtie.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("BowTie template loaded")

    def draw_bowtie_rounded_ui(self):
        """Create a rounded bowtie antenna."""
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
        self.antenna_template = "BowTieRounded"

        self._add_header("Rounded_Bowtie", "10")

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
        image = self._add_image(os.path.join(self.images_path, "BowtieRounded.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Bowtie rounded template loaded")

    def draw_bowtie_slot_ui(self):
        """Create a slot bowtie antenna."""
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
        self.antenna_template = "BowTieSlot"

        self._add_header("Slot_Bowtie", "10")

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
        image = self._add_image(os.path.join(self.images_path, "BowtieSlot.jpg"))
        self.image_layout.addLayout(image, 0, 0, 1, 1)

        self.write_log_line("Bowtie rounded template loaded")
