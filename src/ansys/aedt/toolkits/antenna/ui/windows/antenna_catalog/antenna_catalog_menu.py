from functools import partial

from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame

from pyvistaqt import BackgroundPlotter
import pyvista as pv

# toolkit PySide6 Widgets
from ansys.aedt.toolkits.common.ui.utils.widgets import PyLabel
from ansys.aedt.toolkits.common.ui.utils.widgets import PyPushButton

from windows.antenna_catalog.antenna_catalog_page import Ui_AntennaCatalog
from windows.antenna_catalog.antenna_catalog_column import Ui_LeftColumn

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

        plotter = BackgroundPlotter(show=False)
        antenna_path = antenna_info["path"]
        antenna_name = antenna_info["name"]

        for element in antenna_info:
            if element in ["path", "name"]:
                continue
            antenna_properties = antenna_info[element]
            file_path = os.path.join(antenna_path, "model", antenna_properties["name"] + ".obj")
            cad_mesh = pv.read(file_path)
            plotter.add_mesh(
                cad_mesh,
                color=antenna_properties["color"],
                show_scalar_bar=False,
                opacity=antenna_properties["opacity"]
            )

        plotter.view_isometric()
        plotter.set_background(color=app_color["bg_one"])

        layout.addWidget(plotter)

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
        # self.geometry_combo = self.geometry_menu_widget.findChild(QComboBox, "geometry_combo")
        # self.multiplier = self.geometry_menu_widget.findChild(QLineEdit, "multiplier")
        # self.select_geometry_label = self.geometry_menu_widget.findChild(QLabel, "select_geometry_label")
        # self.multiplier_label = self.geometry_menu_widget.findChild(QLabel, "dimension_multiplier_label")
        # self.geometry_button_layout = None
        # self.geometry_button = None
        # self.geometry_thread = None

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
            layout_row_obj.addWidget(button_obj)
            button_obj.clicked.connect(partial(self.antenna_catalog_button_clicked, selected_antenna))

            self.antenna_catalog.append(button_obj)

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

                grid_item = AntennaItem(antenna_index, antenna_model_info, app_color)
                grid_item.setFixedSize(400, 400)
                grid_layout.addWidget(grid_item, i * 2, j * 2)
                line_color = """
                    border: 2px solid {_color};
                """
                custom_style = line_color.format(_color=app_color["dark_two"])
                grid_item.setStyleSheet(custom_style)

                grid_item.antenna_item_signal.connect(self.on_grid_item_clicked)

                antenna_cont += 1

        scroll_widget.setLayout(grid_layout)
        scroll_area.setWidget(scroll_widget)

        self.antenna_catalog_layout.addWidget(scroll_area)

        self.ui.set_page(self.antenna_catalog_menu_widget)

        # Slot method to handle grid item clicks

    def on_grid_item_clicked(self, index):
        available_antennas = antenna_catalog[self.main_window.properties.antenna.antenna_model_selected]
        self.main_window.properties.antenna.antenna_selected = available_antennas["models"][index]
        self.ui.update_logger("{} selected".format(self.main_window.properties.antenna.antenna_selected))

        # # Common UI API
        # geometry_button_layout = self.geometry_menu_widget.findChild(QVBoxLayout, "button_layout")
        #
        # # Create geometry button
        # row_returns = self.ui.add_n_buttons(
        #     self.antenna_selector_column_vertical_layout, num_buttons=2, height=100, width=[300], text=["Create Geometry"], font_size=20
        # )
        #
        # self.geometry_button_layout = row_returns[0]
        # self.geometry_button = row_returns[1]
        # self.geometry_button_layout.addWidget(self.geometry_button)
        # self.geometry_button.clicked.connect(self.geometry_button_clicked)
        #
        # # UI from Designer
        #
        # # Combo box
        # combo_box_style = """
        #     QComboBox {{
        #         border: none;
        #         padding: 10px;
        #         color: {_color};
        #         background-color: {_bg_color};
        #         selection-background-color: red;
        #         font-size: {_font_size}pt;
        #     }}
        #     QComboBox QAbstractItemView {{
        #         border: none;
        #         background-color: {_bg_color};
        #         color: {_color};
        #     }}
        # """
        # custom_style = combo_box_style.format(
        #     _color=text_color, _bg_color=background, _font_size=self.main_window.properties.font["title_size"]
        # )
        # self.geometry_combo.setStyleSheet(custom_style)
        #
        # # Multiplier line
        # line_style = """
        #     QLineEdit {{
        #     border: none;
        #     padding: 10px;
        #     color: {_color};
        #     background-color: {_bg_color};
        #     selection-background-color: red;
        #     font-size: {_font_size}pt;
        #     }}
        # """
        # custom_style = line_style.format(
        #     _color=text_color, _bg_color=background, _font_size=self.main_window.properties.font["title_size"]
        # )
        # self.multiplier.setStyleSheet(custom_style)
        #
        # # Multiplier label button
        # multiplier_label_style = """
        #             QLabel {{
        #             color: {_color};
        #             font-size: {_font_size}pt;
        #             font-weight: bold;
        #             }}
        #             """
        # custom_style = multiplier_label_style.format(
        #     _color=text_color, _bg_color=background, _font_size=self.main_window.properties.font["title_size"]
        # )
        # self.multiplier_label.setStyleSheet(custom_style)
        #
        # # Geometry label button
        # select_geometry_label_style = """
        #                     QLabel {{
        #                     color: {_color};
        #                     font-size: {_font_size}pt;
        #                     font-weight: bold;
        #                     }}
        #                     """
        # custom_style = select_geometry_label_style.format(
        #     _color=text_color, _bg_color=background, _font_size=self.main_window.properties.font["title_size"]
        # )
        # self.select_geometry_label.setStyleSheet(custom_style)
        #
        # # Set Column
        # msg = "Press 'Create Geometry' button"
        # label_widget = PyLabel(
        #     text=msg,
        #     font_size=self.ui.app.properties.font["title_size"],
        #     color=self.ui.themes["app_color"]["text_description"],
        # )
        # self.geometry_column_vertical_layout.addWidget(label_widget)

    # def clear_layout(self, layout):
    #     while layout.count():
    #         child = layout.takeAt(0)
    #         if child.widget():
    #             child.widget().deleteLater()
    #         elif child.layout():
    #             self.clear_layout(child.layout())

    # def geometry_button_clicked(self):
    #     if not self.main_window.settings_menu.aedt_thread or (
    #         hasattr(self.main_window.settings_menu.aedt_thread, "aedt_launched")
    #         and not self.main_window.settings_menu.aedt_thread.aedt_launched
    #     ):
    #         msg = "AEDT not launched."
    #         self.ui.update_logger(msg)
    #         return False
    #
    #     if self.geometry_thread and self.geometry_thread.isRunning() or self.main_window.backend_busy():
    #         msg = "Toolkit running"
    #         self.ui.update_logger(msg)
    #         self.main_window.logger.debug(msg)
    #         return False
    #
    #     be_properties = self.main_window.get_properties()
    #
    #     geometry = self.geometry_combo.currentText()
    #     multiplier = self.multiplier.text()
    #
    #     be_properties["example"]["geometry"] = geometry
    #     be_properties["example"]["multiplier"] = multiplier
    #
    #     self.main_window.set_properties(be_properties)
    #
    #     if be_properties.get("active_project"):
    #         self.ui.update_progress(0)
    #         selected_project = self.main_window.home_menu.project_combobox.currentText()
    #         selected_design = self.main_window.home_menu.design_combobox.currentText()
    #
    #         # Start a separate thread for the backend call
    #         self.geometry_thread = CreateGeometryThread(
    #             app=self,
    #             selected_project=selected_project,
    #             selected_design=selected_design,
    #         )
    #         self.geometry_thread.finished_signal.connect(self.geometry_created_finished)
    #
    #         msg = "Creating geometry."
    #         self.ui.update_logger(msg)
    #
    #         self.geometry_thread.start()
    #
    #     else:
    #         self.ui.update_logger("Toolkit not connect to AEDT.")
    #
    # def geometry_created_finished(self, success):
    #     self.ui.update_progress(100)
    #     selected_project = self.main_window.home_menu.project_combobox.currentText()
    #     selected_design = self.main_window.home_menu.design_combobox.currentText()
    #
    #     properties = self.main_window.get_properties()
    #     active_project = self.main_window.get_project_name(properties["active_project"])
    #     active_design = properties["active_design"]
    #     if active_project != selected_project or active_design != selected_design:
    #         self.main_window.home_menu.update_project()
    #         self.main_window.home_menu.update_design()
    #
    #     if success:
    #         msg = "Geometry created."
    #         self.ui.update_logger(msg)
    #     else:
    #         msg = f"Failed backend call: {self.main_window.url}"
    #         self.ui.update_logger(msg)
