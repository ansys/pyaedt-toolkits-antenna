# -*- coding: utf-8 -*-

import os
import sys

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from pyaedt import Hfss
from pyaedt import settings
import pyqtgraph as pg
import qdarkstyle

from ansys.aedt.toolkits.antennas.patch import RectangularPatchProbe
from ansys.aedt.toolkits.antennas.ui.antennas_main import Ui_MainWindow

settings.use_grpc_api = True
current_path = os.path.join(os.getcwd(), "ui", "images")
os.environ["QT_API"] = "pyside6"


class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.parameters = {}
        self.setupUi(self)
        self._font = QtGui.QFont()
        self._font.setPointSize(12)
        self.setFont(self._font)
        header = self.property_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

        icon = QtGui.QIcon()
        icon.addFile(
            os.path.join(current_path, "logo_cropped.png"),
            QtCore.QSize(),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        icon.addFile(
            os.path.join(current_path, "logo_cropped.png"),
            QtCore.QSize(),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        self.setWindowIcon(icon)
        self.actionRectangular_with_probe.triggered.connect(
            lambda checked: self.on_Rect_Patch_w_probe_selected()
        )
        self.actionConical.triggered.connect(lambda checked: self.on_Horn_Conical())
        self.menubar.setFont(self._font)
        self.setWindowTitle("PyAEDT Antenna Wizard")
        self.length_unit = ""

        self.closeButton.clicked.connect(self.release_and_close)
        self.pushButton_5.clicked.connect(self.analyze_antenna)
        self.oantenna = None
        self.hfss = None
        self.connect_hfss.clicked.connect(self.launch_hfss)
        sizePolicy_antenna = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy_antenna.setHorizontalStretch(0)
        sizePolicy_antenna.setVerticalStretch(0)
        sizePolicy_antenna.setHeightForWidth(self.antenna_settings.sizePolicy().hasHeightForWidth())
        self.antenna_settings.setSizePolicy(sizePolicy_antenna)
        self.splitter_2.setSizePolicy(sizePolicy_antenna)
        pass

    def launch_hfss(self):
        """Initialize  Hfss."""
        non_graphical = self.nongraphical.isChecked()
        self.hfss = Hfss(specified_version="2022.2", non_graphical=non_graphical)
        self.add_status_bar_message("Hfss Connected.")

    def analyze_antenna(self):
        """Solves current report and plots antenna results."""

        if not self.hfss:
            self.launch_hfss()
        num_cores = int(self.numcores.text())
        self.hfss.analyze_nominal(num_cores)
        sol_data = self.hfss.post.get_solution_data()
        self.graphWidget = pg.PlotWidget()
        freq = sol_data.primary_sweep_values
        val = sol_data.data_db20()
        # plot data: x, y values
        self.results.addWidget(self.graphWidget)
        self.graphWidget.plot(
            freq,
            val,
        )
        self.graphWidget.setTitle("Scattering Plot")
        self.graphWidget.setLabel(
            "bottom",
            "Frequency GHz",
        )
        self.graphWidget.setLabel(
            "left",
            "Value in dB",
        )

        self.antenna1widget = pg.PlotWidget()
        solution = self.hfss.post.get_solution_data(
            "GainTotal",
            self.hfss.nominal_adaptive,
            primary_sweep_variable="Theta",
            context="3D",
            report_category="Far Fields",
        )
        theta = solution.primary_sweep_values
        val = solution.data_db20()
        # plot data: x, y values
        self.results.addWidget(self.antenna1widget)
        self.antenna1widget.plot(theta, val)
        self.antenna1widget.setTitle(
            "Realized gain at Phi {}".format(solution.intrinsics["Phi"][0])
        )
        self.antenna1widget.setLabel(
            "left",
            "Realized Gain",
        )
        self.antenna1widget.setLabel(
            "bottom",
            "Theta",
        )
        self.antenna2widget = pg.PlotWidget()
        solution.primary_sweep = "Phi"
        phi = solution.primary_sweep_values
        val = solution.data_db20()
        # plot data: x, y values
        self.results.addWidget(self.antenna2widget)
        self.antenna2widget.plot(phi, val)
        self.antenna2widget.setTitle(
            "Realized gain at Theta {}".format(solution.intrinsics["Theta"][0])
        )
        self.antenna2widget.setLabel(
            "left",
            "Realized Gain",
        )
        self.antenna2widget.setLabel(
            "bottom",
            "Phi",
        )

    def add_status_bar_message(self, message):
        """Add a status bar message.

        Parameters
        ----------
        message : str

        """
        myStatus = QtWidgets.QStatusBar()
        myStatus.showMessage(message, 3000000)
        self.setStatusBar(myStatus)

    def release_and_close(self):
        """Release Desktop."""
        if self.hfss:
            self.hfss.release_desktop(False, False)
        self.close()

    def get_antenna(self, antenna, synth_only=False):
        """Synthesize and create the antenna in Hfss.

        Parameters
        ----------
        antenna : :class:
        synth_only : bool
        """
        if not self.hfss:
            self.launch_hfss()
        huygens = self.huygens.isChecked()
        component3d = self.component_3d.isChecked()
        create_setup = self.create_hfss_setup.isChecked()
        lattice_pair = self.lattice_pair.isChecked()
        model_units = self.units.currentText()
        frequnits = self.frequnits.currentText()
        if not self.oantenna:
            self.oantenna = self.hfss.add_from_toolkit(
                antenna,
                draw=not synth_only,
                frequency_unit=frequnits,
                length_unit=model_units,
                huygens_box=huygens,
            )
        x_pos = float(self.x_position.text())
        y_pos = float(self.y_position.text())
        z_pos = float(self.z_position.text())
        self.oantenna.origin = [x_pos, y_pos, z_pos]
        self.oantenna.frequency = float(self.frequency.text())
        self.oantenna.outer_boundary = (
            None
            if self.parameters["boundary"].currentText() == "None"
            else self.parameters["boundary"].currentText()
        )
        for param in self.parameters:
            if param in dir(self.oantenna):
                if isinstance(self.parameters[param], QtWidgets.QComboBox):
                    self.oantenna.__setattr__(param, self.parameters[param].currentText())
                elif isinstance(self.parameters[param], QtWidgets.QLineEdit):
                    try:
                        self.oantenna.__setattr__(param, float(self.parameters[param].text()))
                    except:
                        self.oantenna.__setattr__(param, self.parameters[param].text())

        self.oantenna._parameters = self.oantenna._synthesis()
        if not synth_only:
            if not self.oantenna.object_list:
                self.oantenna.draw()
            if component3d:
                self.oantenna.create_3dcomponent(replace=True)
            if create_setup:
                freq = float(self.frequency.text())
                setup = self.hfss.create_setup()
                setup.props["Frequency"] = str(freq) + frequnits
                sweep1 = setup.add_sweep()
                sweep1.props["RangeStart"] = str(freq * 0.8) + frequnits
                sweep1.props["RangeEnd"] = str(freq * 1.2) + frequnits
                sweep1.update()

        self.property_table.setRowCount(len(self.oantenna._parameters.items()))
        i = 0
        __sortingEnabled = self.property_table.isSortingEnabled()
        self.property_table.setSortingEnabled(False)
        self.property_table.setRowCount(len(self.oantenna._parameters.values()))
        for par, value in self.oantenna._parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.property_table.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(value) + self.oantenna.length_unit)
            self.property_table.setItem(i, 1, item)
            i += 1

        self.property_table.setSortingEnabled(__sortingEnabled)
        self.hfss.modeler.fit_all()
        if synth_only:
            self.add_status_bar_message("Synthesis completed.")
        else:
            self.add_status_bar_message("Project created correctly.")

    def create_rectangular_probe_design(self, synth_only=False):
        """Create a rectangular probe patch.

        Parameters
        ----------
        synth_only : bool
        """
        self.get_antenna(RectangularPatchProbe, synth_only)

    def create_conical_horn_design(self, synth_only=False):
        """Create a conical horn antenna.

        Parameters
        ----------
        synth_only : bool
        """
        self.get_antenna(RectangularPatchProbe, synth_only)

    def closeEvent(self, event):
        """Close UI."""
        close = QtWidgets.QMessageBox.question(
            self, "QUIT", "Confirm quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
            app.quit()
        else:
            event.ignore()

    def clear_antenna_settings(self, layout):
        """Clear all antenna settings."""
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QtWidgets.QWidgetItem):
                item.widget().close()
                # or
                # item.widget().setParent(None)
            elif isinstance(item, QtWidgets.QSpacerItem):
                pass
                # no need to do extra stuff
            else:
                self.clear_antenna_settings(item.layout())

            # remove the item from layout
            layout.removeItem(item)
        self.parameters = {}

    def add_line(self, title, variable_value, label_value, line_type, value):
        """Add a new parameter to antenna settings."""
        self.__dict__[title] = QtWidgets.QHBoxLayout()
        line = self.__dict__[title]
        line.setObjectName(title)

        label = QtWidgets.QLabel()
        label.setObjectName("{}_label".format(title))
        line.addWidget(label)
        label.setText(label_value)
        label.setFont(self._font)
        spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        line.addItem(spacer)
        if line_type == "edit":
            name = "{}".format(variable_value)
            self.__dict__[name] = QtWidgets.QLineEdit()
            edit = self.__dict__[name]
            edit.setObjectName(name)
            edit.setFont(self._font)
            edit.setText(value)
            line.addWidget(edit)
        elif line_type == "combo":
            name = "{}".format(variable_value)
            self.__dict__[name] = QtWidgets.QComboBox()
            edit = self.__dict__[name]
            edit.setObjectName(name)
            edit.setFont(self._font)
            for v in value:
                edit.addItem(v)
            line.addWidget(edit)
        self.parameters[name] = edit
        return line

    def add_image(self, image_path):
        """Add the image to antenna settings."""
        line_0 = QtWidgets.QHBoxLayout()
        line_0.setObjectName("line_0")

        line_0_spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        line_0.addItem(line_0_spacer)

        antenna_image = QtWidgets.QLabel()
        antenna_image.setObjectName("antenna_image")

        antenna_image.setScaledContents(True)
        _pixmap = QtGui.QPixmap(image_path)
        antenna_image.setPixmap(_pixmap)
        _pixmap = _pixmap.scaled(
            antenna_image.width(),
            antenna_image.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        line_0.addWidget(antenna_image)

        line_0_spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        line_0.addItem(line_0_spacer)
        return line_0

    def add_antenna_buttons(self, method_create):
        """Add create buttons to antenna settings."""
        line_buttons = QtWidgets.QHBoxLayout()
        line_buttons.setObjectName("line_buttons")

        synth_button = QtWidgets.QPushButton()
        synth_button.setObjectName("synth_button")
        synth_button.setFont(self._font)

        line_buttons.addWidget(synth_button)

        line_buttons_spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )

        line_buttons.addItem(line_buttons_spacer)

        create_button = QtWidgets.QPushButton()
        create_button.setObjectName("create_button")
        create_button.setFont(self._font)

        line_buttons.addWidget(create_button)

        synth_button.setText("Synthesis")
        create_button.setText("Create Hfss Project")
        synth_button.clicked.connect(lambda: method_create(True))
        create_button.clicked.connect(lambda: method_create(False))
        return line_buttons

    def on_Rect_Patch_w_probe_selected(self):
        """Create Rectangular Patch UI."""
        self.clear_antenna_settings(self.layout_settings)

        top_spacer = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )

        self.layout_settings.addItem(top_spacer, 2, 0, 1, 1)

        image = self.add_image(os.path.join(current_path, "Patch.png"))
        self.layout_settings.addLayout(image, 0, 0, 1, 1)

        line1 = self.add_line("line_1", "antenna_name", "Antenna Name", "edit", "Patch")
        self.layout_settings.addLayout(line1, 3, 0, 1, 1)

        line2 = self.add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            ["FR4_epoxy", "teflon_based", "Rogers RT/duroid 6002 (tm)"],
        )
        self.layout_settings.addLayout(line2, 4, 0, 1, 1)

        line3 = self.add_line("line_3", "frequency", "Frequency", "edit", "10")
        self.layout_settings.addLayout(line3, 5, 0, 1, 1)

        line4 = self.add_line("line_4", "substrate_height", "Subtsrate height", "edit", "0.254")
        self.layout_settings.addLayout(line4, 6, 0, 1, 1)

        line5 = self.add_line(
            "line_5",
            "boundary",
            "Boundary Condition",
            "combo",
            ["Radiation", "PML", "FEBI", "None"],
        )
        self.layout_settings.addLayout(line5, 7, 0, 1, 1)

        line6 = self.add_line("line_6", "x_position", "Origin X Position", "edit", "0.0")
        self.layout_settings.addLayout(line6, 8, 0, 1, 1)
        line7 = self.add_line("line_7", "y_position", "Origin Y Position", "edit", "0.0")
        self.layout_settings.addLayout(line7, 9, 0, 1, 1)
        line8 = self.add_line("line_8", "z_position", "Origin Z Position", "edit", "0.0")
        self.layout_settings.addLayout(line8, 10, 0, 1, 1)

        line_buttons = self.add_antenna_buttons(self.create_rectangular_probe_design)
        self.layout_settings.addLayout(line_buttons, 13, 0, 1, 1)

        bottom_spacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.layout_settings.addItem(bottom_spacer, 14, 0, 1, 1)

    def on_Horn_Conical(self):
        """Create Conical Horn UI."""
        self.clear_antenna_settings(self.layout_settings)

        top_spacer = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )

        self.layout_settings.addItem(top_spacer, 2, 0, 1, 1)

        image = self.add_image(os.path.join(current_path, "HornConical.jpg"))
        self.layout_settings.addLayout(image, 0, 0, 1, 1)

        line1 = self.add_line("line_1", "antenna_name", "Antenna Name", "edit", "Patch")
        self.layout_settings.addLayout(line1, 3, 0, 1, 1)

        line2 = self.add_line("line_2", "frequency", "Frequency", "edit", "10")
        self.layout_settings.addLayout(line2, 5, 0, 1, 1)

        line5 = self.add_line(
            "line_5",
            "boundary",
            "Boundary Condition",
            "combo",
            [
                "Radiation",
                "PML",
                "FEBI",
                "None",
            ],
        )
        self.layout_settings.addLayout(line5, 7, 0, 1, 1)

        line6 = self.add_line("line_6", "x_position", "Origin X Position", "edit", "0.0")
        self.layout_settings.addLayout(line6, 8, 0, 1, 1)
        line7 = self.add_line("line_7", "y_position", "Origin Y Position", "edit", "0.0")
        self.layout_settings.addLayout(line7, 9, 0, 1, 1)
        line8 = self.add_line("line_8", "z_position", "Origin Z Position", "edit", "0.0")
        self.layout_settings.addLayout(line8, 10, 0, 1, 1)

        line_buttons = self.add_antenna_buttons(self.create_conical_horn_design)
        self.layout_settings.addLayout(line_buttons, 13, 0, 1, 1)

        bottom_spacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.layout_settings.addItem(bottom_spacer, 14, 0, 1, 1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ApplicationWindow()
    w.show()
    sys.exit(app.exec())
