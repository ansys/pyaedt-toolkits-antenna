from ansys.aedt.toolkits.antennas.ui.common.logger_handler import logger


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

        # Update antenna type
        self.antenna_template = "BowTie"

        self._add_header("Bowtie.jpg", "Bowtie", "10")

        line2 = self._add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            list(self.default_materials.keys()),
        )
        self.antenna_settings_layout.addLayout(line2, 6, 0, 1, 1)

        line4 = self._add_line("line_4", "substrate_height", "Substrate height", "edit", "1.575")
        self.antenna_settings_layout.addLayout(line4, 7, 0, 1, 1)
        self._add_footer(self.get_antenna)
        self.write_log_line("BowTie template loaded")
