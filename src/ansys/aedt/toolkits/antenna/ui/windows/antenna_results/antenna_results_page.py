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
        AntennaResults.resize(605, 442)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AntennaResults.sizePolicy().hasHeightForWidth())
        AntennaResults.setSizePolicy(sizePolicy)
        AntennaResults.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(AntennaResults)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.antenna_results_layout = QVBoxLayout()
        self.antenna_results_layout.setSpacing(0)
        self.antenna_results_layout.setObjectName(u"antenna_results_layout")
        self.antenna_results_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.antenna_results_layout.setContentsMargins(-1, 0, -1, 20)
        self.farfield_results = QHBoxLayout()
        self.farfield_results.setObjectName(u"farfield_results")
        self.farfield_2d_frame = QFrame(AntennaResults)
        self.farfield_2d_frame.setObjectName(u"farfield_2d_frame")
        self.farfield_2d_layout = QVBoxLayout(self.farfield_2d_frame)
        self.farfield_2d_layout.setObjectName(u"farfield_2d_layout")

        self.farfield_results.addWidget(self.farfield_2d_frame)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.farfield_results.addItem(self.horizontalSpacer)

        self.farfield_3d_frame = QFrame(AntennaResults)
        self.farfield_3d_frame.setObjectName(u"farfield_3d_frame")
        self.farfield_3d_layout = QVBoxLayout(self.farfield_3d_frame)
        self.farfield_3d_layout.setObjectName(u"farfield_3d_layout")

        self.farfield_results.addWidget(self.farfield_3d_frame)


        self.antenna_results_layout.addLayout(self.farfield_results)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.antenna_results_layout.addItem(self.verticalSpacer)

        self.scattering_frame = QFrame(AntennaResults)
        self.scattering_frame.setObjectName(u"scattering_frame")
        self.scattering_layout = QVBoxLayout(self.scattering_frame)
        self.scattering_layout.setObjectName(u"scattering_layout")

        self.antenna_results_layout.addWidget(self.scattering_frame)


        self.verticalLayout_2.addLayout(self.antenna_results_layout)


        self.retranslateUi(AntennaResults)

        QMetaObject.connectSlotsByName(AntennaResults)
    # setupUi

    def retranslateUi(self, AntennaResults):
        AntennaResults.setWindowTitle(QCoreApplication.translate("AntennaResults", u"Form", None))
    # retranslateUi

