# -*- coding: utf-8 -*-
################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

import os

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QDate
from PySide6.QtCore import QDateTime
from PySide6.QtCore import QLocale
from PySide6.QtCore import QMetaObject
from PySide6.QtCore import QObject
from PySide6.QtCore import QPoint
from PySide6.QtCore import QRect
from PySide6.QtCore import QSize
from PySide6.QtCore import QTime
from PySide6.QtCore import QUrl
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtGui import QConicalGradient
from PySide6.QtGui import QCursor
from PySide6.QtGui import QFont
from PySide6.QtGui import QFontDatabase
from PySide6.QtGui import QGradient
from PySide6.QtGui import QIcon
from PySide6.QtGui import QImage
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QLinearGradient
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPalette
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QRadialGradient
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QStatusBar
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QWidget

current_path = os.path.join(os.getcwd(), "ui")


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(810, 789)
        icon = QIcon()
        icon.addFile(
            os.path.join(current_path, "pyansys-logo-black-cropped.png"),
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        icon.addFile(
            os.path.join(current_path, "pyansys-logo-black-cropped.png"),
            QSize(),
            QIcon.Normal,
            QIcon.On,
        )
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.000000000000000)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_2 = QAction(MainWindow)
        self.actionSave_2.setObjectName("actionSave_2")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionMHz = QAction(MainWindow)
        self.actionMHz.setObjectName("actionMHz")
        self.actionMHz.setCheckable(True)
        self.actionGHz = QAction(MainWindow)
        self.actionGHz.setObjectName("actionGHz")
        self.actionGHz.setCheckable(True)
        self.actionGHz_2 = QAction(MainWindow)
        self.actionGHz_2.setObjectName("actionGHz_2")
        self.actionGHz_2.setCheckable(True)
        self.actionmm = QAction(MainWindow)
        self.actionmm.setObjectName("actionmm")
        self.actionmm.setCheckable(True)
        self.actionin = QAction(MainWindow)
        self.actionin.setObjectName("actionin")
        self.actionin.setCheckable(True)
        self.actioncm = QAction(MainWindow)
        self.actioncm.setObjectName("actioncm")
        self.actioncm.setCheckable(True)
        self.actionmil = QAction(MainWindow)
        self.actionmil.setObjectName("actionmil")
        self.actionmil.setCheckable(True)
        self.actionAntennas = QAction(MainWindow)
        self.actionAntennas.setObjectName("actionAntennas")
        self.actionRectangular_with_probe = QAction(MainWindow)
        self.actionRectangular_with_probe.setObjectName("actionRectangular_with_probe")
        self.actionArrays_Synthesis = QAction(MainWindow)
        self.actionArrays_Synthesis.setObjectName("actionArrays_Synthesis")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_6 = QGridLayout(self.centralwidget)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.gridLayout_5 = QGridLayout(self.widget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.splitter = QSplitter(self.widget)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName("frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_4 = QGridLayout(self.frame)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.graphicsView = QGraphicsView(self.frame)
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView.setAutoFillBackground(False)
        self.graphicsView.setFrameShape(QFrame.Box)

        self.gridLayout_4.addWidget(self.graphicsView, 0, 0, 1, 1)

        self.splitter.addWidget(self.frame)
        self.frame_2 = QFrame(self.splitter)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tableWidget = QTableWidget(self.frame_2)
        if self.tableWidget.columnCount() < 2:
            self.tableWidget.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableWidget.setObjectName("tableWidget")

        self.gridLayout_2.addWidget(self.tableWidget, 0, 0, 1, 1)

        self.splitter.addWidget(self.frame_2)

        self.gridLayout_5.addWidget(self.splitter, 0, 1, 4, 1)

        self.Rect_Patch_w_probe_settings = QFrame(self.widget)
        self.Rect_Patch_w_probe_settings.setObjectName("Rect_Patch_w_probe_settings")
        self.Rect_Patch_w_probe_settings.setFrameShape(QFrame.StyledPanel)
        self.Rect_Patch_w_probe_settings.setFrameShadow(QFrame.Raised)
        self.Rect_Patch_w_probe_settings.setLineWidth(12)
        self.gridLayout = QGridLayout(self.Rect_Patch_w_probe_settings)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_5 = QLabel(self.Rect_Patch_w_probe_settings)
        self.label_5.setObjectName("label_5")

        self.horizontalLayout_2.addWidget(self.label_5)

        self.comboBox = QComboBox(self.Rect_Patch_w_probe_settings)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")

        self.horizontalLayout_2.addWidget(self.comboBox)

        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QLabel(self.Rect_Patch_w_probe_settings)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout.addWidget(self.label_4)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.lineEdit = QLineEdit(self.Rect_Patch_w_probe_settings)
        self.lineEdit.setObjectName("lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_6 = QLabel(self.Rect_Patch_w_probe_settings)
        self.label_6.setObjectName("label_6")

        self.horizontalLayout_3.addWidget(self.label_6)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.lineEdit_2 = QLineEdit(self.Rect_Patch_w_probe_settings)
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.horizontalLayout_3.addWidget(self.lineEdit_2)

        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_7 = QLabel(self.Rect_Patch_w_probe_settings)
        self.label_7.setObjectName("label_7")

        self.horizontalLayout_4.addWidget(self.label_7)

        self.comboBox_2 = QComboBox(self.Rect_Patch_w_probe_settings)
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.addItem("")
        self.comboBox_2.setObjectName("comboBox_2")

        self.horizontalLayout_4.addWidget(self.comboBox_2)

        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)

        self.gridLayout_5.addWidget(self.Rect_Patch_w_probe_settings, 0, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_2, 1, 0, 1, 1)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_8 = QLabel(self.widget)
        self.label_8.setObjectName("label_8")

        self.horizontalLayout_5.addWidget(self.label_8)

        self.horizontalSpacer_5 = QSpacerItem(107, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_5)

        self.checkBox_4 = QCheckBox(self.widget)
        self.checkBox_4.setObjectName("checkBox_4")

        self.horizontalLayout_5.addWidget(self.checkBox_4)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.gridLayout_3.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_9 = QLabel(self.widget)
        self.label_9.setObjectName("label_9")

        self.horizontalLayout_6.addWidget(self.label_9)

        self.horizontalSpacer_6 = QSpacerItem(101, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)

        self.checkBox_5 = QCheckBox(self.widget)
        self.checkBox_5.setObjectName("checkBox_5")

        self.horizontalLayout_6.addWidget(self.checkBox_5)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)

        self.gridLayout_3.addLayout(self.horizontalLayout_6, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_10 = QLabel(self.widget)
        self.label_10.setObjectName("label_10")

        self.horizontalLayout_7.addWidget(self.label_10)

        self.horizontalSpacer_7 = QSpacerItem(108, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_7)

        self.checkBox_6 = QCheckBox(self.widget)
        self.checkBox_6.setObjectName("checkBox_6")

        self.horizontalLayout_7.addWidget(self.checkBox_6)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_10)

        self.gridLayout_3.addLayout(self.horizontalLayout_7, 2, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_12 = QLabel(self.widget)
        self.label_12.setObjectName("label_12")

        self.horizontalLayout_9.addWidget(self.label_12)

        self.horizontalSpacer_9 = QSpacerItem(108, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_9)

        self.checkBox_8 = QCheckBox(self.widget)
        self.checkBox_8.setObjectName("checkBox_8")

        self.horizontalLayout_9.addWidget(self.checkBox_8)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_11)

        self.gridLayout_3.addLayout(self.horizontalLayout_9, 3, 0, 1, 1)

        self.gridLayout_5.addLayout(self.gridLayout_3, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer, 3, 0, 2, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer)

        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")

        self.horizontalLayout_11.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.widget)
        self.pushButton_2.setObjectName("pushButton_2")

        self.horizontalLayout_11.addWidget(self.pushButton_2)

        self.closeButton = QPushButton(self.widget)
        self.closeButton.setObjectName("closeButton")

        self.horizontalLayout_11.addWidget(self.closeButton)

        self.gridLayout_5.addLayout(self.horizontalLayout_11, 4, 1, 1, 1)

        self.gridLayout_6.addWidget(self.widget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 810, 22))
        self.menuLoad = QMenu(self.menubar)
        self.menuLoad.setObjectName("menuLoad")
        self.menuArrays = QMenu(self.menubar)
        self.menuArrays.setObjectName("menuArrays")
        self.menuDesign = QMenu(self.menuArrays)
        self.menuDesign.setObjectName("menuDesign")
        self.menuPatch = QMenu(self.menuDesign)
        self.menuPatch.setObjectName("menuPatch")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuUnits = QMenu(self.menuSettings)
        self.menuUnits.setObjectName("menuUnits")
        self.menuLength = QMenu(self.menuUnits)
        self.menuLength.setObjectName("menuLength")
        self.menuFrequency = QMenu(self.menuUnits)
        self.menuFrequency.setObjectName("menuFrequency")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuLoad.menuAction())
        self.menubar.addAction(self.menuArrays.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuLoad.addAction(self.actionSave)
        self.menuLoad.addAction(self.actionSave_2)
        self.menuLoad.addAction(self.actionQuit)
        self.menuArrays.addAction(self.menuDesign.menuAction())
        self.menuArrays.addAction(self.actionArrays_Synthesis)
        self.menuDesign.addAction(self.menuPatch.menuAction())
        self.menuPatch.addAction(self.actionRectangular_with_probe)
        self.menuSettings.addAction(self.menuUnits.menuAction())
        self.menuUnits.addSeparator()
        self.menuUnits.addAction(self.menuLength.menuAction())
        self.menuUnits.addAction(self.menuFrequency.menuAction())
        self.menuLength.addAction(self.actionmm)
        self.menuLength.addAction(self.actionin)
        self.menuLength.addAction(self.actioncm)
        self.menuLength.addAction(self.actionmil)
        self.menuFrequency.addAction(self.actionMHz)
        self.menuFrequency.addAction(self.actionGHz)
        self.menuFrequency.addAction(self.actionGHz_2)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "PyAEDT Antenna Toolkit", None)
        )
        self.actionSave.setText(QCoreApplication.translate("MainWindow", "Load", None))
        self.actionSave_2.setText(QCoreApplication.translate("MainWindow", "Save", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", "Quit", None))
        self.actionMHz.setText(QCoreApplication.translate("MainWindow", "KHz", None))
        self.actionGHz.setText(QCoreApplication.translate("MainWindow", "MHz", None))
        self.actionGHz_2.setText(QCoreApplication.translate("MainWindow", "GHz", None))
        self.actionmm.setText(QCoreApplication.translate("MainWindow", "mm", None))
        self.actionin.setText(QCoreApplication.translate("MainWindow", "in", None))
        self.actioncm.setText(QCoreApplication.translate("MainWindow", "cm", None))
        self.actionmil.setText(QCoreApplication.translate("MainWindow", "mil", None))
        self.actionAntennas.setText(QCoreApplication.translate("MainWindow", "Antennas", None))
        self.actionRectangular_with_probe.setText(
            QCoreApplication.translate("MainWindow", "Rectangular with probe", None)
        )
        self.actionArrays_Synthesis.setText(
            QCoreApplication.translate("MainWindow", "Arrays Synthesis", None)
        )
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", "Property", None))
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", "Value", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", "Material name", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", "FR4_epoxy", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", "teflon_based", None))
        self.comboBox.setItemText(
            2, QCoreApplication.translate("MainWindow", "Rogers RT/duroid 6002 (tm)", None)
        )

        self.label_4.setText(QCoreApplication.translate("MainWindow", "Frequency", None))
        self.lineEdit.setText(QCoreApplication.translate("MainWindow", "10", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", "Subtsrate height", None))
        self.lineEdit_2.setText(QCoreApplication.translate("MainWindow", "0.254", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", "Boundary Condition", None))
        self.comboBox_2.setItemText(0, QCoreApplication.translate("MainWindow", "None", None))
        self.comboBox_2.setItemText(1, QCoreApplication.translate("MainWindow", "Radiation", None))
        self.comboBox_2.setItemText(2, QCoreApplication.translate("MainWindow", "PML", None))
        self.comboBox_2.setItemText(3, QCoreApplication.translate("MainWindow", "FEBI", None))

        self.label_8.setText(QCoreApplication.translate("MainWindow", "Huygens", None))
        self.checkBox_4.setText("")
        self.label_9.setText(QCoreApplication.translate("MainWindow", "3D Component", None))
        self.checkBox_5.setText("")
        self.label_10.setText(QCoreApplication.translate("MainWindow", "Create setup", None))
        self.checkBox_6.setText("")
        self.label_12.setText(QCoreApplication.translate("MainWindow", "Lattice pair", None))
        self.checkBox_8.setText("")
        self.pushButton.setText(QCoreApplication.translate("MainWindow", "Synthesis", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", "Create", None))
        self.closeButton.setText(QCoreApplication.translate("MainWindow", "Close", None))
        self.menuLoad.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuArrays.setTitle(QCoreApplication.translate("MainWindow", "Antennas", None))
        self.menuDesign.setTitle(QCoreApplication.translate("MainWindow", "Design", None))
        self.menuPatch.setTitle(QCoreApplication.translate("MainWindow", "Patch", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", "Settings", None))
        self.menuUnits.setTitle(QCoreApplication.translate("MainWindow", "Units", None))
        self.menuLength.setTitle(QCoreApplication.translate("MainWindow", "Length", None))
        self.menuFrequency.setTitle(QCoreApplication.translate("MainWindow", "Frequency", None))

    # retranslateUi
