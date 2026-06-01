# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path
import sys

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
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
import pyvista as pv
from pyvistaqt import BackgroundPlotter

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
CATALOG_DIR = Path(__file__).parent
CATALOG_FILE = CATALOG_DIR / "antenna_catalog.toml"

if CATALOG_FILE.is_file():
    with CATALOG_FILE.open(mode="rb") as file_handler:
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
            file_path = antenna_path / "model" / f"{antenna_properties['name']}.obj"
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

    def mousePressEvent(self, event):  # noqa: N802
        self.antenna_item_signal.emit(self.index)
        super().mousePressEvent(event)


class DetachedImageDialog(QDialog):
    """Display a larger image preview with mouse-based zoom and panning."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.resize(900, 700)

        self._pixmap = QPixmap(str(image_path))
        self._zoom_factor = 1.0
        self._fit_scale = 1.0

        dialog_layout = QVBoxLayout(self)
        self.scroll_area = ImageScrollArea(self._apply_zoom, self)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)

        dialog_layout.addWidget(self.scroll_area)

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        self._zoom_factor = 1.0
        self._update_pixmap(reset_view=True)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self._update_pixmap()

    def _fit_to_viewport_scale(self):
        if self._pixmap.isNull():
            return 1.0

        viewport_size = self.scroll_area.viewport().size()
        if viewport_size.width() <= 0 or viewport_size.height() <= 0:
            return 1.0

        width_scale = viewport_size.width() / self._pixmap.width()
        height_scale = viewport_size.height() / self._pixmap.height()
        return min(width_scale, height_scale)

    def _update_pixmap(self, reset_view=False):
        if self._pixmap.isNull():
            return

        self._fit_scale = self._fit_to_viewport_scale()
        effective_scale = max(self._fit_scale * self._zoom_factor, 0.01)

        scaled_width = max(
            1,
            int(self._pixmap.width() * effective_scale),
        )
        scaled_height = max(
            1,
            int(self._pixmap.height() * effective_scale),
        )
        scaled_pixmap = self._pixmap.scaled(
            scaled_width,
            scaled_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())

        if reset_view:
            self.scroll_area.horizontalScrollBar().setValue(0)
            self.scroll_area.verticalScrollBar().setValue(0)

    def _apply_zoom(self, factor, anchor_pos):
        previous_size = self.image_label.size()
        previous_horizontal = self.scroll_area.horizontalScrollBar().value()
        previous_vertical = self.scroll_area.verticalScrollBar().value()

        self._zoom_factor = min(max(self._zoom_factor * factor, 0.25), 5.0)
        self._update_pixmap()

        if previous_size.width() <= 0 or previous_size.height() <= 0:
            return

        width_ratio = (previous_horizontal + anchor_pos.x()) / previous_size.width()
        height_ratio = (previous_vertical + anchor_pos.y()) / previous_size.height()
        current_size = self.image_label.size()
        self.scroll_area.horizontalScrollBar().setValue(
            int(width_ratio * current_size.width() - anchor_pos.x())
        )
        self.scroll_area.verticalScrollBar().setValue(
            int(height_ratio * current_size.height() - anchor_pos.y())
        )


class ImageScrollArea(QScrollArea):
    """Scroll area supporting mouse-wheel zoom and drag panning."""

    def __init__(self, zoom_callback, parent=None):
        super().__init__(parent)
        self._zoom_callback = zoom_callback
        self._drag_origin = None
        self._horizontal_origin = 0
        self._vertical_origin = 0
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.OpenHandCursor)

    def wheelEvent(self, event):  # noqa: N802
        zoom_step = 1.1 if event.angleDelta().y() > 0 else 1 / 1.1
        self._zoom_callback(zoom_step, event.position())
        event.accept()

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_origin = event.position().toPoint()
            self._horizontal_origin = self.horizontalScrollBar().value()
            self._vertical_origin = self.verticalScrollBar().value()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._drag_origin is not None:
            delta = event.position().toPoint() - self._drag_origin
            self.horizontalScrollBar().setValue(self._horizontal_origin - delta.x())
            self.verticalScrollBar().setValue(self._vertical_origin - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        if event.button() == Qt.LeftButton and self._drag_origin is not None:
            self._drag_origin = None
            self.setCursor(Qt.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


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
                antenna_path = CATALOG_DIR / selected_model.lower() / antenna_selected.lower()
                antenna_model_info = {}
                properties_file = antenna_path / "model" / "properties.toml"
                if properties_file.is_file():
                    with properties_file.open(mode="rb") as file_handler:
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
        antenna_path = (
            CATALOG_DIR
            / selected_model.lower()
            / self.main_window.properties.antenna.antenna_selected.lower()
        )

        # Load antenna picture
        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.botton_image_layout)
        antenna_picture = next(
            (path for path in antenna_path.rglob("*") if path.suffix.lower() in {".jpg", ".jpeg", ".png"}),
            None,
        )

        if antenna_picture and antenna_picture.is_file():
            image = self.add_image(antenna_picture)
            self.main_window.antenna_synthesis_menu.botton_image_layout.addLayout(image, 0, 0, 1, 1)

        # Load antenna input parameters
        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.antenna_input)
        antenna_parameters = {}
        parameters_file = antenna_path / "parameters.toml"
        if parameters_file.is_file():
            with parameters_file.open(mode="rb") as parameter_handler:
                antenna_parameters = tomllib.load(parameter_handler)
        if antenna_parameters:
            for parameter in antenna_parameters:
                line = self.add_line(parameter.replace("_", " "), antenna_parameters[parameter])
                self.main_window.antenna_synthesis_menu.antenna_input.addLayout(line)

        self.main_window.ui.clear_layout(self.main_window.antenna_synthesis_menu.table_layout)

        # Populate synthesis page
        self.ui.set_page(self.main_window.antenna_synthesis_menu.antenna_synthesis_menu_widget)

    def add_image(self, image_path):
        """Add the image to antenna settings."""
        image_layout = QGridLayout()
        image_layout.setObjectName("image_layout_pixmap")
        image_layout.setContentsMargins(12, 12, 12, 12)
        antenna_image = QLabel()
        antenna_image.setObjectName("antenna_picture")
        antenna_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        antenna_image.setAlignment(Qt.AlignCenter)

        open_detached_button = QPushButton("Open")
        open_detached_button.setObjectName("open_detached_image_button")
        open_detached_button.setFixedSize(64, 28)
        button_color = QColor(self.ui.themes["app_color"]["dark_three"])
        text_color = self.ui.themes["app_color"]["text_foreground"]
        open_detached_button.setStyleSheet(
            "padding: 4px 8px; border-radius: 6px;"
            f"background-color: rgba({button_color.red()}, {button_color.green()}, {button_color.blue()}, 150);"
            f"color: {text_color};"
        )

        def open_detached_view():
            dialog = DetachedImageDialog(image_path, self.main_window)
            dialog.exec()

        open_detached_button.clicked.connect(open_detached_view)

        def resize_pixmap():
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(antenna_image.width(), antenna_image.height(),
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)
            antenna_image.setPixmap(pixmap)

        antenna_image.resizeEvent = lambda event: resize_pixmap()

        resize_pixmap()
        image_layout.addWidget(antenna_image, 0, 0)
        image_layout.addWidget(open_detached_button, 0, 0, alignment=Qt.AlignBottom | Qt.AlignRight)
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
