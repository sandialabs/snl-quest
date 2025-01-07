# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'processesxPQlLo.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTextBrowser,
    QTextEdit, QVBoxLayout, QWidget)
import afr.resources_rc

class Ui_process_viewer(object):
    def setupUi(self, process_viewer):
        if not process_viewer.objectName():
            process_viewer.setObjectName(u"process_viewer")
        process_viewer.resize(763, 908)
        self.verticalLayout = QVBoxLayout(process_viewer)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_62 = QLabel(process_viewer)
        self.label_62.setObjectName(u"label_62")
        self.label_62.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout.addWidget(self.label_62)

        self.frame_115 = QFrame(process_viewer)
        self.frame_115.setObjectName(u"frame_115")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_115.sizePolicy().hasHeightForWidth())
        self.frame_115.setSizePolicy(sizePolicy)
        self.frame_115.setFrameShape(QFrame.NoFrame)
        self.frame_115.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_55 = QHBoxLayout(self.frame_115)
        self.horizontalLayout_55.setObjectName(u"horizontalLayout_55")
        self.frame_113 = QFrame(self.frame_115)
        self.frame_113.setObjectName(u"frame_113")
        sizePolicy.setHeightForWidth(self.frame_113.sizePolicy().hasHeightForWidth())
        self.frame_113.setSizePolicy(sizePolicy)
        self.frame_113.setFrameShape(QFrame.NoFrame)
        self.frame_113.setFrameShadow(QFrame.Raised)
        self.verticalLayout_64 = QVBoxLayout(self.frame_113)
        self.verticalLayout_64.setObjectName(u"verticalLayout_64")
        self.frame_114 = QFrame(self.frame_113)
        self.frame_114.setObjectName(u"frame_114")
        self.frame_114.setFrameShape(QFrame.NoFrame)
        self.frame_114.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_48 = QHBoxLayout(self.frame_114)
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.label_60 = QLabel(self.frame_114)
        self.label_60.setObjectName(u"label_60")
        self.label_60.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_48.addWidget(self.label_60)

        self.pushButton_6 = QPushButton(self.frame_114)
        self.pushButton_6.setObjectName(u"pushButton_6")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_6.setIcon(icon)
        self.pushButton_6.setIconSize(QSize(24, 24))
        self.pushButton_6.setFlat(True)

        self.horizontalLayout_48.addWidget(self.pushButton_6, 0, Qt.AlignLeft)


        self.verticalLayout_64.addWidget(self.frame_114, 0, Qt.AlignTop)

        self.frame_123 = QFrame(self.frame_113)
        self.frame_123.setObjectName(u"frame_123")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_123.sizePolicy().hasHeightForWidth())
        self.frame_123.setSizePolicy(sizePolicy1)
        self.frame_123.setMinimumSize(QSize(0, 250))
        self.frame_123.setFrameShape(QFrame.NoFrame)
        self.frame_123.setFrameShadow(QFrame.Raised)
        self.prog_layout = QVBoxLayout(self.frame_123)
        self.prog_layout.setObjectName(u"prog_layout")

        self.verticalLayout_64.addWidget(self.frame_123)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_64.addItem(self.verticalSpacer_2)


        self.horizontalLayout_55.addWidget(self.frame_113)

        self.optim_view = QTextEdit(self.frame_115)
        self.optim_view.setObjectName(u"optim_view")
        self.optim_view.setReadOnly(True)

        self.horizontalLayout_55.addWidget(self.optim_view)

        self.horizontalLayout_55.setStretch(0, 1)
        self.horizontalLayout_55.setStretch(1, 2)

        self.verticalLayout.addWidget(self.frame_115)

        self.proc_info = QFrame(process_viewer)
        self.proc_info.setObjectName(u"proc_info")
        self.proc_info.setFrameShape(QFrame.NoFrame)
        self.proc_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.proc_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.proc_info)
        self.textBrowser.setObjectName(u"textBrowser")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy2)
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.hide_proc = QPushButton(self.proc_info)
        self.hide_proc.setObjectName(u"hide_proc")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.hide_proc.setIcon(icon1)
        self.hide_proc.setIconSize(QSize(24, 24))
        self.hide_proc.setFlat(True)

        self.verticalLayout_2.addWidget(self.hide_proc, 0, Qt.AlignHCenter)


        self.verticalLayout.addWidget(self.proc_info)


        self.retranslateUi(process_viewer)

        QMetaObject.connectSlotsByName(process_viewer)
    # setupUi

    def retranslateUi(self, process_viewer):
        process_viewer.setWindowTitle(QCoreApplication.translate("process_viewer", u"Form", None))
        self.label_62.setText(QCoreApplication.translate("process_viewer", u"Optimization", None))
        self.label_60.setText(QCoreApplication.translate("process_viewer", u"Solving", None))
        self.pushButton_6.setText("")
        self.textBrowser.setHtml(QCoreApplication.translate("process_viewer", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Please wait as an optimal solution is found. The terminal output to displayed on this page serves as a sense of progress and is for informational purposes only.</p></body></html>", None))
        self.hide_proc.setText("")
    # retranslateUi

