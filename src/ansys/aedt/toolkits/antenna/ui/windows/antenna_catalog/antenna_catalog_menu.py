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

from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from pyvistaqt import BackgroundPlotter
import pyvista as pv

# toolkit PySide6 Widgets
from ansys.aedt.toolkits.common.ui.utils.widgets import PyPushButton

from ansys.aedt.toolkits.antenna.ui.windows.antenna_catalog.antenna_catalog_page import Ui_AntennaCatalog
from ansys.aedt.toolkits.antenna.ui.windows.antenna_catalog.antenna_catalog_column import Ui_LeftColumn

import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

antenna_catalog = {}
if os.path.isfile(os.path.join(os.path.dirname(__file__), "antenna_catalog.toml")):
    with open(os.path.join(os.path.dirname(__file__), "antenna_catalog.toml"), mode="rb") as file_handler:
        antenna_catalog = tomllib.load(file_handler)


class AntennaItem(QWidget):
    """Antenna item."""
    antenna_item_signal = Signal(int)

    def __init__(self, index, antenna_info, app_color):
        super().__init__()
        self.index = index

        text_color = app_color["text_active"]
        background = app_color["dark_three"]

        layout = QVBoxLayout(self)

        self.plotter = BackgroundPlotter(show=False)
        antenna_path = antenna_info["path"]
        antenna_name = antenna_info["name"]

        for element in antenna_info:
            if element in ["path", "name"]:
                continue
            antenna_properties = antenna_info[element]
            file_path = os.path.join(antenna_path, "model", antenna_properties["name"] + ".obj")
            cad_mesh = pv.read(file_path)
            self.plotter.add_mesh(
                cad_mesh,
                color=antenna_properties["color"],
                show_scalar_bar=False,
                opacity=antenna_properties["opacity"]
            )

        self.plotter.view_isometric()
        self.plotter.set_background(color=app_color["bg_one"])

        layout.addWidget(self.plotter)

        label = QLabel(antenna_name)
        layout.addWidget(label)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        antenna_label_style = """
                            QLabel {{
                            color: {_color};
                            font-size: {_font_size}pt;
                            font-weight: bold;
                            }}
                            """
        custom_style = antenna_label_style.format(
            _color=text_color, _bg_color=background, _font_size=20
        )
        label.setStyleSheet(custom_style)

    def mousePressEvent(self, event):
        self.antenna_item_signal.emit(self.index)
        super().mousePressEvent(event)


class AntennaCatalogMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui

        # Add properties
        self.main_window.properties.antenna.available_models = list(antenna_catalog.keys())

        # Add page
        antenna_catalog_menu_index = self.ui.add_page(Ui_AntennaCatalog)
        self.ui.load_pages.pages.setCurrentIndex(antenna_catalog_menu_index)
        self.antenna_catalog_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.antenna_catalog_column_widget = new_column_widget
        self.antenna_catalog_column_vertical_layout = new_ui.antenna_catalog_vertical_layout

        # Specific properties
        self.antenna_catalog = None
        self.antenna_catalog_layout = self.antenna_catalog_menu_widget.findChild(QVBoxLayout, "antenna_catalog_layout")
        self.grid_item = []

    def setup(self):
        # Modify theme
        app_color = self.main_window.ui.themes["app_color"]

        # Antenna catalog column
        available_antennas = self.main_window.properties.antenna.available_models

        layout_row_obj = QVBoxLayout()
        scroll_widget = QWidget()

        self.antenna_catalog = [layout_row_obj]
        for idx in range(len(available_antennas)):
            selected_antenna = available_antennas[idx]
            button_obj = PyPushButton(
                text=selected_antenna,
                radius=8,
                color=app_color["text_foreground"],
                bg_color=app_color["dark_one"],
                bg_color_hover=app_color["dark_three"],
                bg_color_pressed=app_color["dark_four"],
                font_size=20,
            )
            button_obj.setMinimumHeight(30)
            button_obj.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
            layout_row_obj.addWidget(button_obj)
            button_obj.clicked.connect(partial(self.antenna_catalog_button_clicked, selected_antenna))

            self.antenna_catalog.append(button_obj)

        layout_row_obj.setAlignment(Qt.AlignTop)

        scroll_widget.setLayout(layout_row_obj)

        scroll_area = QScrollArea()  # Create the scroll area
        scroll_area.setWidgetResizable(True)  # Allow resizing of the contained widget
        scroll_area.setWidget(scroll_widget)

        combo_box_style = """background-color: {_bg_color};"""

        custom_style = combo_box_style.format(_bg_color=app_color["dark_three"])

        scroll_area.setStyleSheet(custom_style)

        self.antenna_catalog_column_vertical_layout.addWidget(scroll_area)

    def antenna_catalog_button_clicked(self, selected_model):
        self.main_window.ui.clear_layout(self.antenna_catalog_layout)

        app_color = self.main_window.ui.themes["app_color"]
        background = app_color["dark_three"]

        # Antenna catalog menu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        grid_layout = QGridLayout()

        combo_box_style = """
                            background-color: {_bg_color};
                            """

        custom_style = combo_box_style.format(_bg_color=background)

        scroll_area.setStyleSheet(custom_style)

        available_antennas = {}
        if selected_model in self.main_window.properties.antenna.available_models:
            self.ui.update_logger("{} menu selected".format(selected_model))
            self.main_window.properties.antenna.antenna_model_selected = selected_model
            available_antennas = antenna_catalog[selected_model]
            if len(available_antennas["models"]) == 1:
                rows = 1
                columns = 1
            else:
                columns = 2
                rows = (len(available_antennas["models"]) + columns - 1) // columns
        else:
            self.ui.update_logger("No antennas available")
            rows = 0
            columns = 0

        antenna_cont = 0
        for i in range(rows):
            for j in range(columns):
                if available_antennas and antenna_cont >= len(available_antennas["models"]):
                    break
                antenna_index = i * columns + j
                antenna_selected = available_antennas["models"][antenna_index]
                antenna_path = os.path.join(os.path.dirname(__file__), selected_model.lower(), antenna_selected.lower())
                antenna_model_info = {}
                if os.path.isfile(os.path.join(antenna_path, "model", "properties.toml")):
                    with open(os.path.join(antenna_path, "model", "properties.toml"), mode="rb") as file_handler:
                        antenna_model_info = tomllib.load(file_handler)
                if not antenna_model_info:
                    antenna_cont += 1
                    continue

                antenna_model_info["path"] = antenna_path

                frame = QFrame()
                frame.setFrameShape(QFrame.Box)
                frame.setFrameShadow(QFrame.Raised)  # Optional: Set shadow effect
                frame_layout = QVBoxLayout(frame)
                frame_layout.setContentsMargins(0, 0, 0, 0)

                self.grid_item.append(AntennaItem(antenna_index, antenna_model_info, app_color))
                self.grid_item[-1].setFixedSize(400, 400)
                grid_layout.addWidget(self.grid_item[-1], i * 2, j * 2)
                line_color = """
                    border: 2px solid {_color};
                """
                custom_style = line_color.format(_color=app_color["dark_two"])
                self.grid_item[-1].setStyleSheet(custom_style)

                self.grid_item[-1].antenna_item_signal.connect(self.on_grid_item_clicked)

                antenna_cont += 1

        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)

        self.antenna_catalog_layout.addWidget(scroll_area)

        self.ui.set_page(self.antenna_catalog_menu_widget)

    def on_grid_item_clicked(self, index):
        if self.main_window.properties.antenna.antenna_created:
            self.ui.update_logger("{} antenna generated".format(self.main_window.properties.antenna.antenna_created))
            return
        available_antennas = antenna_catalog[self.main_window.properties.antenna.antenna_model_selected]
        self.main_window.properties.antenna.antenna_selected = available_antennas["models"][index]
        self.ui.update_logger("{} selected".format(self.main_window.properties.antenna.antenna_selected))

        selected_model = self.main_window.properties.antenna.antenna_model_selected
        antenna_path = os.path.join(os.path.dirname(__file__),
                                    selected_model.lower(),
                                    self.main_window.properties.antenna.antenna_selected.lower())

        # Load antenna picture
        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.botton_image_layout)
        antenna_picture = ""
        for root, dirs, files in os.walk(antenna_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    antenna_picture = os.path.join(root, file)
                    break

        if os.path.isfile(antenna_picture):
            image = self.add_image(antenna_picture)
            self.main_window.antenna_synthesis_menu.botton_image_layout.addLayout(image, 0, 0, 1, 1)

        # Load antenna input parameters
        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.antenna_input)
        antenna_parameters = {}
        if os.path.isfile(os.path.join(antenna_path, "parameters.toml")):
            with open(os.path.join(antenna_path, "parameters.toml"), mode="rb") as parameter_handler:
                antenna_parameters = tomllib.load(parameter_handler)
        if antenna_parameters:
            for parameter in antenna_parameters:
                line = self.add_line(parameter.replace("_", " "), antenna_parameters[parameter])
                self.main_window.antenna_synthesis_menu.antenna_input.addLayout(line)

        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.table_layout)

        # Populate synthesis page
        self.ui.set_page(self.main_window.antenna_synthesis_menu.antenna_synthesis_menu_widget)

    @staticmethod
    def add_image(image_path):
        """Add the image to antenna settings."""
        image_layout = QHBoxLayout()
        image_layout.setObjectName("image_layout_pixmap")
        antenna_image = QLabel()
        antenna_image.setObjectName("antenna_picture")
        antenna_image.setScaledContents(True)
        antenna_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def resize_pixmap():
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(antenna_image.width(), antenna_image.height(),
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
            antenna_image.setPixmap(pixmap)

        antenna_image.resizeEvent = lambda event: resize_pixmap()

        resize_pixmap()
        image_layout.addWidget(antenna_image)
        return image_layout

    def add_line(self, label_value, value):
        """Add a new parameter to antenna settings."""
        layout_line = QHBoxLayout()

        label = QLabel()
        layout_line.addWidget(label)
        label.setText(label_value)
        font = QFont(self.main_window.properties.font["family"], self.main_window.properties.font["title_size"])
        label.setFont(font)
        font.setPointSize(self.main_window.properties.font["title_size"])

        if isinstance(value, list):
            combobox = QComboBox()
            combobox.addItems(value)
            combobox.setFixedWidth(200)
            combobox.setStyleSheet("border: 2px solid {};".format(self.ui.themes['app_color']['text_foreground']))
            layout_line.addWidget(combobox)
            combobox.setFont(font)
            for i in range(combobox.count()):
                combobox.setItemData(i, font, Qt.FontRole)
        else:
            edit = QLineEdit()
            edit.setFont(font)
            edit.setText(str(value))
            edit.setFixedWidth(200)
            edit.setStyleSheet("border: 2px solid {};".format(self.ui.themes['app_color']['text_foreground']))
            layout_line.addWidget(edit)

        spacer = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout_line.addItem(spacer)

        return layout_line
