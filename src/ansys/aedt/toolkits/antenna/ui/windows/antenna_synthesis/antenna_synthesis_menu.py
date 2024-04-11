from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QTableWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from pyvistaqt import BackgroundPlotter
import pyvista as pv

# toolkit PySide6 Widgets
from ansys.aedt.toolkits.common.ui.utils.widgets import PyLabel
from ansys.aedt.toolkits.common.ui.utils.widgets import PyPushButton

from windows.antenna_synthesis.antenna_synthesis_page import Ui_AntennaSynthesis

import os
import sys


# if sys.version_info >= (3, 11):
#     import tomllib
# else:
#     import tomli as tomllib
#
# antenna_catalog = {}
# if os.path.isfile(os.path.join(os.path.dirname(__file__), "antenna_synteh.toml")):
#     with open(os.path.join(os.path.dirname(__file__), "antenna_catalog.toml"), mode="rb") as file_handler:
#         antenna_catalog = tomllib.load(file_handler)


class AntennaSynthesisMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui

        # Add page
        antenna_synthesis_menu_index = self.ui.add_page(Ui_AntennaSynthesis)
        self.ui.load_pages.pages.setCurrentIndex(antenna_synthesis_menu_index)
        self.antenna_synthesis_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Specific properties
        self.antenna_synthesis_layout = self.antenna_synthesis_menu_widget.findChild(QHBoxLayout,
                                                                                     "antenna_synthesis_layout")

        self.antenna_synthesis_left_layout = self.antenna_synthesis_layout.findChild(QVBoxLayout,
                                                                                     "left_settings_layout")

        self.antenna_input = self.antenna_synthesis_left_layout.findChild(QVBoxLayout,
                                                                          "antenna_input")

        self.antenna_synthesis_right_layout = self.antenna_synthesis_layout.findChild(QVBoxLayout,
                                                                                      "right_settings_layout")

        self.top_antenna_options_frame = self.antenna_synthesis_menu_widget.findChild(QFrame,
                                                                                      "top_antenna_options_frame")
        self.top_antenna_options_frame.setFrameShape(QFrame.Box)

        self.top_antenna_settings_layout = self.top_antenna_options_frame.findChild(QHBoxLayout,
                                                                                    "top_antenna_settings_layout")
        self.top_antenna_settings_options_layout = (
            self.top_antenna_settings_layout.findChild(QVBoxLayout, "top_antenna_settings_options_layout"))

        self.component_3d = self.antenna_synthesis_menu_widget.findChild(QCheckBox, "component_3d")
        self.create_setup = self.antenna_synthesis_menu_widget.findChild(QCheckBox, "create_hfss_setup")
        self.lattice_pair = self.antenna_synthesis_menu_widget.findChild(QCheckBox, "lattice_pair")

        self.sweep_layout = self.top_antenna_settings_options_layout.findChild(QHBoxLayout, "sweep_layout")
        self.sweep_value = self.antenna_synthesis_menu_widget.findChild(QLabel, "slider_value")
        self.sweep_slider = self.antenna_synthesis_menu_widget.findChild(QSlider, "sweep_slider")
        self.sweep_label = self.antenna_synthesis_menu_widget.findChild(QLabel, "sweep_label")

        self.bottom_antenna_options_frame = self.antenna_synthesis_menu_widget.findChild(QFrame,
                                                                                      "bottom_antenna_options_frame")

        self.botton_antenna_settings_layout = \
            self.bottom_antenna_options_frame.findChild(QHBoxLayout, "botton_antenna_settings_layout")
        self.bottom_antenna_options_frame.setFrameShape(QFrame.Box)

        self.botton_image_frame = self.bottom_antenna_options_frame.findChild(QFrame, "botton_image_frame")
        self.botton_image_frame.setFrameShape(QFrame.Box)

        self.botton_image_layout = self.botton_image_frame.findChild(QGridLayout, "botton_image_layout")

        self.table_frame = self.bottom_antenna_options_frame.findChild(QFrame, "table_frame")

        self.table_layout = self.table_frame.findChild(QVBoxLayout, "table_layout")

        self.parameter_table = None

        self.image_layout = None
        self.antenna_button_layout = None
        self.synthesis_button = None
        self.create_antenna_button = None

    def setup(self):
        # Modify theme
        app_color = self.main_window.ui.themes["app_color"]

        widge_style = """
        background-color: {_bg_color};
        color: {_color};
        """

        custom_style = widge_style.format(_bg_color=app_color["dark_three"],
                                          _color=app_color["text_foreground"])

        self.antenna_synthesis_menu_widget.setStyleSheet(custom_style)

        # Add table
        self.parameter_table = QTableWidget(0, 2)  # 0 initial rows, 2 columns
        self.parameter_table.setObjectName("parameter_table")  # Set object name

        self.parameter_table.setHorizontalHeaderLabels(["Parameter", "Value"])

        header = self.parameter_table.horizontalHeader()
        custom_style = """
        QHeaderView::section {{
        background-color: {_bg_color};
        color: {_color};
        }}
        """

        table_header_style = custom_style.format(_bg_color=app_color["dark_three"],
                                                 _color=app_color["text_foreground"])

        header.setStyleSheet(table_header_style)

        self.parameter_table.setFixedWidth(250)

        self.table_layout.addWidget(self.parameter_table)

        # Sweep slider
        self.sweep_slider.valueChanged.connect(self.sweep_changed)

        # Antenna image
        # image_container = QWidget()
        # self.image_layout = QVBoxLayout(image_container)
        # self.botton_image_layout.addWidget(image_container)

        # Set minimum and maximum size for the image_container
        # image_container.setMinimumSize(200, 200)
        # image_container.setMaximumSize(500, 500)

        # Antenna button
        row_returns = self.ui.add_n_buttons(
            self.antenna_synthesis_left_layout,
            num_buttons=2,
            height=40,
            width=[200, 200],
            text=["Synthesis", "Generate"],
            font_size=18
        )

        self.antenna_button_layout = row_returns[0]
        self.synthesis_button = row_returns[1]
        self.create_antenna_button = row_returns[2]

        self.synthesis_button.clicked.connect(self.synthesis_button_clicked)
        self.create_antenna_button.clicked.connect(self.create_antenna_button_clicked)

        self.create_antenna_button.setEnabled(False)

    def sweep_changed(self):
        self.sweep_value.setText(str(self.sweep_slider.value()))

    def synthesis_button_clicked(self):
        self.ui.update_logger("Synthesis")

    def create_antenna_button_clicked(self):
        self.ui.update_logger("Create Antenna")
