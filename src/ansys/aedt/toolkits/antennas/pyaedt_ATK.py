import sys
import os
from PySide6 import QtWidgets, QtCore, QtGui
from MainWindow import Ui_MainWindow
import time


class ApplicationWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.setupUi(self)

        self.Rect_Patch_w_probe_settings.hide()

        self.actionRectangular_with_probe.triggered.connect(lambda checked: self.on_Rect_Patch_w_probe_selected())

        self.scene = QtWidgets.QGraphicsScene(self)
        self.graphicsView.setScene(self.scene)

        self.length_unit = ''

        group_unit = QtGui.QActionGroup(self.menuUnits)
        texts = ["mm", "in", "cm", "mil"]
        for text in texts:
            action = QtGui.QAction(text, self.menuLength, checkable=True, checked=text == texts[0])
            self.menuLength.addAction(action)
            group_unit.addAction(action)
        group_unit.setExclusive(True)

        group_frequency = QtGui.QActionGroup(self.menuUnits)
        texts = ["Hz", "KHz", "MHz", "GHz"]
        for text in texts:
            action = QtGui.QAction(text, self.menuFrequency, checkable=True, checked=text == texts[0])
            self.menuFrequency.addAction(action)
            group_frequency.addAction(action)
        group_frequency.setExclusive(True)

        # Signals
        # self.load_pushButton.clicked.connect(self.loadFile)
        # self.close_pushButton.clicked.connect(self.closeFile)


    def on_Rect_Patch_w_probe_selected(self):
        self.Rect_Patch_w_probe_settings.show()
        self.pixmap_item = self.scene.addPixmap(QtGui.QPixmap())
        pixmap = QtGui.QPixmap("D:\\3-Python_Programs\\Demo_Pyside6\\Patch.png")
        pixmapitem = self.scene.addPixmap(pixmap)


    def closeEvent(self, event): # Use if the main window is closed by the user
        close = QtWidgets.QMessageBox.question(self, "QUIT", "Confirm quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
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