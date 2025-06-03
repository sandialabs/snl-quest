# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cost_scene_uiJkVNmx.ui'
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

class Ui_cost_scene(object):
    def setupUi(self, cost_scene):
        if not cost_scene.objectName():
            cost_scene.setObjectName(u"cost_scene")
        cost_scene.resize(1466, 1015)
        self.verticalLayout = QVBoxLayout(cost_scene)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_18 = QFrame(cost_scene)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setFrameShape(QFrame.NoFrame)
        self.frame_18.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.frame_18)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.label_4 = QLabel(self.frame_18)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_15.addWidget(self.label_4)

        self.frame_19 = QFrame(self.frame_18)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setFrameShape(QFrame.NoFrame)
        self.frame_19.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_19)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.frame_20 = QFrame(self.frame_19)
        self.frame_20.setObjectName(u"frame_20")
        self.frame_20.setFrameShape(QFrame.NoFrame)
        self.frame_20.setFrameShadow(QFrame.Raised)
        self.verticalLayout_49 = QVBoxLayout(self.frame_20)
        self.verticalLayout_49.setObjectName(u"verticalLayout_49")
        self.frame_88 = QFrame(self.frame_20)
        self.frame_88.setObjectName(u"frame_88")
        self.frame_88.setFrameShape(QFrame.NoFrame)
        self.frame_88.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_51 = QHBoxLayout(self.frame_88)
        self.horizontalLayout_51.setSpacing(60)
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.frame_89 = QFrame(self.frame_88)
        self.frame_89.setObjectName(u"frame_89")
        self.frame_89.setFrameShape(QFrame.NoFrame)
        self.frame_89.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.frame_89)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.frame_16 = QFrame(self.frame_89)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setFrameShape(QFrame.NoFrame)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_16)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_17 = QLabel(self.frame_16)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_8.addWidget(self.label_17)

        self.pushButton_3 = QPushButton(self.frame_16)
        self.pushButton_3.setObjectName(u"pushButton_3")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_3.setIcon(icon)
        self.pushButton_3.setIconSize(QSize(24, 24))
        self.pushButton_3.setFlat(True)

        self.horizontalLayout_8.addWidget(self.pushButton_3, 0, Qt.AlignLeft)


        self.verticalLayout_14.addWidget(self.frame_16)

        self.frame_122 = QFrame(self.frame_89)
        self.frame_122.setObjectName(u"frame_122")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_122.sizePolicy().hasHeightForWidth())
        self.frame_122.setSizePolicy(sizePolicy)
        self.frame_122.setFrameShape(QFrame.NoFrame)
        self.frame_122.setFrameShadow(QFrame.Raised)
        self.cost_pie_layout = QHBoxLayout(self.frame_122)
        self.cost_pie_layout.setObjectName(u"cost_pie_layout")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.cost_pie_layout.addItem(self.verticalSpacer_2)


        self.verticalLayout_14.addWidget(self.frame_122)


        self.horizontalLayout_51.addWidget(self.frame_89)

        self.frame_90 = QFrame(self.frame_88)
        self.frame_90.setObjectName(u"frame_90")
        self.frame_90.setFrameShape(QFrame.NoFrame)
        self.frame_90.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_90)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.frame_90)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setMinimumSize(QSize(300, 360))
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 427, 360))
        self.verticalLayout_area = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_area.setSpacing(0)
        self.verticalLayout_area.setObjectName(u"verticalLayout_area")
        self.verticalLayout_area.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_39 = QLabel(self.frame)
        self.label_39.setObjectName(u"label_39")

        self.verticalLayout_4.addWidget(self.label_39)

        self.frame_44 = QFrame(self.frame)
        self.frame_44.setObjectName(u"frame_44")
        self.frame_44.setFrameShape(QFrame.NoFrame)
        self.frame_44.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_26 = QHBoxLayout(self.frame_44)
        self.horizontalLayout_26.setSpacing(6)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.s_cost_input = QLineEdit(self.frame_44)
        self.s_cost_input.setObjectName(u"s_cost_input")

        self.horizontalLayout_26.addWidget(self.s_cost_input)

        self.s_cost_input_store = QPushButton(self.frame_44)
        self.s_cost_input_store.setObjectName(u"s_cost_input_store")
        self.s_cost_input_store.setMaximumSize(QSize(0, 0))
        self.s_cost_input_store.setFlat(True)

        self.horizontalLayout_26.addWidget(self.s_cost_input_store)


        self.verticalLayout_4.addWidget(self.frame_44)


        self.verticalLayout_area.addWidget(self.frame)

        self.frame_2 = QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_2)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_38 = QLabel(self.frame_2)
        self.label_38.setObjectName(u"label_38")

        self.verticalLayout_5.addWidget(self.label_38)

        self.frame_43 = QFrame(self.frame_2)
        self.frame_43.setObjectName(u"frame_43")
        self.frame_43.setFrameShape(QFrame.NoFrame)
        self.frame_43.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_25 = QHBoxLayout(self.frame_43)
        self.horizontalLayout_25.setSpacing(6)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.w_cost_input = QLineEdit(self.frame_43)
        self.w_cost_input.setObjectName(u"w_cost_input")

        self.horizontalLayout_25.addWidget(self.w_cost_input)

        self.w_cost_input_store = QPushButton(self.frame_43)
        self.w_cost_input_store.setObjectName(u"w_cost_input_store")
        self.w_cost_input_store.setMaximumSize(QSize(0, 0))
        self.w_cost_input_store.setFlat(True)

        self.horizontalLayout_25.addWidget(self.w_cost_input_store)


        self.verticalLayout_5.addWidget(self.frame_43)


        self.verticalLayout_area.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.scrollAreaWidgetContents)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_3)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.label_37 = QLabel(self.frame_3)
        self.label_37.setObjectName(u"label_37")

        self.verticalLayout_6.addWidget(self.label_37)

        self.frame_21 = QFrame(self.frame_3)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setFrameShape(QFrame.NoFrame)
        self.frame_21.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_21)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.pcs_cost_input = QLineEdit(self.frame_21)
        self.pcs_cost_input.setObjectName(u"pcs_cost_input")

        self.horizontalLayout_10.addWidget(self.pcs_cost_input)


        self.verticalLayout_6.addWidget(self.frame_21)


        self.verticalLayout_area.addWidget(self.frame_3)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.horizontalLayout_51.addWidget(self.frame_90, 0, Qt.AlignTop)

        self.horizontalLayout_51.setStretch(0, 2)
        self.horizontalLayout_51.setStretch(1, 5)

        self.verticalLayout_49.addWidget(self.frame_88)


        self.horizontalLayout_9.addWidget(self.frame_20)


        self.verticalLayout_15.addWidget(self.frame_19)

        self.cost_scenarios_info = QFrame(self.frame_18)
        self.cost_scenarios_info.setObjectName(u"cost_scenarios_info")
        sizePolicy.setHeightForWidth(self.cost_scenarios_info.sizePolicy().hasHeightForWidth())
        self.cost_scenarios_info.setSizePolicy(sizePolicy)
        self.cost_scenarios_info.setFrameShape(QFrame.NoFrame)
        self.cost_scenarios_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.cost_scenarios_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.cost_scenarios_info)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.hide_cost = QPushButton(self.cost_scenarios_info)
        self.hide_cost.setObjectName(u"hide_cost")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.hide_cost.setIcon(icon1)
        self.hide_cost.setIconSize(QSize(24, 24))
        self.hide_cost.setFlat(True)

        self.verticalLayout_2.addWidget(self.hide_cost, 0, Qt.AlignHCenter)


        self.verticalLayout_15.addWidget(self.cost_scenarios_info)


        self.verticalLayout.addWidget(self.frame_18)

        self.frame_63 = QFrame(cost_scene)
        self.frame_63.setObjectName(u"frame_63")
        self.frame_63.setFrameShape(QFrame.NoFrame)
        self.frame_63.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_30 = QHBoxLayout(self.frame_63)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.horizontalSpacer_18 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_30.addItem(self.horizontalSpacer_18)

        self.pcs_cost_input_store = QPushButton(self.frame_63)
        self.pcs_cost_input_store.setObjectName(u"pcs_cost_input_store")
        self.pcs_cost_input_store.setMaximumSize(QSize(0, 0))

        self.horizontalLayout_30.addWidget(self.pcs_cost_input_store)

        self.es4_cost_input_store = QPushButton(self.frame_63)
        self.es4_cost_input_store.setObjectName(u"es4_cost_input_store")
        self.es4_cost_input_store.setFlat(True)

        self.horizontalLayout_30.addWidget(self.es4_cost_input_store)


        self.verticalLayout.addWidget(self.frame_63)


        self.retranslateUi(cost_scene)

        QMetaObject.connectSlotsByName(cost_scene)
    # setupUi

    def retranslateUi(self, cost_scene):
        cost_scene.setWindowTitle(QCoreApplication.translate("cost_scene", u"Form", None))
        self.label_4.setText(QCoreApplication.translate("cost_scene", u"Data Collection", None))
        self.label_17.setText(QCoreApplication.translate("cost_scene", u"Inital Renewable and Energy Storage System Costs", None))
        self.pushButton_3.setText("")
        self.label_39.setText(QCoreApplication.translate("cost_scene", u"PV Cost ($/MW):", None))
        self.s_cost_input.setText("")
        self.s_cost_input.setPlaceholderText(QCoreApplication.translate("cost_scene", u"1551273", None))
        self.s_cost_input_store.setText("")
        self.label_38.setText(QCoreApplication.translate("cost_scene", u" Wind Cost ($/MW):", None))
        self.w_cost_input.setText("")
        self.w_cost_input.setPlaceholderText(QCoreApplication.translate("cost_scene", u"1676095", None))
        self.w_cost_input_store.setText("")
        self.label_37.setText(QCoreApplication.translate("cost_scene", u" Power Conversion System Cost ($/MW):", None))
        self.pcs_cost_input.setText("")
        self.pcs_cost_input.setPlaceholderText(QCoreApplication.translate("cost_scene", u"347000", None))
        self.textBrowser.setHtml(QCoreApplication.translate("cost_scene", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Please enter inital costs for renewable generation and energy storage systems. Cost scenarios are built with a 2.5% discount rate.</p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Cost of photovoltaic power "
                        "per megawatt ($/MW).</li>\n"
"<li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Cost of wind power per megawatt ($/MW).</li></ul>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Cost of a power conversion system per megawatt-hour ($/MW).</li>\n"
"<li style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"> Cost of energy storage system per megawatt-hour ($/MWh).</li></ul></body></html>", None))
        self.hide_cost.setText("")
        self.pcs_cost_input_store.setText(QCoreApplication.translate("cost_scene", u"Save", None))
        self.es4_cost_input_store.setText(QCoreApplication.translate("cost_scene", u"Next", None))
    # retranslateUi

