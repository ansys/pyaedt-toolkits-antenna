# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'antenna_catalog_page.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QMetaObject
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLayout
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QVBoxLayout


class Ui_AntennaCatalog(object):
    def setupUi(self, AntennaCatalog):
        if not AntennaCatalog.objectName():
            AntennaCatalog.setObjectName(u"AntennaCatalog")
        AntennaCatalog.resize(605, 442)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AntennaCatalog.sizePolicy().hasHeightForWidth())
        AntennaCatalog.setSizePolicy(sizePolicy)
        AntennaCatalog.setMinimumSize(QSize(0, 0))
        self.verticalLayout_2 = QVBoxLayout(AntennaCatalog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.antenna_catalog_layout = QVBoxLayout()
        self.antenna_catalog_layout.setSpacing(0)
        self.antenna_catalog_layout.setObjectName(u"antenna_catalog_layout")
        self.antenna_catalog_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.antenna_catalog_layout.setContentsMargins(-1, 0, -1, 20)

        self.verticalLayout_2.addLayout(self.antenna_catalog_layout)


        self.retranslateUi(AntennaCatalog)

        QMetaObject.connectSlotsByName(AntennaCatalog)
    # setupUi

    def retranslateUi(self, AntennaCatalog):
        AntennaCatalog.setWindowTitle(QCoreApplication.translate("AntennaCatalog", u"Form", None))
    # retranslateUi

