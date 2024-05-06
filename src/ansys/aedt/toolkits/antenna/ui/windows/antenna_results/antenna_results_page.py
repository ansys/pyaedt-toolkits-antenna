# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'antenna_results_page.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLayout,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_AntennaResults(object):
    def setupUi(self, AntennaResults):
        if not AntennaResults.objectName():
            AntennaResults.setObjectName(u"AntennaResults")
        AntennaResults.resize(1471, 1083)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AntennaResults.sizePolicy().hasHeightForWidth())
        AntennaResults.setSizePolicy(sizePolicy)
        AntennaResults.setMinimumSize(QSize(0, 0))
        self.horizontalLayout = QHBoxLayout(AntennaResults)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.antenna_results_layout = QVBoxLayout()
        self.antenna_results_layout.setSpacing(0)
        self.antenna_results_layout.setObjectName(u"antenna_results_layout")
        self.antenna_results_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.antenna_results_layout.setContentsMargins(-1, 0, -1, 0)
        self.farfield_2d_results = QHBoxLayout()
        self.farfield_2d_results.setObjectName(u"farfield_2d_results")
        self.farfield_2d_phi_frame = QFrame(AntennaResults)
        self.farfield_2d_phi_frame.setObjectName(u"farfield_2d_phi_frame")
        self.farfield_2d_phi_frame.setMaximumSize(QSize(350, 16777215))
        self.farfield_2d_phi_layout = QVBoxLayout(self.farfield_2d_phi_frame)
        self.farfield_2d_phi_layout.setObjectName(u"farfield_2d_phi_layout")

        self.farfield_2d_results.addWidget(self.farfield_2d_phi_frame)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.farfield_2d_results.addItem(self.horizontalSpacer)

        self.farfield_2d_theta_frame = QFrame(AntennaResults)
        self.farfield_2d_theta_frame.setObjectName(u"farfield_2d_theta_frame")
        self.farfield_2d_theta_frame.setMaximumSize(QSize(350, 16777215))
        self.farfield_2d_theta_layout = QVBoxLayout(self.farfield_2d_theta_frame)
        self.farfield_2d_theta_layout.setObjectName(u"farfield_2d_theta_layout")

        self.farfield_2d_results.addWidget(self.farfield_2d_theta_frame)


        self.antenna_results_layout.addLayout(self.farfield_2d_results)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.antenna_results_layout.addItem(self.verticalSpacer_2)

        self.scattering_frame = QFrame(AntennaResults)
        self.scattering_frame.setObjectName(u"scattering_frame")
        self.scattering_frame.setMaximumSize(QSize(740, 16777215))
        self.scattering_layout = QVBoxLayout(self.scattering_frame)
        self.scattering_layout.setObjectName(u"scattering_layout")

        self.antenna_results_layout.addWidget(self.scattering_frame)


        self.horizontalLayout.addLayout(self.antenna_results_layout)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.farfield_3d_result_layout = QVBoxLayout()
        self.farfield_3d_result_layout.setObjectName(u"farfield_3d_result_layout")
        self.farfield_3d_frame = QFrame(AntennaResults)
        self.farfield_3d_frame.setObjectName(u"farfield_3d_frame")
        self.farfield_3d_layout = QVBoxLayout(self.farfield_3d_frame)
        self.farfield_3d_layout.setObjectName(u"farfield_3d_layout")
        self.farfield_3d_layout.setContentsMargins(-1, 1, -1, -1)

        self.farfield_3d_result_layout.addWidget(self.farfield_3d_frame)


        self.horizontalLayout.addLayout(self.farfield_3d_result_layout)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)


        self.retranslateUi(AntennaResults)

        QMetaObject.connectSlotsByName(AntennaResults)
    # setupUi

    def retranslateUi(self, AntennaResults):
        AntennaResults.setWindowTitle(QCoreApplication.translate("AntennaResults", u"Form", None))
    # retranslateUi

