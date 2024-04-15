# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'antenna_synthesis_page.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLayout, QSizePolicy,
    QSlider, QSpacerItem, QVBoxLayout, QWidget)

class Ui_AntennaSynthesis(object):
    def setupUi(self, AntennaSynthesis):
        if not AntennaSynthesis.objectName():
            AntennaSynthesis.setObjectName(u"AntennaSynthesis")
        AntennaSynthesis.resize(956, 661)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AntennaSynthesis.sizePolicy().hasHeightForWidth())
        AntennaSynthesis.setSizePolicy(sizePolicy)
        AntennaSynthesis.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(AntennaSynthesis)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.antenna_synthesis_layout = QHBoxLayout()
        self.antenna_synthesis_layout.setObjectName(u"antenna_synthesis_layout")
        self.antenna_synthesis_layout.setContentsMargins(6, -1, 6, 6)
        self.left_settings_layout = QVBoxLayout()
        self.left_settings_layout.setObjectName(u"left_settings_layout")
        self.left_settings_layout.setContentsMargins(6, -1, 6, 0)
        self.antenna_input_frame = QFrame(AntennaSynthesis)
        self.antenna_input_frame.setObjectName(u"antenna_input_frame")
        sizePolicy.setHeightForWidth(self.antenna_input_frame.sizePolicy().hasHeightForWidth())
        self.antenna_input_frame.setSizePolicy(sizePolicy)
        self.antenna_input_frame.setMinimumSize(QSize(0, 0))
        self.antenna_input = QVBoxLayout(self.antenna_input_frame)
        self.antenna_input.setObjectName(u"antenna_input")
        self.antenna_input.setContentsMargins(6, 1, 6, 1)

        self.left_settings_layout.addWidget(self.antenna_input_frame)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.left_settings_layout.addItem(self.verticalSpacer_2)


        self.antenna_synthesis_layout.addLayout(self.left_settings_layout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.antenna_synthesis_layout.addItem(self.horizontalSpacer)

        self.right_settings_layout = QVBoxLayout()
        self.right_settings_layout.setObjectName(u"right_settings_layout")
        self.right_settings_layout.setContentsMargins(6, -1, 6, -1)
        self.top_antenna_options_frame = QFrame(AntennaSynthesis)
        self.top_antenna_options_frame.setObjectName(u"top_antenna_options_frame")
        self.top_antenna_settings_layout = QHBoxLayout(self.top_antenna_options_frame)
        self.top_antenna_settings_layout.setObjectName(u"top_antenna_settings_layout")
        self.top_antenna_settings_layout.setContentsMargins(6, -1, 1, 1)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.top_antenna_settings_layout.addItem(self.horizontalSpacer_2)

        self.top_antenna_settings_options_layout = QVBoxLayout()
        self.top_antenna_settings_options_layout.setObjectName(u"top_antenna_settings_options_layout")
        self.top_antenna_settings_options_layout.setContentsMargins(6, -1, 0, 0)
        self.component_3d = QCheckBox(self.top_antenna_options_frame)
        self.component_3d.setObjectName(u"component_3d")

        self.top_antenna_settings_options_layout.addWidget(self.component_3d)

        self.create_hfss_setup = QCheckBox(self.top_antenna_options_frame)
        self.create_hfss_setup.setObjectName(u"create_hfss_setup")
        self.create_hfss_setup.setChecked(True)

        self.top_antenna_settings_options_layout.addWidget(self.create_hfss_setup)

        self.lattice_pair = QCheckBox(self.top_antenna_options_frame)
        self.lattice_pair.setObjectName(u"lattice_pair")

        self.top_antenna_settings_options_layout.addWidget(self.lattice_pair)

        self.sweep_widget = QWidget(self.top_antenna_options_frame)
        self.sweep_widget.setObjectName(u"sweep_widget")
        self.sweep_layout = QHBoxLayout(self.sweep_widget)
        self.sweep_layout.setSpacing(6)
        self.sweep_layout.setObjectName(u"sweep_layout")
        self.sweep_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.sweep_layout.setContentsMargins(1, -1, -1, -1)
        self.sweep_label = QLabel(self.sweep_widget)
        self.sweep_label.setObjectName(u"sweep_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sweep_label.sizePolicy().hasHeightForWidth())
        self.sweep_label.setSizePolicy(sizePolicy1)

        self.sweep_layout.addWidget(self.sweep_label)

        self.sweep_slider = QSlider(self.sweep_widget)
        self.sweep_slider.setObjectName(u"sweep_slider")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.sweep_slider.sizePolicy().hasHeightForWidth())
        self.sweep_slider.setSizePolicy(sizePolicy2)
        self.sweep_slider.setMaximum(100)
        self.sweep_slider.setSingleStep(5)
        self.sweep_slider.setPageStep(5)
        self.sweep_slider.setValue(20)
        self.sweep_slider.setOrientation(Qt.Horizontal)
        self.sweep_slider.setTickPosition(QSlider.TicksAbove)
        self.sweep_slider.setTickInterval(5)

        self.sweep_layout.addWidget(self.sweep_slider)

        self.slider_value = QLabel(self.sweep_widget)
        self.slider_value.setObjectName(u"slider_value")
        sizePolicy.setHeightForWidth(self.slider_value.sizePolicy().hasHeightForWidth())
        self.slider_value.setSizePolicy(sizePolicy)

        self.sweep_layout.addWidget(self.slider_value)


        self.top_antenna_settings_options_layout.addWidget(self.sweep_widget)

        self.verticalSpacer_4 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.top_antenna_settings_options_layout.addItem(self.verticalSpacer_4)


        self.top_antenna_settings_layout.addLayout(self.top_antenna_settings_options_layout)


        self.right_settings_layout.addWidget(self.top_antenna_options_frame)

        self.verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.right_settings_layout.addItem(self.verticalSpacer)

        self.bottom_antenna_options_frame = QFrame(AntennaSynthesis)
        self.bottom_antenna_options_frame.setObjectName(u"bottom_antenna_options_frame")
        self.botton_antenna_settings_layout = QHBoxLayout(self.bottom_antenna_options_frame)
        self.botton_antenna_settings_layout.setObjectName(u"botton_antenna_settings_layout")
        self.botton_antenna_settings_layout.setContentsMargins(6, 6, 6, 6)
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.botton_antenna_settings_layout.addItem(self.horizontalSpacer_3)

        self.table_frame = QFrame(self.bottom_antenna_options_frame)
        self.table_frame.setObjectName(u"table_frame")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.table_frame.sizePolicy().hasHeightForWidth())
        self.table_frame.setSizePolicy(sizePolicy3)
        self.table_frame.setMinimumSize(QSize(200, 0))
        self.table_frame.setMaximumSize(QSize(250, 16777215))
        self.table_layout = QVBoxLayout(self.table_frame)
        self.table_layout.setObjectName(u"table_layout")
        self.table_layout.setContentsMargins(6, 6, 6, 6)
        self.table_layout_2 = QVBoxLayout()
        self.table_layout_2.setObjectName(u"table_layout_2")
        self.table_layout_2.setContentsMargins(-1, -1, 6, -1)

        self.table_layout.addLayout(self.table_layout_2)


        self.botton_antenna_settings_layout.addWidget(self.table_frame)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.botton_antenna_settings_layout.addItem(self.horizontalSpacer_4)

        self.botton_image_frame = QFrame(self.bottom_antenna_options_frame)
        self.botton_image_frame.setObjectName(u"botton_image_frame")
        self.botton_image_layout = QGridLayout(self.botton_image_frame)
        self.botton_image_layout.setObjectName(u"botton_image_layout")
        self.botton_image_layout.setContentsMargins(6, 6, 6, 6)
        self.botton_image_layout_2 = QGridLayout()
        self.botton_image_layout_2.setSpacing(0)
        self.botton_image_layout_2.setObjectName(u"botton_image_layout_2")

        self.botton_image_layout.addLayout(self.botton_image_layout_2, 0, 0, 1, 1)


        self.botton_antenna_settings_layout.addWidget(self.botton_image_frame)


        self.right_settings_layout.addWidget(self.bottom_antenna_options_frame)


        self.antenna_synthesis_layout.addLayout(self.right_settings_layout)


        self.verticalLayout_2.addLayout(self.antenna_synthesis_layout)


        self.retranslateUi(AntennaSynthesis)

        QMetaObject.connectSlotsByName(AntennaSynthesis)
    # setupUi

    def retranslateUi(self, AntennaSynthesis):
        AntennaSynthesis.setWindowTitle(QCoreApplication.translate("AntennaSynthesis", u"Form", None))
        self.component_3d.setText(QCoreApplication.translate("AntennaSynthesis", u"3D Component", None))
        self.create_hfss_setup.setText(QCoreApplication.translate("AntennaSynthesis", u"Create HFSS Setup", None))
        self.lattice_pair.setText(QCoreApplication.translate("AntennaSynthesis", u"Lattice pair", None))
        self.sweep_label.setText(QCoreApplication.translate("AntennaSynthesis", u"Sweep Bandwidth %", None))
        self.slider_value.setText(QCoreApplication.translate("AntennaSynthesis", u"20", None))
    # retranslateUi

