from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget

from ansys.aedt.toolkits.antenna.ui.windows.help.help_column import Ui_LeftColumn
from ansys.aedt.toolkits.antenna.ui.windows.help.help_page import Ui_help

import tempfile
from ansys.aedt.toolkits.antenna import __version__

DOCUMENTATION_URL = "https://aedt.antenna.toolkit.docs.pyansys.com/"
ISSUE_TRACKER_URL = "https://github.com/ansys/pyaedt-toolkits-antenna/issues"
ABOUT_TEXT = f"""<h2>Antenna Toolkit {__version__}</h2>
<p>Project using <a href='https://wiki.qt.io/Qt_for_Python'> PySide6</a>, Copyright 2024 The Qt Company Ltd.</p>
<p>The graphical user interface (GUI) components are licensed under <a href='https://www.gnu.org/licenses/lgpl-3.0.en.html'>LGPL v3.0</a>.</p> 
<p>Except for the GUI components, your use of this software is governed by the MIT License. In addition, this package allows you to access a software that is licensed under separate terms ("Separately Licensed Software"). If you choose to install such Separately Licensed Software, you acknowledge that you are responsible for complying with any associated terms and conditions.</p>
<p>Copyright 2023 - 2024 ANSYS, Inc. All rights reserved.</p>
<p>If you have any questions or issues, please open an issue in <a href='{ISSUE_TRACKER_URL}'>pyaedt-toolkits-antenna Issues</a> page.</p>
<p>Alternatively, you can contact us at <a href='mailto:pyansys.core@ansys.com'>pyansys.core@ansys.com</a>.</p>
"""


class HelpMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui
        self.temp_folder = tempfile.mkdtemp()

        # Add page
        help_menu_index = self.ui.add_page(Ui_help)
        self.ui.load_pages.pages.setCurrentIndex(help_menu_index)
        self.help_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.help_column_widget = new_column_widget
        self.help_column_vertical_layout = new_ui.help_vertical_layout

        # Specific properties
        self.help_label = self.help_menu_widget.findChild(QLabel, "help_label")
        self.help_grid = self.help_menu_widget.findChild(QGridLayout, "help_grid")

        self.help_button_layout = None
        self.help_button = None
        self.online_documentation_button = None
        self.issue_tracker_button = None

    def setup(self):
        # Modify theme
        app_color = self.main_window.ui.themes["app_color"]
        text_color = app_color["text_active"]
        background = app_color["dark_three"]

        # Label button
        help_label_style = """
        QLabel {{
        color: {_color};
        font-size: {_font_size}pt;
        font-weight: bold;
        }}
        """
        custom_style = help_label_style.format(
            _color=text_color, _bg_color=background, _font_size=self.main_window.properties.font["title_size"]
        )
        self.help_label.setStyleSheet(custom_style)

        # Set column

        # About button
        row_returns = self.ui.add_n_buttons(
            self.help_column_vertical_layout, num_buttons=1,
            height=40,
            width=[200],
            text=["About"],
            font_size=self.main_window.properties.font["title_size"]
        )
        self.help_button_layout = row_returns[0]
        self.help_button = row_returns[1]
        self.help_button_layout.addWidget(self.help_button)
        self.help_button.clicked.connect(self.about_button_clicked)

        # Documentation button
        row_returns = self.ui.add_n_buttons(
            self.help_column_vertical_layout, num_buttons=1,
            height=40,
            width=[200],
            text=["Documentation website"],
            font_size=self.main_window.properties.font["title_size"]
        )
        self.help_button_layout = row_returns[0]
        self.online_documentation_button = row_returns[1]
        self.help_button_layout.addWidget(self.online_documentation_button)
        self.online_documentation_button.clicked.connect(self.visit_website)

        # Issue tracker button
        row_returns = self.ui.add_n_buttons(
            self.help_column_vertical_layout, num_buttons=1,
            height=40,
            width=[200],
            text=["Issue tracker"],
            font_size=self.main_window.properties.font["title_size"]
        )

        self.help_button_layout = row_returns[0]
        self.issue_tracker_button = row_returns[1]
        self.help_button_layout.addWidget(self.issue_tracker_button)
        self.issue_tracker_button.clicked.connect(self.report_issue)

    def about_button_clicked(self):
        """Display the PyAEDT Antenna Toolkit 'About' information."""

        mbox = QtWidgets.QMessageBox.about(self.main_window, "About", ABOUT_TEXT)

    def visit_website(self):
        """Access the PyAEDT Antenna Toolkit documentation."""
        url = QtCore.QUrl(DOCUMENTATION_URL)
        QtGui.QDesktopServices.openUrl(url)

    def report_issue(self):
        """Access the PyAEDT Antenna Toolkit issues tracker."""
        url = QtCore.QUrl(ISSUE_TRACKER_URL)
        QtGui.QDesktopServices.openUrl(url)
