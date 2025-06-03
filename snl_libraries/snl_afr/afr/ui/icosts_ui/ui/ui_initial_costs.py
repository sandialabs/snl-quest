# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'initial_costsdHvQJz.ui'
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
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTextBrowser, QVBoxLayout, QWidget)
import afr.resources_rc

class Ui_initial_cost_widget(object):
    def setupUi(self, initial_cost_widget):
        if not initial_cost_widget.objectName():
            initial_cost_widget.setObjectName(u"initial_cost_widget")
        initial_cost_widget.resize(1540, 1069)
        self.verticalLayout = QVBoxLayout(initial_cost_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_12 = QFrame(initial_cost_widget)
        self.frame_12.setObjectName(u"frame_12")
        self.frame_12.setFrameShape(QFrame.NoFrame)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_12)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_3 = QLabel(self.frame_12)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_12.addWidget(self.label_3)

        self.frame_13 = QFrame(self.frame_12)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.NoFrame)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.frame_14 = QFrame(self.frame_13)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.NoFrame)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.verticalLayout_43 = QVBoxLayout(self.frame_14)
        self.verticalLayout_43.setObjectName(u"verticalLayout_43")
        self.frame_75 = QFrame(self.frame_14)
        self.frame_75.setObjectName(u"frame_75")
        self.frame_75.setFrameShape(QFrame.NoFrame)
        self.frame_75.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_38 = QHBoxLayout(self.frame_75)
        self.horizontalLayout_38.setSpacing(60)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.frame_76 = QFrame(self.frame_75)
        self.frame_76.setObjectName(u"frame_76")
        self.frame_76.setFrameShape(QFrame.NoFrame)
        self.frame_76.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame_76)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.frame_69 = QFrame(self.frame_76)
        self.frame_69.setObjectName(u"frame_69")
        self.frame_69.setFrameShape(QFrame.NoFrame)
        self.frame_69.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_47 = QHBoxLayout(self.frame_69)
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.label_14 = QLabel(self.frame_69)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_47.addWidget(self.label_14, 0, Qt.AlignTop)

        self.pushButton_2 = QPushButton(self.frame_69)
        self.pushButton_2.setObjectName(u"pushButton_2")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_2.setIcon(icon)
        self.pushButton_2.setIconSize(QSize(24, 24))
        self.pushButton_2.setFlat(True)

        self.horizontalLayout_47.addWidget(self.pushButton_2, 0, Qt.AlignLeft|Qt.AlignTop)


        self.verticalLayout_10.addWidget(self.frame_69)

        self.frame_3 = QFrame(self.frame_76)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.initial_pie_layout = QHBoxLayout(self.frame_3)
        self.initial_pie_layout.setObjectName(u"initial_pie_layout")
        self.verticalSpacer_3 = QSpacerItem(20, 283, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.initial_pie_layout.addItem(self.verticalSpacer_3)


        self.verticalLayout_10.addWidget(self.frame_3)


        self.horizontalLayout_38.addWidget(self.frame_76)

        self.frame_78 = QFrame(self.frame_75)
        self.frame_78.setObjectName(u"frame_78")
        self.frame_78.setFrameShape(QFrame.NoFrame)
        self.frame_78.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_78)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.horizontalLayout.addItem(self.verticalSpacer_2)

        self.scrollArea = QScrollArea(self.frame_78)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(300, 300))
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 442, 300))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setMinimumSize(QSize(0, 0))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_27 = QLabel(self.frame)
        self.label_27.setObjectName(u"label_27")

        self.verticalLayout_5.addWidget(self.label_27)

        self.frame_15 = QFrame(self.frame)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setFrameShape(QFrame.NoFrame)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_15)
        self.horizontalLayout_7.setSpacing(6)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.sic_input = QLineEdit(self.frame_15)
        self.sic_input.setObjectName(u"sic_input")

        self.horizontalLayout_7.addWidget(self.sic_input)

        self.sic_input_store = QPushButton(self.frame_15)
        self.sic_input_store.setObjectName(u"sic_input_store")
        self.sic_input_store.setMaximumSize(QSize(0, 0))
        self.sic_input_store.setFlat(True)

        self.horizontalLayout_7.addWidget(self.sic_input_store)


        self.verticalLayout_5.addWidget(self.frame_15)


        self.verticalLayout_3.addWidget(self.frame)

        self.frame_2 = QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_28 = QLabel(self.frame_2)
        self.label_28.setObjectName(u"label_28")

        self.verticalLayout_4.addWidget(self.label_28)

        self.frame_35 = QFrame(self.frame_2)
        self.frame_35.setObjectName(u"frame_35")
        self.frame_35.setFrameShape(QFrame.NoFrame)
        self.frame_35.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.frame_35)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.wic_input = QLineEdit(self.frame_35)
        self.wic_input.setObjectName(u"wic_input")

        self.horizontalLayout_17.addWidget(self.wic_input)


        self.verticalLayout_4.addWidget(self.frame_35)


        self.verticalLayout_3.addWidget(self.frame_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.horizontalLayout_38.addWidget(self.frame_78, 0, Qt.AlignTop)

        self.horizontalLayout_38.setStretch(0, 1)
        self.horizontalLayout_38.setStretch(1, 5)

        self.verticalLayout_43.addWidget(self.frame_75)


        self.horizontalLayout_6.addWidget(self.frame_14)


        self.verticalLayout_12.addWidget(self.frame_13)


        self.verticalLayout.addWidget(self.frame_12)

        self.i_cost_info = QFrame(initial_cost_widget)
        self.i_cost_info.setObjectName(u"i_cost_info")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.i_cost_info.sizePolicy().hasHeightForWidth())
        self.i_cost_info.setSizePolicy(sizePolicy1)
        self.i_cost_info.setFrameShape(QFrame.NoFrame)
        self.i_cost_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.i_cost_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.i_cost_info)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.hide_ic = QPushButton(self.i_cost_info)
        self.hide_ic.setObjectName(u"hide_ic")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.hide_ic.setIcon(icon1)
        self.hide_ic.setFlat(True)

        self.verticalLayout_2.addWidget(self.hide_ic, 0, Qt.AlignHCenter)


        self.verticalLayout.addWidget(self.i_cost_info)

        self.frame_38 = QFrame(initial_cost_widget)
        self.frame_38.setObjectName(u"frame_38")
        self.frame_38.setFrameShape(QFrame.NoFrame)
        self.frame_38.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_38)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_18.addItem(self.horizontalSpacer_4)

        self.wic_input_store = QPushButton(self.frame_38)
        self.wic_input_store.setObjectName(u"wic_input_store")
        self.wic_input_store.setMaximumSize(QSize(0, 0))

        self.horizontalLayout_18.addWidget(self.wic_input_store)

        self.next_2 = QPushButton(self.frame_38)
        self.next_2.setObjectName(u"next_2")
        self.next_2.setFlat(True)

        self.horizontalLayout_18.addWidget(self.next_2)


        self.verticalLayout.addWidget(self.frame_38)


        self.retranslateUi(initial_cost_widget)

        QMetaObject.connectSlotsByName(initial_cost_widget)
    # setupUi

    def retranslateUi(self, initial_cost_widget):
        initial_cost_widget.setWindowTitle(QCoreApplication.translate("initial_cost_widget", u"Form", None))
        self.label_3.setText(QCoreApplication.translate("initial_cost_widget", u"Data Collection", None))
        self.label_14.setText(QCoreApplication.translate("initial_cost_widget", u"Initial Renewable and Energy Storage Capacities", None))
        self.pushButton_2.setText("")
        self.label_27.setText(QCoreApplication.translate("initial_cost_widget", u" Inital Solar Capacity (MW):", None))
        self.sic_input.setPlaceholderText(QCoreApplication.translate("initial_cost_widget", u"2415.94", None))
        self.sic_input_store.setText("")
        self.label_28.setText(QCoreApplication.translate("initial_cost_widget", u" Initial Wind Capacity (MW):", None))
        self.wic_input.setPlaceholderText(QCoreApplication.translate("initial_cost_widget", u"3218.7", None))
        self.textBrowser.setHtml(QCoreApplication.translate("initial_cost_widget", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Please enter the initial renewable and energy storage capacities on the system in MW.</p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Initial photovoltaic power capacity, e.g., <span style=\" font-family:'Co"
                        "urier New';\">1706.89</span> MW.</li>\n"
"<li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Initial wind power capacity, e.g., <span style=\" font-family:'Courier New';\">658</span> MW.</li>\n"
"<li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Initial storage capacity </li></ul></body></html>", None))
        self.hide_ic.setText("")
        self.wic_input_store.setText(QCoreApplication.translate("initial_cost_widget", u"Save", None))
        self.next_2.setText(QCoreApplication.translate("initial_cost_widget", u"Next", None))
    # retranslateUi

