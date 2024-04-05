# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'toolkit.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

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
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QHeaderView
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QProgressBar
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSlider
from PySide6.QtWidgets import QSpacerItem
from PySide6.QtWidgets import QStatusBar
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1226, 1178)
        self.action_save_project = QAction(MainWindow)
        self.action_save_project.setObjectName("action_save_project")
        font = QFont()
        font.setPointSize(12)
        self.action_save_project.setFont(font)
        self.actionBowtieNormal = QAction(MainWindow)
        self.actionBowtieNormal.setObjectName("actionBowtieNormal")
        self.actionBowtieNormal.setFont(font)
        self.actionBowtieRounded = QAction(MainWindow)
        self.actionBowtieRounded.setObjectName("actionBowtieRounded")
        self.actionBowtieRounded.setFont(font)
        self.actionBowtieSlot = QAction(MainWindow)
        self.actionBowtieSlot.setObjectName("actionBowtieSlot")
        self.actionBowtieSlot.setFont(font)
        self.actionDipolePlanar = QAction(MainWindow)
        self.actionDipolePlanar.setObjectName("actionDipolePlanar")
        self.actionDipolePlanar.setFont(font)
        self.actionDipoleWire = QAction(MainWindow)
        self.actionDipoleWire.setObjectName("actionDipoleWire")
        self.actionDipoleWire.setFont(font)
        self.actionArchimedean = QAction(MainWindow)
        self.actionArchimedean.setObjectName("actionArchimedean")
        self.actionArchimedean.setFont(font)
        self.actionLog = QAction(MainWindow)
        self.actionLog.setObjectName("actionLog")
        self.actionLog.setFont(font)
        self.actionSinuous = QAction(MainWindow)
        self.actionSinuous.setObjectName("actionSinuous")
        self.actionSinuous.setFont(font)
        self.actionAxial = QAction(MainWindow)
        self.actionAxial.setObjectName("actionAxial")
        self.actionAxial.setFont(font)
        self.actionAxial_Mode_Continuous_Taper = QAction(MainWindow)
        self.actionAxial_Mode_Continuous_Taper.setObjectName("actionAxial_Mode_Continuous_Taper")
        self.actionAxial_Mode_Continuous_Taper.setFont(font)
        self.actionNormal_Mode = QAction(MainWindow)
        self.actionNormal_Mode.setObjectName("actionNormal_Mode")
        self.actionNormal_Mode.setFont(font)
        self.actionQuadrifilar_Open = QAction(MainWindow)
        self.actionQuadrifilar_Open.setObjectName("actionQuadrifilar_Open")
        self.actionQuadrifilar_Open.setFont(font)
        self.actionQuadrifilar_Short = QAction(MainWindow)
        self.actionQuadrifilar_Short.setObjectName("actionQuadrifilar_Short")
        self.actionQuadrifilar_Short.setFont(font)
        self.actionConical_Corrugated = QAction(MainWindow)
        self.actionConical_Corrugated.setObjectName("actionConical_Corrugated")
        self.actionConical_Corrugated.setFont(font)
        self.actionConical = QAction(MainWindow)
        self.actionConical.setObjectName("actionConical")
        self.actionConical.setFont(font)
        self.actionE_Plane_Sectoral = QAction(MainWindow)
        self.actionE_Plane_Sectoral.setObjectName("actionE_Plane_Sectoral")
        self.actionE_Plane_Sectoral.setFont(font)
        self.actionElliptical = QAction(MainWindow)
        self.actionElliptical.setObjectName("actionElliptical")
        self.actionElliptical.setFont(font)
        self.actionH_Plane_Sectoral = QAction(MainWindow)
        self.actionH_Plane_Sectoral.setObjectName("actionH_Plane_Sectoral")
        self.actionH_Plane_Sectoral.setFont(font)
        self.actionPyramidal = QAction(MainWindow)
        self.actionPyramidal.setObjectName("actionPyramidal")
        self.actionPyramidal.setFont(font)
        self.actionPyramidal_Ridged = QAction(MainWindow)
        self.actionPyramidal_Ridged.setObjectName("actionPyramidal_Ridged")
        self.actionPyramidal_Ridged.setFont(font)
        self.actionQuad_Ridged = QAction(MainWindow)
        self.actionQuad_Ridged.setObjectName("actionQuad_Ridged")
        self.actionQuad_Ridged.setFont(font)
        self.actionLDPA_Dipole_array = QAction(MainWindow)
        self.actionLDPA_Dipole_array.setObjectName("actionLDPA_Dipole_array")
        self.actionLDPA_Dipole_array.setFont(font)
        self.actionToothed = QAction(MainWindow)
        self.actionToothed.setObjectName("actionToothed")
        self.actionToothed.setFont(font)
        self.actionTrapezoidal = QAction(MainWindow)
        self.actionTrapezoidal.setObjectName("actionTrapezoidal")
        self.actionTrapezoidal.setFont(font)
        self.actionBicone = QAction(MainWindow)
        self.actionBicone.setObjectName("actionBicone")
        self.actionBicone.setFont(font)
        self.actionDiscone = QAction(MainWindow)
        self.actionDiscone.setObjectName("actionDiscone")
        self.actionDiscone.setFont(font)
        self.actionBlade_Antenna = QAction(MainWindow)
        self.actionBlade_Antenna.setObjectName("actionBlade_Antenna")
        self.actionBlade_Antenna.setFont(font)
        self.actionCircular_Disc = QAction(MainWindow)
        self.actionCircular_Disc.setObjectName("actionCircular_Disc")
        self.actionCircular_Disc.setFont(font)
        self.actionElliptical_Base_Strip = QAction(MainWindow)
        self.actionElliptical_Base_Strip.setObjectName("actionElliptical_Base_Strip")
        self.actionElliptical_Base_Strip.setFont(font)
        self.actionVertical_Trapezoidal = QAction(MainWindow)
        self.actionVertical_Trapezoidal.setObjectName("actionVertical_Trapezoidal")
        self.actionVertical_Trapezoidal.setFont(font)
        self.actionWireMonopole = QAction(MainWindow)
        self.actionWireMonopole.setObjectName("actionWireMonopole")
        self.actionWireMonopole.setFont(font)
        self.actionWire_Infinite_ground = QAction(MainWindow)
        self.actionWire_Infinite_ground.setObjectName("actionWire_Infinite_ground")
        self.actionWire_Infinite_ground.setFont(font)
        self.actionShorting_Pin = QAction(MainWindow)
        self.actionShorting_Pin.setObjectName("actionShorting_Pin")
        self.actionShorting_Pin.setFont(font)
        self.actionShorting_Plate = QAction(MainWindow)
        self.actionShorting_Plate.setObjectName("actionShorting_Plate")
        self.actionShorting_Plate.setFont(font)
        self.actionPlanar_Inverted_F = QAction(MainWindow)
        self.actionPlanar_Inverted_F.setObjectName("actionPlanar_Inverted_F")
        self.actionPlanar_Inverted_F.setFont(font)
        self.actionElliptical_Edge_Fed = QAction(MainWindow)
        self.actionElliptical_Edge_Fed.setObjectName("actionElliptical_Edge_Fed")
        self.actionElliptical_Edge_Fed.setFont(font)
        self.actionElliptical_Inset_Fed = QAction(MainWindow)
        self.actionElliptical_Inset_Fed.setObjectName("actionElliptical_Inset_Fed")
        self.actionElliptical_Inset_Fed.setFont(font)
        self.actionElliptical_Probe_Fed = QAction(MainWindow)
        self.actionElliptical_Probe_Fed.setObjectName("actionElliptical_Probe_Fed")
        self.actionElliptical_Probe_Fed.setFont(font)
        self.actionRectangular_Edge_Fed = QAction(MainWindow)
        self.actionRectangular_Edge_Fed.setObjectName("actionRectangular_Edge_Fed")
        self.actionRectangular_Edge_Fed.setFont(font)
        self.actionRectangular_Inset_Fed = QAction(MainWindow)
        self.actionRectangular_Inset_Fed.setObjectName("actionRectangular_Inset_Fed")
        self.actionRectangular_Inset_Fed.setFont(font)
        self.actionRectangular_Probe_Fed = QAction(MainWindow)
        self.actionRectangular_Probe_Fed.setObjectName("actionRectangular_Probe_Fed")
        self.actionRectangular_Probe_Fed.setFont(font)
        self.actionPlanarArchimidean = QAction(MainWindow)
        self.actionPlanarArchimidean.setObjectName("actionPlanarArchimidean")
        self.actionPlanarArchimidean.setFont(font)
        self.actionPlanar_Archimidean_Absorber = QAction(MainWindow)
        self.actionPlanar_Archimidean_Absorber.setObjectName("actionPlanar_Archimidean_Absorber")
        self.actionPlanar_Archimidean_Absorber.setFont(font)
        self.actionPlanar_Log = QAction(MainWindow)
        self.actionPlanar_Log.setObjectName("actionPlanar_Log")
        self.actionPlanar_Log.setFont(font)
        self.actionPlanar_Log_Absorber = QAction(MainWindow)
        self.actionPlanar_Log_Absorber.setObjectName("actionPlanar_Log_Absorber")
        self.actionPlanar_Log_Absorber.setFont(font)
        self.actionPlanar_Sinuous = QAction(MainWindow)
        self.actionPlanar_Sinuous.setObjectName("actionPlanar_Sinuous")
        self.actionPlanar_Sinuous.setFont(font)
        self.actionPlanar_Sinuous_Absorber = QAction(MainWindow)
        self.actionPlanar_Sinuous_Absorber.setObjectName("actionPlanar_Sinuous_Absorber")
        self.actionPlanar_Sinuous_Absorber.setFont(font)
        self.actionCassegrain = QAction(MainWindow)
        self.actionCassegrain.setObjectName("actionCassegrain")
        self.actionCassegrain.setFont(font)
        self.actionGregorian = QAction(MainWindow)
        self.actionGregorian.setObjectName("actionGregorian")
        self.actionGregorian.setFont(font)
        self.actionParabolic = QAction(MainWindow)
        self.actionParabolic.setObjectName("actionParabolic")
        self.actionParabolic.setFont(font)
        self.actionSplash_Plate = QAction(MainWindow)
        self.actionSplash_Plate.setObjectName("actionSplash_Plate")
        self.actionSplash_Plate.setFont(font)
        self.actionCavity_backed_array = QAction(MainWindow)
        self.actionCavity_backed_array.setObjectName("actionCavity_backed_array")
        self.actionCavity_backed_array.setFont(font)
        self.actionCavity_backed_T_bar_fed = QAction(MainWindow)
        self.actionCavity_backed_T_bar_fed.setObjectName("actionCavity_backed_T_bar_fed")
        self.actionCavity_backed_T_bar_fed.setFont(font)
        self.actionGap_Feed = QAction(MainWindow)
        self.actionGap_Feed.setObjectName("actionGap_Feed")
        self.actionGap_Feed.setFont(font)
        self.actionMicrostrip_Feed = QAction(MainWindow)
        self.actionMicrostrip_Feed.setObjectName("actionMicrostrip_Feed")
        self.actionMicrostrip_Feed.setFont(font)
        self.actionVivaldi = QAction(MainWindow)
        self.actionVivaldi.setObjectName("actionVivaldi")
        self.actionVivaldi.setFont(font)
        self.actionVivaldi_Stepped = QAction(MainWindow)
        self.actionVivaldi_Stepped.setObjectName("actionVivaldi_Stepped")
        self.actionVivaldi_Stepped.setFont(font)
        self.actionQuasiYagi = QAction(MainWindow)
        self.actionQuasiYagi.setObjectName("actionQuasiYagi")
        self.actionQuasiYagi.setFont(font)
        self.actionQuasiYagiWire = QAction(MainWindow)
        self.actionQuasiYagiWire.setObjectName("actionQuasiYagiWire")
        self.actionQuasiYagiWire.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_menu = QWidget(self.centralwidget)
        self.main_menu.setObjectName("main_menu")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.main_menu.sizePolicy().hasHeightForWidth())
        self.main_menu.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.main_menu)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, 2, -1)
        self.release_button = QPushButton(self.main_menu)
        self.release_button.setObjectName("release_button")
        self.release_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_button, 3, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 3, 1, 1, 1)

        self.release_and_exit_button = QPushButton(self.main_menu)
        self.release_and_exit_button.setObjectName("release_and_exit_button")
        self.release_and_exit_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_and_exit_button, 3, 3, 1, 1)

        self.toolkit_tab = QTabWidget(self.main_menu)
        self.toolkit_tab.setObjectName("toolkit_tab")
        sizePolicy1.setHeightForWidth(self.toolkit_tab.sizePolicy().hasHeightForWidth())
        self.toolkit_tab.setSizePolicy(sizePolicy1)
        self.toolkit_tab.setTabShape(QTabWidget.Rounded)
        self.toolkit_tab.setIconSize(QSize(20, 20))
        self.toolkit_tab.setMovable(True)
        self.settings = QWidget()
        self.settings.setObjectName("settings")
        self.horizontalLayout_25 = QHBoxLayout(self.settings)
        self.horizontalLayout_25.setObjectName("horizontalLayout_25")
        self.settings_layout = QVBoxLayout()
        self.settings_layout.setObjectName("settings_layout")
        self.cores_layout = QHBoxLayout()
        self.cores_layout.setObjectName("cores_layout")

        self.settings_layout.addLayout(self.cores_layout)

        self.graphical_layout = QHBoxLayout()
        self.graphical_layout.setObjectName("graphical_layout")
        self.graphical_label = QLabel(self.settings)
        self.graphical_label.setObjectName("graphical_label")

        self.graphical_layout.addWidget(self.graphical_label)

        self.non_graphical_combo = QComboBox(self.settings)
        self.non_graphical_combo.addItem("")
        self.non_graphical_combo.addItem("")
        self.non_graphical_combo.setObjectName("non_graphical_combo")

        self.graphical_layout.addWidget(self.non_graphical_combo)

        self.settings_layout.addLayout(self.graphical_layout)

        self.aedt_version_layout = QHBoxLayout()
        self.aedt_version_layout.setObjectName("aedt_version_layout")
        self.version_label = QLabel(self.settings)
        self.version_label.setObjectName("version_label")

        self.aedt_version_layout.addWidget(self.version_label)

        self.aedt_version_combo = QComboBox(self.settings)
        self.aedt_version_combo.setObjectName("aedt_version_combo")

        self.aedt_version_layout.addWidget(self.aedt_version_combo)

        self.settings_layout.addLayout(self.aedt_version_layout)

        self.aedt_sessions_layout = QHBoxLayout()
        self.aedt_sessions_layout.setObjectName("aedt_sessions_layout")
        self.aedt_sessions_label = QLabel(self.settings)
        self.aedt_sessions_label.setObjectName("aedt_sessions_label")

        self.aedt_sessions_layout.addWidget(self.aedt_sessions_label)

        self.process_id_combo = QComboBox(self.settings)
        self.process_id_combo.addItem("")
        self.process_id_combo.setObjectName("process_id_combo")

        self.aedt_sessions_layout.addWidget(self.process_id_combo)

        self.settings_layout.addLayout(self.aedt_sessions_layout)

        self.project_path_layout = QHBoxLayout()
        self.project_path_layout.setObjectName("project_path_layout")
        self.project_path_label = QLabel(self.settings)
        self.project_path_label.setObjectName("project_path_label")

        self.project_path_layout.addWidget(self.project_path_label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.project_path_layout.addItem(self.horizontalSpacer_2)

        self.project_name = QLineEdit(self.settings)
        self.project_name.setObjectName("project_name")

        self.project_path_layout.addWidget(self.project_name)

        self.settings_layout.addLayout(self.project_path_layout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.browse_project = QPushButton(self.settings)
        self.browse_project.setObjectName("browse_project")

        self.horizontalLayout_5.addWidget(self.browse_project)

        self.settings_layout.addLayout(self.horizontalLayout_5)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.settings_layout.addItem(self.verticalSpacer_8)

        self.connect_aedtapp = QPushButton(self.settings)
        self.connect_aedtapp.setObjectName("connect_aedtapp")
        self.connect_aedtapp.setMinimumSize(QSize(0, 40))

        self.settings_layout.addWidget(self.connect_aedtapp)

        self.horizontalLayout_25.addLayout(self.settings_layout)

        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_29)

        self.toolkit_tab.addTab(self.settings, "")
        self.design = QWidget()
        self.design.setObjectName("design")
        self.design_layout_2 = QVBoxLayout(self.design)
        self.design_layout_2.setObjectName("design_layout_2")
        self.design_layout = QHBoxLayout()
        self.design_layout.setObjectName("design_layout")
        self.design_settings = QFrame(self.design)
        self.design_settings.setObjectName("design_settings")
        sizePolicy1.setHeightForWidth(self.design_settings.sizePolicy().hasHeightForWidth())
        self.design_settings.setSizePolicy(sizePolicy1)
        self.design_settings.setFrameShape(QFrame.StyledPanel)
        self.design_settings.setFrameShadow(QFrame.Raised)
        self.design_settings.setLineWidth(12)
        self.layout_settings = QGridLayout(self.design_settings)
        self.layout_settings.setObjectName("layout_settings")
        self.geometry_creation = QHBoxLayout()
        self.geometry_creation.setObjectName("geometry_creation")
        self.geometry_creation.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.geometry_creation_layout = QVBoxLayout()
        self.geometry_creation_layout.setObjectName("geometry_creation_layout")
        self.aedt_design_layout = QHBoxLayout()
        self.aedt_design_layout.setObjectName("aedt_design_layout")
        self.aedt_design_layout.setContentsMargins(0, 0, 0, -1)
        self.project_aedt_layout = QVBoxLayout()
        self.project_aedt_layout.setObjectName("project_aedt_layout")
        self.project_aedt_layout.setContentsMargins(-1, 0, -1, -1)
        self.project_adt_label = QLabel(self.design_settings)
        self.project_adt_label.setObjectName("project_adt_label")
        self.project_adt_label.setFont(font)
        self.project_adt_label.setAlignment(Qt.AlignCenter)

        self.project_aedt_layout.addWidget(self.project_adt_label)

        self.project_aedt_combo = QComboBox(self.design_settings)
        self.project_aedt_combo.addItem("")
        self.project_aedt_combo.setObjectName("project_aedt_combo")

        self.project_aedt_layout.addWidget(self.project_aedt_combo)

        self.aedt_design_layout.addLayout(self.project_aedt_layout)

        self.design_aedt_layout = QVBoxLayout()
        self.design_aedt_layout.setObjectName("design_aedt_layout")
        self.design_aedt_label = QLabel(self.design_settings)
        self.design_aedt_label.setObjectName("design_aedt_label")
        self.design_aedt_label.setFont(font)
        self.design_aedt_label.setAlignment(Qt.AlignCenter)

        self.design_aedt_layout.addWidget(self.design_aedt_label)

        self.design_aedt_combo = QComboBox(self.design_settings)
        self.design_aedt_combo.addItem("")
        self.design_aedt_combo.setObjectName("design_aedt_combo")

        self.design_aedt_layout.addWidget(self.design_aedt_combo)

        self.aedt_design_layout.addLayout(self.design_aedt_layout)

        self.geometry_creation_layout.addLayout(self.aedt_design_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.geometry_creation_layout.addItem(self.verticalSpacer)

        self.antenna_settings = QFrame(self.design_settings)
        self.antenna_settings.setObjectName("antenna_settings")
        sizePolicy.setHeightForWidth(self.antenna_settings.sizePolicy().hasHeightForWidth())
        self.antenna_settings.setSizePolicy(sizePolicy)
        self.antenna_settings.setFrameShape(QFrame.StyledPanel)
        self.antenna_settings.setFrameShadow(QFrame.Raised)
        self.antenna_settings.setLineWidth(12)
        self.antenna_settings_layout = QGridLayout(self.antenna_settings)
        self.antenna_settings_layout.setObjectName("antenna_settings_layout")

        self.geometry_creation_layout.addWidget(self.antenna_settings)

        self.geometry_creation.addLayout(self.geometry_creation_layout)

        self.layout_settings.addLayout(self.geometry_creation, 7, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.layout_settings.addItem(self.horizontalSpacer_4, 7, 2, 1, 1)

        self.new_layout = QVBoxLayout()
        self.new_layout.setObjectName("new_layout")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, 0, -1, -1)
        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_10)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.component_3d = QCheckBox(self.design_settings)
        self.component_3d.setObjectName("component_3d")
        self.component_3d.setFont(font)

        self.verticalLayout_2.addWidget(self.component_3d)

        self.create_hfss_setup = QCheckBox(self.design_settings)
        self.create_hfss_setup.setObjectName("create_hfss_setup")
        self.create_hfss_setup.setEnabled(True)
        self.create_hfss_setup.setFont(font)
        self.create_hfss_setup.setChecked(True)

        self.verticalLayout_2.addWidget(self.create_hfss_setup)

        self.lattice_pair = QCheckBox(self.design_settings)
        self.lattice_pair.setObjectName("lattice_pair")
        self.lattice_pair.setFont(font)

        self.verticalLayout_2.addWidget(self.lattice_pair)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, -1, 0, 0)
        self.sweep_label = QLabel(self.design_settings)
        self.sweep_label.setObjectName("sweep_label")
        self.sweep_label.setFont(font)

        self.horizontalLayout_9.addWidget(self.sweep_label)

        self.sweep_slider = QSlider(self.design_settings)
        self.sweep_slider.setObjectName("sweep_slider")
        self.sweep_slider.setMaximum(100)
        self.sweep_slider.setSingleStep(5)
        self.sweep_slider.setValue(20)
        self.sweep_slider.setOrientation(Qt.Horizontal)
        self.sweep_slider.setTickPosition(QSlider.TicksAbove)
        self.sweep_slider.setTickInterval(5)

        self.horizontalLayout_9.addWidget(self.sweep_slider)

        self.slider_value = QLabel(self.design_settings)
        self.slider_value.setObjectName("slider_value")
        self.slider_value.setFont(font)

        self.horizontalLayout_9.addWidget(self.slider_value)

        self.verticalLayout_2.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_8.addLayout(self.verticalLayout_2)

        self.new_layout.addLayout(self.horizontalLayout_8)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.new_layout.addItem(self.verticalSpacer_2)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_9)

        self.property_table = QTableWidget(self.design_settings)
        if self.property_table.columnCount() < 2:
            self.property_table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.property_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.property_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.property_table.setObjectName("property_table")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.property_table.sizePolicy().hasHeightForWidth())
        self.property_table.setSizePolicy(sizePolicy2)
        self.property_table.setFont(font)
        self.property_table.setColumnCount(2)

        self.horizontalLayout_6.addWidget(self.property_table)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)

        self.image_layout = QGridLayout()
        self.image_layout.setObjectName("image_layout")

        self.horizontalLayout_6.addLayout(self.image_layout)

        self.new_layout.addLayout(self.horizontalLayout_6)

        self.layout_settings.addLayout(self.new_layout, 7, 3, 1, 1)

        self.design_layout.addWidget(self.design_settings)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.design_layout.addItem(self.horizontalSpacer_5)

        self.design_layout_2.addLayout(self.design_layout)

        self.toolkit_tab.addTab(self.design, "")
        self.analysis = QWidget()
        self.analysis.setObjectName("analysis")
        self.verticalLayout_3 = QVBoxLayout(self.analysis)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.options = QHBoxLayout()
        self.options.setObjectName("options")
        self.options.setContentsMargins(-1, 0, -1, -1)
        self.analyze = QPushButton(self.analysis)
        self.analyze.setObjectName("analyze")

        self.options.addWidget(self.analyze)

        self.get_results = QPushButton(self.analysis)
        self.get_results.setObjectName("get_results")
        self.get_results.setEnabled(False)
        self.get_results.setCheckable(False)
        self.get_results.setChecked(False)
        self.get_results.setAutoDefault(False)

        self.options.addWidget(self.get_results)

        self.verticalLayout_3.addLayout(self.options)

        self.results = QVBoxLayout()
        self.results.setObjectName("results")

        self.verticalLayout_3.addLayout(self.results)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.toolkit_tab.addTab(self.analysis, "")
        self.toolkit_settings = QWidget()
        self.toolkit_settings.setObjectName("toolkit_settings")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.toolkit_settings.sizePolicy().hasHeightForWidth())
        self.toolkit_settings.setSizePolicy(sizePolicy3)
        self.toolkit_settings.setMaximumSize(QSize(320, 200))
        self.toolkit_settings_layout = QVBoxLayout(self.toolkit_settings)
        self.toolkit_settings_layout.setObjectName("toolkit_settings_layout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.freq_units_label = QLabel(self.toolkit_settings)
        self.freq_units_label.setObjectName("freq_units_label")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.freq_units_label.sizePolicy().hasHeightForWidth())
        self.freq_units_label.setSizePolicy(sizePolicy4)

        self.horizontalLayout_2.addWidget(self.freq_units_label)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_6)

        self.frequnits = QComboBox(self.toolkit_settings)
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.setObjectName("frequnits")
        sizePolicy5 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.frequnits.sizePolicy().hasHeightForWidth())
        self.frequnits.setSizePolicy(sizePolicy5)

        self.horizontalLayout_2.addWidget(self.frequnits)

        self.toolkit_settings_layout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.length_label = QLabel(self.toolkit_settings)
        self.length_label.setObjectName("length_label")

        self.horizontalLayout_3.addWidget(self.length_label)

        self.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_31)

        self.units = QComboBox(self.toolkit_settings)
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.addItem("")
        self.units.setObjectName("units")
        sizePolicy6 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.units.sizePolicy().hasHeightForWidth())
        self.units.setSizePolicy(sizePolicy6)

        self.horizontalLayout_3.addWidget(self.units)

        self.toolkit_settings_layout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.cores_label = QLabel(self.toolkit_settings)
        self.cores_label.setObjectName("cores_label")

        self.horizontalLayout_4.addWidget(self.cores_label)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)

        self.numcores = QLineEdit(self.toolkit_settings)
        self.numcores.setObjectName("numcores")
        sizePolicy6.setHeightForWidth(self.numcores.sizePolicy().hasHeightForWidth())
        self.numcores.setSizePolicy(sizePolicy6)

        self.horizontalLayout_4.addWidget(self.numcores)

        self.toolkit_settings_layout.addLayout(self.horizontalLayout_4)

        self.toolkit_tab.addTab(self.toolkit_settings, "")

        self.gridLayout.addWidget(self.toolkit_tab, 0, 0, 1, 5)

        self.verticalLayout.addWidget(self.main_menu)

        self.log_text = QPlainTextEdit(self.centralwidget)
        self.log_text.setObjectName("log_text")
        sizePolicy7 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.log_text.sizePolicy().hasHeightForWidth())
        self.log_text.setSizePolicy(sizePolicy7)

        self.verticalLayout.addWidget(self.log_text)

        self.progress_bar = QProgressBar(self.centralwidget)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setFocusPolicy(Qt.NoFocus)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setOrientation(Qt.Horizontal)
        self.progress_bar.setTextDirection(QProgressBar.TopToBottom)

        self.verticalLayout.addWidget(self.progress_bar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.top_menu_bar = QMenuBar(MainWindow)
        self.top_menu_bar.setObjectName("top_menu_bar")
        self.top_menu_bar.setGeometry(QRect(0, 0, 1226, 28))
        self.top_menu_bar.setFont(font)
        self.top_menu = QMenu(self.top_menu_bar)
        self.top_menu.setObjectName("top_menu")
        self.top_menu.setFont(font)
        self.menuAntennas = QMenu(self.top_menu_bar)
        self.menuAntennas.setObjectName("menuAntennas")
        self.menuAntennas.setFont(font)
        self.menuBowtie = QMenu(self.menuAntennas)
        self.menuBowtie.setObjectName("menuBowtie")
        self.menuBowtie.setFont(font)
        self.menuConical_Spiral = QMenu(self.menuAntennas)
        self.menuConical_Spiral.setObjectName("menuConical_Spiral")
        self.menuDipole = QMenu(self.menuAntennas)
        self.menuDipole.setObjectName("menuDipole")
        self.menuHelix = QMenu(self.menuAntennas)
        self.menuHelix.setObjectName("menuHelix")
        self.menuHorn = QMenu(self.menuAntennas)
        self.menuHorn.setObjectName("menuHorn")
        self.menuLog_Periodic = QMenu(self.menuAntennas)
        self.menuLog_Periodic.setObjectName("menuLog_Periodic")
        self.menuMisc = QMenu(self.menuAntennas)
        self.menuMisc.setObjectName("menuMisc")
        self.menuMonopole = QMenu(self.menuAntennas)
        self.menuMonopole.setObjectName("menuMonopole")
        self.menuPIFA = QMenu(self.menuAntennas)
        self.menuPIFA.setObjectName("menuPIFA")
        self.menuPatch = QMenu(self.menuAntennas)
        self.menuPatch.setObjectName("menuPatch")
        self.menuPlanar_Spiral = QMenu(self.menuAntennas)
        self.menuPlanar_Spiral.setObjectName("menuPlanar_Spiral")
        self.menuReflector = QMenu(self.menuAntennas)
        self.menuReflector.setObjectName("menuReflector")
        self.menuSlot = QMenu(self.menuAntennas)
        self.menuSlot.setObjectName("menuSlot")
        self.menuVivaldi = QMenu(self.menuAntennas)
        self.menuVivaldi.setObjectName("menuVivaldi")
        self.menuYagi_Uda = QMenu(self.menuAntennas)
        self.menuYagi_Uda.setObjectName("menuYagi_Uda")
        MainWindow.setMenuBar(self.top_menu_bar)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName("status_bar")
        MainWindow.setStatusBar(self.status_bar)

        self.top_menu_bar.addAction(self.top_menu.menuAction())
        self.top_menu_bar.addAction(self.menuAntennas.menuAction())
        self.top_menu.addAction(self.action_save_project)
        self.menuAntennas.addAction(self.menuBowtie.menuAction())
        self.menuAntennas.addAction(self.menuConical_Spiral.menuAction())
        self.menuAntennas.addAction(self.menuDipole.menuAction())
        self.menuAntennas.addAction(self.menuHelix.menuAction())
        self.menuAntennas.addAction(self.menuHorn.menuAction())
        self.menuAntennas.addAction(self.menuLog_Periodic.menuAction())
        self.menuAntennas.addAction(self.menuMisc.menuAction())
        self.menuAntennas.addAction(self.menuMonopole.menuAction())
        self.menuAntennas.addAction(self.menuPIFA.menuAction())
        self.menuAntennas.addAction(self.menuPatch.menuAction())
        self.menuAntennas.addAction(self.menuPlanar_Spiral.menuAction())
        self.menuAntennas.addAction(self.menuReflector.menuAction())
        self.menuAntennas.addAction(self.menuSlot.menuAction())
        self.menuAntennas.addAction(self.menuVivaldi.menuAction())
        self.menuAntennas.addAction(self.menuYagi_Uda.menuAction())
        self.menuBowtie.addAction(self.actionBowtieNormal)
        self.menuBowtie.addAction(self.actionBowtieRounded)
        self.menuBowtie.addAction(self.actionBowtieSlot)
        self.menuConical_Spiral.addAction(self.actionArchimedean)
        self.menuConical_Spiral.addAction(self.actionLog)
        self.menuConical_Spiral.addAction(self.actionSinuous)
        self.menuDipole.addAction(self.actionDipolePlanar)
        self.menuDipole.addAction(self.actionDipoleWire)
        self.menuHelix.addAction(self.actionAxial)
        self.menuHelix.addAction(self.actionAxial_Mode_Continuous_Taper)
        self.menuHelix.addAction(self.actionNormal_Mode)
        self.menuHelix.addAction(self.actionQuadrifilar_Open)
        self.menuHelix.addAction(self.actionQuadrifilar_Short)
        self.menuHorn.addAction(self.actionConical_Corrugated)
        self.menuHorn.addAction(self.actionConical)
        self.menuHorn.addAction(self.actionE_Plane_Sectoral)
        self.menuHorn.addAction(self.actionElliptical)
        self.menuHorn.addAction(self.actionH_Plane_Sectoral)
        self.menuHorn.addAction(self.actionPyramidal)
        self.menuHorn.addAction(self.actionPyramidal_Ridged)
        self.menuHorn.addAction(self.actionQuad_Ridged)
        self.menuLog_Periodic.addAction(self.actionLDPA_Dipole_array)
        self.menuLog_Periodic.addAction(self.actionToothed)
        self.menuLog_Periodic.addAction(self.actionTrapezoidal)
        self.menuMisc.addAction(self.actionBicone)
        self.menuMisc.addAction(self.actionDiscone)
        self.menuMonopole.addAction(self.actionBlade_Antenna)
        self.menuMonopole.addAction(self.actionCircular_Disc)
        self.menuMonopole.addAction(self.actionElliptical_Base_Strip)
        self.menuMonopole.addAction(self.actionVertical_Trapezoidal)
        self.menuMonopole.addAction(self.actionWireMonopole)
        self.menuMonopole.addAction(self.actionWire_Infinite_ground)
        self.menuPIFA.addAction(self.actionShorting_Pin)
        self.menuPIFA.addAction(self.actionShorting_Plate)
        self.menuPIFA.addAction(self.actionPlanar_Inverted_F)
        self.menuPatch.addAction(self.actionElliptical_Edge_Fed)
        self.menuPatch.addAction(self.actionElliptical_Inset_Fed)
        self.menuPatch.addAction(self.actionElliptical_Probe_Fed)
        self.menuPatch.addAction(self.actionRectangular_Edge_Fed)
        self.menuPatch.addAction(self.actionRectangular_Inset_Fed)
        self.menuPatch.addAction(self.actionRectangular_Probe_Fed)
        self.menuPlanar_Spiral.addAction(self.actionPlanarArchimidean)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Archimidean_Absorber)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Log)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Log_Absorber)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Sinuous)
        self.menuPlanar_Spiral.addAction(self.actionPlanar_Sinuous_Absorber)
        self.menuReflector.addAction(self.actionCassegrain)
        self.menuReflector.addAction(self.actionGregorian)
        self.menuReflector.addAction(self.actionParabolic)
        self.menuReflector.addAction(self.actionSplash_Plate)
        self.menuSlot.addAction(self.actionCavity_backed_array)
        self.menuSlot.addAction(self.actionCavity_backed_T_bar_fed)
        self.menuSlot.addAction(self.actionGap_Feed)
        self.menuSlot.addAction(self.actionMicrostrip_Feed)
        self.menuVivaldi.addAction(self.actionVivaldi)
        self.menuVivaldi.addAction(self.actionVivaldi_Stepped)
        self.menuYagi_Uda.addAction(self.actionQuasiYagi)
        self.menuYagi_Uda.addAction(self.actionQuasiYagiWire)

        self.retranslateUi(MainWindow)

        self.toolkit_tab.setCurrentIndex(0)
        self.get_results.setDefault(False)
        self.frequnits.setCurrentIndex(3)
        self.units.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", "MainWindow", None))
        self.action_save_project.setText(QCoreApplication.translate("MainWindow", "Save project", None))
        self.actionBowtieNormal.setText(QCoreApplication.translate("MainWindow", "Normal", None))
        self.actionBowtieRounded.setText(QCoreApplication.translate("MainWindow", "Rounded", None))
        self.actionBowtieSlot.setText(QCoreApplication.translate("MainWindow", "Slot", None))
        self.actionDipolePlanar.setText(QCoreApplication.translate("MainWindow", "Planar", None))
        self.actionDipoleWire.setText(QCoreApplication.translate("MainWindow", "Wire", None))
        self.actionArchimedean.setText(QCoreApplication.translate("MainWindow", "Archimedean", None))
        self.actionLog.setText(QCoreApplication.translate("MainWindow", "Log", None))
        self.actionSinuous.setText(QCoreApplication.translate("MainWindow", "Sinuous", None))
        self.actionAxial.setText(QCoreApplication.translate("MainWindow", "Axial Mode", None))
        self.actionAxial_Mode_Continuous_Taper.setText(
            QCoreApplication.translate("MainWindow", "Axial Mode Continuous Taper", None)
        )
        self.actionNormal_Mode.setText(QCoreApplication.translate("MainWindow", "Normal Mode", None))
        self.actionQuadrifilar_Open.setText(QCoreApplication.translate("MainWindow", "Quadrifilar Open", None))
        self.actionQuadrifilar_Short.setText(QCoreApplication.translate("MainWindow", "Quadrifilar Short", None))
        self.actionConical_Corrugated.setText(QCoreApplication.translate("MainWindow", "Conical Corrugated", None))
        self.actionConical.setText(QCoreApplication.translate("MainWindow", "Conical", None))
        self.actionE_Plane_Sectoral.setText(QCoreApplication.translate("MainWindow", "E-Plane Sectoral", None))
        self.actionElliptical.setText(QCoreApplication.translate("MainWindow", "Elliptical", None))
        self.actionH_Plane_Sectoral.setText(QCoreApplication.translate("MainWindow", "H-Plane Sectoral", None))
        self.actionPyramidal.setText(QCoreApplication.translate("MainWindow", "Pyramidal ", None))
        self.actionPyramidal_Ridged.setText(QCoreApplication.translate("MainWindow", "Pyramidal Ridged", None))
        self.actionQuad_Ridged.setText(QCoreApplication.translate("MainWindow", "Quad Ridged ", None))
        self.actionLDPA_Dipole_array.setText(QCoreApplication.translate("MainWindow", "LDPA Dipole array", None))
        self.actionToothed.setText(QCoreApplication.translate("MainWindow", "Toothed", None))
        self.actionTrapezoidal.setText(QCoreApplication.translate("MainWindow", "Trapezoidal", None))
        self.actionBicone.setText(QCoreApplication.translate("MainWindow", "Bicone", None))
        self.actionDiscone.setText(QCoreApplication.translate("MainWindow", "Discone", None))
        self.actionBlade_Antenna.setText(QCoreApplication.translate("MainWindow", "Blade Antenna", None))
        self.actionCircular_Disc.setText(QCoreApplication.translate("MainWindow", "Circular Disc ", None))
        self.actionElliptical_Base_Strip.setText(
            QCoreApplication.translate("MainWindow", "Elliptical-Base Strip", None)
        )
        self.actionVertical_Trapezoidal.setText(QCoreApplication.translate("MainWindow", "Vertical Trapezoidal", None))
        self.actionWireMonopole.setText(QCoreApplication.translate("MainWindow", "Wire", None))
        self.actionWire_Infinite_ground.setText(
            QCoreApplication.translate("MainWindow", "Wire - Infinite ground", None)
        )
        self.actionShorting_Pin.setText(QCoreApplication.translate("MainWindow", "Shorting Pin", None))
        self.actionShorting_Plate.setText(QCoreApplication.translate("MainWindow", "Shorting Plate", None))
        self.actionPlanar_Inverted_F.setText(QCoreApplication.translate("MainWindow", "Planar Inverted-F", None))
        self.actionElliptical_Edge_Fed.setText(QCoreApplication.translate("MainWindow", "Elliptical-Edge Fed", None))
        self.actionElliptical_Inset_Fed.setText(QCoreApplication.translate("MainWindow", "Elliptical-Inset Fed", None))
        self.actionElliptical_Probe_Fed.setText(QCoreApplication.translate("MainWindow", "Elliptical-Probe Fed", None))
        self.actionRectangular_Edge_Fed.setText(QCoreApplication.translate("MainWindow", "Rectangular-Edge Fed", None))
        self.actionRectangular_Inset_Fed.setText(
            QCoreApplication.translate("MainWindow", "Rectangular-Inset Fed", None)
        )
        self.actionRectangular_Probe_Fed.setText(
            QCoreApplication.translate("MainWindow", "Rectangular-Probe Fed", None)
        )
        self.actionPlanarArchimidean.setText(QCoreApplication.translate("MainWindow", "Planar Archimidean", None))
        self.actionPlanar_Archimidean_Absorber.setText(
            QCoreApplication.translate("MainWindow", "Planar Archimidean with Absorber", None)
        )
        self.actionPlanar_Log.setText(QCoreApplication.translate("MainWindow", "Planar Log", None))
        self.actionPlanar_Log_Absorber.setText(
            QCoreApplication.translate("MainWindow", "Planar Log with Absorber", None)
        )
        self.actionPlanar_Sinuous.setText(QCoreApplication.translate("MainWindow", "Planar Sinuous", None))
        self.actionPlanar_Sinuous_Absorber.setText(
            QCoreApplication.translate("MainWindow", "Planar Sinuous with Absorber", None)
        )
        self.actionCassegrain.setText(QCoreApplication.translate("MainWindow", "Cassegrain", None))
        self.actionGregorian.setText(QCoreApplication.translate("MainWindow", "Gregorian", None))
        self.actionParabolic.setText(QCoreApplication.translate("MainWindow", "Parabolic", None))
        self.actionSplash_Plate.setText(QCoreApplication.translate("MainWindow", "Splash Plate", None))
        self.actionCavity_backed_array.setText(QCoreApplication.translate("MainWindow", "Cavity backed array", None))
        self.actionCavity_backed_T_bar_fed.setText(
            QCoreApplication.translate("MainWindow", "Cavity backed T-bar-fed", None)
        )
        self.actionGap_Feed.setText(QCoreApplication.translate("MainWindow", "Gap Feed", None))
        self.actionMicrostrip_Feed.setText(QCoreApplication.translate("MainWindow", "Microstrip Feed", None))
        self.actionVivaldi.setText(QCoreApplication.translate("MainWindow", "Vivaldi", None))
        self.actionVivaldi_Stepped.setText(QCoreApplication.translate("MainWindow", "Vivaldi Stepped", None))
        self.actionQuasiYagi.setText(QCoreApplication.translate("MainWindow", "Quasi-Yagi", None))
        self.actionQuasiYagiWire.setText(QCoreApplication.translate("MainWindow", "Wire", None))
        self.release_button.setText(QCoreApplication.translate("MainWindow", " Close Toolkit ", None))
        self.release_and_exit_button.setText(
            QCoreApplication.translate("MainWindow", " Close Desktop and Toolkit ", None)
        )
        self.graphical_label.setText(QCoreApplication.translate("MainWindow", "Non Graphical", None))
        self.non_graphical_combo.setItemText(0, QCoreApplication.translate("MainWindow", "False", None))
        self.non_graphical_combo.setItemText(1, QCoreApplication.translate("MainWindow", "True", None))

        self.version_label.setText(QCoreApplication.translate("MainWindow", "AEDT Version", None))
        self.aedt_sessions_label.setText(QCoreApplication.translate("MainWindow", "Available AEDT Sessions", None))
        self.process_id_combo.setItemText(0, QCoreApplication.translate("MainWindow", "Create New Session", None))

        self.project_path_label.setText(QCoreApplication.translate("MainWindow", "Project Name", None))
        self.browse_project.setText(QCoreApplication.translate("MainWindow", "Select aedt project", None))
        self.connect_aedtapp.setText(QCoreApplication.translate("MainWindow", "  Launch AEDT  ", None))
        self.toolkit_tab.setTabText(
            self.toolkit_tab.indexOf(self.settings), QCoreApplication.translate("MainWindow", " AEDT Settings ", None)
        )
        self.project_adt_label.setText(QCoreApplication.translate("MainWindow", "Project selected", None))
        self.project_aedt_combo.setItemText(0, QCoreApplication.translate("MainWindow", "No project", None))

        self.design_aedt_label.setText(QCoreApplication.translate("MainWindow", "Design selected", None))
        self.design_aedt_combo.setItemText(0, QCoreApplication.translate("MainWindow", "No design", None))

        self.component_3d.setText(QCoreApplication.translate("MainWindow", "3D Component", None))
        self.create_hfss_setup.setText(QCoreApplication.translate("MainWindow", "Create HFSS Setup", None))
        self.lattice_pair.setText(QCoreApplication.translate("MainWindow", "Lattice pair", None))
        self.sweep_label.setText(QCoreApplication.translate("MainWindow", "Sweep Bandwidth %", None))
        self.slider_value.setText(QCoreApplication.translate("MainWindow", "20", None))
        ___qtablewidgetitem = self.property_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", "Property", None))
        ___qtablewidgetitem1 = self.property_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", "Value", None))
        self.toolkit_tab.setTabText(
            self.toolkit_tab.indexOf(self.design), QCoreApplication.translate("MainWindow", " Design ", None)
        )
        self.analyze.setText(QCoreApplication.translate("MainWindow", "Analyze Project", None))
        self.get_results.setText(QCoreApplication.translate("MainWindow", "Get results", None))
        self.toolkit_tab.setTabText(
            self.toolkit_tab.indexOf(self.analysis), QCoreApplication.translate("MainWindow", " Analysis ", None)
        )
        self.freq_units_label.setText(QCoreApplication.translate("MainWindow", "Frequency Units", None))
        self.frequnits.setItemText(0, QCoreApplication.translate("MainWindow", "Hz", None))
        self.frequnits.setItemText(1, QCoreApplication.translate("MainWindow", "KHz", None))
        self.frequnits.setItemText(2, QCoreApplication.translate("MainWindow", "MHz", None))
        self.frequnits.setItemText(3, QCoreApplication.translate("MainWindow", "GHz", None))
        self.frequnits.setItemText(4, QCoreApplication.translate("MainWindow", "THz", None))

        self.length_label.setText(QCoreApplication.translate("MainWindow", "Length Units", None))
        self.units.setItemText(0, QCoreApplication.translate("MainWindow", "um", None))
        self.units.setItemText(1, QCoreApplication.translate("MainWindow", "mm", None))
        self.units.setItemText(2, QCoreApplication.translate("MainWindow", "cm", None))
        self.units.setItemText(3, QCoreApplication.translate("MainWindow", "m", None))
        self.units.setItemText(4, QCoreApplication.translate("MainWindow", "mil", None))
        self.units.setItemText(5, QCoreApplication.translate("MainWindow", "in", None))

        self.cores_label.setText(QCoreApplication.translate("MainWindow", "Number of Cores", None))
        self.numcores.setText(QCoreApplication.translate("MainWindow", "4", None))
        self.toolkit_tab.setTabText(
            self.toolkit_tab.indexOf(self.toolkit_settings),
            QCoreApplication.translate("MainWindow", "Toolkit Settings", None),
        )
        self.top_menu.setTitle(QCoreApplication.translate("MainWindow", "File", None))
        self.menuAntennas.setTitle(QCoreApplication.translate("MainWindow", "Antennas", None))
        self.menuBowtie.setTitle(QCoreApplication.translate("MainWindow", "BowTie", None))
        self.menuConical_Spiral.setTitle(QCoreApplication.translate("MainWindow", "Conical Spiral", None))
        self.menuDipole.setTitle(QCoreApplication.translate("MainWindow", "Dipole", None))
        self.menuHelix.setTitle(QCoreApplication.translate("MainWindow", "Helix", None))
        self.menuHorn.setTitle(QCoreApplication.translate("MainWindow", "Horn", None))
        self.menuLog_Periodic.setTitle(QCoreApplication.translate("MainWindow", "Log Periodic", None))
        self.menuMisc.setTitle(QCoreApplication.translate("MainWindow", "Misc", None))
        self.menuMonopole.setTitle(QCoreApplication.translate("MainWindow", "Monopole", None))
        self.menuPIFA.setTitle(QCoreApplication.translate("MainWindow", "PIFA", None))
        self.menuPatch.setTitle(QCoreApplication.translate("MainWindow", "Patch", None))
        self.menuPlanar_Spiral.setTitle(QCoreApplication.translate("MainWindow", "Planar Spiral", None))
        self.menuReflector.setTitle(QCoreApplication.translate("MainWindow", "Reflector", None))
        self.menuSlot.setTitle(QCoreApplication.translate("MainWindow", "Slot", None))
        self.menuVivaldi.setTitle(QCoreApplication.translate("MainWindow", "Vivaldi", None))
        self.menuYagi_Uda.setTitle(QCoreApplication.translate("MainWindow", "Yagi-Uda", None))

    # retranslateUi
