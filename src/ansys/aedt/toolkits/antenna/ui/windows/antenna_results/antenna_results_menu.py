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

from PySide6.QtCore import QThread
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
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from pyvistaqt import BackgroundPlotter
import pyvista as pv
import pyqtgraph as pg

# toolkit PySide6 Widgets
from ansys.aedt.toolkits.common.ui.utils.widgets import PyPushButton

from windows.antenna_results.antenna_results_page import Ui_AntennaResults
from windows.antenna_results.antenna_results_column import Ui_LeftColumn

import os
import sys


class GetResultsThread(QThread):
    finished_signal = Signal(bool)

    def __init__(self, app):
        super().__init__()
        self.main_window = app.main_window

    def run(self):
        success = self.main_window.analyze_design()
        self.finished_signal.emit(success)


class AntennaResultsMenu(object):
    def __init__(self, main_window):
        # General properties
        self.main_window = main_window
        self.ui = main_window.ui

        # Add page
        antenna_results_menu_index = self.ui.add_page(Ui_AntennaResults)
        self.ui.load_pages.pages.setCurrentIndex(antenna_results_menu_index)
        self.antenna_results_menu_widget = self.ui.load_pages.pages.currentWidget()

        # Add left column
        new_column_widget = QWidget()
        new_ui = Ui_LeftColumn()
        new_ui.setupUi(new_column_widget)
        self.ui.left_column.menus.menus.addWidget(new_column_widget)
        self.antenna_results_column_widget = new_column_widget
        self.antenna_results_column_vertical_layout = new_ui.antenna_results_vertical_layout

        # Specific properties
        self.farfield_2d_phi_layout = self.antenna_results_menu_widget.findChild(QVBoxLayout, "farfield_2d_phi_layout")
        self.farfield_2d_phi_frame = self.antenna_results_menu_widget.findChild(QFrame, "farfield_2d_phi_frame")
        self.farfield_2d_phi_frame.setFrameShape(QFrame.Box)

        self.farfield_2d_theta_layout = self.antenna_results_menu_widget.findChild(QVBoxLayout, "farfield_2d_theta_layout")
        self.farfield_2d_theta_frame = self.antenna_results_menu_widget.findChild(QFrame, "farfield_2d_theta_frame")
        self.farfield_2d_theta_frame.setFrameShape(QFrame.Box)

        self.farfield_3d_layout = self.antenna_results_menu_widget.findChild(QVBoxLayout, "farfield_3d_layout")
        self.farfield_3d_frame = self.antenna_results_menu_widget.findChild(QFrame, "farfield_3d_frame")
        self.farfield_3d_frame.setFrameShape(QFrame.Box)

        self.scattering_layout = self.antenna_results_menu_widget.findChild(QVBoxLayout, "scattering_layout")
        self.scattering_frame = self.antenna_results_menu_widget.findChild(QFrame, "scattering_frame")

        self.scattering_frame.setFrameShape(QFrame.Box)

        self.antenna_results_thread = None
        self.scattering_graph = None
        self.farfield_2d_phi_widget = None
        self.farfield_2d_phi_graph = None
        self.farfield_2d_theta_graph = None
        self.farfield_3d_plotter = None
        self.cad_actor = None

    def setup(self):
        # Modify theme
        app_color = self.main_window.ui.themes["app_color"]

        layout_row_obj = QVBoxLayout()

        layout_line = QHBoxLayout()

        label = QLabel()
        layout_line.addWidget(label)
        label.setText("Cores")
        font = QFont(self.main_window.properties.font["family"], self.main_window.properties.font["title_size"])
        label.setFont(font)
        font.setPointSize(self.main_window.properties.font["title_size"])

        spacer = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout_line.addItem(spacer)

        edit = QLineEdit()
        edit.setFont(font)
        edit.setText("4")
        edit.setFixedWidth(200)
        edit.setStyleSheet("border: 2px solid {};".format(self.ui.themes['app_color']['text_foreground']))
        layout_line.addWidget(edit)

        spacer = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout_line.addItem(spacer)

        layout_row_obj.addLayout(layout_line)

        layout_row_obj.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))

        button_obj = PyPushButton(
            text="Get Results",
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
        button_obj.clicked.connect(self.antenna_results_button_clicked)

        layout_row_obj.setAlignment(Qt.AlignTop)

        self.antenna_results_column_vertical_layout.addLayout(layout_row_obj)

        # Set results page

        # Scattering
        self.scattering_graph = pg.PlotWidget()
        self.scattering_layout.addWidget(self.scattering_graph)

        # 2D Cut phi
        # Add combobox
        # Add check box
        self.farfield_2d_phi_graph = pg.PlotWidget()
        self.farfield_2d_phi_layout.addWidget(self.farfield_2d_phi_graph)

        # 2D Cut theta
        self.farfield_2d_theta_graph = pg.PlotWidget()
        self.farfield_2d_theta_layout.addWidget(self.farfield_2d_theta_graph)

        # 3D
        self.farfield_3d_plotter = BackgroundPlotter(show=False)
        self.farfield_3d_plotter.view_isometric()
        self.farfield_3d_plotter.set_background(color=self.main_window.ui.themes["app_color"]["bg_one"])
        logo_path = os.path.join(os.path.dirname(__file__), "ANSYS_logo.obj")
        cad_mesh = pv.read(logo_path)
        self.cad_actor = self.farfield_3d_plotter.add_mesh(cad_mesh)
        self.farfield_3d_layout.addWidget(self.farfield_3d_plotter)

    def antenna_results_button_clicked(self):
        if (not self.main_window.properties.antenna.antenna_created
                or not self.main_window.properties.antenna.create_setup):
            self.ui.update_logger("Antenna can not be solved")
            return
        # Start a separate thread for the backend call
        self.antenna_results_thread = GetResultsThread(app=self)
        self.antenna_results_thread.finished_signal.connect(self.antenna_results_finished)
        msg = "Analyzing antenna"
        self.ui.update_logger(msg)

        self.antenna_results_thread.start()

    def antenna_results_finished(self):
        self.ui.update_progress(100)

        farfield_data = self.main_window.export_farfield()

        farfield_data.polar_plot_3d_pyvista()

        scattering_results = self.main_window.scattering_results()

        # Create layout

        selected_project = self.main_window.home_menu.project_combobox.currentText()
        selected_design = self.main_window.home_menu.design_combobox.currentText()

        properties = self.main_window.get_properties()
        active_project = self.main_window.get_project_name(properties["active_project"])
        active_design = properties["active_design"]
        if active_project != selected_project or active_design != selected_design:
            self.main_window.home_menu.update_project()
            self.main_window.home_menu.update_design()
