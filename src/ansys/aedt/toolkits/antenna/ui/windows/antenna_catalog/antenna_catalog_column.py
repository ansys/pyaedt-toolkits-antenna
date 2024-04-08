# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'antenna_catalog_column.ui'
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_LeftColumn(object):
    def setupUi(self, LeftColumn):
        if not LeftColumn.objectName():
            LeftColumn.setObjectName(u"LeftColumn")
        LeftColumn.resize(815, 600)
        self.verticalLayout = QVBoxLayout(LeftColumn)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.menus = QStackedWidget(LeftColumn)
        self.menus.setObjectName(u"menus")
        self.menu_antenna_catalog = QWidget()
        self.menu_antenna_catalog.setObjectName(u"menu_antenna_catalog")
        self.menu_home_layout = QVBoxLayout(self.menu_antenna_catalog)
        self.menu_home_layout.setSpacing(5)
        self.menu_home_layout.setObjectName(u"menu_home_layout")
        self.menu_home_layout.setContentsMargins(5, 5, 5, 5)
        self.antenna_catalog_vertical_layout = QVBoxLayout()
        self.antenna_catalog_vertical_layout.setObjectName(u"antenna_catalog_vertical_layout")

        self.menu_home_layout.addLayout(self.antenna_catalog_vertical_layout)

        self.menus.addWidget(self.menu_antenna_catalog)

        self.verticalLayout.addWidget(self.menus)


        self.retranslateUi(LeftColumn)

        self.menus.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(LeftColumn)
    # setupUi

    def retranslateUi(self, LeftColumn):
        LeftColumn.setWindowTitle(QCoreApplication.translate("LeftColumn", u"Form", None))
    # retranslateUi

