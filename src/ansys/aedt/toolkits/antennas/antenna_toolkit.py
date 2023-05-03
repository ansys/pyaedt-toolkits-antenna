# -*- coding: utf-8 -*-
import os
from pathlib import Path
import re
import sys

import ansys.aedt.toolkits.antennas.common_ui
from ansys.aedt.toolkits.antennas.common_ui import RunnerAnalsysis
from ansys.aedt.toolkits.antennas.common_ui import RunnerHfss
from ansys.aedt.toolkits.antennas.common_ui import XStream
from ansys.aedt.toolkits.antennas.common_ui import active_sessions
from ansys.aedt.toolkits.antennas.common_ui import handler
from ansys.aedt.toolkits.antennas.common_ui import line_colors
from ansys.aedt.toolkits.antennas.common_ui import logger

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
package_path = current_path.parents[3]
sys.path.append(os.path.abspath(package_path))
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from pyaedt import Hfss
from pyaedt.misc import list_installed_ansysem
import pyqtgraph as pg
import qdarkstyle

from ansys.aedt.toolkits.antennas.models.bowtie import BowTie
from ansys.aedt.toolkits.antennas.models.bowtie import BowTieRounded
from ansys.aedt.toolkits.antennas.models.bowtie import BowTieSlot
from ansys.aedt.toolkits.antennas.models.conical_spiral import Archimedean
from ansys.aedt.toolkits.antennas.models.helix import AxialMode
from ansys.aedt.toolkits.antennas.models.horn import Conical
from ansys.aedt.toolkits.antennas.models.horn import Corrugated
from ansys.aedt.toolkits.antennas.models.horn import EPlane
from ansys.aedt.toolkits.antennas.models.horn import Elliptical
from ansys.aedt.toolkits.antennas.models.horn import HPlane
from ansys.aedt.toolkits.antennas.models.horn import Pyramidal
from ansys.aedt.toolkits.antennas.models.horn import PyramidalRidged
from ansys.aedt.toolkits.antennas.models.horn import QuadRidged
from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchEdge
from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchInset
from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchProbe
from ansys.aedt.toolkits.antennas.ui.antennas_main import Ui_MainWindow

images_path = os.path.join(os.path.dirname(__file__), "ui", "images")
os.environ["QT_API"] = "pyside6"

import logging

handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, desktop_pid=None, desktop_version=None):
        super(ApplicationWindow, self).__init__()
        self.__thread = QtCore.QThreadPool()
        self.__thread.setMaxThreadCount(4)
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
            os.path.join(images_path, "logo_cropped.png"),
            QtCore.QSize(),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        icon.addFile(
            os.path.join(images_path, "logo_cropped.png"),
            QtCore.QSize(),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        self.setWindowIcon(icon)

        self.menubar.setFont(self._font)
        self.setWindowTitle("PyAEDT Antenna Wizard")
        self.length_unit = ""
        self.create_button = None

        self.release_and_exit_button.clicked.connect(self.release_and_close)
        self.release_button.clicked.connect(self.release_only)
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
        for ver in list_installed_ansysem():
            ver = "20{}.{}".format(
                ver.replace("ANSYSEM_ROOT", "")[:2], ver.replace("ANSYSEM_ROOT", "")[-1]
            )
            self.aedt_version_combo.addItem(ver)
        self.aedt_version_combo.currentTextChanged.connect(self.find_process_ids)
        self.browse_project.clicked.connect(self.browse_for_project)

        tc = self.log_text.textCursor()
        tc.setPosition(self.log_text.document().characterCount())
        self.log_text.setTextCursor(tc)
        XStream.stdout().messageWritten.connect(lambda value: self.write_log_line(value))
        XStream.stderr().messageWritten.connect(lambda value: self.write_log_line(value))
        self.find_process_ids()
        self.antenna1widget = None
        self.antenna2widget = None
        self.touchstone_graph = None
        self.color = -1
        self.actionRectangular_with_probe.triggered.connect(
            lambda checked: self.draw_rectangular_probe_ui()
        )
        self.actionConical.triggered.connect(lambda checked: self.draw_conical_horn_ui())
        self.actionConical_Corrugated.triggered.connect(
            lambda checked: self.draw_conical_horn_corrugated_ui()
        )
        self.actionElliptical.triggered.connect(lambda checked: self.draw_elliptical_horn_ui())
        self.actionE_Plane.triggered.connect(lambda checked: self.draw_eplane_horn_ui())
        self.actionH_Plane.triggered.connect(lambda checked: self.draw_hplane_horn_ui())
        self.actionPyramidal.triggered.connect(lambda checked: self.draw_pyramidal_horn_ui())
        self.actionPyramidal_Ridged.triggered.connect(
            lambda checked: self.draw_pyramidal_rid_horn_ui()
        )
        self.actionQuad_Ridged.triggered.connect(lambda checked: self.draw_quad_ridged_horn_ui())
        self.actionAxial.triggered.connect(lambda checked: self.draw_axial_helix_ui())
        self.actionRectangular_Edge.triggered.connect(
            lambda checked: self.draw_rectangular_probe_edge_ui()
        )
        self.actionRectangular_Inset.triggered.connect(
            lambda checked: self.draw_rectangular_probe_inset_ui()
        )
        self.actionBowtieSlot.triggered.connect(lambda checked: self.draw_bowtie_slot_ui())
        self.actionBowtieNormal.triggered.connect(lambda checked: self.draw_bowtie_normal_ui())
        self.actionBowtieRounded.triggered.connect(lambda checked: self.draw_bowtie_rounded_ui())
        self.actionArchimedean.triggered.connect(lambda checked: self.draw_conical_archimedean_ui())
        self.actionLog.triggered.connect(lambda checked: self.draw_conical_log_ui())
        self.actionSinous.triggered.connect(lambda checked: self.draw_conical_sinuous_ui())
        self.actionPlanar.triggered.connect(lambda checked: self.draw_dipole_planar_ui())
        self.actionWire.triggered.connect(lambda checked: self.draw_dipole_wire_ui())
        self.actionLog_Periodic_Array.triggered.connect(
            lambda checked: self.draw_log_periodic_array_ui()
        )
        self.actionLog_Trap.triggered.connect(lambda checked: self.draw_log_periodic_trap_ui())

        self.actionLog_Tooth.triggered.connect(lambda checked: self.draw_log_periodic_tooth_ui())
        self.actionBicone.triggered.connect(lambda checked: self.draw_bicone_ui())
        self.actionDiscone.triggered.connect(lambda checked: self.draw_discone_ui())
        self.actionBlade.triggered.connect(lambda checked: self.draw_blade_ui())
        self.actionWire_2.triggered.connect(lambda checked: self.draw_wire_monopole_ui())
        self.actionWire_with_Infinite_Gnd.triggered.connect(
            lambda checked: self.draw_wire_monopole_inf_gnd_ui()
        )
        self.actionCircular_Disc.triggered.connect(
            lambda checked: self.draw_monopole_circuilar_disc_ui()
        )
        self.actionElliptical_Base_Strip.triggered.connect(
            lambda checked: self.draw_monopole_elliptical_ui()
        )
        self.actionVertical_Trapezoidal.triggered.connect(
            lambda checked: self.draw_monopole_trapezoid_ui()
        )
        self.actionPlanar_Inverted.triggered.connect(lambda checked: self.draw_pifa_planar_ui())
        self.actionShorting_Pin.triggered.connect(lambda checked: self.draw_pifa_shorting_pin_ui())
        self.actionShorting_Plate.triggered.connect(
            lambda checked: self.draw_pifa_shorting_plate_ui()
        )
        self.actionPlanar_Archimedean.triggered.connect(
            lambda checked: self.draw_pspiral_archimedean_ui()
        )
        self.actionPlanar_Archimedean_Cavity.triggered.connect(
            lambda checked: self.draw_pspiral_archimedean_cavity_ui()
        )
        self.actionPlanar_Log.triggered.connect(lambda checked: self.draw_pspiral_log_ui())
        self.actionPlanar_Log_Cavity.triggered.connect(
            lambda checked: self.draw_pspiral_log_cavity_ui()
        )
        self.actionPlanar_Sinous.triggered.connect(lambda checked: self.draw_pspiral_sinuous_ui())
        self.actionPlanar_Sinous_Cavity.triggered.connect(
            lambda checked: self.draw_pspiral_sinuous_cavity_ui()
        )
        self.actionVivaldi_2.triggered.connect(lambda checked: self.draw_vivaldi_ui())
        self.actionVivaldi_Stepped.triggered.connect(lambda checked: self.draw_vivaldi_stepper_ui())
        self.actionSlot_Gap.triggered.connect(lambda checked: self.draw_slot_gap_ui())
        self.actionSlot_T_Bar.triggered.connect(lambda checked: self.draw_slot_tbar_ui())
        self.actionSlot_Microstrip.triggered.connect(lambda checked: self.draw_slot_microstrip_ui())
        self.actionSlot_Cavity_Backed_Array.triggered.connect(
            lambda checked: self.draw_slot_cavity_ui()
        )
        self.actionElliptical_Edge_2.triggered.connect(
            lambda checked: self.draw_patch_elliptical_edge_ui()
        )
        self.actionElliptical_Inset.triggered.connect(
            lambda checked: self.draw_patch_elliptical_inset_ui()
        )
        self.actionElliptical_with_Probe.triggered.connect(
            lambda checked: self.draw_patch_elliptical_probe_ui()
        )

        self.sweep_slider.valueChanged.connect(self.value_changed)
        if desktop_pid or desktop_version:
            self.launch_hfss(desktop_pid, desktop_version)

    def value_changed(self):
        self.slider_value.setText(str(self.sweep_slider.value()))

    def write_log_line(self, value):
        self.log_text.insertPlainText(value)
        tc = self.log_text.textCursor()
        tc.setPosition(self.log_text.document().characterCount())
        self.log_text.setTextCursor(tc)

    def update_project(self):
        sel = self.property_table.selectedItems()
        if sel and self.oantenna:
            sel_key = self.property_table.item(self.property_table.row(sel[0]), 0).text()
            key = self.oantenna.synthesis_parameters.__getattribute__(sel_key).hfss_variable
            val = self.property_table.item(self.property_table.row(sel[0]), 1).text()
        else:
            return
        if self.hfss and sel and key in self.hfss.variable_manager.independent_variable_names:
            ratio_re = re.compile("|".join(["ratio", "coefficient", "points", "number"]))
            if "angle" in key:
                if "deg" not in val:
                    val = val + "deg"
            elif ratio_re.search(key):
                val = val
            else:
                if self.oantenna.length_unit not in val:
                    val = val + self.oantenna.length_unit
            self.hfss[key] = val
            ansys.aedt.toolkits.antennas.common_ui.logger.info(
                "Key {} updated to value {}.".format(key, val)
            )
            self.add_status_bar_message("Project updated.")

    def browse_for_project(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontConfirmOverwrite, True)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        fileName, _ = dialog.getOpenFileName(
            self,
            "Open or create new aedt file",
            "",
            "Aedt Files (*.aedt)",
        )
        if fileName:
            self.project_name.setText(fileName)

    def find_process_ids(self):
        self.process_id_combo.clear()
        self.process_id_combo.addItem("Create New Session")
        sessions = active_sessions(version=self.aedt_version_combo.currentText())
        for session in sessions:
            if session[1] == -1:
                self.process_id_combo.addItem("Process {}".format(session[0], session[1]))
            else:
                self.process_id_combo.addItem(
                    "Process {} on gRPC {}".format(session[0], session[1])
                )

    def launch_hfss(self, pid=None, version=None):
        non_graphical = eval(self.non_graphical_combo.currentText())
        if version is None:
            version = self.aedt_version_combo.currentText()
        if pid:
            selected_process = "Process {}".format(pid)
        else:
            selected_process = self.process_id_combo.currentText()
        projectname = self.project_name.text()
        process_id_combo_splitted = selected_process.split(" ")
        args = {
            "non_graphical": non_graphical,
            "version": version,
            "selected_process": selected_process,
            "projectname": projectname,
            "process_id_combo_splitted": process_id_combo_splitted,
        }
        print(args)
        if self.hfss:
            try:
                self.hfss.release_desktop(False, False)
            except:
                pass
        worker_1 = RunnerHfss()
        worker_1.hfss_args = args
        worker_1.signals.progressed.connect(lambda value: self.update_progress(value))
        worker_1.signals.completed.connect(lambda: self.update_hfss(worker_1, version))

        self.__thread.start(worker_1)
        pass

    def update_progress(self, value):
        self.progressBar.setValue(value)
        if self.progressBar.isHidden():
            self.progressBar.setVisible(True)

    def update_hfss(
        self,
        worker_1,
        version=None,
    ):
        if worker_1.pid != -1:
            module = sys.modules["__main__"]
            try:
                del module.COMUtil
            except AttributeError:
                pass
            try:
                del module.oDesktop
            except AttributeError:
                pass
            try:
                del module.pyaedt_initialized
            except AttributeError:
                pass
            try:
                del module.oAnsoftApplication
            except AttributeError:
                pass
            if version is None:
                version = self.aedt_version_combo.currentText()

            self.hfss = Hfss(
                specified_version=version,
                projectname=worker_1.projectname,
                designname=worker_1.designname,
                aedt_process_id=worker_1.pid,
            )
        else:
            self.hfss = worker_1.hfss
        self.update_progress(100)

    def analyze_antenna(self):
        """Solves current report and plots antenna results."""
        self.add_status_bar_message("Analysis started.")
        if self.progressBar.value() < 100:
            self.add_status_bar_message("Waiting for previous process to terminate.")
            return
        self.update_progress(25)
        self.color += 1
        if self.color == 5:
            self.color = 0
        # if not self.hfss:
        #     self.launch_hfss()
        num_cores = self.numcores.text()
        self.hfss.save_project()
        project_file = self.hfss.results_directory[:-7]
        design_name = self.hfss.design_name
        self.hfss.solve_in_batch(run_in_thread=True, machine="localhost", num_cores=num_cores)
        self.update_progress(50)
        if self.hfss.last_run_log:
            worker_1 = RunnerAnalsysis()
            worker_1.logger_file = self.hfss.last_run_log
            worker_1.signals.messaged.connect(
                lambda value: ansys.aedt.toolkits.antennas.common_ui.logger.info(value)
            )
            worker_1.signals.completed.connect(
                lambda: self._udpdate_results(project_file, design_name)
            )
            self.__thread.start(worker_1)

    def _udpdate_results(self, project_file, design_name):
        self.update_progress(75)
        self.hfss.load_project(project_file, design_name=design_name)

        name = "Simulation {}".format(self.color)
        sol_data = self.hfss.post.get_solution_data()
        if not sol_data:
            return
        if not self.touchstone_graph:
            self.touchstone_graph = pg.PlotWidget()
            self.results.addWidget(self.touchstone_graph)
        freq = sol_data.primary_sweep_values
        val = sol_data.data_db20()
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

        self.field_solution = self.hfss.post.get_solution_data(
            "GainTotal",
            self.hfss.nominal_adaptive,
            primary_sweep_variable="Theta",
            context="3D",
            report_category="Far Fields",
        )

        if not self.antenna1widget:
            self.antenna1widget = pg.PlotWidget()
            line = self.add_line(
                "combo_phi",
                "combo_phi_box",
                "Phi",
                "combo",
                self.field_solution.intrinsics["Phi"],
            )
            self.checked_overlap_1 = QtWidgets.QCheckBox()
            self.checked_overlap_1.setObjectName("checked_overlap_1")
            self.checked_overlap_1.setChecked(True)
            self.checked_overlap_1.setText("Overlap Plot")
            line.addWidget(self.checked_overlap_1)
            self.results.addLayout(line)
            self.results.addWidget(self.antenna1widget)

        theta = self.field_solution.primary_sweep_values
        val = self.field_solution.data_db20()
        # plot data: x, y values
        self.antenna1widget.plot(
            theta,
            val,
            pen=line_colors[self.color],
            name=name,
        )
        self.antenna1widget.setTitle(
            "Realized gain at Phi {}".format(self.field_solution.intrinsics["Phi"][0])
        )
        self.antenna1widget.setLabel(
            "left",
            "Realized Gain",
        )
        self.antenna1widget.setLabel(
            "bottom",
            "Theta",
        )
        if not self.antenna2widget:
            line2 = self.add_line(
                "combo_theta",
                "combo_theta_box",
                "Theta",
                "combo",
                self.field_solution.intrinsics["Theta"],
            )
            self.checked_overlap_2 = QtWidgets.QCheckBox()
            self.checked_overlap_2.setObjectName("checked_overlap_2")
            self.checked_overlap_2.setChecked(True)
            self.checked_overlap_2.setText("Overlap Plot")
            line2.addWidget(self.checked_overlap_2)
            self.results.addLayout(line2)

            self.antenna2widget = pg.PlotWidget()
            self.results.addWidget(self.antenna2widget)

        self.field_solution.primary_sweep = "Phi"
        phi = self.field_solution.primary_sweep_values
        val = self.field_solution.data_db20()
        # plot data: x, y values
        self.antenna2widget.plot(
            phi,
            val,
            pen=line_colors[self.color],
            name=name,
        )
        self.antenna2widget.setTitle(
            "Realized gain at Theta {}".format(self.field_solution.intrinsics["Theta"][0])
        )
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
        self.update_progress(100)
        self.add_status_bar_message("Analysis Completed.")

    def update_phi(self):
        """Update Gain Total Plot by changing the Phi value."""
        try:
            self.field_solution.primary_sweep = "Theta"
            theta = self.field_solution.primary_sweep_values
            self.field_solution.active_intrinsic["Phi"] = float(self.combo_phi_box.currentText())
            val = self.field_solution.data_db20()
            # plot data: x, y values
            if not self.checked_overlap_1.isChecked():
                self.antenna1widget.clear()
            self.antenna1widget.plot(theta, val, pen=line_colors[self.color])
        except:
            pass

    def update_theta(self):
        """Update Gain Total Plot by changing the Theta value."""
        try:
            self.field_solution.primary_sweep = "Phi"
            phi = self.field_solution.primary_sweep_values
            self.field_solution.active_intrinsic["Theta"] = float(
                self.combo_theta_box.currentText()
            )
            val = self.field_solution.data_db20()
            if not self.checked_overlap_2.isChecked():
                self.antenna2widget.clear()
            self.antenna2widget.plot(phi, val, pen=line_colors[self.color])
        except:
            pass

    def add_status_bar_message(self, message):
        """Add a status bar message.

        Parameters
        ----------
        message : str
           Text for the status bar message.

        """
        myStatus = QtWidgets.QStatusBar()
        myStatus.showMessage(message, 3000000)
        self.setStatusBar(myStatus)

    def release_only(self):
        """Release AEDT."""
        if self.hfss:
            self.hfss.release_desktop(False, False)
        self.close()

    def release_and_close(self):
        """Release AEDT."""
        if self.hfss:
            self.hfss.release_desktop(True, True)
        self.close()

    def get_antenna(self, antenna, synth_only=False):
        """Synthesize and create the antenna in HFSS.

        Parameters
        ----------
        antenna : :class:
            Type of antenna to create.
        synth_only : bool, optional
            Whether to only synthesize the anttena. The default is ``False``.
        """
        if self.progressBar.value() < 100:
            self.add_status_bar_message("Waiting for the previous process to terminate.")
            return
        self.progressBar.setValue(0)
        self.property_table.itemChanged.connect(None)

        if not self.hfss:
            self.add_status_bar_message("Launch HFSS.")
        component3d = self.component_3d.isChecked()
        create_setup = self.create_hfss_setup.isChecked()
        lattice_pair = self.lattice_pair.isChecked()
        model_units = self.units.currentText()
        frequnits = self.frequnits.currentText()
        if not self.oantenna:
            self.oantenna = self.hfss.add_from_toolkit(
                antenna,
                draw=False,
                frequency_unit=frequnits,
                length_unit=model_units,
            )
        self.progressBar.setValue(33)

        x_pos = float(self.x_position.text())
        y_pos = float(self.y_position.text())
        z_pos = float(self.z_position.text())
        self.oantenna.origin = [x_pos, y_pos, z_pos]
        if "frequency" in self.__dir__():
            self.oantenna.frequency = float(self.frequency.text())
        elif "start_frequency" in self.__dir__() and "stop_frequency" in self.__dir__():
            self.oantenna.start_frequency = float(self.start_frequency.text())
            self.oantenna.stop_frequency = float(self.stop_frequency.text())
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
                self.oantenna.init_model()
                self.oantenna.model_hfss()
                self.oantenna.setup_hfss()
            if component3d:
                self.oantenna.create_3dcomponent(replace=True)
            if create_setup:
                freq = float(self.oantenna.frequency)
                setup = self.hfss.create_setup()
                setup.props["Frequency"] = str(freq) + frequnits
                if int(self.sweep_slider.value()) > 0:
                    sweep1 = setup.add_sweep()
                    perc_sweep = (int(self.sweep_slider.value())) / 100
                    sweep1.props["RangeStart"] = str(freq * (1 - perc_sweep)) + frequnits
                    sweep1.props["RangeEnd"] = str(freq * (1 + perc_sweep)) + frequnits
                    sweep1.update()
            self.create_button.setEnabled(False)
        self.progressBar.setValue(66)

        self.property_table.setRowCount(len(self.oantenna._parameters.items()))
        i = 0
        __sortingEnabled = self.property_table.isSortingEnabled()
        self.property_table.setSortingEnabled(False)
        self.property_table.setRowCount(len(self.oantenna._parameters.values()))
        for par, value in self.oantenna._parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.property_table.setItem(i, 0, item)
            ratio_re = re.compile("|".join(["ratio", "coefficient", "points", "number"]))
            if "angle" in par:
                item = QtWidgets.QTableWidgetItem(str(round(value, 3)) + "deg")
            elif ratio_re.search(par):
                item = QtWidgets.QTableWidgetItem(str(round(value, 3)))
            else:
                item = QtWidgets.QTableWidgetItem(str(round(value, 3)) + self.oantenna.length_unit)
            self.property_table.setItem(i, 1, item)
            i += 1

        self.property_table.setSortingEnabled(__sortingEnabled)
        self.hfss.modeler.fit_all()
        if synth_only:
            self.add_status_bar_message("Synthesis completed.")
        else:
            self.add_status_bar_message("Project created correctly.")
            self.property_table.itemChanged.connect(self.update_project)
        self.progressBar.setValue(100)

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

    def add_line(self, title, variable_value, label_value, line_type, value, add_paramers=True):
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
            40, 20, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )
        line.addItem(spacer)
        if line_type == "edit":
            name = "{}".format(variable_value)
            self.__dict__[name] = QtWidgets.QLineEdit()
            edit = self.__dict__[name]
            edit.setObjectName(name)
            edit.setFont(self._font)
            edit.setText(value)
            edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            line.addWidget(edit)
        elif line_type == "combo":
            name = "{}".format(variable_value)
            self.__dict__[name] = QtWidgets.QComboBox()
            edit = self.__dict__[name]
            edit.setObjectName(name)
            edit.setFont(self._font)
            for v in value:
                edit.addItem(str(v))

            line.addWidget(edit)
        if add_paramers:
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

        antenna_image.setMaximumHeight(self.centralwidget.height() / 3)
        antenna_image.setScaledContents(True)
        _pixmap = QtGui.QPixmap(image_path)
        _pixmap = _pixmap.scaled(
            antenna_image.width(),
            antenna_image.height(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        antenna_image.setPixmap(_pixmap)

        line_0.addWidget(antenna_image)

        line_0_spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )

        line_0.addItem(line_0_spacer)
        return line_0

    def add_antenna_buttons(self, method_create):
        """Add buttons to antenna settings."""
        line_buttons = QtWidgets.QHBoxLayout()
        line_buttons.setObjectName("line_buttons")

        synth_button = QtWidgets.QPushButton()
        synth_button.setObjectName("synth_button")
        synth_button.setFont(self._font)
        synth_button.setMinimumSize(QtCore.QSize(100, 40))

        line_buttons.addWidget(synth_button)

        line_buttons_spacer = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        line_buttons.addItem(line_buttons_spacer)
        self.create_button = QtWidgets.QPushButton()
        self.create_button.setObjectName("create_button")
        self.create_button.setFont(self._font)
        self.create_button.setMinimumSize(QtCore.QSize(160, 40))

        line_buttons.addWidget(self.create_button)

        synth_button.setText("Synthesis")
        self.create_button.setText("Create Hfss Project")
        synth_button.clicked.connect(lambda: method_create(True))
        self.create_button.clicked.connect(lambda: method_create(False))
        return line_buttons

    def _add_header(self, image_name, antenna_name, frequency):
        self.tabWidget.setCurrentIndex(1)
        self.clear_antenna_settings(self.layout_settings)

        top_spacer = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )

        self.layout_settings.addItem(top_spacer, 2, 0, 1, 1)

        image = self.add_image(os.path.join(images_path, image_name))
        self.layout_settings.addLayout(image, 0, 0, 1, 1)

        line1 = self.add_line("line_1", "antenna_name", "Antenna Name", "edit", antenna_name)
        self.layout_settings.addLayout(line1, 3, 0, 1, 1)

        if not isinstance(frequency, list):
            line2 = self.add_line("line_2", "frequency", "Frequency", "edit", str(frequency))
            self.layout_settings.addLayout(line2, 4, 0, 1, 1)
        elif len(frequency) == 2:
            line2 = self.add_line(
                "line_2", "start_frequency", "Start frequency", "edit", str(frequency[0])
            )
            self.layout_settings.addLayout(line2, 4, 0, 1, 1)
            line3 = self.add_line(
                "line_2", "stop_frequency", "Stop frequency", "edit", str(frequency[1])
            )
            self.layout_settings.addLayout(line3, 5, 0, 1, 1)

        # line3 = self.add_line("line_2", "antenna_material", "Antenna Material", "combo",
        #                       ["pec", "copper", "aluminum", "steel"])
        # self.layout_settings.addLayout(line3, 5, 0, 1, 1)

    def _add_footer(self, method_name):
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
        self.layout_settings.addLayout(line5, 10, 0, 1, 1)
        line6 = self.add_line("line_6", "x_position", "Origin X Position", "edit", "0.0")
        self.layout_settings.addLayout(line6, 11, 0, 1, 1)
        line7 = self.add_line("line_7", "y_position", "Origin Y Position", "edit", "0.0")
        self.layout_settings.addLayout(line7, 12, 0, 1, 1)
        line8 = self.add_line("line_8", "z_position", "Origin Z Position", "edit", "0.0")
        self.layout_settings.addLayout(line8, 13, 0, 1, 1)
        line9 = self.add_line(
            "line_9", "coordinate_system", "Coordinate System", "combo", ["Global"]
        )
        if self.hfss:
            for cs in self.hfss.modeler.coordinate_systems:
                self.coordinate_system.addItem(cs.name)
        self.layout_settings.addLayout(line9, 14, 0, 1, 1)
        line_buttons = self.add_antenna_buttons(method_name)
        self.layout_settings.addLayout(line_buttons, 15, 0, 1, 1)
        bottom_spacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.layout_settings.addItem(bottom_spacer, 16, 0, 1, 1)

    def draw_rectangular_probe_ui(self):
        """Create a rectangular probe antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return
        self._add_header("Patch.png", "RectangularPatch", "10")

        line2 = self.add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            ["FR4_epoxy", "teflon_based", "Rogers RT/duroid 6002 (tm)"],
        )
        self.layout_settings.addLayout(line2, 6, 0, 1, 1)

        line4 = self.add_line("line_4", "substrate_height", "Subtsrate height", "edit", "0.254")
        self.layout_settings.addLayout(line4, 7, 0, 1, 1)

        self._add_footer(self.create_rectangular_probe_design)

    def create_rectangular_probe_design(self, synth_only=False):
        """Create a rectangular probe antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(RectangularPatchProbe, synth_only)

    def draw_rectangular_probe_inset_ui(self):
        """Create a rectangular probe patch antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return
        self._add_header("RectInset.jpg", "RectangularPatchInset", "10")

        line2 = self.add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            ["FR4_epoxy", "teflon_based", "Rogers RT/duroid 6002 (tm)"],
        )
        self.layout_settings.addLayout(line2, 6, 0, 1, 1)

        line4 = self.add_line("line_4", "substrate_height", "Subtsrate height", "edit", "0.254")
        self.layout_settings.addLayout(line4, 7, 0, 1, 1)

        self._add_footer(self.create_rectangular_probe_inset_design)

    def create_rectangular_probe_inset_design(self, synth_only=False):
        """Create a rectangular probe patch antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(RectangularPatchInset, synth_only)

    def draw_rectangular_probe_edge_ui(self):
        """Create a rectangular patch antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return
        self._add_header("RectEdge.jpg", "RectangularPatchEdge", "10")

        line2 = self.add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            ["FR4_epoxy", "teflon_based", "Rogers RT/duroid 6002 (tm)"],
        )
        self.layout_settings.addLayout(line2, 6, 0, 1, 1)

        line4 = self.add_line("line_4", "substrate_height", "Subtsrate height", "edit", "0.254")
        self.layout_settings.addLayout(line4, 7, 0, 1, 1)

        self._add_footer(self.create_rectangular_probe_edge_design)

    def create_rectangular_probe_edge_design(self, synth_only=False):
        """Create a rectangular patch antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(RectangularPatchEdge, synth_only)

    def draw_conical_horn_ui(self):
        """Create a conical horn antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return
        self._add_header("HornConical.jpg", "HornConical", "10")

        self._add_footer(self.create_conical_horn_design)

    def create_conical_horn_design(self, synth_only=False):
        """Create a conical horn antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(Conical, synth_only)

    def draw_axial_helix_ui(self):
        """Create an axial mode helix antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("AxialMode.jpg", "AxialMode", "10")
        line2 = self.add_line(
            "line_2",
            "gain_value",
            "Expected Gain (dB)",
            "edit",
            "10",
        )
        self.layout_settings.addLayout(line2, 6, 0, 1, 1)
        line3 = self.add_line(
            "line_3",
            "feeder_lenth",
            "Feeder Length",
            "edit",
            "10",
        )
        self.layout_settings.addLayout(line3, 7, 0, 1, 1)
        self._add_footer(self.create_axial_helic_design)

    def create_axial_helic_design(self, synth_only=False):
        """Create an axial mode helix antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(AxialMode, synth_only)

    def draw_bowtie_normal_ui(self):
        """Create a bowtie antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("Bowtie.jpg", "Bowtie", "10")

        line2 = self.add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            ["FR4_epoxy", "teflon_based", "Rogers RT/duroid 6002 (tm)"],
        )
        self.layout_settings.addLayout(line2, 6, 0, 1, 1)

        line4 = self.add_line("line_4", "substrate_height", "Subtsrate height", "edit", "0.254")
        self.layout_settings.addLayout(line4, 7, 0, 1, 1)
        self._add_footer(self.create_bowtie_normal_design)

    def create_bowtie_normal_design(self, synth_only=False):
        """Create a bowtie  antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """

        self.get_antenna(BowTie, synth_only)

    def draw_bowtie_rounded_ui(self):
        """Create a bowtie rounded antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("BowtieRounded.jpg", "BowtieRound", "10")
        line2 = self.add_line(
            "line_2",
            "material",
            "Substrate Material",
            "combo",
            ["FR4_epoxy", "teflon_based", "Rogers RT/duroid 6002 (tm)"],
        )
        self.layout_settings.addLayout(line2, 6, 0, 1, 1)

        line4 = self.add_line("line_4", "substrate_height", "Subtsrate height", "edit", "0.254")
        self.layout_settings.addLayout(line4, 7, 0, 1, 1)
        self._add_footer(self.create_bowtie_rounded_design)

    def create_bowtie_rounded_design(self, synth_only=False):
        """Create a bowtie rounded antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """

        self.get_antenna(BowTieRounded, synth_only)

    def draw_bowtie_slot_ui(self):
        """Create a bowtie slot antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("BowtieSlot.jpg", "BowtieSlot", "10")
        self._add_footer(self.create_bowtie_slot_design)

    def create_bowtie_slot_design(self, synth_only=False):
        """Create a bowtie slot antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(BowTieSlot, synth_only)

    def draw_conical_archimedean_ui(self):
        """Create a conical Archimedean antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("ConicalArchimedean.jpg", "Archimedean", ["4", "10"])
        self._add_footer(self.create_conical_archimedean_design)

    def create_conical_archimedean_design(self, synth_only=False):
        """Create a conical archimedean antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(Archimedean, synth_only)

    def draw_conical_log_ui(self):
        """Create a conical log antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("ConicalLog.jpg", "Archimedean", "10")
        self._add_footer(self.create_conical_log_design)

    def create_conical_log_design(self, synth_only=False):
        """Create a conical log antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_conical_sinuous_ui(self):
        """Create a conical sinuous antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("ConicalSinuous.jpg", "Archimedean", "10")
        self._add_footer(self.create_conical_sinuous_design)

    def create_conical_sinuous_design(self, synth_only=False):
        """Create a conical sinuous antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_dipole_planar_ui(self):
        """Create a planar dipole antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarDipole.jpg", "PlanarDipole", "10")
        self._add_footer(self.create_planar_dipole_design)

    def create_planar_dipole_design(self, synth_only=False):
        """Create a planar dipole antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_dipole_wire_ui(self):
        """Create a wire dipole antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("WireDipole.jpg", "PlanarDipole", "10")
        self._add_footer(self.create_wire_dipole_design)

    def create_wire_dipole_design(self, synth_only=False):
        """Create a wire dipole antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_conical_horn_corrugated_ui(self):
        """Create a conical horn corrugated antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornConicalCorrugated.jpg", "HornCorrugated", "10")
        self._add_footer(self.create_horn_corrugated_design)

    def create_horn_corrugated_design(self, synth_only=False):
        """Create a conical horn corrugated antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(Corrugated, synth_only)

    def draw_eplane_horn_ui(self):
        """Create an E-plane horn antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornEPlane.jpg", "HornEPlane", "10")
        self._add_footer(self.create_horn_eplane_design)

    def create_horn_eplane_design(self, synth_only=False):
        """Create an E-plane horn antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(EPlane, synth_only)

    def draw_hplane_horn_ui(self):
        """Create an H-plane horn antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornHPlane.jpg", "HornHPlane", "10")
        self._add_footer(self.create_horn_hplane_design)

    def create_horn_hplane_design(self, synth_only=False):
        """Create an H-plane horn antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(HPlane, synth_only)

    def draw_pyramidal_horn_ui(self):
        """Create a horn pyramidal antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornPyramidal.jpg", "HornPyramidal", "10")
        self._add_footer(self.create_horn_pyramidal_design)

    def create_horn_pyramidal_design(self, synth_only=False):
        """Create a horn pyramidal antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(Pyramidal, synth_only)

    def draw_pyramidal_rid_horn_ui(self):
        """Create a pyramidal ridged horn antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornPyramidalRidged.png", "HornPyramidalRid", "10")
        self._add_footer(self.create_horn_pyramidal_rid_design)

    def create_horn_pyramidal_rid_design(self, synth_only=False):
        """Create a conical horn pyramidal antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(PyramidalRidged, synth_only)

    def draw_elliptical_horn_ui(self):
        """Create a horn elliptical antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornElliptical.jpg", "HornElliptical", "10")
        self._add_footer(self.create_horn_elliptical_design)

    def create_horn_elliptical_design(self, synth_only=False):
        """Create a horn elliptical antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(Elliptical, synth_only)

    def draw_quad_ridged_horn_ui(self):
        """Create a quad-ridged horn antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("HornQuadRidged.png", "HornQuadRidged", "10")
        self._add_footer(self.create_horn_quad_design)

    def create_horn_quad_design(self, synth_only=False):
        """Create a quad-ridged antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.get_antenna(QuadRidged, synth_only)

    def draw_log_periodic_array_ui(self):
        """Create a log periodic array antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("LogPeriodicArray.png", "LogPeriodicArray", "10")
        self._add_footer(self.create_log_periodic_array_design)

    def create_log_periodic_array_design(self, synth_only=False):
        """Create a log periodic array antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_log_periodic_tooth_ui(self):
        """Create a log periodic tooth antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("LogTooth.jpg", "LogTooth", "10")
        self._add_footer(self.create_log_periodic_tooth_design)

    def create_log_periodic_tooth_design(self, synth_only=False):
        """Create a log periodic tooth antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_log_periodic_trap_ui(self):
        """Create a log periodic trap antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("LogTrap.jpg", "LogTrap", "10")
        self._add_footer(self.create_log_periodic_trap_design)

    def create_log_periodic_trap_design(self, synth_only=False):
        """Create a log periodic trap antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_bicone_ui(self):
        """Create a biconical antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("Bicone.jpg", "Bicone", "10")
        self._add_footer(self.create_log_periodic_trap_design)

    def create_bicone_design(self, synth_only=False):
        """Create a biconical antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_discone_ui(self):
        """Create a discone antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("Discone.jpg", "Discone", "10")
        self._add_footer(self.create_discone_design)

    def create_discone_design(self, synth_only=False):
        """Create a discone antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_blade_ui(self):
        """Create a discone antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("Blade_Antenna.jpg", "Blade", "10")
        self._add_footer(self.create_blade_design)

    def create_blade_design(self, synth_only=False):
        """Create a discone antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_wire_monopole_ui(self):
        """Create a discone antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("WireMonopole.jpg", "Wire", "10")
        self._add_footer(self.create_wire_monopole_design)

    def create_wire_monopole_design(self, synth_only=False):
        """Create a wire monopole antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")

        # self.get_antenna(AxialMode, synth_only)

    def draw_wire_monopole_inf_gnd_ui(self):
        """Create a wire monopole with infinite ground antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("WireMonopole_InfGnd.jpg", "Wire", "10")
        self._add_footer(self.create_wire_monopole_inf_gnd_design)

    def create_wire_monopole_inf_gnd_design(self, synth_only=False):
        """Create a wire monopole circular disc antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_monopole_circuilar_disc_ui(self):
        """Create a wire monopole with infinite ground antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("CircularDiscMonopole.png", "Wire", "10")
        self._add_footer(self.draw_monopole_circuilar_disc_design)

    def draw_monopole_circuilar_disc_design(self, synth_only=False):
        """Create a wire monopole circular disc antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_monopole_elliptical_ui(self):
        """Create a wire monopole elliptical base strip antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("EllipticalBaseStripMonopole.png", "Elliptica", "10")
        self._add_footer(self.draw_monopole_elliptical_design)

    def draw_monopole_elliptical_design(self, synth_only=False):
        """Create a wire monopole elliptical base strip antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_monopole_trapezoid_ui(self):
        """Create a wire monopole vertical trapezoid antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("VerticalTrapezoidalMonopole.png", "Trapezoid", "10")
        self._add_footer(self.draw_monopole_elliptical_design)

    def draw_monopole_elliptical_design(self, synth_only=False):
        """Create a wire monopole vertical trapezoid antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pifa_planar_ui(self):
        """Create a PIFA planar antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarInvertedF.jpg", "Trapezoid", "10")
        self._add_footer(self.draw_pifa_planar_design)

    def draw_pifa_planar_design(self, synth_only=False):
        """Create a PIFA planar antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pifa_shorting_pin_ui(self):
        """Create a PIFA shorting pin antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("ShortingPin.jpg", "Trapezoid", "10")
        self._add_footer(self.draw_pifa_planar_design)

    def draw_pifa_shorting_pin_design(self, synth_only=False):
        """Create a PIFA shorting pin antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pifa_shorting_plate_ui(self):
        """Create a PIFA shorting plate antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("ShortingPlate.jpg", "Trapezoid", "10")
        self._add_footer(self.draw_pifa_planar_design)

    def draw_pifa_shorting_plate_design(self, synth_only=False):
        """Create a PIFA shorting plate antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pspiral_archimedean_ui(self):
        """Create a Planar Spiral Archimedean antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarArchimedean.jpg", "Archi", "10")
        self._add_footer(self.draw_pspiral_archimedean_design)

    def draw_pspiral_archimedean_design(self, synth_only=False):
        """Create a Planar Spiral Archimedean antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pspiral_archimedean_cavity_ui(self):
        """Create a Planar Spiral Archimedean cavity antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarArchimedeanCavity.jpg", "Cavity", "10")
        self._add_footer(self.draw_pspiral_archimedean_cavity_design)

    def draw_pspiral_archimedean_cavity_design(self, synth_only=False):
        """Create a Planar Spiral Archimedean cavity antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pspiral_log_ui(self):
        """Create a Planar Log antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarLog.jpg", "Log", "10")
        self._add_footer(self.draw_pspiral_log_design)

    def draw_pspiral_log_design(self, synth_only=False):
        """Create a Planar Log antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pspiral_log_cavity_ui(self):
        """Create a Planar Log cavity antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarLogCavity.jpg", "Log", "10")
        self._add_footer(self.draw_pspiral_log_cavity_design)

    def draw_pspiral_log_cavity_design(self, synth_only=False):
        """Create a Planar Log cavity antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pspiral_sinuous_ui(self):
        """Create a Planar sinuous antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarSinuous.jpg", "sinous", "10")
        self._add_footer(self.draw_pspiral_sinuous_design)

    def draw_pspiral_sinuous_design(self, synth_only=False):
        """Create a Planar Log sinuous antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_pspiral_sinuous_cavity_ui(self):
        """Create a Planar sinuous cavity antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("PlanarSinuousCavity.jpg", "sinuous", "10")
        self._add_footer(self.draw_pspiral_sinuous_cavity_design)

    def draw_pspiral_sinuous_cavity_design(self, synth_only=False):
        """Create a Planar sinuous cavity antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_slot_cavity_ui(self):
        """Create a Slot gap antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("SlotCavityBackedArray.png", "sinuous", "10")
        self._add_footer(self.draw_slot_cavity_design)

    def draw_slot_cavity_design(self, synth_only=False):
        """Create a Slot cavity backed antenna array.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_slot_gap_ui(self):
        """Create a Slot gap antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("SlotGap.jpg", "sinuous", "10")
        self._add_footer(self.draw_slot_gap_design)

    def draw_slot_gap_design(self, synth_only=False):
        """Create a Slot gap antenna antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_slot_microstrip_ui(self):
        """Create a Slot microstrip antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("SlotMicrostrip.jpg", "Slot", "10")
        self._add_footer(self.draw_slot_microstrip_design)

    def draw_slot_microstrip_design(self, synth_only=False):
        """Create a Slot gap microstrip antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_slot_tbar_ui(self):
        """Create a Slot T-Bar antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("SlotTBar.png", "Slot", "10")
        self._add_footer(self.draw_slot_tbar_design)

    def draw_slot_tbar_design(self, synth_only=False):
        """Create a Slot T-Bar antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_vivaldi_ui(self):
        """Create a vivaldi antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("Vivaldi.jpg", "Vivaldi", "10")
        self._add_footer(self.draw_vivaldi_design)

    def draw_vivaldi_design(self, synth_only=False):
        """Create a Vivaldi antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_vivaldi_stepper_ui(self):
        """Create a vivaldi stepped antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("VivaldiStepped.jpg", "Vivaldi", "10")
        self._add_footer(self.draw_vivaldi_stepped_design)

    def draw_vivaldi_stepped_design(self, synth_only=False):
        """Create a Vivaldi stepped antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_patch_elliptical_edge_ui(self):
        """Create a patch elliptical edge antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("EllipticalEdge.jpg", "Elliptical", "10")
        self._add_footer(self.draw_patch_elliptical_edge_design)

    def draw_patch_elliptical_edge_design(self, synth_only=False):
        """Create a patch elliptical edge antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_patch_elliptical_inset_ui(self):
        """Create a patch elliptical inset antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("EllipticalInset.jpg", "Elliptical", "10")
        self._add_footer(self.draw_patch_elliptical_inset_design)

    def draw_patch_elliptical_inset_design(self, synth_only=False):
        """Create a patch elliptical inset antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)

    def draw_patch_elliptical_probe_ui(self):
        """Create a patch elliptical inset antenna UI."""
        if self.create_button and not self.create_button.isEnabled():
            self.add_status_bar_message(
                "Antenna already exists in project. To add a new antenna, relaunch Antenna Wizard."
            )
            return

        self._add_header("EllipticalProbe.jpg", "Elliptical", "10")
        self._add_footer(self.draw_patch_elliptical_probe_design)

    def draw_patch_elliptical_probe_design(self, synth_only=False):
        """Create a patch elliptical probe antenna.

        Parameters
        ----------
        synth_only : bool, optional
            Whether to only synthesize the antenna. The default
            is ``False``.
        """
        self.add_status_bar_message("Antenna not supported yet.")
        # self.get_antenna(AxialMode, synth_only)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    desktop_pid = None
    desktop_version = None
    if len(sys.argv) > 2:
        desktop_pid = sys.argv[1]
        desktop_version = sys.argv[2]
    w = ApplicationWindow(desktop_pid, desktop_version)
    w.show()
    sys.exit(app.exec())
