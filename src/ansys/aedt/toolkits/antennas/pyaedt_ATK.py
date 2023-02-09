import sys

from MainWindow import Ui_MainWindow
from PySide6 import QtGui
from PySide6 import QtWidgets


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

    def on_Rect_Patch_w_probe_selected(self):
        self.Rect_Patch_w_probe_settings.show()
        self.pixmap_item = self.scene.addPixmap(QtGui.QPixmap())
        pixmap = QtGui.QPixmap("D:\\3-Python_Programs\\Demo_Pyside6\\Patch.png")
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
