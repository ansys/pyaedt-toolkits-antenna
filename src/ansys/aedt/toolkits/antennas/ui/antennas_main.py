# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'antenna_toolkitQlOmDQ.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPlainTextEdit, QProgressBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QSplitter, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1047, 1130)
        self.actionRectangular_with_probe = QAction(MainWindow)
        self.actionRectangular_with_probe.setObjectName(u"actionRectangular_with_probe")
        font = QFont()
        font.setPointSize(12)
        self.actionRectangular_with_probe.setFont(font)
        self.actionElliptical_Edge = QAction(MainWindow)
        self.actionElliptical_Edge.setObjectName(u"actionElliptical_Edge")
        self.actionRectangular_Inset = QAction(MainWindow)
        self.actionRectangular_Inset.setObjectName(u"actionRectangular_Inset")
        self.actionRectangular_Inset.setFont(font)
        self.actionRectangular_Edge = QAction(MainWindow)
        self.actionRectangular_Edge.setObjectName(u"actionRectangular_Edge")
        self.actionRectangular_Edge.setFont(font)
        self.actionElliptical_with_Probe = QAction(MainWindow)
        self.actionElliptical_with_Probe.setObjectName(u"actionElliptical_with_Probe")
        self.actionElliptical_with_Probe.setFont(font)
        self.actionElliptical_Inset = QAction(MainWindow)
        self.actionElliptical_Inset.setObjectName(u"actionElliptical_Inset")
        self.actionElliptical_Inset.setFont(font)
        self.actionElliptical_Edge_2 = QAction(MainWindow)
        self.actionElliptical_Edge_2.setObjectName(u"actionElliptical_Edge_2")
        self.actionElliptical_Edge_2.setFont(font)
        self.actionConical = QAction(MainWindow)
        self.actionConical.setObjectName(u"actionConical")
        self.actionConical.setFont(font)
        self.actionConical_Corrugated = QAction(MainWindow)
        self.actionConical_Corrugated.setObjectName(u"actionConical_Corrugated")
        self.actionConical_Corrugated.setFont(font)
        self.actionElliptical = QAction(MainWindow)
        self.actionElliptical.setObjectName(u"actionElliptical")
        self.actionElliptical.setFont(font)
        self.actionE_Plane = QAction(MainWindow)
        self.actionE_Plane.setObjectName(u"actionE_Plane")
        self.actionE_Plane.setFont(font)
        self.actionH_Plane = QAction(MainWindow)
        self.actionH_Plane.setObjectName(u"actionH_Plane")
        self.actionH_Plane.setFont(font)
        self.actionPyramidal = QAction(MainWindow)
        self.actionPyramidal.setObjectName(u"actionPyramidal")
        self.actionPyramidal.setFont(font)
        self.actionPyramidal_Ridged = QAction(MainWindow)
        self.actionPyramidal_Ridged.setObjectName(u"actionPyramidal_Ridged")
        self.actionPyramidal_Ridged.setFont(font)
        self.actionQuad_Ridged = QAction(MainWindow)
        self.actionQuad_Ridged.setObjectName(u"actionQuad_Ridged")
        self.actionQuad_Ridged.setFont(font)
        self.actionAxial = QAction(MainWindow)
        self.actionAxial.setObjectName(u"actionAxial")
        self.actionAxial.setFont(font)
        self.actionBowtieNormal = QAction(MainWindow)
        self.actionBowtieNormal.setObjectName(u"actionBowtieNormal")
        self.actionBowtieNormal.setFont(font)
        self.actionBowtieRounded = QAction(MainWindow)
        self.actionBowtieRounded.setObjectName(u"actionBowtieRounded")
        self.actionBowtieRounded.setFont(font)
        self.actionBowtieSlot = QAction(MainWindow)
        self.actionBowtieSlot.setObjectName(u"actionBowtieSlot")
        self.actionBowtieSlot.setFont(font)
        self.actionCassegrain = QAction(MainWindow)
        self.actionCassegrain.setObjectName(u"actionCassegrain")
        self.actionCassegrain.setFont(font)
        self.actionGregorian = QAction(MainWindow)
        self.actionGregorian.setObjectName(u"actionGregorian")
        self.actionGregorian.setFont(font)
        self.actionParabolic = QAction(MainWindow)
        self.actionParabolic.setObjectName(u"actionParabolic")
        self.actionParabolic.setFont(font)
        self.actionSplash_Plate = QAction(MainWindow)
        self.actionSplash_Plate.setObjectName(u"actionSplash_Plate")
        self.actionSplash_Plate.setFont(font)
        self.actionArchimedean = QAction(MainWindow)
        self.actionArchimedean.setObjectName(u"actionArchimedean")
        self.actionArchimedean.setFont(font)
        self.actionLog = QAction(MainWindow)
        self.actionLog.setObjectName(u"actionLog")
        self.actionLog.setFont(font)
        self.actionSinous = QAction(MainWindow)
        self.actionSinous.setObjectName(u"actionSinous")
        self.actionSinous.setFont(font)
        self.actionGPS_Patch_Ceramic = QAction(MainWindow)
        self.actionGPS_Patch_Ceramic.setObjectName(u"actionGPS_Patch_Ceramic")
        self.actionPlanar = QAction(MainWindow)
        self.actionPlanar.setObjectName(u"actionPlanar")
        self.actionPlanar.setFont(font)
        self.actionWire = QAction(MainWindow)
        self.actionWire.setObjectName(u"actionWire")
        self.actionWire.setFont(font)
        self.actionLog_Periodic_Array = QAction(MainWindow)
        self.actionLog_Periodic_Array.setObjectName(u"actionLog_Periodic_Array")
        self.actionLog_Periodic_Array.setFont(font)
        self.actionLog_Tooth = QAction(MainWindow)
        self.actionLog_Tooth.setObjectName(u"actionLog_Tooth")
        self.actionLog_Tooth.setFont(font)
        self.actionLog_Trap = QAction(MainWindow)
        self.actionLog_Trap.setObjectName(u"actionLog_Trap")
        self.actionLog_Trap.setFont(font)
        self.actionBicone = QAction(MainWindow)
        self.actionBicone.setObjectName(u"actionBicone")
        self.actionBicone.setFont(font)
        self.actionDiscone = QAction(MainWindow)
        self.actionDiscone.setObjectName(u"actionDiscone")
        self.actionDiscone.setFont(font)
        self.actionBlade = QAction(MainWindow)
        self.actionBlade.setObjectName(u"actionBlade")
        self.actionBlade.setFont(font)
        self.actionWire_2 = QAction(MainWindow)
        self.actionWire_2.setObjectName(u"actionWire_2")
        self.actionWire_2.setFont(font)
        self.actionWire_with_Infinite_Gnd = QAction(MainWindow)
        self.actionWire_with_Infinite_Gnd.setObjectName(u"actionWire_with_Infinite_Gnd")
        self.actionWire_with_Infinite_Gnd.setFont(font)
        self.actionCircular_Disc = QAction(MainWindow)
        self.actionCircular_Disc.setObjectName(u"actionCircular_Disc")
        self.actionCircular_Disc.setFont(font)
        self.actionElliptical_Base_Strip = QAction(MainWindow)
        self.actionElliptical_Base_Strip.setObjectName(u"actionElliptical_Base_Strip")
        self.actionElliptical_Base_Strip.setFont(font)
        self.actionVertical_Trapezoidal = QAction(MainWindow)
        self.actionVertical_Trapezoidal.setObjectName(u"actionVertical_Trapezoidal")
        self.actionVertical_Trapezoidal.setFont(font)
        self.actionPlanar_Inverted = QAction(MainWindow)
        self.actionPlanar_Inverted.setObjectName(u"actionPlanar_Inverted")
        self.actionPlanar_Inverted.setFont(font)
        self.actionShorting_Pin = QAction(MainWindow)
        self.actionShorting_Pin.setObjectName(u"actionShorting_Pin")
        self.actionShorting_Pin.setFont(font)
        self.actionShorting_Plate = QAction(MainWindow)
        self.actionShorting_Plate.setObjectName(u"actionShorting_Plate")
        self.actionShorting_Plate.setFont(font)
        self.actionPlanar_Archimedean = QAction(MainWindow)
        self.actionPlanar_Archimedean.setObjectName(u"actionPlanar_Archimedean")
        self.actionPlanar_Archimedean.setFont(font)
        self.actionPlanar_Archimedean_Cavity = QAction(MainWindow)
        self.actionPlanar_Archimedean_Cavity.setObjectName(u"actionPlanar_Archimedean_Cavity")
        self.actionPlanar_Archimedean_Cavity.setFont(font)
        self.actionPlanar_Log = QAction(MainWindow)
        self.actionPlanar_Log.setObjectName(u"actionPlanar_Log")
        self.actionPlanar_Log.setFont(font)
        self.actionPlanar_Log_Cavity = QAction(MainWindow)
        self.actionPlanar_Log_Cavity.setObjectName(u"actionPlanar_Log_Cavity")
        self.actionPlanar_Log_Cavity.setFont(font)
        self.actionPlanar_Sinous = QAction(MainWindow)
        self.actionPlanar_Sinous.setObjectName(u"actionPlanar_Sinous")
        self.actionPlanar_Sinous.setFont(font)
        self.actionPlanar_Sinous_Cavity = QAction(MainWindow)
        self.actionPlanar_Sinous_Cavity.setObjectName(u"actionPlanar_Sinous_Cavity")
        self.actionPlanar_Sinous_Cavity.setFont(font)
        self.actionSlot_Cavity_Backed_Array = QAction(MainWindow)
        self.actionSlot_Cavity_Backed_Array.setObjectName(u"actionSlot_Cavity_Backed_Array")
        self.actionSlot_Cavity_Backed_Array.setFont(font)
        self.actionSlot_Gap = QAction(MainWindow)
        self.actionSlot_Gap.setObjectName(u"actionSlot_Gap")
        self.actionSlot_Gap.setFont(font)
        self.actionSlot_Microstrip = QAction(MainWindow)
        self.actionSlot_Microstrip.setObjectName(u"actionSlot_Microstrip")
        self.actionSlot_Microstrip.setFont(font)
        self.actionSlot_T_Bar = QAction(MainWindow)
        self.actionSlot_T_Bar.setObjectName(u"actionSlot_T_Bar")
        self.actionSlot_T_Bar.setFont(font)
        self.actionVivaldi_2 = QAction(MainWindow)
        self.actionVivaldi_2.setObjectName(u"actionVivaldi_2")
        self.actionVivaldi_2.setFont(font)
        self.actionVivaldi_Stepped = QAction(MainWindow)
        self.actionVivaldi_Stepped.setObjectName(u"actionVivaldi_Stepped")
        self.actionVivaldi_Stepped.setFont(font)
        self.actionCircular = QAction(MainWindow)
        self.actionCircular.setObjectName(u"actionCircular")
        self.actionCircular.setFont(font)
        self.actionRectangular = QAction(MainWindow)
        self.actionRectangular.setObjectName(u"actionRectangular")
        self.actionRectangular.setFont(font)
        self.actionRectangular_Slot = QAction(MainWindow)
        self.actionRectangular_Slot.setObjectName(u"actionRectangular_Slot")
        self.actionRectangular_Slot.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.release_and_exit_button = QPushButton(self.widget)
        self.release_and_exit_button.setObjectName(u"release_and_exit_button")
        self.release_and_exit_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_and_exit_button, 3, 3, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 3, 1, 1, 1)

        self.connect_hfss = QPushButton(self.widget)
        self.connect_hfss.setObjectName(u"connect_hfss")
        self.connect_hfss.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.connect_hfss, 3, 0, 1, 1)

        self.tabWidget = QTabWidget(self.widget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tabWidget.setTabShape(QTabWidget.Triangular)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_25 = QHBoxLayout(self.tab)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_22.addWidget(self.label_3)

        self.frequnits = QComboBox(self.tab)
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.setObjectName(u"frequnits")

        self.horizontalLayout_22.addWidget(self.frequnits)


        self.verticalLayout_4.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_12 = QLabel(self.tab)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_23.addWidget(self.label_12)

        self.units = QComboBox(self.tab)
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.setObjectName(u"units")

        self.horizontalLayout_23.addWidget(self.units)


        self.verticalLayout_4.addLayout(self.horizontalLayout_23)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_13 = QLabel(self.tab)
        self.label_13.setObjectName(u"label_13")

        self.horizontalLayout_24.addWidget(self.label_13)

        self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_24.addItem(self.horizontalSpacer_30)

        self.numcores = QLineEdit(self.tab)
        self.numcores.setObjectName(u"numcores")

        self.horizontalLayout_24.addWidget(self.numcores)


        self.verticalLayout_4.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_26.addWidget(self.label_4)

        self.non_graphical_combo = QComboBox(self.tab)
        self.non_graphical_combo.addItem("")
        self.non_graphical_combo.addItem("")
        self.non_graphical_combo.setObjectName(u"non_graphical_combo")

        self.horizontalLayout_26.addWidget(self.non_graphical_combo)


        self.verticalLayout_4.addLayout(self.horizontalLayout_26)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.aedt_version_combo = QComboBox(self.tab)
        self.aedt_version_combo.setObjectName(u"aedt_version_combo")

        self.horizontalLayout.addWidget(self.aedt_version_combo)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(self.tab)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_3.addWidget(self.label_5)

        self.process_id_combo = QComboBox(self.tab)
        self.process_id_combo.addItem("")
        self.process_id_combo.setObjectName(u"process_id_combo")

        self.horizontalLayout_3.addWidget(self.process_id_combo)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_4.addWidget(self.label_6)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.project_name = QLineEdit(self.tab)
        self.project_name.setObjectName(u"project_name")

        self.horizontalLayout_4.addWidget(self.project_name)


        self.verticalLayout_4.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.browse_project = QPushButton(self.tab)
        self.browse_project.setObjectName(u"browse_project")

        self.horizontalLayout_5.addWidget(self.browse_project)


        self.verticalLayout_4.addLayout(self.horizontalLayout_5)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_8)


        self.horizontalLayout_25.addLayout(self.verticalLayout_4)

        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_29)

        self.tabWidget.addTab(self.tab, "")
        self.design = QWidget()
        self.design.setObjectName(u"design")
        self.verticalLayout_2 = QVBoxLayout(self.design)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.antenna_settings = QFrame(self.design)
        self.antenna_settings.setObjectName(u"antenna_settings")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.antenna_settings.sizePolicy().hasHeightForWidth())
        self.antenna_settings.setSizePolicy(sizePolicy2)
        self.antenna_settings.setFrameShape(QFrame.StyledPanel)
        self.antenna_settings.setFrameShadow(QFrame.Raised)
        self.antenna_settings.setLineWidth(12)
        self.layout_settings = QGridLayout(self.antenna_settings)
        self.layout_settings.setObjectName(u"layout_settings")

        self.horizontalLayout_20.addWidget(self.antenna_settings)

        self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_27)

        self.splitter_2 = QSplitter(self.design)
        self.splitter_2.setObjectName(u"splitter_2")
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(Qt.Vertical)
        self.frame_3 = QFrame(self.splitter_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_7 = QGridLayout(self.frame_3)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_7.addItem(self.verticalSpacer_5, 2, 0, 1, 1)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.component_3d = QCheckBox(self.frame_3)
        self.component_3d.setObjectName(u"component_3d")
        self.component_3d.setChecked(False)

        self.horizontalLayout_19.addWidget(self.component_3d)

        self.horizontalSpacer_25 = QSpacerItem(101, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_25)

        self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_26)


        self.gridLayout_8.addLayout(self.horizontalLayout_19, 1, 0, 1, 1)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.create_hfss_setup = QCheckBox(self.frame_3)
        self.create_hfss_setup.setObjectName(u"create_hfss_setup")
        self.create_hfss_setup.setChecked(True)

        self.horizontalLayout_16.addWidget(self.create_hfss_setup)

        self.horizontalSpacer_19 = QSpacerItem(108, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_19)

        self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_20)


        self.gridLayout_8.addLayout(self.horizontalLayout_16, 2, 0, 1, 1)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.lattice_pair = QCheckBox(self.frame_3)
        self.lattice_pair.setObjectName(u"lattice_pair")

        self.horizontalLayout_17.addWidget(self.lattice_pair)

        self.horizontalSpacer_21 = QSpacerItem(108, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_21)

        self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_22)


        self.gridLayout_8.addLayout(self.horizontalLayout_17, 4, 0, 1, 1)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.huygens = QCheckBox(self.frame_3)
        self.huygens.setObjectName(u"huygens")
        self.huygens.setChecked(True)

        self.horizontalLayout_18.addWidget(self.huygens)

        self.horizontalSpacer_23 = QSpacerItem(107, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_23)

        self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_24)


        self.gridLayout_8.addLayout(self.horizontalLayout_18, 0, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_7 = QLabel(self.frame_3)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_6.addWidget(self.label_7)

        self.sweep_slider = QSlider(self.frame_3)
        self.sweep_slider.setObjectName(u"sweep_slider")
        self.sweep_slider.setMaximum(100)
        self.sweep_slider.setSingleStep(5)
        self.sweep_slider.setValue(20)
        self.sweep_slider.setTracking(True)
        self.sweep_slider.setOrientation(Qt.Horizontal)
        self.sweep_slider.setTickPosition(QSlider.TicksAbove)
        self.sweep_slider.setTickInterval(5)

        self.horizontalLayout_6.addWidget(self.sweep_slider)

        self.slider_value = QLabel(self.frame_3)
        self.slider_value.setObjectName(u"slider_value")

        self.horizontalLayout_6.addWidget(self.slider_value)


        self.gridLayout_8.addLayout(self.horizontalLayout_6, 5, 0, 1, 1)


        self.gridLayout_7.addLayout(self.gridLayout_8, 0, 0, 1, 1)

        self.splitter_2.addWidget(self.frame_3)
        self.frame_4 = QFrame(self.splitter_2)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.gridLayout_9 = QGridLayout(self.frame_4)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.property_table = QTableWidget(self.frame_4)
        if (self.property_table.columnCount() < 2):
            self.property_table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.property_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.property_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.property_table.setObjectName(u"property_table")

        self.gridLayout_9.addWidget(self.property_table, 0, 0, 1, 1)

        self.splitter_2.addWidget(self.frame_4)

        self.horizontalLayout_20.addWidget(self.splitter_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_20)

        self.tabWidget.addTab(self.design, "")
        self.analysis = QWidget()
        self.analysis.setObjectName(u"analysis")
        self.verticalLayout_3 = QVBoxLayout(self.analysis)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.pushButton_5 = QPushButton(self.analysis)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.verticalLayout_3.addWidget(self.pushButton_5)

        self.results = QVBoxLayout()
        self.results.setObjectName(u"results")

        self.verticalLayout_3.addLayout(self.results)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_7)

        self.tabWidget.addTab(self.analysis, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 5)

        self.release_button = QPushButton(self.widget)
        self.release_button.setObjectName(u"release_button")
        self.release_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_button, 3, 2, 1, 1)


        self.verticalLayout.addWidget(self.widget)

        self.log_text = QPlainTextEdit(self.centralwidget)
        self.log_text.setObjectName(u"log_text")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.log_text.sizePolicy().hasHeightForWidth())
        self.log_text.setSizePolicy(sizePolicy3)

        self.verticalLayout.addWidget(self.log_text)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout.addWidget(self.progressBar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1047, 28))
        self.menubar.setFont(font)
        self.menuAntennas = QMenu(self.menubar)
        self.menuAntennas.setObjectName(u"menuAntennas")
        self.menuAntennas.setFont(font)
        self.menuPatch = QMenu(self.menuAntennas)
        self.menuPatch.setObjectName(u"menuPatch")
        self.menuHorn = QMenu(self.menuAntennas)
        self.menuHorn.setObjectName(u"menuHorn")
        self.menuHelix = QMenu(self.menuAntennas)
        self.menuHelix.setObjectName(u"menuHelix")
        self.menuBowtie = QMenu(self.menuAntennas)
        self.menuBowtie.setObjectName(u"menuBowtie")
        self.menuConical_Spiral = QMenu(self.menuAntennas)
        self.menuConical_Spiral.setObjectName(u"menuConical_Spiral")
        self.menuCustom = QMenu(self.menuAntennas)
        self.menuCustom.setObjectName(u"menuCustom")
        self.menuDipole = QMenu(self.menuAntennas)
        self.menuDipole.setObjectName(u"menuDipole")
        self.menuLog_Periodic = QMenu(self.menuAntennas)
        self.menuLog_Periodic.setObjectName(u"menuLog_Periodic")
        self.menuMiscellaneous = QMenu(self.menuAntennas)
        self.menuMiscellaneous.setObjectName(u"menuMiscellaneous")
        self.menuMonopole = QMenu(self.menuAntennas)
        self.menuMonopole.setObjectName(u"menuMonopole")
        self.menuPIFA = QMenu(self.menuAntennas)
        self.menuPIFA.setObjectName(u"menuPIFA")
        self.menuPlanar_Spiral = QMenu(self.menuAntennas)
        self.menuPlanar_Spiral.setObjectName(u"menuPlanar_Spiral")
        self.menuSlot = QMenu(self.menuAntennas)
        self.menuSlot.setObjectName(u"menuSlot")
        self.menuVivaldi = QMenu(self.menuAntennas)
        self.menuVivaldi.setObjectName(u"menuVivaldi")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.menuAntennas.menuAction())
        self.menuAntennas.addAction(self.menuBowtie.menuAction())
        self.menuAntennas.addAction(self.menuConical_Spiral.menuAction())
        self.menuAntennas.addAction(self.menuCustom.menuAction())
        self.menuAntennas.addAction(self.menuDipole.menuAction())
        self.menuAntennas.addAction(self.menuHelix.menuAction())
        self.menuAntennas.addAction(self.menuHorn.menuAction())
        self.menuAntennas.addAction(self.menuLog_Periodic.menuAction())
        self.menuAntennas.addAction(self.menuMiscellaneous.menuAction())
        self.menuAntennas.addAction(self.menuMonopole.menuAction())
        self.menuAntennas.addAction(self.menuPatch.menuAction())
        self.menuAntennas.addAction(self.menuPIFA.menuAction())
        self.menuAntennas.addAction(self.menuPlanar_Spiral.menuAction())
        self.menuAntennas.addAction(self.menuSlot.menuAction())
        self.menuAntennas.addAction(self.menuVivaldi.menuAction())
        self.menuPatch.addAction(self.actionRectangular_with_probe)
        self.menuPatch.addAction(self.actionRectangular_Inset)
        self.menuPatch.addAction(self.actionRectangular_Edge)
        self.menuPatch.addAction(self.actionElliptical_with_Probe)
        self.menuPatch.addAction(self.actionElliptical_Inset)
        self.menuPatch.addAction(self.actionElliptical_Edge_2)
        self.menuHorn.addAction(self.actionConical)
        self.menuHorn.addAction(self.actionConical_Corrugated)
        self.menuHorn.addAction(self.actionElliptical)
        self.menuHorn.addAction(self.actionE_Plane)
        self.menuHorn.addAction(self.actionH_Plane)
        self.menuHorn.addAction(self.actionPyramidal)
        self.menuHorn.addAction(self.actionPyramidal_Ridged)
        self.menuHorn.addAction(self.actionQuad_Ridged)
        self.menuHelix.addAction(self.actionAxial)
        self.menuBowtie.addAction(self.actionBowtieNormal)
        self.menuBowtie.addAction(self.actionBowtieRounded)
        self.menuBowtie.addAction(self.actionBowtieSlot)
        self.menuConical_Spiral.addAction(self.actionArchimedean)
        self.menuConical_Spiral.addAction(self.actionLog)
        self.menuConical_Spiral.addAction(self.actionSinous)
        self.menuDipole.addAction(self.actionPlanar)
        self.menuDipole.addAction(self.actionWire)
        self.menuLog_Periodic.addAction(self.actionLog_Periodic_Array)
        self.menuLog_Periodic.addAction(self.actionLog_Tooth)
        self.menuLog_Periodic.addAction(self.actionLog_Trap)
        self.menuMiscellaneous.addAction(self.actionBicone)
        self.menuMiscellaneous.addAction(self.actionDiscone)
        self.menuMonopole.addAction(self.actionBlade)
        self.menuMonopole.addAction(self.actionWire_2)
        self.menuMonopole.addAction(self.actionWire_with_Infinite_Gnd)
        self.menuMonopole.addAction(self.actionCircular_Disc)
        self.menuMonopole.addAction(self.actionElliptical_Base_Strip)
        self.menuMonopole.addAction(self.actionVertical_Trapezoidal)
        self.menuPIFA.addAction(self.actionPlanar_Inverted)
        self.menuPIFA.addAction(self.actionShorting_Pin)
        self.menuPIFA.addAction(self.actionShorting_Plate)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Archimedean)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Archimedean_Cavity)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Log)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Log_Cavity)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Sinous)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Sinous_Cavity)
        self.menuSlot.addAction(self.actionSlot_Cavity_Backed_Array)
        self.menuSlot.addAction(self.actionSlot_Gap)
        self.menuSlot.addAction(self.actionSlot_Microstrip)
        self.menuSlot.addAction(self.actionSlot_T_Bar)
        self.menuVivaldi.addAction(self.actionVivaldi_2)
        self.menuVivaldi.addAction(self.actionVivaldi_Stepped)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.frequnits.setCurrentIndex(3)
        self.units.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionRectangular_with_probe.setText(QCoreApplication.translate("MainWindow", u"Rectangular with Probe", None))
        self.actionElliptical_Edge.setText(QCoreApplication.translate("MainWindow", u"Elliptical Edge", None))
        self.actionRectangular_Inset.setText(QCoreApplication.translate("MainWindow", u"Rectangular Inset", None))
        self.actionRectangular_Edge.setText(QCoreApplication.translate("MainWindow", u"Rectangular Edge", None))
        self.actionElliptical_with_Probe.setText(QCoreApplication.translate("MainWindow", u"Elliptical with Probe", None))
        self.actionElliptical_Inset.setText(QCoreApplication.translate("MainWindow", u"Elliptical Inset", None))
        self.actionElliptical_Edge_2.setText(QCoreApplication.translate("MainWindow", u"Elliptical Edge", None))
        self.actionConical.setText(QCoreApplication.translate("MainWindow", u"Conical", None))
        self.actionConical_Corrugated.setText(QCoreApplication.translate("MainWindow", u"Conical Corrugated", None))
        self.actionElliptical.setText(QCoreApplication.translate("MainWindow", u"Elliptical", None))
        self.actionE_Plane.setText(QCoreApplication.translate("MainWindow", u"E-Plane", None))
        self.actionH_Plane.setText(QCoreApplication.translate("MainWindow", u"H-Plane", None))
        self.actionPyramidal.setText(QCoreApplication.translate("MainWindow", u"Pyramidal", None))
        self.actionPyramidal_Ridged.setText(QCoreApplication.translate("MainWindow", u"Pyramidal Ridged", None))
        self.actionQuad_Ridged.setText(QCoreApplication.translate("MainWindow", u"Quad Ridged", None))
        self.actionAxial.setText(QCoreApplication.translate("MainWindow", u"Axial", None))
        self.actionBowtieNormal.setText(QCoreApplication.translate("MainWindow", u"Normal", None))
        self.actionBowtieRounded.setText(QCoreApplication.translate("MainWindow", u"Rounded", None))
        self.actionBowtieSlot.setText(QCoreApplication.translate("MainWindow", u"Slot", None))
        self.actionCassegrain.setText(QCoreApplication.translate("MainWindow", u"Cassegrain", None))
        self.actionGregorian.setText(QCoreApplication.translate("MainWindow", u"Gregorian", None))
        self.actionParabolic.setText(QCoreApplication.translate("MainWindow", u"Parabolic", None))
        self.actionSplash_Plate.setText(QCoreApplication.translate("MainWindow", u"Splash Plate", None))
        self.actionArchimedean.setText(QCoreApplication.translate("MainWindow", u"Archimedean", None))
        self.actionLog.setText(QCoreApplication.translate("MainWindow", u"Log", None))
        self.actionSinous.setText(QCoreApplication.translate("MainWindow", u"Sinous", None))
        self.actionGPS_Patch_Ceramic.setText(QCoreApplication.translate("MainWindow", u"GPS Patch Ceramic", None))
        self.actionPlanar.setText(QCoreApplication.translate("MainWindow", u"Planar", None))
        self.actionWire.setText(QCoreApplication.translate("MainWindow", u"Wire", None))
        self.actionLog_Periodic_Array.setText(QCoreApplication.translate("MainWindow", u"Log Periodic Array", None))
        self.actionLog_Tooth.setText(QCoreApplication.translate("MainWindow", u"Log Tooth", None))
        self.actionLog_Trap.setText(QCoreApplication.translate("MainWindow", u"Log Trap", None))
        self.actionBicone.setText(QCoreApplication.translate("MainWindow", u"Bicone", None))
        self.actionDiscone.setText(QCoreApplication.translate("MainWindow", u"Discone", None))
        self.actionBlade.setText(QCoreApplication.translate("MainWindow", u"Blade", None))
        self.actionWire_2.setText(QCoreApplication.translate("MainWindow", u"Wire", None))
        self.actionWire_with_Infinite_Gnd.setText(QCoreApplication.translate("MainWindow", u"Wire with Infinite Gnd", None))
        self.actionCircular_Disc.setText(QCoreApplication.translate("MainWindow", u"Circular Disc", None))
        self.actionElliptical_Base_Strip.setText(QCoreApplication.translate("MainWindow", u"Elliptical Base Strip", None))
        self.actionVertical_Trapezoidal.setText(QCoreApplication.translate("MainWindow", u"Vertical Trapezoidal", None))
        self.actionPlanar_Inverted.setText(QCoreApplication.translate("MainWindow", u"Planar Inverted", None))
        self.actionShorting_Pin.setText(QCoreApplication.translate("MainWindow", u"Shorting Pin", None))
        self.actionShorting_Plate.setText(QCoreApplication.translate("MainWindow", u"Shorting Plate", None))
        self.actionPlanar_Archimedean.setText(QCoreApplication.translate("MainWindow", u"Planar Archimedean", None))
        self.actionPlanar_Archimedean_Cavity.setText(QCoreApplication.translate("MainWindow", u"Planar Archimedean Cavity", None))
        self.actionPlanar_Log.setText(QCoreApplication.translate("MainWindow", u"Planar Log", None))
        self.actionPlanar_Log_Cavity.setText(QCoreApplication.translate("MainWindow", u"Planar Log Cavity", None))
        self.actionPlanar_Sinous.setText(QCoreApplication.translate("MainWindow", u"Planar Sinous", None))
        self.actionPlanar_Sinous_Cavity.setText(QCoreApplication.translate("MainWindow", u"Planar Sinous Cavity", None))
        self.actionSlot_Cavity_Backed_Array.setText(QCoreApplication.translate("MainWindow", u"Slot Cavity Backed Array", None))
        self.actionSlot_Gap.setText(QCoreApplication.translate("MainWindow", u"Slot Gap", None))
        self.actionSlot_Microstrip.setText(QCoreApplication.translate("MainWindow", u"Slot Microstrip", None))
        self.actionSlot_T_Bar.setText(QCoreApplication.translate("MainWindow", u"Slot T Bar", None))
        self.actionVivaldi_2.setText(QCoreApplication.translate("MainWindow", u"Vivaldi", None))
        self.actionVivaldi_Stepped.setText(QCoreApplication.translate("MainWindow", u"Vivaldi Stepped", None))
        self.actionCircular.setText(QCoreApplication.translate("MainWindow", u"Circular", None))
        self.actionRectangular.setText(QCoreApplication.translate("MainWindow", u"Rectangular", None))
        self.actionRectangular_Slot.setText(QCoreApplication.translate("MainWindow", u"Rectangular Slot", None))
        self.release_and_exit_button.setText(QCoreApplication.translate("MainWindow", u" Close Desktop and Wizard ", None))
        self.connect_hfss.setText(QCoreApplication.translate("MainWindow", u"  Launch HFSS  ", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Frequency Units", None))
        self.frequnits.setItemText(0, QCoreApplication.translate("MainWindow", u"Hz", None))
        self.frequnits.setItemText(1, QCoreApplication.translate("MainWindow", u"KHz", None))
        self.frequnits.setItemText(2, QCoreApplication.translate("MainWindow", u"MHz", None))
        self.frequnits.setItemText(3, QCoreApplication.translate("MainWindow", u"GHz", None))
        self.frequnits.setItemText(4, QCoreApplication.translate("MainWindow", u"THz", None))

        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Length Units", None))
        self.units.setItemText(0, QCoreApplication.translate("MainWindow", u"um", None))
        self.units.setItemText(1, QCoreApplication.translate("MainWindow", u"mm", None))
        self.units.setItemText(2, QCoreApplication.translate("MainWindow", u"cm", None))
        self.units.setItemText(3, QCoreApplication.translate("MainWindow", u"m", None))
        self.units.setItemText(4, QCoreApplication.translate("MainWindow", u"mil", None))
        self.units.setItemText(5, QCoreApplication.translate("MainWindow", u"in", None))

        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Number of Cores", None))
        self.numcores.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Non Graphical", None))
        self.non_graphical_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"False", None))
        self.non_graphical_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"True", None))

        self.label.setText(QCoreApplication.translate("MainWindow", u"AEDT Version", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Available AEDT Sessions", None))
        self.process_id_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Create New Session", None))

        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Project Name", None))
        self.browse_project.setText(QCoreApplication.translate("MainWindow", u"Select aedt project", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u" Settings ", None))
        self.component_3d.setText(QCoreApplication.translate("MainWindow", u"3D Component", None))
        self.create_hfss_setup.setText(QCoreApplication.translate("MainWindow", u"Create Hfss Setup", None))
        self.lattice_pair.setText(QCoreApplication.translate("MainWindow", u"Lattice pair", None))
        self.huygens.setText(QCoreApplication.translate("MainWindow", u"Huygens", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Sweep Bandwidth %", None))
        self.slider_value.setText(QCoreApplication.translate("MainWindow", u"20", None))
        ___qtablewidgetitem = self.property_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Property", None));
        ___qtablewidgetitem1 = self.property_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Value", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.design), QCoreApplication.translate("MainWindow", u" Design ", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Analyze Project", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.analysis), QCoreApplication.translate("MainWindow", u" Analysys ", None))
        self.release_button.setText(QCoreApplication.translate("MainWindow", u" Close Antenna Wizard ", None))
        self.menuAntennas.setTitle(QCoreApplication.translate("MainWindow", u"Antennas", None))
        self.menuPatch.setTitle(QCoreApplication.translate("MainWindow", u"Patch", None))
        self.menuHorn.setTitle(QCoreApplication.translate("MainWindow", u"Horn", None))
        self.menuHelix.setTitle(QCoreApplication.translate("MainWindow", u"Helix", None))
        self.menuBowtie.setTitle(QCoreApplication.translate("MainWindow", u"Bowtie", None))
        self.menuConical_Spiral.setTitle(QCoreApplication.translate("MainWindow", u"Conical Spiral", None))
        self.menuCustom.setTitle(QCoreApplication.translate("MainWindow", u"Custom", None))
        self.menuDipole.setTitle(QCoreApplication.translate("MainWindow", u"Dipole", None))
        self.menuLog_Periodic.setTitle(QCoreApplication.translate("MainWindow", u"Log Periodic", None))
        self.menuMiscellaneous.setTitle(QCoreApplication.translate("MainWindow", u"Miscellaneous", None))
        self.menuMonopole.setTitle(QCoreApplication.translate("MainWindow", u"Monopole", None))
        self.menuPIFA.setTitle(QCoreApplication.translate("MainWindow", u"PIFA", None))
        self.menuPlanar_Spiral.setTitle(QCoreApplication.translate("MainWindow", u"Planar Spiral", None))
        self.menuSlot.setTitle(QCoreApplication.translate("MainWindow", u"Slot", None))
        self.menuVivaldi.setTitle(QCoreApplication.translate("MainWindow", u"Vivaldi", None))
    # retranslateUi

