# -*- coding: utf-8 -*-

import os
import sys

from pyaedt import Hfss
from pyaedt import settings

settings.use_grpc_api = True

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from ui.antennas_main import Ui_MainWindow
from ui.antennas_main import current_path

from ansys.aedt.toolkits.antennas.patch import RectangularPatchProbe

enc = QtCore.QStringEncoder(QtCore.QStringConverter.Encoding.Utf16)
dec = QtCore.QStringDecoder(QtCore.QStringConverter.Encoding.Utf16)


class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.setupUi(self)

        self.Rect_Patch_w_probe_settings.hide()

        self.actionRectangular_with_probe.triggered.connect(
            lambda checked: self.on_Rect_Patch_w_probe_selected()
        )

        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)
        self.length_unit = ""
        self.pushButton.clicked.connect(self.synth)
        self.pushButton_2.clicked.connect(self.create)
        self.closeButton.clicked.connect(self.release_and_close)
        self.oantenna = None
        self.hfss = Hfss(specified_version="2023.1")
        pass

    def release_and_close(self):
        if self.hfss:
            self.hfss.release_desktop(False, False)
        self.close()

    def synth(self):
        freq = float(self.lineEdit.text())
        sub_height = float(self.lineEdit_2.text())
        material = self.comboBox.currentText()
        boundary = self.comboBox_2.currentText()
        if boundary == "None":
            boundary = None
        self.oantenna = self.hfss.add_from_toolkit(
            RectangularPatchProbe,
            draw=False,
            frequency=freq,
            material=material,
            outer_boundary=boundary,
            substrate_height=sub_height,
        )
        n = 0
        self.tableWidget.setRowCount(len(self.oantenna._parameters.items()))
        i = 0
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setRowCount(len(self.oantenna._parameters.values()))
        for par, value in self.oantenna._parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.tableWidget.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(value) + self.oantenna.length_unit)
            self.tableWidget.setItem(i, 1, item)
            i += 1

        self.tableWidget.setSortingEnabled(__sortingEnabled)

    def create(self):
        freq = float(self.lineEdit.text())
        sub_height = float(self.lineEdit_2.text())
        material = self.comboBox.currentText()
        boundary = self.comboBox_2.currentText()
        if boundary == "None":
            boundary = None
        self.huygens = self.checkBox_4.isChecked()
        self.component3d = self.checkBox_5.isChecked()
        self.create_setup = self.checkBox_6.isChecked()
        self.lattice_pair = self.checkBox_8.isChecked()
        self.oantenna = self.hfss.add_from_toolkit(
            RectangularPatchProbe,
            draw=True,
            frequency=freq,
            material=material,
            outer_boundary=boundary,
            substrate_height=sub_height,
            huygens_box=self.huygens,
        )
        self.oantenna.create_3dcomponent(replace=True)
        if self.create_setup:
            setup = self.hfss.create_setup()
            setup.props["Frequency"] = str(freq) + "GHz"
        self.tableWidget.setRowCount(len(self.oantenna._parameters.items()))
        i = 0
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setRowCount(len(self.oantenna._parameters.values()))
        for par, value in self.oantenna._parameters.items():
            item = QtWidgets.QTableWidgetItem(par)
            self.tableWidget.setItem(i, 0, item)
            item = QtWidgets.QTableWidgetItem(str(value) + self.oantenna.length_unit)
            self.tableWidget.setItem(i, 1, item)
            i += 1

        self.tableWidget.setSortingEnabled(__sortingEnabled)

    def on_Rect_Patch_w_probe_selected(self):
        self.Rect_Patch_w_probe_settings.show()
        self.pixmap_item = self.scene.addPixmap(QtGui.QPixmap())
        pixmap = QtGui.QPixmap(os.path.join(current_path, "Patch.png"))
        print(os.path.join(current_path, "Patch.png"))
        pixmapitem = self.scene.addPixmap(pixmap)

        # self.scene = QtGui.QGraphicsScene(self)
        # self.scene.setSceneRect(QtCore.QRectF(0, 0, 245, 245))
        # self.graphicsView.setScene(self.scene)
        # self.item = QtGui.QGraphicsEllipseItem(0, 0, 60, 40)
        # self.scene.addItem(self.item)

        # QtGui.QPixmap(":/Image/Pictures/Huawei-img.jpg")
        # item = QtWidgets.QGraphicsPixmapItem(
        # QtWidgets.QPixmap.fromImage("D:\\3-Python_Programs\\pyaedt_ATK\\Patch.png"))
        # self.scene.addItem(item)
        # self.graphicsView.show()

        # Signals
        # self.load_pushButton.clicked.connect(self.loadFile)
        # self.close_pushButton.clicked.connect(self.closeFile)

    def closeEvent(self, event):  # Use if the main window is closed by the user
        close = QtWidgets.QMessageBox.question(
            self, "QUIT", "Confirm quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if close == QtWidgets.QMessageBox.Yes:
            event.accept()
            app.quit()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ApplicationWindow()
    w.show()
    sys.exit(app.exec())
