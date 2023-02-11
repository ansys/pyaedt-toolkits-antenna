# -*- coding: utf-8 -*-

import sys
import os
from pyaedt import Hfss, settings
settings.use_grpc_api = True
import qdarkstyle
from ansys.aedt.toolkits.antennas.patch import RectangularPatchProbe
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import QCoreApplication
from ui.antennas_main import Ui_MainWindow
import pyqtgraph as pg
import time

current_path = os.path.join(os.getcwd(), "ui")
os.environ["QT_API"] = "pyside6"

class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.setupUi(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.setFont(font)
        header = self.property_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))

        icon = QtGui.QIcon()
        icon.addFile(os.path.join(current_path, "logo_cropped.png"), QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addFile(os.path.join(current_path, "logo_cropped.png"), QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.On)

        self.actionRectangular_with_probe.triggered.connect(lambda checked: self.on_Rect_Patch_w_probe_selected())


        self.length_unit = ''

        self.closeButton.clicked.connect(self.release_and_close)
        self.pushButton_5.clicked.connect(self.analyze_antenna)
        self.oantenna = None
        self.hfss = None
        self.connect_hfss.clicked.connect(self.launch_hfss)
        pass

    def launch_hfss(self):
        non_graphical = self.nongraphical.isChecked()
        self.hfss = Hfss(specified_version="2022.2", non_graphical=non_graphical)
        self.add_status_bar_message("Hfss Connected.")

    def analyze_antenna(self):
        if not self.hfss:
            self.launch_hfss()
        num_cores=int(self.numcores.text())
        self.hfss.analyze_nominal(num_cores)
        sol_data = self.hfss.post.get_solution_data()
        self.graphWidget = pg.PlotWidget()
        freq = sol_data.primary_sweep_values
        val = sol_data.data_db20()
        # plot data: x, y values
        self.results.addWidget(self.graphWidget)
        self.graphWidget.plot(freq, val,)
        self.graphWidget.setTitle("Scattering Plot")
        self.graphWidget.setLabel('bottom', 'Frequency GHz',)
        self.graphWidget.setLabel('left', 'Value in dB',)

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
        self.antenna1widget.setTitle("Realized gain at Phi {}".format(solution.intrinsics["Phi"][0]))
        self.antenna1widget.setLabel('left', 'Realized Gain',)
        self.antenna1widget.setLabel('bottom', 'Theta',)
        self.antenna2widget = pg.PlotWidget()
        solution.primary_sweep = "Phi"
        phi = solution.primary_sweep_values
        val = solution.data_db20()
        # plot data: x, y values
        self.results.addWidget(self.antenna2widget)
        self.antenna2widget.plot(phi, val)
        self.antenna2widget.setTitle("Realized gain at Theta {}".format(solution.intrinsics["Theta"][0]))
        self.antenna2widget.setLabel('left', 'Realized Gain',)
        self.antenna2widget.setLabel('bottom', 'Phi',)


    def add_status_bar_message(self, message):
        myStatus = QtWidgets.QStatusBar()
        myStatus.showMessage(message, 3000000)
        self.setStatusBar(myStatus)

    def release_and_close(self):
        if self.hfss:
            self.hfss.release_desktop(False,False)
        self.close()

    def synth(self):
        if not self.hfss:
            self.launch_hfss()

        freq = round(float(self.line_3_edit.text()), 3)
        sub_height = float(self.line_4_edit.text())
        material = self.line_2_combo.currentText()
        boundary = self.line_5_combo.currentText()
        if boundary == "None":
            boundary=None
        model_units = self.units.currentText()
        frequnits = self.frequnits.currentText()
        self.oantenna = self.hfss.add_from_toolkit(RectangularPatchProbe,
                                            draw=False,
                                            frequency=freq,
                                            frequency_unit=frequnits,
                                            length_unit=model_units,
                                            material=material,
                                            outer_boundary=boundary,
                                            substrate_height=sub_height)
        n = 0
        self.property_table.setRowCount( len(self.oantenna._parameters.items()))
        i=0
        __sortingEnabled = self.property_table.isSortingEnabled()
        self.property_table.setSortingEnabled(False)
        self.property_table.setRowCount(len(self.oantenna._parameters.values()))
        for par, value in self.oantenna._parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.property_table.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(value)+self.oantenna.length_unit)
            self.property_table.setItem(i, 1, item)
            i+=1
        self.property_table.setSortingEnabled(__sortingEnabled)
        self.add_status_bar_message("Synthesis completed.")

    def create(self):
        if not self.hfss:
            non_graphical = self.nongraphical.isChecked()
            self.add_status_bar_message("Opening Hfss. Please wait...")
            self.hfss = Hfss(specified_version="2022.2", non_graphical=non_graphical)
            self.add_status_bar_message("Hfss Opened.")

        freq = float(self.lineEdit.text())
        sub_height = float(self.lineEdit_2.text())
        material = self.comboBox.currentText()
        boundary = self.comboBox_2.currentText()
        if boundary == "None":
            boundary=None
        self.huygens = self.checkBox_4.isChecked()
        self.component3d = self.checkBox_5.isChecked()
        self.create_setup = self.checkBox_6.isChecked()
        self.lattice_pair = self.checkBox_8.isChecked()
        self.antenna_name = self.lineEdit_4.text()
        model_units = self.units.currentText()
        frequnits = self.frequnits.currentText()
        self.oantenna = self.hfss.add_from_toolkit(RectangularPatchProbe,
                                            draw=True,
                                            frequency=freq,
                                            material=material,
                                            frequency_unit=frequnits,
                                            length_unit=model_units,
                                            outer_boundary=boundary,
                                            substrate_height=sub_height,
                                            huygens_box=self.huygens,
                                            antenna_name=self.antenna_name,)
        self.oantenna.create_3dcomponent(replace=True)
        if self.create_setup:
            setup = self.hfss.create_setup()
            setup.props["Frequency"] = str(freq)+frequnits
            sweep1 = setup.add_sweep()
            sweep1.props["RangeStart"] = str(freq*0.8)+frequnits
            sweep1.props["RangeEnd"] = str(freq*1.2)+frequnits
            sweep1.update()

        self.property_table.setRowCount( len(self.oantenna._parameters.items()))
        i=0
        __sortingEnabled = self.property_table.isSortingEnabled()
        self.property_table.setSortingEnabled(False)
        self.property_table.setRowCount(len(self.oantenna._parameters.values()))
        for par, value in self.oantenna._parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.property_table.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(value)+self.oantenna.length_unit)
            self.property_table.setItem(i, 1, item)
            i+=1

        self.property_table.setSortingEnabled(__sortingEnabled)
        self.hfss.modeler.fit_all()
        self.add_status_bar_message("Project created correctly.")


    def closeEvent(self, event): # Use if the main window is closed by the user
        close = QtWidgets.QMessageBox.question(self, "QUIT", "Confirm quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
            app.quit()
        else:
            event.ignore()

    def clear_antenna_settings(self, layout):
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
    def on_Rect_Patch_w_probe_selected(self):
        self.clear_antenna_settings(self.gridLayout_6)
        self.vertical_spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,
                                                     QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_6.addItem(self.vertical_spacer, 14, 0, 1, 1)

        self.line_1 = QtWidgets.QHBoxLayout()
        self.line_1.setObjectName(u"line_1")
        self.line_1_label = QtWidgets.QLabel(self.antenna_settings)
        self.line_1_label.setObjectName(u"label_2")
        self.line_1.addWidget(self.line_1_label)
        self.line_1_label.setText("Antenna Name")
        self.line_1_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                   QtWidgets.QSizePolicy.Minimum)
        self.line_1.addItem(self.line_1_spacer)
        self.line_1_edit = QtWidgets.QLineEdit(self.antenna_settings)
        self.line_1_edit.setObjectName(u"line_1_edit")
        self.line_1.addWidget(self.line_1_edit)
        self.gridLayout_6.addLayout(self.line_1, 4, 0, 1, 1)

        self.line_2 = QtWidgets.QHBoxLayout()
        self.line_2.setObjectName(u"line_2")
        self.line_2_label = QtWidgets.QLabel(self.antenna_settings)
        self.line_2_label.setObjectName(u"line_2_label")

        self.line_2.addWidget(self.line_2_label)

        self.line_2_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                   QtWidgets.QSizePolicy.Minimum)

        self.line_2.addItem(self.line_2_spacer)

        self.line_2_combo = QtWidgets.QComboBox(self.antenna_settings)
        self.line_2_combo.addItem("")
        self.line_2_combo.addItem("")
        self.line_2_combo.addItem("")
        self.line_2_combo.setObjectName(u"line_2_combo")
        sizePolicy2 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.line_2_combo.sizePolicy().hasHeightForWidth())
        self.line_2_combo.setSizePolicy(sizePolicy2)
        self.line_2_combo.addItem("FR4_epoxy")
        self.line_2_combo.addItem("teflon_based")
        self.line_2_combo.addItem("Rogers RT/duroid 6002 (tm)")
        self.line_2.addWidget(self.line_2_combo)

        self.gridLayout_6.addLayout(self.line_2, 10, 0, 1, 1)

        self.vertical_spacer_2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum,
                                                       QtWidgets.QSizePolicy.Fixed)

        self.gridLayout_6.addItem(self.vertical_spacer_2, 2, 0, 1, 1)

        self.line_3 = QtWidgets.QHBoxLayout()
        self.line_3.setObjectName(u"line_3")
        self.label_9 = QtWidgets.QLabel(self.antenna_settings)
        self.label_9.setObjectName(u"label_9")

        self.line_3.addWidget(self.label_9)

        self.horizontalSpacer_17 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                         QtWidgets.QSizePolicy.Minimum)

        self.line_3.addItem(self.horizontalSpacer_17)

        self.line_3_edit = QtWidgets.QLineEdit(self.antenna_settings)
        self.line_3_edit.setObjectName(u"line_3_edit")

        self.line_3.addWidget(self.line_3_edit)

        self.gridLayout_6.addLayout(self.line_3, 8, 0, 1, 1)

        self.antenna_image = QtWidgets.QLabel(self.antenna_settings)
        self.antenna_image.setObjectName(u"antenna_image")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHeightForWidth(self.antenna_image.sizePolicy().hasHeightForWidth())
        self.antenna_image.setSizePolicy(sizePolicy)
        self.antenna_image.setScaledContents(True)

        self.gridLayout_6.addWidget(self.antenna_image, 0, 0, 1, 1)

        self.line_4 = QtWidgets.QHBoxLayout()
        self.line_4.setObjectName(u"line_4")
        self.line_4_label = QtWidgets.QLabel(self.antenna_settings)
        self.line_4_label.setObjectName(u"line_4_label")

        self.line_4.addWidget(self.line_4_label)

        self.line4_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                  QtWidgets.QSizePolicy.Minimum)

        self.line_4.addItem(self.line4_spacer)

        self.line_4_edit = QtWidgets.QLineEdit(self.antenna_settings)
        self.line_4_edit.setObjectName(u"line_4_edit")

        self.line_4.addWidget(self.line_4_edit)

        self.gridLayout_6.addLayout(self.line_4, 9, 0, 1, 1)

        self.line_5 = QtWidgets.QHBoxLayout()
        self.line_5.setObjectName(u"line_5")
        self.line_5_label = QtWidgets.QLabel(self.antenna_settings)
        self.line_5_label.setObjectName(u"line_5_label")

        self.line_5.addWidget(self.line_5_label)

        self.line_5_combo = QtWidgets.QComboBox(self.antenna_settings)
        self.line_5_combo.addItem("None")
        self.line_5_combo.addItem("Radiation")
        self.line_5_combo.addItem("PML")
        self.line_5_combo.addItem("FEBI")
        self.line_5_combo.setObjectName(u"line_5_combo")

        self.line_5.addWidget(self.line_5_combo)

        self.gridLayout_6.addLayout(self.line_5, 12, 0, 1, 1)

        self.line_buttons = QtWidgets.QHBoxLayout()
        self.line_buttons.setObjectName(u"line_buttons")
        self.synth_button = QtWidgets.QPushButton(self.antenna_settings)
        self.synth_button.setObjectName(u"synth_button")

        self.line_buttons.addWidget(self.synth_button)

        self.line_buttons_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                                                         QtWidgets.QSizePolicy.Minimum)

        self.line_buttons.addItem(self.line_buttons_spacer)

        self.create_button = QtWidgets.QPushButton(self.antenna_settings)
        self.create_button.setObjectName(u"create_button")

        self.line_buttons.addWidget(self.create_button)

        self.gridLayout_6.addLayout(self.line_buttons, 13, 0, 1, 1)

        self.line_1_edit.setText("Patch_1")
        self.line_2_label.setText("Material name")
        self.label_9.setText("Frequency")
        self.line_3_edit.setText("10")
        self.antenna_image.setText("")
        self.line_4_label.setText("Subtsrate height")
        self.line_4_edit.setText("0.254")
        self.line_5_label.setText("Boundary Condition")

        self.synth_button.setText("Synthesis")
        self.create_button.setText("Create Hfss Project")

        pixmap = QtGui.QPixmap(os.path.join(current_path, "Patch.png"))
        self.antenna_image.setPixmap(pixmap)
        self.synth_button.clicked.connect(self.synth)
        self.create_button.clicked.connect(self.create)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ApplicationWindow()
    w.show()
    sys.exit(app.exec())