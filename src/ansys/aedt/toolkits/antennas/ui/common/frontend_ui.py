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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QMainWindow, QMenu, QMenuBar, QPlainTextEdit,
    QProgressBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1107, 1178)
        self.action_save_project = QAction(MainWindow)
        self.action_save_project.setObjectName(u"action_save_project")
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
        self.release_button = QPushButton(self.main_menu)
        self.release_button.setObjectName(u"release_button")
        self.release_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_button, 3, 2, 1, 1)

        self.release_and_exit_button = QPushButton(self.main_menu)
        self.release_and_exit_button.setObjectName(u"release_and_exit_button")
        self.release_and_exit_button.setMinimumSize(QSize(0, 40))

        self.gridLayout.addWidget(self.release_and_exit_button, 3, 3, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 3, 1, 1, 1)

        self.toolkit_tab = QTabWidget(self.main_menu)
        self.toolkit_tab.setObjectName(u"toolkit_tab")
        sizePolicy1.setHeightForWidth(self.toolkit_tab.sizePolicy().hasHeightForWidth())
        self.toolkit_tab.setSizePolicy(sizePolicy1)
        self.toolkit_tab.setTabShape(QTabWidget.Triangular)
        self.settings = QWidget()
        self.settings.setObjectName(u"settings")
        self.horizontalLayout_25 = QHBoxLayout(self.settings)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.settings_layout = QVBoxLayout()
        self.settings_layout.setObjectName(u"settings_layout")
        self.cores_layout = QHBoxLayout()
        self.cores_layout.setObjectName(u"cores_layout")
        self.cores_label = QLabel(self.settings)
        self.cores_label.setObjectName(u"cores_label")

        self.cores_layout.addWidget(self.cores_label)

        self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.cores_layout.addItem(self.horizontalSpacer_30)

        self.numcores = QLineEdit(self.settings)
        self.numcores.setObjectName(u"numcores")

        self.cores_layout.addWidget(self.numcores)


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
        self.verticalLayout_2 = QVBoxLayout(self.design)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.design_layout = QHBoxLayout()
        self.design_layout.setObjectName(u"design_layout")
        self.design_settings = QFrame(self.design)
        self.design_settings.setObjectName(u"design_settings")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.design_settings.sizePolicy().hasHeightForWidth())
        self.design_settings.setSizePolicy(sizePolicy2)
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
        font = QFont()
        font.setPointSize(12)
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

        self.dimension_multiplier_title = QLabel(self.design_settings)
        self.dimension_multiplier_title.setObjectName(u"dimension_multiplier_title")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.dimension_multiplier_title.sizePolicy().hasHeightForWidth())
        self.dimension_multiplier_title.setSizePolicy(sizePolicy3)
        font1 = QFont()
        font1.setPointSize(14)
        self.dimension_multiplier_title.setFont(font1)
        self.dimension_multiplier_title.setAlignment(Qt.AlignCenter)

        self.geometry_creation_layout.addWidget(self.dimension_multiplier_title)

        self.multiplier_layout = QHBoxLayout()
        self.multiplier_layout.setObjectName(u"multiplier_layout")
        self.value_title = QLabel(self.design_settings)
        self.value_title.setObjectName(u"value_title")
        self.value_title.setFont(font)

        self.multiplier_layout.addWidget(self.value_title)

        self.multiplier = QLineEdit(self.design_settings)
        self.multiplier.setObjectName(u"multiplier")
        sizePolicy4 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.multiplier.sizePolicy().hasHeightForWidth())
        self.multiplier.setSizePolicy(sizePolicy4)

        self.multiplier_layout.addWidget(self.multiplier)


        self.geometry_creation_layout.addLayout(self.multiplier_layout)

        self.select_geometry_title = QLabel(self.design_settings)
        self.select_geometry_title.setObjectName(u"select_geometry_title")
        sizePolicy3.setHeightForWidth(self.select_geometry_title.sizePolicy().hasHeightForWidth())
        self.select_geometry_title.setSizePolicy(sizePolicy3)
        self.select_geometry_title.setFont(font1)
        self.select_geometry_title.setAlignment(Qt.AlignHCenter|Qt.AlignTop)

        self.geometry_creation_layout.addWidget(self.select_geometry_title)

        self.geometry_select_layout = QHBoxLayout()
        self.geometry_select_layout.setObjectName(u"geometry_select_layout")
        self.geometry_select_layout.setContentsMargins(-1, -1, -1, 0)
        self.geometry_title = QLabel(self.design_settings)
        self.geometry_title.setObjectName(u"geometry_title")
        self.geometry_title.setFont(font)

        self.geometry_select_layout.addWidget(self.geometry_title)

        self.geometry_combo = QComboBox(self.design_settings)
        self.geometry_combo.addItem("")
        self.geometry_combo.addItem("")
        self.geometry_combo.setObjectName(u"geometry_combo")
        self.geometry_combo.setFont(font)

        self.geometry_select_layout.addWidget(self.geometry_combo)


        self.geometry_creation_layout.addLayout(self.geometry_select_layout)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.geometry_creation_layout.addItem(self.verticalSpacer_6)

        self.create_geometry_buttom = QPushButton(self.design_settings)
        self.create_geometry_buttom.setObjectName(u"create_geometry_buttom")
        self.create_geometry_buttom.setMinimumSize(QSize(0, 50))
        self.create_geometry_buttom.setFont(font)

        self.geometry_creation_layout.addWidget(self.create_geometry_buttom)


        self.geometry_creation.addLayout(self.geometry_creation_layout)


        self.layout_settings.addLayout(self.geometry_creation, 7, 1, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.layout_settings.addItem(self.horizontalSpacer_4, 7, 2, 1, 1)

        self.new_layout = QVBoxLayout()
        self.new_layout.setObjectName(u"new_layout")
        self.frame = QFrame(self.design_settings)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)

        self.new_layout.addWidget(self.frame)


        self.layout_settings.addLayout(self.new_layout, 7, 3, 1, 1)


        self.design_layout.addWidget(self.design_settings)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.design_layout.addItem(self.horizontalSpacer_5)


        self.verticalLayout_2.addLayout(self.design_layout)

        self.toolkit_tab.addTab(self.design, "")

        self.gridLayout.addWidget(self.toolkit_tab, 0, 0, 1, 5)


        self.verticalLayout.addWidget(self.main_menu)

        self.log_text = QPlainTextEdit(self.centralwidget)
        self.log_text.setObjectName(u"log_text")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.log_text.sizePolicy().hasHeightForWidth())
        self.log_text.setSizePolicy(sizePolicy5)

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
        MainWindow.setMenuBar(self.top_menu_bar)
        self.status_bar = QStatusBar(MainWindow)
        self.status_bar.setObjectName(u"status_bar")
        MainWindow.setStatusBar(self.status_bar)

        self.top_menu_bar.addAction(self.top_menu.menuAction())
        self.top_menu.addAction(self.action_save_project)

        self.retranslateUi(MainWindow)

        self.toolkit_tab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action_save_project.setText(QCoreApplication.translate("MainWindow", u"Save project", None))
        self.release_button.setText(QCoreApplication.translate("MainWindow", u" Close Toolkit ", None))
        self.release_and_exit_button.setText(QCoreApplication.translate("MainWindow", u" Close Desktop and Toolkit ", None))
        self.cores_label.setText(QCoreApplication.translate("MainWindow", u"Number of Cores", None))
        self.numcores.setText(QCoreApplication.translate("MainWindow", u"4", None))
        self.graphical_label.setText(QCoreApplication.translate("MainWindow", u"Non Graphical", None))
        self.non_graphical_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"False", None))
        self.non_graphical_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"True", None))

        self.version_label.setText(QCoreApplication.translate("MainWindow", u"AEDT Version", None))
        self.aedt_sessions_label.setText(QCoreApplication.translate("MainWindow", u"Available AEDT Sessions", None))
        self.process_id_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Create New Session", None))

        self.project_path_label.setText(QCoreApplication.translate("MainWindow", u"Project Name", None))
        self.browse_project.setText(QCoreApplication.translate("MainWindow", u"Select aedt project", None))
        self.connect_aedtapp.setText(QCoreApplication.translate("MainWindow", u"  Launch AEDT  ", None))
        self.toolkit_tab.setTabText(self.toolkit_tab.indexOf(self.settings), QCoreApplication.translate("MainWindow", u" Settings ", None))
        self.project_adt_label.setText(QCoreApplication.translate("MainWindow", u"Project  selected", None))
        self.project_aedt_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"No project", None))

        self.design_aedt_label.setText(QCoreApplication.translate("MainWindow", u"Design selected", None))
        self.design_aedt_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"No design", None))

        self.dimension_multiplier_title.setText(QCoreApplication.translate("MainWindow", u"Dimension multiplier", None))
        self.value_title.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.multiplier.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.select_geometry_title.setText(QCoreApplication.translate("MainWindow", u"Select geometry", None))
        self.geometry_title.setText(QCoreApplication.translate("MainWindow", u"Geometry", None))
        self.geometry_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Box", None))
        self.geometry_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"Sphere", None))

        self.create_geometry_buttom.setText(QCoreApplication.translate("MainWindow", u"Create geometry", None))
        self.toolkit_tab.setTabText(self.toolkit_tab.indexOf(self.design), QCoreApplication.translate("MainWindow", u" Design ", None))
        self.top_menu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
    # retranslateUi

