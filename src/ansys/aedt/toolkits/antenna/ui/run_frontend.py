# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys

# isort: off

# Default user interface properties
from ansys.aedt.toolkits.antenna.ui.models import properties

# isort: on

# PySide6 Widgets
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow

# Toolkit frontend API
from actions import Frontend
from ansys.aedt.toolkits.common.ui.common_windows.home_menu import HomeMenu
from ansys.aedt.toolkits.common.ui.common_windows.settings_column import SettingsMenu

# Import general common frontend modules
from ansys.aedt.toolkits.common.ui.logger_handler import logger

# Common windows
from ansys.aedt.toolkits.common.ui.main_window.main_window_layout import MainWindowLayout

# New windows
from windows.antenna_catalog.antenna_catalog_menu import AntennaCatalogMenu
from windows.antenna_results.antenna_results_menu import AntennaResultsMenu
from windows.antenna_synthesis.antenna_synthesis_menu import AntennaSynthesisMenu
from windows.help.help_menu import HelpMenu

# Windows


# Backend URL and port
if len(sys.argv) == 3:
    properties.backend_url = sys.argv[1]
    properties.backend_port = int(sys.argv[2])

url = properties.backend_url
port = properties.backend_port

os.environ["QT_API"] = "pyside6"
os.environ["QT_FONT_DPI"] = "96"

if properties.high_resolution or os.environ.get("AEDT_TOOLKIT_HIGH_RESOLUTION") == "True":
    os.environ["QT_SCALE_FACTOR"] = "2"


class ApplicationWindow(QMainWindow, Frontend):
    def __init__(self):
        super().__init__()

        self.thread = None
        self.properties = properties

        # General Settings

        # Create main window layout
        self.ui = MainWindowLayout(self)
        self.ui.setup()

        # Settings menu
        self.settings_menu = SettingsMenu(self)
        self.settings_menu.setup()

        # Check backend connection
        success = self.check_connection()

        # Populate settings column
        if not success:
            msg = "Error getting properties from backend. User interface running without backend"
            self.ui.update_logger(msg)
            logger.error(msg)
            self.settings_menu.signal_flag = False
            self.settings_menu.aedt_version.addItem("Backend OFF")
            self.settings_menu.aedt_session.addItem("Backend OFF")
        else:
            # Get default properties
            be_properties = self.get_properties()
            # Get AEDT installed versions
            installed_versions = self.installed_versions()

            self.settings_menu.aedt_session.clear()
            self.settings_menu.aedt_session.addItem("New Session")
            if installed_versions:
                self.settings_menu.connect_aedt.setEnabled(True)
                for ver in installed_versions:
                    self.settings_menu.aedt_version.addItem(ver)
            else:
                self.settings_menu.aedt_version.addItem("AEDT not installed")

            if be_properties.get("aedt_version") in installed_versions:
                self.settings_menu.aedt_version.setCurrentText(be_properties.get("aedt_version"))

        # Custom toolkit setup starts here
        # Home menu
        self.home_menu = HomeMenu(self)
        self.home_menu.setup()

        # Modeler menu
        self.antenna_catalog_menu = AntennaCatalogMenu(self)
        self.antenna_catalog_menu.setup()
        self.ui.left_menu.clicked.connect(self.antenna_catalog_menu_clicked)

        # Synthesis menu
        self.antenna_synthesis_menu = AntennaSynthesisMenu(self)
        self.antenna_synthesis_menu.setup()
        self.ui.left_menu.clicked.connect(self.antenna_synthesis_menu_clicked)

        # Results menu
        self.antenna_results_menu = AntennaResultsMenu(self)
        self.antenna_results_menu.setup()
        self.ui.left_menu.clicked.connect(self.antenna_results_menu_clicked)

        # Help menu
        self.help_menu = HelpMenu(self)
        self.help_menu.setup()
        self.ui.left_menu.clicked.connect(self.help_menu_clicked)

        # Home page as first page
        self.ui.set_page(self.ui.load_pages.home_page)

    def antenna_catalog_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()

        if menu_name == "antenna_catalog_menu":
            selected_menu.set_active(True)

            is_left_visible = self.ui.is_left_column_visible()

            self.ui.set_left_column_menu(
                menu=self.antenna_catalog_menu.antenna_catalog_column_widget,
                title=properties.add_left_menus[1]["btn_text"],
                icon_path=self.ui.images_load.icon_path(properties.add_left_menus[1]["btn_icon"]),
            )

            if not is_left_visible:
                self.ui.toggle_left_column()

    def antenna_synthesis_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()

        if menu_name == "antenna_synthesis_menu":
            selected_menu.set_active(True)
            self.ui.set_page(self.antenna_synthesis_menu.antenna_synthesis_menu_widget)

    def antenna_results_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()

        if menu_name == "antenna_results_menu":
            selected_menu.set_active(True)
            self.ui.set_page(self.antenna_results_menu.antenna_results_menu_widget)
            is_left_visible = self.ui.is_left_column_visible()

            self.ui.set_left_column_menu(
                menu=self.antenna_results_menu.antenna_results_column_widget,
                title=properties.add_left_menus[3]["btn_text"],
                icon_path=self.ui.images_load.icon_path(properties.add_left_menus[3]["btn_icon"]),
            )

            if not is_left_visible:
                self.ui.toggle_left_column()

    def help_menu_clicked(self):
        selected_menu = self.ui.get_selected_menu()
        menu_name = selected_menu.objectName()

        if menu_name == "help_menu":
            selected_menu.set_active(True)
            self.ui.set_page(self.help_menu.help_menu_widget)

            # TODO: Update path once help menu is released
            self.ui.set_left_column_menu(
                menu=self.help_menu.help_column_widget,
                title="Help",
                icon_path=self.ui.images_load.icon_path("help.svg"),
            )

            is_left_visible = self.ui.is_left_column_visible()
            if not is_left_visible:
                self.ui.toggle_left_column()

    def closeEvent(self, event):
        if self.antenna_catalog_menu.grid_item:
            for item in self.antenna_catalog_menu.grid_item:
                item.plotter.close()
        # Remove Antenna
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    sys.exit(app.exec())
