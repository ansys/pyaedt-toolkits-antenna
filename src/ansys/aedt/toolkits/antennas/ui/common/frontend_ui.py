# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'toolkit.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
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
    QLayout, QLineEdit, QMainWindow, QMenu,
    QMenuBar, QPlainTextEdit, QProgressBar, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QStatusBar,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1107, 1178)
        self.action_save_project = QAction(MainWindow)
        self.action_save_project.setObjectName(u"action_save_project")
        font = QFont()
        font.setPointSize(12)
        self.action_save_project.setFont(font)
        self.actionBowtieNormal = QAction(MainWindow)
        self.actionBowtieNormal.setObjectName(u"actionBowtieNormal")
        self.actionBowtieNormal.setFont(font)
        self.actionBowtieRounded = QAction(MainWindow)
        self.actionBowtieRounded.setObjectName(u"actionBowtieRounded")
        self.actionBowtieSlot = QAction(MainWindow)
        self.actionBowtieSlot.setObjectName(u"actionBowtieSlot")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.main_menu = QWidget(self.centralwidget)
        self.main_menu.setObjectName(u"main_menu")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.main_menu.sizePolicy().hasHeightForWidth())
        self.main_menu.setSizePolicy(sizePolicy1)
        self.gridLayout = QGridLayout(self.main_menu)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, 2, -1)
        self.release_button = QPushButton(self.main_menu)
        self.release_button.setObjectName(u"release_button")
        self.release_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_button, 3, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 3, 1, 1, 1)

        self.release_and_exit_button = QPushButton(self.main_menu)
        self.release_and_exit_button.setObjectName(u"release_and_exit_button")
        self.release_and_exit_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_and_exit_button, 3, 3, 1, 1)

        self.toolkit_tab = QTabWidget(self.main_menu)
        self.toolkit_tab.setObjectName(u"toolkit_tab")
        sizePolicy1.setHeightForWidth(self.toolkit_tab.sizePolicy().hasHeightForWidth())
        self.toolkit_tab.setSizePolicy(sizePolicy1)
        self.toolkit_tab.setTabShape(QTabWidget.Rounded)
        self.toolkit_tab.setIconSize(QSize(20, 20))
        self.toolkit_tab.setMovable(True)
        self.settings = QWidget()
        self.settings.setObjectName(u"settings")
        self.horizontalLayout_25 = QHBoxLayout(self.settings)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.settings_layout = QVBoxLayout()
        self.settings_layout.setObjectName(u"settings_layout")
        self.cores_layout = QHBoxLayout()
        self.cores_layout.setObjectName(u"cores_layout")

        self.settings_layout.addLayout(self.cores_layout)

        self.graphical_layout = QHBoxLayout()
        self.graphical_layout.setObjectName(u"graphical_layout")
        self.graphical_label = QLabel(self.settings)
        self.graphical_label.setObjectName(u"graphical_label")

        self.graphical_layout.addWidget(self.graphical_label)

        self.non_graphical_combo = QComboBox(self.settings)
        self.non_graphical_combo.addItem("")
        self.non_graphical_combo.addItem("")
        self.non_graphical_combo.setObjectName(u"non_graphical_combo")

        self.graphical_layout.addWidget(self.non_graphical_combo)


        self.settings_layout.addLayout(self.graphical_layout)

        self.aedt_version_layout = QHBoxLayout()
        self.aedt_version_layout.setObjectName(u"aedt_version_layout")
        self.version_label = QLabel(self.settings)
        self.version_label.setObjectName(u"version_label")

        self.aedt_version_layout.addWidget(self.version_label)

        self.aedt_version_combo = QComboBox(self.settings)
        self.aedt_version_combo.setObjectName(u"aedt_version_combo")

        self.aedt_version_layout.addWidget(self.aedt_version_combo)


        self.settings_layout.addLayout(self.aedt_version_layout)

        self.aedt_sessions_layout = QHBoxLayout()
        self.aedt_sessions_layout.setObjectName(u"aedt_sessions_layout")
        self.aedt_sessions_label = QLabel(self.settings)
        self.aedt_sessions_label.setObjectName(u"aedt_sessions_label")

        self.aedt_sessions_layout.addWidget(self.aedt_sessions_label)

        self.process_id_combo = QComboBox(self.settings)
        self.process_id_combo.addItem("")
        self.process_id_combo.setObjectName(u"process_id_combo")

        self.aedt_sessions_layout.addWidget(self.process_id_combo)


        self.settings_layout.addLayout(self.aedt_sessions_layout)

        self.project_path_layout = QHBoxLayout()
        self.project_path_layout.setObjectName(u"project_path_layout")
        self.project_path_label = QLabel(self.settings)
        self.project_path_label.setObjectName(u"project_path_label")

        self.project_path_layout.addWidget(self.project_path_label)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.project_path_layout.addItem(self.horizontalSpacer_2)

        self.project_name = QLineEdit(self.settings)
        self.project_name.setObjectName(u"project_name")

        self.project_path_layout.addWidget(self.project_name)


        self.settings_layout.addLayout(self.project_path_layout)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.browse_project = QPushButton(self.settings)
        self.browse_project.setObjectName(u"browse_project")

        self.horizontalLayout_5.addWidget(self.browse_project)


        self.settings_layout.addLayout(self.horizontalLayout_5)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.settings_layout.addItem(self.verticalSpacer_8)

        self.connect_aedtapp = QPushButton(self.settings)
        self.connect_aedtapp.setObjectName(u"connect_aedtapp")
        self.connect_aedtapp.setMinimumSize(QSize(0, 40))

        self.settings_layout.addWidget(self.connect_aedtapp)


        self.horizontalLayout_25.addLayout(self.settings_layout)

        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.horizontalLayout_25.addItem(self.horizontalSpacer_29)

        self.toolkit_tab.addTab(self.settings, "")
        self.design = QWidget()
        self.design.setObjectName(u"design")
        self.design_layout_2 = QVBoxLayout(self.design)
        self.design_layout_2.setObjectName(u"design_layout_2")
        self.design_layout = QHBoxLayout()
        self.design_layout.setObjectName(u"design_layout")
        self.design_settings = QFrame(self.design)
        self.design_settings.setObjectName(u"design_settings")
        sizePolicy1.setHeightForWidth(self.design_settings.sizePolicy().hasHeightForWidth())
        self.design_settings.setSizePolicy(sizePolicy1)
        self.design_settings.setFrameShape(QFrame.StyledPanel)
        self.design_settings.setFrameShadow(QFrame.Raised)
        self.design_settings.setLineWidth(12)
        self.layout_settings = QGridLayout(self.design_settings)
        self.layout_settings.setObjectName(u"layout_settings")
        self.geometry_creation = QHBoxLayout()
        self.geometry_creation.setObjectName(u"geometry_creation")
        self.geometry_creation.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.geometry_creation_layout = QVBoxLayout()
        self.geometry_creation_layout.setObjectName(u"geometry_creation_layout")
        self.aedt_design_layout = QHBoxLayout()
        self.aedt_design_layout.setObjectName(u"aedt_design_layout")
        self.aedt_design_layout.setContentsMargins(0, 0, 0, -1)
        self.project_aedt_layout = QVBoxLayout()
        self.project_aedt_layout.setObjectName(u"project_aedt_layout")
        self.project_aedt_layout.setContentsMargins(-1, 0, -1, -1)
        self.project_adt_label = QLabel(self.design_settings)
        self.project_adt_label.setObjectName(u"project_adt_label")
        self.project_adt_label.setFont(font)
        self.project_adt_label.setAlignment(Qt.AlignCenter)

        self.project_aedt_layout.addWidget(self.project_adt_label)

        self.project_aedt_combo = QComboBox(self.design_settings)
        self.project_aedt_combo.addItem("")
        self.project_aedt_combo.setObjectName(u"project_aedt_combo")

        self.project_aedt_layout.addWidget(self.project_aedt_combo)


        self.aedt_design_layout.addLayout(self.project_aedt_layout)

        self.design_aedt_layout = QVBoxLayout()
        self.design_aedt_layout.setObjectName(u"design_aedt_layout")
        self.design_aedt_label = QLabel(self.design_settings)
        self.design_aedt_label.setObjectName(u"design_aedt_label")
        self.design_aedt_label.setFont(font)
        self.design_aedt_label.setAlignment(Qt.AlignCenter)

        self.design_aedt_layout.addWidget(self.design_aedt_label)

        self.design_aedt_combo = QComboBox(self.design_settings)
        self.design_aedt_combo.addItem("")
        self.design_aedt_combo.setObjectName(u"design_aedt_combo")

        self.design_aedt_layout.addWidget(self.design_aedt_combo)


        self.aedt_design_layout.addLayout(self.design_aedt_layout)


        self.geometry_creation_layout.addLayout(self.aedt_design_layout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.geometry_creation_layout.addItem(self.verticalSpacer)

        self.antenna_settings = QFrame(self.design_settings)
        self.antenna_settings.setObjectName(u"antenna_settings")
        sizePolicy.setHeightForWidth(self.antenna_settings.sizePolicy().hasHeightForWidth())
        self.antenna_settings.setSizePolicy(sizePolicy)
        self.antenna_settings.setFrameShape(QFrame.StyledPanel)
        self.antenna_settings.setFrameShadow(QFrame.Raised)
        self.antenna_settings.setLineWidth(12)
        self.antenna_settings_layout = QGridLayout(self.antenna_settings)
        self.antenna_settings_layout.setObjectName(u"antenna_settings_layout")

        self.geometry_creation_layout.addWidget(self.antenna_settings)


        self.geometry_creation.addLayout(self.geometry_creation_layout)


        self.layout_settings.addLayout(self.geometry_creation, 7, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.layout_settings.addItem(self.horizontalSpacer_4, 7, 2, 1, 1)

        self.new_layout = QVBoxLayout()
        self.new_layout.setObjectName(u"new_layout")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.component_3d = QCheckBox(self.design_settings)
        self.component_3d.setObjectName(u"component_3d")

        self.verticalLayout_4.addWidget(self.component_3d)

        self.create_hfss_setup = QCheckBox(self.design_settings)
        self.create_hfss_setup.setObjectName(u"create_hfss_setup")
        self.create_hfss_setup.setEnabled(True)
        self.create_hfss_setup.setChecked(True)

        self.verticalLayout_4.addWidget(self.create_hfss_setup)

        self.lattice_pair = QCheckBox(self.design_settings)
        self.lattice_pair.setObjectName(u"lattice_pair")

        self.verticalLayout_4.addWidget(self.lattice_pair)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sweep_label = QLabel(self.design_settings)
        self.sweep_label.setObjectName(u"sweep_label")

        self.horizontalLayout.addWidget(self.sweep_label)

        self.sweep_slider = QSlider(self.design_settings)
        self.sweep_slider.setObjectName(u"sweep_slider")
        self.sweep_slider.setMaximum(100)
        self.sweep_slider.setSingleStep(5)
        self.sweep_slider.setValue(20)
        self.sweep_slider.setOrientation(Qt.Horizontal)
        self.sweep_slider.setTickPosition(QSlider.TicksAbove)
        self.sweep_slider.setTickInterval(5)

        self.horizontalLayout.addWidget(self.sweep_slider)

        self.slider_value = QLabel(self.design_settings)
        self.slider_value.setObjectName(u"slider_value")

        self.horizontalLayout.addWidget(self.slider_value)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.new_layout.addLayout(self.verticalLayout_4)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.new_layout.addItem(self.verticalSpacer_2)

        self.property_table = QTableWidget(self.design_settings)
        if (self.property_table.columnCount() < 2):
            self.property_table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.property_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.property_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.property_table.setObjectName(u"property_table")
        self.property_table.setColumnCount(2)

        self.new_layout.addWidget(self.property_table)


        self.layout_settings.addLayout(self.new_layout, 7, 3, 1, 1)


        self.design_layout.addWidget(self.design_settings)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.design_layout.addItem(self.horizontalSpacer_5)


        self.design_layout_2.addLayout(self.design_layout)

        self.toolkit_tab.addTab(self.design, "")
        self.analysis = QWidget()
        self.analysis.setObjectName(u"analysis")
        self.verticalLayout_3 = QVBoxLayout(self.analysis)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.options = QHBoxLayout()
        self.options.setObjectName(u"options")
        self.options.setContentsMargins(-1, 0, -1, -1)
        self.analyze = QPushButton(self.analysis)
        self.analyze.setObjectName(u"analyze")

        self.options.addWidget(self.analyze)

        self.get_results = QPushButton(self.analysis)
        self.get_results.setObjectName(u"get_results")
        self.get_results.setEnabled(False)
        self.get_results.setCheckable(False)
        self.get_results.setChecked(False)
        self.get_results.setAutoDefault(False)

        self.options.addWidget(self.get_results)


        self.verticalLayout_3.addLayout(self.options)

        self.results = QVBoxLayout()
        self.results.setObjectName(u"results")

        self.verticalLayout_3.addLayout(self.results)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.toolkit_tab.addTab(self.analysis, "")
        self.toolkit_settings = QWidget()
        self.toolkit_settings.setObjectName(u"toolkit_settings")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.toolkit_settings.sizePolicy().hasHeightForWidth())
        self.toolkit_settings.setSizePolicy(sizePolicy2)
        self.toolkit_settings.setMaximumSize(QSize(320, 200))
        self.toolkit_settings_layout = QVBoxLayout(self.toolkit_settings)
        self.toolkit_settings_layout.setObjectName(u"toolkit_settings_layout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.freq_units_label = QLabel(self.toolkit_settings)
        self.freq_units_label.setObjectName(u"freq_units_label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.freq_units_label.sizePolicy().hasHeightForWidth())
        self.freq_units_label.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.freq_units_label)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_6)

        self.frequnits = QComboBox(self.toolkit_settings)
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.addItem("")
        self.frequnits.setObjectName(u"frequnits")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frequnits.sizePolicy().hasHeightForWidth())
        self.frequnits.setSizePolicy(sizePolicy4)

        self.horizontalLayout_2.addWidget(self.frequnits)


        self.toolkit_settings_layout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.length_label = QLabel(self.toolkit_settings)
        self.length_label.setObjectName(u"length_label")

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
        self.units.setObjectName(u"units")
        sizePolicy5 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.units.sizePolicy().hasHeightForWidth())
        self.units.setSizePolicy(sizePolicy5)

        self.horizontalLayout_3.addWidget(self.units)


        self.toolkit_settings_layout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.cores_label = QLabel(self.toolkit_settings)
        self.cores_label.setObjectName(u"cores_label")

        self.horizontalLayout_4.addWidget(self.cores_label)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_7)

        self.numcores = QLineEdit(self.toolkit_settings)
        self.numcores.setObjectName(u"numcores")
        sizePolicy5.setHeightForWidth(self.numcores.sizePolicy().hasHeightForWidth())
        self.numcores.setSizePolicy(sizePolicy5)

        self.horizontalLayout_4.addWidget(self.numcores)


        self.toolkit_settings_layout.addLayout(self.horizontalLayout_4)

        self.toolkit_tab.addTab(self.toolkit_settings, "")

        self.gridLayout.addWidget(self.toolkit_tab, 0, 0, 1, 5)


        self.verticalLayout.addWidget(self.main_menu)

        self.log_text = QPlainTextEdit(self.centralwidget)
        self.log_text.setObjectName(u"log_text")
        sizePolicy6 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.log_text.sizePolicy().hasHeightForWidth())
        self.log_text.setSizePolicy(sizePolicy6)

        self.verticalLayout.addWidget(self.log_text)

        self.progress_bar = QProgressBar(self.centralwidget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setFocusPolicy(Qt.NoFocus)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setOrientation(Qt.Horizontal)
        self.progress_bar.setTextDirection(QProgressBar.TopToBottom)

        self.verticalLayout.addWidget(self.progress_bar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.top_menu_bar = QMenuBar(MainWindow)
        self.top_menu_bar.setObjectName(u"top_menu_bar")
        self.top_menu_bar.setGeometry(QRect(0, 0, 1107, 28))
        self.top_menu_bar.setFont(font)
        self.top_menu = QMenu(self.top_menu_bar)
        self.top_menu.setObjectName(u"top_menu")
        self.top_menu.setFont(font)
        self.menuAntennas = QMenu(self.top_menu_bar)
        self.menuAntennas.setObjectName(u"menuAntennas")
        self.menuAntennas.setFont(font)
        self.menuBowtie = QMenu(self.menuAntennas)
        self.menuBowtie.setObjectName(u"menuBowtie")
        self.menuBowtie.setFont(font)
        MainWindow.setMenuBar(self.top_menu_bar)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName(u"status_bar")
        MainWindow.setStatusBar(self.status_bar)

        self.top_menu_bar.addAction(self.top_menu.menuAction())
        self.top_menu_bar.addAction(self.menuAntennas.menuAction())
        self.top_menu.addAction(self.action_save_project)
        self.menuAntennas.addAction(self.menuBowtie.menuAction())
        self.menuBowtie.addAction(self.actionBowtieNormal)
        self.menuBowtie.addAction(self.actionBowtieRounded)
        self.menuBowtie.addAction(self.actionBowtieSlot)

        self.retranslateUi(MainWindow)

        self.toolkit_tab.setCurrentIndex(3)
        self.get_results.setDefault(False)
        self.frequnits.setCurrentIndex(3)
        self.units.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_save_project.setText(QCoreApplication.translate("MainWindow", u"Save project", None))
        self.actionBowtieNormal.setText(QCoreApplication.translate("MainWindow", u"Normal", None))
        self.actionBowtieRounded.setText(QCoreApplication.translate("MainWindow", u"Rounded", None))
        self.actionBowtieSlot.setText(QCoreApplication.translate("MainWindow", u"Slot", None))
        self.release_button.setText(QCoreApplication.translate("MainWindow", u" Close Toolkit ", None))
        self.release_and_exit_button.setText(QCoreApplication.translate("MainWindow", u" Close Desktop and Toolkit ", None))
        self.graphical_label.setText(QCoreApplication.translate("MainWindow", u"Non Graphical", None))
        self.non_graphical_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"False", None))
        self.non_graphical_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"True", None))

        self.version_label.setText(QCoreApplication.translate("MainWindow", u"AEDT Version", None))
        self.aedt_sessions_label.setText(QCoreApplication.translate("MainWindow", u"Available AEDT Sessions", None))
        self.process_id_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Create New Session", None))

        self.project_path_label.setText(QCoreApplication.translate("MainWindow", u"Project Name", None))
        self.browse_project.setText(QCoreApplication.translate("MainWindow", u"Select aedt project", None))
        self.connect_aedtapp.setText(QCoreApplication.translate("MainWindow", u"  Launch AEDT  ", None))
        self.toolkit_tab.setTabText(self.toolkit_tab.indexOf(self.settings), QCoreApplication.translate("MainWindow", u" AEDT Settings ", None))
        self.project_adt_label.setText(QCoreApplication.translate("MainWindow", u"Project  selected", None))
        self.project_aedt_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"No project", None))

        self.design_aedt_label.setText(QCoreApplication.translate("MainWindow", u"Design selected", None))
        self.design_aedt_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"No design", None))

        self.component_3d.setText(QCoreApplication.translate("MainWindow", u"3D Component", None))
        self.create_hfss_setup.setText(QCoreApplication.translate("MainWindow", u"Create Hfss Setup", None))
        self.lattice_pair.setText(QCoreApplication.translate("MainWindow", u"Lattice pair", None))
        self.sweep_label.setText(QCoreApplication.translate("MainWindow", u"Sweep Bandwidth %", None))
        self.slider_value.setText(QCoreApplication.translate("MainWindow", u"20", None))
        ___qtablewidgetitem = self.property_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Property", None));
        ___qtablewidgetitem1 = self.property_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Value", None));
        self.toolkit_tab.setTabText(self.toolkit_tab.indexOf(self.design), QCoreApplication.translate("MainWindow", u" Design ", None))
        self.analyze.setText(QCoreApplication.translate("MainWindow", u"Analyze Project", None))
        self.get_results.setText(QCoreApplication.translate("MainWindow", u"Get results", None))
        self.toolkit_tab.setTabText(self.toolkit_tab.indexOf(self.analysis), QCoreApplication.translate("MainWindow", u" Analysis ", None))
        self.freq_units_label.setText(QCoreApplication.translate("MainWindow", u"Frequency Units", None))
        self.frequnits.setItemText(0, QCoreApplication.translate("MainWindow", u"Hz", None))
        self.frequnits.setItemText(1, QCoreApplication.translate("MainWindow", u"KHz", None))
        self.frequnits.setItemText(2, QCoreApplication.translate("MainWindow", u"MHz", None))
        self.frequnits.setItemText(3, QCoreApplication.translate("MainWindow", u"GHz", None))
        self.frequnits.setItemText(4, QCoreApplication.translate("MainWindow", u"THz", None))

        self.length_label.setText(QCoreApplication.translate("MainWindow", u"Length Units", None))
        self.units.setItemText(0, QCoreApplication.translate("MainWindow", u"um", None))
        self.units.setItemText(1, QCoreApplication.translate("MainWindow", u"mm", None))
        self.units.setItemText(2, QCoreApplication.translate("MainWindow", u"cm", None))
        self.units.setItemText(3, QCoreApplication.translate("MainWindow", u"m", None))
        self.units.setItemText(4, QCoreApplication.translate("MainWindow", u"mil", None))
        self.units.setItemText(5, QCoreApplication.translate("MainWindow", u"in", None))

        self.cores_label.setText(QCoreApplication.translate("MainWindow", u"Number of Cores", None))
        self.numcores.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.toolkit_tab.setTabText(self.toolkit_tab.indexOf(self.toolkit_settings), QCoreApplication.translate("MainWindow", u"Toolkit Settings", None))
        self.top_menu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuAntennas.setTitle(QCoreApplication.translate("MainWindow", u"Antennas", None))
        self.menuBowtie.setTitle(QCoreApplication.translate("MainWindow", u"BowTie", None))
    # retranslateUi

