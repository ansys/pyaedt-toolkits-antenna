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
import base64
from PySide6.QtCore import QThread
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QTableWidgetItem

import pyvista as pv
from pyvistaqt import BackgroundPlotter
from ansys.aedt.toolkits.antenna.ui.windows.antenna_synthesis.antenna_synthesis_page import Ui_AntennaSynthesis


class GenerateAntennaThread(QThread):
    finished_signal = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.main_window = app.main_window

    def run(self):
        success = self.main_window.antenna_generate()
        self.finished_signal.emit(success)


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
        self.antenna_synthesis_layout = self.antenna_synthesis_menu_widget.findChild(
            QHBoxLayout, "antenna_synthesis_layout"
        )

        self.antenna_synthesis_left_layout = self.antenna_synthesis_layout.findChild(
            QVBoxLayout, "left_settings_layout"
        )

        self.antenna_input_frame = self.antenna_synthesis_menu_widget.findChild(QFrame, "antenna_input_frame")
        self.antenna_input_frame.setFrameShape(QFrame.Box)

        self.antenna_input = self.antenna_input_frame.findChild(QVBoxLayout, "antenna_input")

        self.antenna_synthesis_right_layout = self.antenna_synthesis_layout.findChild(
            QVBoxLayout, "right_settings_layout"
        )

        self.top_antenna_options_frame = self.antenna_synthesis_menu_widget.findChild(
            QFrame, "top_antenna_options_frame"
        )
        self.top_antenna_options_frame.setFrameShape(QFrame.Box)

        self.top_antenna_settings_layout = self.top_antenna_options_frame.findChild(
            QHBoxLayout, "top_antenna_settings_layout"
        )
        self.top_antenna_settings_options_layout = self.top_antenna_settings_layout.findChild(
            QVBoxLayout, "top_antenna_settings_options_layout"
        )

        self.component_3d = self.antenna_synthesis_menu_widget.findChild(QCheckBox, "component_3d")
        self.create_setup = self.antenna_synthesis_menu_widget.findChild(QCheckBox, "create_hfss_setup")
        self.lattice_pair = self.antenna_synthesis_menu_widget.findChild(QCheckBox, "lattice_pair")

        self.sweep_layout = self.top_antenna_settings_options_layout.findChild(QWidget, "sweep_layout")
        self.sweep_value = self.antenna_synthesis_menu_widget.findChild(QLabel, "slider_value")
        self.sweep_slider = self.antenna_synthesis_menu_widget.findChild(QSlider, "sweep_slider")
        self.sweep_label = self.antenna_synthesis_menu_widget.findChild(QLabel, "sweep_label")

        self.length_unit = self.top_antenna_options_frame.findChild(QLineEdit, "length_unit")
        self.frequency_unit = self.top_antenna_options_frame.findChild(QLineEdit, "frequency_unit")

        self.bottom_antenna_options_frame = self.antenna_synthesis_menu_widget.findChild(
            QFrame, "bottom_antenna_options_frame"
        )

        self.botton_antenna_settings_layout = self.bottom_antenna_options_frame.findChild(
            QHBoxLayout, "botton_antenna_settings_layout"
        )
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
        self.generate_antenna_button = None
        self.generate_antenna_thread = None
        self.model_info = None

    def setup(self):
        # Modify theme
        app_color = self.main_window.ui.themes["app_color"]

        widge_style = """
        background-color: {_bg_color};
        color: {_color};
        """

        custom_style = widge_style.format(_bg_color=app_color["dark_three"], _color=app_color["text_foreground"])

        self.antenna_synthesis_menu_widget.setStyleSheet(custom_style)

        # Sweep slider
        self.sweep_slider.valueChanged.connect(self.sweep_changed)

        # Antenna button
        row_returns = self.ui.add_n_buttons(
            self.antenna_synthesis_left_layout,
            num_buttons=2,
            height=40,
            width=[200, 200],
            text=["Synthesis", "Generate"],
            font_size=18,
        )

        self.antenna_button_layout = row_returns[0]
        self.synthesis_button = row_returns[1]
        self.generate_antenna_button = row_returns[2]

        self.synthesis_button.clicked.connect(self.synthesis_button_clicked)
        self.generate_antenna_button.clicked.connect(self.generate_antenna_button_clicked)

        self.generate_antenna_button.setEnabled(False)

    def sweep_changed(self):
        self.sweep_value.setText(str(self.sweep_slider.value()))

    def synthesis_button_clicked(self):
        success = self.main_window.check_connection()
        if not success:
            self.ui.update_logger("Backend not running")
            return
        if (
            not self.main_window.properties.antenna.antenna_model_selected
            or not self.main_window.properties.antenna.antenna_selected
        ):
            self.ui.update_logger("No antenna selected")
            return
        elif (not isinstance(self.main_window.settings_menu.aedt_thread, bool) and
              self.main_window.settings_menu.aedt_thread and self.main_window.settings_menu.aedt_thread.isRunning()):
            self.ui.update_logger("AEDT launching")
            return
        else:
            is_backend_busy = self.main_window.backend_busy()
            if is_backend_busy:
                self.ui.update_logger("Toolkit running")
                return
            self.main_window.properties.antenna.antenna_parameters = self.main_window.antenna_synthesis()
            if self.main_window.properties.antenna.antenna_parameters:
                self.__update_antenna_table()
                be_properties = self.main_window.get_properties()
                if be_properties.get("selected_process") != 0:
                    self.generate_antenna_button.setEnabled(True)

    def generate_antenna_button_clicked(self):
        if (not self.main_window.settings_menu.aedt_thread or
                (hasattr(self.main_window.settings_menu.aedt_thread, 'aedt_launched') and
                 not self.main_window.settings_menu.aedt_thread.aedt_launched)):
            msg = "AEDT not launched."
            self.ui.update_logger(msg)
            return False

        if self.generate_antenna_thread and self.generate_antenna_thread.isRunning() or self.main_window.backend_busy():
            msg = "Toolkit running"
            self.ui.update_logger(msg)
            self.main_window.logger.debug(msg)
            return False

        be_properties = self.main_window.get_properties()

        if be_properties.get("selected_process") != 0:
            self.ui.update_progress(50)
            active_project = self.main_window.home_menu.project_combobox.currentText()
            active_design = self.main_window.home_menu.design_combobox.currentText()

            for project in be_properties["project_list"]:
                if self.main_window.get_project_name(project) == active_project:
                    be_properties["active_project"] = project
                    break
            be_properties["active_design"] = active_design

            self.main_window.set_properties(be_properties)

            # Start a separate thread for the backend call
            self.generate_antenna_thread = GenerateAntennaThread(app=self)
            self.generate_antenna_thread.finished_signal.connect(self.antenna_created_finished)

            msg = "Generating antenna"
            self.ui.update_logger(msg)

            self.generate_antenna_thread.start()

        else:
            self.ui.update_logger("Toolkit not connect to AEDT.")

    def parameter_value_change(self, item):
        if item.column() == 1:
            key = self.parameter_table.item(item.row(), 0).text()
            value = item.text()
            self.ui.update_logger("Changed value of key {} to {}".format(key, value))
            if self.main_window.properties.antenna.antenna_created:
                self.main_window.update_antenna_parameter(key, value)
                selected_project = self.main_window.home_menu.project_combobox.currentText()
                selected_design = self.main_window.home_menu.design_combobox.currentText()
                self.model_info = self.main_window.get_aedt_model(selected_project, selected_design)
                self.__update_antenna_model()

    def __update_antenna_table(self):
        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.table_layout)
        app_color = self.main_window.ui.themes["app_color"]
        num_rows = len(self.main_window.properties.antenna.antenna_parameters)

        self.parameter_table = QTableWidget(num_rows, 2)

        self.parameter_table.setHorizontalHeaderLabels(["Parameter", "Value"])

        h_header = self.parameter_table.horizontalHeader()
        v_header = self.parameter_table.verticalHeader()

        custom_style = """
                        QHeaderView::section {{
                        background-color: {_bg_color};
                        color: {_color};
                        }}
                        """

        table_header_style = custom_style.format(_bg_color=app_color["dark_three"],
                                                 _color=app_color["text_foreground"])

        h_header.setStyleSheet(table_header_style)
        v_header.setStyleSheet(table_header_style)

        for row, (key, value) in enumerate(self.main_window.properties.antenna.antenna_parameters.items()):
            key_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(str(value))

            self.parameter_table.setItem(row, 0, key_item)
            self.parameter_table.setItem(row, 1, value_item)

            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)

        self.parameter_table.itemChanged.connect(self.parameter_value_change)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.parameter_table)
        self.table_layout.addWidget(scroll_area)

    def antenna_created_finished(self):
        self.ui.update_progress(75)
        selected_project = self.main_window.home_menu.project_combobox.currentText()
        selected_design = self.main_window.home_menu.design_combobox.currentText()

        properties = self.main_window.get_properties()
        active_project = self.main_window.get_project_name(properties["active_project"])
        active_design = properties["active_design"]
        if active_project != selected_project or active_design != selected_design:
            self.main_window.home_menu.update_project()
            self.main_window.home_menu.update_design()

        self.main_window.properties.antenna.antenna_created = self.main_window.properties.antenna.antenna_selected
        self.main_window.properties.antenna.create_setup = self.create_setup.isChecked()

        self.generate_antenna_button.setEnabled(False)
        self.synthesis_button.setEnabled(False)

        if self.main_window.properties.backend_url in ["127.0.0.1", "localhost"]:
            encode = False
        else:
            encode = True

        self.model_info = self.main_window.get_aedt_model(properties["active_project"], active_design, encode=encode)
        self.__update_antenna_model(encode)
        self.ui.update_progress(100)

    def __update_antenna_model(self, encode):
        if self.model_info:
            self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.botton_image_layout)

            plotter = BackgroundPlotter(show=False)
            for element in self.model_info:
                if encode:
                    # Decode response
                    encoded_data = self.model_info[element][0]
                    encoded_data_bytes = bytes(encoded_data, "utf-8")
                    decoded_data = base64.b64decode(encoded_data_bytes)
                    # Create obj file locally
                    file_path = os.path.join(self.main_window.temp_folder, element + ".obj")
                    with open(file_path, "wb") as f:
                        f.write(decoded_data)
                    # Create PyVista object
                    if not os.path.exists(file_path):
                        break
                    color = self.model_info[element][1]
                    opacity = self.model_info[element][2]
                else:
                    file_path = element[0]
                    color = element[1]
                    opacity = element[2]

                cad_mesh = pv.read(file_path)

                plotter.add_mesh(cad_mesh,
                                 color=color,
                                 show_scalar_bar=False,
                                 opacity=opacity
                                 )

            plotter.view_isometric()
            plotter.set_background(color=self.main_window.ui.themes["app_color"]["bg_one"])
            plotter.add_axes_at_origin(labels_off=True, line_width=5)
            plotter.show_grid(color=self.main_window.ui.themes["app_color"]["dark_two"])

            image_layout = QHBoxLayout()
            antenna_image = QLabel()
            antenna_image.setScaledContents(True)
            antenna_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            image_layout.addWidget(plotter)

            self.main_window.antenna_synthesis_menu.botton_image_layout.addLayout(image_layout, 0, 0, 1, 1)
