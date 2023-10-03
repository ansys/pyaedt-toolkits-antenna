import base64
import os
import re
import tempfile

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import pyqtgraph as pg
import pyvista as pv
from pyvistaqt import BackgroundPlotter
import requests

from ansys.aedt.toolkits.antenna.ui.common.frontend_api_generic import FrontendGeneric
from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger
from ansys.aedt.toolkits.antenna.ui.common.properties import be_properties

line_colors = ["g", "b", "r", "y", "w"]


class ToolkitFrontend(FrontendGeneric):
    def __init__(self):
        FrontendGeneric.__init__(self)
        self.temp_folder = tempfile.mkdtemp()
        self.synth_button = None
        self.parameters = {}
        self.default_materials = {"FR4_epoxy": 4.4, "Teflon (tm)": 2.1, "Rogers RT / duroid 6002(tm)": 2.94}
        self.touchstone_graph = None
        self.antenna1widget = None
        self.antenna2widget = None
        self.val_theta = None
        self.theta = None
        self.val_phi = None
        self.phi = None
        self.antenna_hfss_model = None

    def get_antenna(self, synth_only=False):
        """Antenna synthesis and HFSS model creation.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """

        self.update_progress(0)
        self.property_table.itemChanged.connect(None)

        # Get properties from backend
        self.get_properties()

        project_selected = self.project_aedt_combo.currentText()
        for project in be_properties.project_list:
            if os.path.splitext(os.path.basename(project))[0] == project_selected and project_selected != "No project":
                be_properties.active_project = project
                design_selected = self.design_aedt_combo.currentText()
                if project_selected in list(be_properties.design_list.keys()):
                    designs = be_properties.design_list[project_selected]
                    for design in designs:
                        if design_selected in list(design.values())[0]:
                            if list(design.keys())[0].lower() == "hfss":
                                be_properties.active_design = design
                            else:
                                be_properties.active_design = {}
                            break
                break

        be_properties.antenna_type = self.antenna_template

        # Options
        component3d = self.component_3d.isChecked()
        be_properties.component_3d = component3d
        create_setup = self.create_hfss_setup.isChecked()
        be_properties.create_setup = create_setup
        lattice_pair = self.lattice_pair.isChecked()
        be_properties.lattice_pair = lattice_pair
        sweep = self.sweep_slider.value()
        be_properties.sweep = sweep
        be_properties.synth_only = synth_only

        # Antenna setting
        antenna_name = self.antenna_name.text()
        be_properties.antenna_name = antenna_name
        x_pos = float(self.x_position.text())
        y_pos = float(self.y_position.text())
        z_pos = float(self.z_position.text())
        be_properties.origin = [x_pos, y_pos, z_pos]
        coordinate_system = self.coordinate_system.text()
        be_properties.coordinate_system = coordinate_system
        if "substrate_height" in self.__dir__():
            substrate_height = float(self.substrate_height.text())
            be_properties.substrate_height = substrate_height
        if "material" in self.__dir__():
            material = self.material.currentText()
            be_properties.material = material
            be_properties.material_properties = {"permittivity": self.default_materials[material]}
        if "gain_value" in self.__dir__():
            gain = self.gain_value.text()
            be_properties.gain_value = float(gain)
        if "feeder_length" in self.__dir__():
            feed = self.feeder_length.text()
            be_properties.feeder_length = float(feed)

        # Toolkit settings
        lenght_unit = self.units.currentText()
        be_properties.length_unit = lenght_unit
        freq_unit = self.frequnits.currentText()
        be_properties.frequency_unit = freq_unit
        num_cores = int(self.numcores.text())
        be_properties.core_number = num_cores

        msg = "User interface inputs loaded"
        logger.debug(msg)
        self.write_log_line(msg)

        if "frequency" in self.__dir__() and self.frequency.text() != "0":
            be_properties.frequency = float(self.frequency.text())
        elif "start_frequency" in self.__dir__() and "stop_frequency" in self.__dir__():
            be_properties.start_frequency = float(self.start_frequency.text())
            be_properties.stop_frequency = float(self.stop_frequency.text())

        be_properties.outer_boundary = (
            None if self.parameters["boundary"].currentText() == "None" else self.parameters["boundary"].currentText()
        )

        # Update backend
        self.set_properties()

        if synth_only:
            response = requests.post(self.url + "/create_antenna")
            if not response.ok:
                msg = f"Failed backend call: {self.url}" + "/create_antenna"
                logger.debug(msg)
                self.write_log_line(msg)
                self.update_progress(100)
                return
            else:
                msg = "Synthesis completed"
                logger.debug(msg)
                self.write_log_line(msg)

        else:
            self.update_progress(50)
            response = requests.get(self.url + "/get_status")
            if response.ok and response.json() == "Backend running":
                self.write_log_line("Please wait, toolkit running")
            else:
                msg = "Creating HFSS model"
                logger.debug(msg)
                self.write_log_line(msg)
                response = requests.post(self.url + "/create_antenna")
                if not response.ok:
                    msg = f"Failed backend call: {self.url}" + "/create_antenna"
                    logger.debug(msg)
                    self.write_log_line(msg)
                    self.update_progress(100)
                    return
                else:
                    msg = "HFSS model created"
                    logger.debug(msg)
                    self.write_log_line(msg)

                self.create_button.setEnabled(False)
                self.synth_button.setEnabled(False)
                self.frequnits.setEnabled(False)
                self.units.setEnabled(False)
                self.project_aedt_combo.setEnabled(False)
                self.design_aedt_combo.setEnabled(False)

                self.get_hfss_model()

                msg = "HFSS model completed"
                logger.debug(msg)
                self.write_log_line(msg)

                arguments = {"close_projects": False, "close_on_exit": False}
                requests.post(self.url + "/close_aedt", json=arguments)

        self.get_properties()

        self.property_table.setRowCount(len(be_properties.parameters.items()))
        i = 0
        __sortingEnabled = self.property_table.isSortingEnabled()
        self.property_table.setSortingEnabled(False)
        self.property_table.setRowCount(len(be_properties.parameters.values()))
        for par, value in be_properties.parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.property_table.setItem(i, 0, item)
            ratio_re = re.compile("|".join(["ratio", "coefficient", "points", "number"]))
            if "angle" in par:
                item = QtWidgets.QTableWidgetItem(str(round(value, 3)) + "deg")
            elif ratio_re.search(par):
                item = QtWidgets.QTableWidgetItem(str(round(value, 3)))
            else:
                item = QtWidgets.QTableWidgetItem(str(round(value, 3)) + be_properties.length_unit)
            self.property_table.setItem(i, 1, item)
            i += 1

        self.property_table.setSortingEnabled(__sortingEnabled)
        self.update_progress(100)

    def add_antenna_buttons(self, method_create):
        """Add buttons to antenna settings."""
        line_buttons = QtWidgets.QHBoxLayout()
        line_buttons.setObjectName("line_buttons")

        self.synth_button = QtWidgets.QPushButton()
        self.synth_button.setObjectName("synth_button")
        font = QtGui.QFont("Arial", 12)
        self.synth_button.setFont(font)
        self.synth_button.setMinimumSize(QtCore.QSize(100, 40))

        line_buttons.addWidget(self.synth_button)

        line_buttons_spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        line_buttons.addItem(line_buttons_spacer)

        self.create_button = QtWidgets.QPushButton()
        self.create_button.setObjectName("create_button")
        self.create_button.setFont(font)
        self.create_button.setMinimumSize(QtCore.QSize(160, 40))

        line_buttons.addWidget(self.create_button)

        self.synth_button.setText("Synthesis")
        self.create_button.setText("Create HFSS Model")
        self.get_properties()
        if be_properties.selected_process == 0 or be_properties.antenna_created:
            self.create_button.setEnabled(False)
        self.synth_button.clicked.connect(lambda: method_create(True))
        self.create_button.clicked.connect(lambda: method_create(False))
        return line_buttons

    def sweep_changed(self):
        self.slider_value.setText(str(self.sweep_slider.value()))
        new_property = {"sweep": int(self.sweep_slider.value())}
        self.set_properties(new_property)

    def update_project(self):
        sel = self.property_table.selectedItems()
        if sel:
            key = self.property_table.item(self.property_table.row(sel[0]), 0).text()
            val = self.property_table.item(self.property_table.row(sel[0]), 1).text()
        else:
            return

        response = requests.get(self.url + "/get_status")
        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        else:
            arguments = {"key": key, "value": val}
            response = requests.put(self.url + "/update_parameters", json=arguments)
            if not response.ok:
                msg = f"Failed backend call: {self.url}" + "/update_parameters"
                logger.debug(msg)
                self.write_log_line(msg)
            else:
                msg = "HFSS geometry completed."
                logger.debug(msg)
                self.write_log_line(msg)
                self.get_properties()
                if be_properties.antenna_created:
                    self.get_hfss_model()

            arguments = {"close_projects": False, "close_on_exit": False}
            requests.post(self.url + "/close_aedt", json=arguments)

    def analyze_antenna(self):
        """Solves current report and plots antenna results."""
        response = requests.get(self.url + "/get_status")
        self.update_progress(0)
        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        elif response.ok and response.json() == "Backend free":
            self.update_progress(25)
            response = requests.get(self.url + "/health")
            if response.ok and response.json() == "Toolkit not connected to AEDT":
                self.get_properties()
                be_properties.core_number = self.numcores.text()
                self.set_properties()
                if not be_properties.active_design:
                    self.write_log_line("Project not loaded")
                    self.update_progress(0)
                    return
                self.numcores.setEnabled(False)
                self.property_table.setEnabled(False)
                logger.debug("Launching analysis in batch")
                self.write_log_line("Analysis launched")
                response = requests.post(self.url + "/analyze")

                if response.status_code == 200:
                    self.update_progress(50)
                    # Start the thread
                    self.running = True
                    self.start()
                    self.analyze.setEnabled(False)
                    self.get_results.setEnabled(True)

                else:
                    self.write_log_line(f"Failed backend call: {self.url}") + "/analyze"
                    self.update_progress(100)
            else:
                self.write_log_line(response.json())
                self.update_progress(100)
        else:
            self.write_log_line(response.json())
            self.update_progress(100)

    def antenna_results(self):
        response = requests.get(self.url + "/get_status")
        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        else:
            self.update_progress(25)
            sparam_response = requests.get(self.url + "/scattering_results")
            self.update_progress(50)
            if not sparam_response.ok:
                msg = f"Failed backend call: {self.url}" + "/scattering_results"
                logger.debug(msg)
                self.write_log_line(msg)
            else:
                sparam = sparam_response.json()
                msg = "Scattering data obtained."
                logger.debug(msg)
                self.write_log_line(msg)
                if not self.touchstone_graph:
                    self.touchstone_graph = pg.PlotWidget()
                    self.results.addWidget(self.touchstone_graph)

                name = "Simulation"
                freq = sparam[0]
                val = sparam[1]
                # plot data: x, y values
                self.touchstone_graph.plot(
                    freq,
                    val,
                    pen=line_colors[self.color],
                    name=name,
                )
                self.touchstone_graph.setTitle("Scattering Plot")
                self.touchstone_graph.setLabel(
                    "bottom",
                    "Frequency GHz",
                )
                self.touchstone_graph.setLabel(
                    "left",
                    "Value in dB",
                )
            farfield_response = requests.get(self.url + "/farfield_results")
            self.update_progress(75)
            if not farfield_response.ok:
                msg = f"Failed backend call: {self.url}" + "/farfield_results"
                logger.debug(msg)
                self.write_log_line(msg)
            else:
                farfield = farfield_response.json()
                msg = "Farfield data obtained."
                logger.debug(msg)
                self.write_log_line(msg)
                if not self.antenna1widget:
                    self.antenna1widget = pg.PlotWidget()
                    line = self._add_line(
                        "combo_phi",
                        "combo_phi_box",
                        "Phi",
                        "combo",
                        farfield[0],
                    )
                    self.checked_overlap_1 = QtWidgets.QCheckBox()
                    self.checked_overlap_1.setObjectName("checked_overlap_1")
                    self.checked_overlap_1.setChecked(True)
                    self.checked_overlap_1.setText("Overlap Plot")
                    line.addWidget(self.checked_overlap_1)
                    self.results.addLayout(line)
                    self.results.addWidget(self.antenna1widget)

                self.theta = farfield[1]
                self.val_theta = farfield[2]

                self.antenna1widget.plot(
                    self.theta,
                    self.val_theta[0],
                    pen=line_colors[self.color],
                    name=name,
                )
                self.antenna1widget.setTitle("Realized gain at Phi {}".format(farfield[0][0]))
                self.antenna1widget.setLabel(
                    "left",
                    "Realized Gain",
                )
                self.antenna1widget.setLabel(
                    "bottom",
                    "Theta",
                )
                if not self.antenna2widget:
                    line2 = self._add_line(
                        "combo_theta",
                        "combo_theta_box",
                        "Theta",
                        "combo",
                        farfield[3],
                    )
                    self.checked_overlap_2 = QtWidgets.QCheckBox()
                    self.checked_overlap_2.setObjectName("checked_overlap_2")
                    self.checked_overlap_2.setChecked(True)
                    self.checked_overlap_2.setText("Overlap Plot")
                    line2.addWidget(self.checked_overlap_2)
                    self.results.addLayout(line2)

                    self.antenna2widget = pg.PlotWidget()
                    self.results.addWidget(self.antenna2widget)

                self.phi = farfield[4]
                self.val_phi = farfield[5]
                # plot data: x, y values
                self.antenna2widget.plot(
                    self.phi,
                    self.val_phi[0],
                    pen=line_colors[self.color],
                    name=name,
                )
                self.antenna2widget.setTitle("Realized gain at Theta {}".format(farfield[3][0]))
                self.antenna2widget.setLabel(
                    "left",
                    "Realized Gain",
                )
                self.antenna2widget.setLabel(
                    "bottom",
                    "Phi",
                )
                self.combo_phi_box.currentTextChanged.connect(self.update_phi)
                self.combo_theta_box.currentTextChanged.connect(self.update_theta)

            self.get_results.setEnabled(False)
            self.update_progress(100)

    def get_hfss_model(self):
        response = requests.get(self.url + "/get_hfss_model")
        msg = "Getting HFSS model"
        logger.debug(msg)
        self.write_log_line(msg)
        if not response.ok:
            msg = f"Failed backend call: {self.url}" + "/get_hfss_model"
            logger.debug(msg)
            self.write_log_line(msg)
            self.update_progress(100)
            return
        else:
            model_info = response.json()
            self.plotter = BackgroundPlotter(show=False)
            for element in model_info:
                # Decode response
                encoded_data = model_info[element][0]
                encoded_data_bytes = bytes(encoded_data, "utf-8")
                decoded_data = base64.b64decode(encoded_data_bytes)
                # Create obj file locally
                file_path = os.path.join(self.temp_folder, element + ".obj")
                with open(file_path, "wb") as f:
                    f.write(decoded_data)
                # Create PyVista object
                if not os.path.exists(file_path):
                    return

                cad_mesh = pv.read(file_path)

                cad_actor = self.plotter.add_mesh(
                    cad_mesh, color=model_info[element][1], show_scalar_bar=False, opacity=model_info[element][2]
                )

            self.plotter.clear_button_widgets()

            self.antenna_hfss_model = QtWidgets.QVBoxLayout()

            self.antenna_hfss_model.addWidget(self.plotter.app_window)
            self.image_layout.addLayout(self.antenna_hfss_model, 0, 0, 1, 1)
            self.plotter.show()

            msg = "HFSS model plotted"
            logger.debug(msg)
            self.write_log_line(msg)

    def _add_header(self, antenna_name, frequency):
        if self.toolkit_tab.count() == 3:
            self.toolkit_tab.setCurrentIndex(0)
        else:
            self.toolkit_tab.setCurrentIndex(1)

        self._clear_antenna_settings(self.antenna_settings_layout)
        self._clear_antenna_settings(self.image_layout)

        # Antenna settings
        top_spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.antenna_settings_layout.addItem(top_spacer, 2, 0, 1, 1)

        line1 = self._add_line("line_1", "antenna_name", "Antenna Name", "edit", antenna_name)
        self.antenna_settings_layout.addLayout(line1, 3, 0, 1, 1)

        if not isinstance(frequency, list):
            line2 = self._add_line("line_2", "frequency", "Frequency", "edit", str(frequency))
            self.antenna_settings_layout.addLayout(line2, 4, 0, 1, 1)
        elif len(frequency) == 2:
            line2 = self._add_line("line_2", "start_frequency", "Start frequency", "edit", str(frequency[0]))
            self.antenna_settings_layout.addLayout(line2, 4, 0, 1, 1)
            line2 = self._add_line("line_2", "stop_frequency", "Stop frequency", "edit", str(frequency[1]))
            self.antenna_settings_layout.addLayout(line2, 5, 0, 1, 1)

    def _clear_antenna_settings(self, layout):
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
                self._clear_antenna_settings(item.layout())

            # remove the item from layout
            layout.removeItem(item)
        self.parameters = {}

    def _add_image(self, image_path):
        """Add the image to antenna settings."""
        line_0_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        line_0 = QtWidgets.QHBoxLayout()
        line_0.setObjectName("line_0")
        line_0.addItem(line_0_spacer)

        antenna_image = QtWidgets.QLabel()
        antenna_image.setObjectName("antenna_image")
        antenna_image.setMaximumHeight(self.centralwidget.height() / 2)
        antenna_image.setScaledContents(True)
        antenna_image.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        _pixmap = QtGui.QPixmap(image_path)
        _pixmap = _pixmap.scaled(
            antenna_image.width(),
            antenna_image.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        antenna_image.setPixmap(_pixmap)

        line_0.addWidget(antenna_image)
        line_0_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        line_0.addItem(line_0_spacer)
        return line_0

    def _add_line(self, title, variable_value, label_value, line_type, value, add_paramers=True):
        """Add a new parameter to antenna settings."""
        self.__dict__[title] = QtWidgets.QHBoxLayout()
        line = self.__dict__[title]
        line.setObjectName(title)

        label = QtWidgets.QLabel()
        label.setObjectName("{}_label".format(title))
        line.addWidget(label)
        label.setText(label_value)
        font = QtGui.QFont("Arial", 12)
        label.setFont(font)
        spacer = QtWidgets.QSpacerItem(
            40 - len(title), 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        line.addItem(spacer)
        if line_type == "edit":
            name = "{}".format(variable_value)
            self.__dict__[name] = QtWidgets.QLineEdit()
            edit = self.__dict__[name]
            edit.setObjectName(name)
            edit.setFont(font)
            edit.setText(value)
            edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            line.addWidget(edit)
        elif line_type == "combo":
            name = "{}".format(variable_value)
            self.__dict__[name] = QtWidgets.QComboBox()
            edit = self.__dict__[name]
            edit.setObjectName(name)
            edit.setFont(font)
            for v in value:
                edit.addItem(str(v))

            line.addWidget(edit)
        if add_paramers:
            self.parameters[name] = edit
        return line

    def _add_footer(self, method_name):
        line5 = self._add_line(
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
        self.antenna_settings_layout.addLayout(line5, 7, 0, 1, 1)
        line6 = self._add_line("line_6", "x_position", "Origin X Position", "edit", "0.0")
        self.antenna_settings_layout.addLayout(line6, 8, 0, 1, 1)
        line7 = self._add_line("line_7", "y_position", "Origin Y Position", "edit", "0.0")
        self.antenna_settings_layout.addLayout(line7, 9, 0, 1, 1)
        line8 = self._add_line("line_8", "z_position", "Origin Z Position", "edit", "0.0")
        self.antenna_settings_layout.addLayout(line8, 10, 0, 1, 1)
        line9 = self._add_line("line_9", "coordinate_system", "Coordinate System", "edit", "Global")
        self.antenna_settings_layout.addLayout(line9, 11, 0, 1, 1)
        bottom_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.antenna_settings_layout.addItem(bottom_spacer, 12, 0, 1, 1)
        line_buttons = self.add_antenna_buttons(method_name)
        self.antenna_settings_layout.addLayout(line_buttons, 13, 0, 1, 1)

    def update_phi(self):
        """Update Gain Total Plot by changing the Phi value."""
        try:
            selected_phi = float(self.combo_phi_box.currentText())
            index = self.phi.index(selected_phi)
            if not self.checked_overlap_1.isChecked():
                self.antenna1widget.clear()
            self.antenna1widget.plot(self.theta, self.val_theta[index], pen=line_colors[self.color])
        except:
            pass

    def update_theta(self):
        """Update Gain Total Plot by changing the Theta value."""
        try:
            selected_theta = float(self.combo_theta_box.currentText())
            index = self.theta.index(selected_theta)
            if not self.checked_overlap_2.isChecked():
                self.antenna2widget.clear()
            self.antenna2widget.plot(self.phi, self.val_phi[index], pen=line_colors[self.color])
        except:
            pass
