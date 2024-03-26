# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_classpUQlRF.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QSizePolicy,
    QTextBrowser, QVBoxLayout, QWidget)
import resources_rc

class Ui_about_container(object):
    def setupUi(self, about_container):
        if not about_container.objectName():
            about_container.setObjectName(u"about_container")
        about_container.resize(1058, 685)
        about_container.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout = QVBoxLayout(about_container)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(about_container)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"border: 0px;\n"
"background-color: rgb(245, 248, 251);")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(24)
        self.label.setFont(font)

        self.verticalLayout_2.addWidget(self.label, 0, Qt.AlignHCenter)

        self.textBrowser = QTextBrowser(self.frame)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"")

        self.verticalLayout_2.addWidget(self.textBrowser)


        self.verticalLayout.addWidget(self.frame)


        self.retranslateUi(about_container)

        QMetaObject.connectSlotsByName(about_container)
    # setupUi

    def retranslateUi(self, about_container):
        about_container.setWindowTitle(QCoreApplication.translate("about_container", u"Form", None))
        self.label.setText(QCoreApplication.translate("about_container", u"Help", None))
        self.textBrowser.setHtml(QCoreApplication.translate("about_container", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt;\">This is a help page</span></p></body></html>", None))
    # retranslateUi

