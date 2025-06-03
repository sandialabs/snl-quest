# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'time_widgeXjlNdQ.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QSpacerItem, QTextBrowser, QVBoxLayout, QWidget)
import afr.resources_rc

class Ui_time_scope_widget(object):
    def setupUi(self, time_scope_widget):
        if not time_scope_widget.objectName():
            time_scope_widget.setObjectName(u"time_scope_widget")
        time_scope_widget.resize(832, 718)
        self.verticalLayout = QVBoxLayout(time_scope_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_6 = QFrame(time_scope_widget)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.frame_6)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_2 = QLabel(self.frame_6)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_11.addWidget(self.label_2)

        self.frame_9 = QFrame(self.frame_6)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.NoFrame)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.frame_8 = QFrame(self.frame_9)
        self.frame_8.setObjectName(u"frame_8")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_8.sizePolicy().hasHeightForWidth())
        self.frame_8.setSizePolicy(sizePolicy)
        self.frame_8.setFrameShape(QFrame.NoFrame)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_40 = QVBoxLayout(self.frame_8)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.frame_11 = QFrame(self.frame_8)
        self.frame_11.setObjectName(u"frame_11")
        self.frame_11.setFrameShape(QFrame.NoFrame)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_35 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_35.setSpacing(10)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.frame_74 = QFrame(self.frame_11)
        self.frame_74.setObjectName(u"frame_74")
        self.frame_74.setFrameShape(QFrame.NoFrame)
        self.frame_74.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_74)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.frame_109 = QFrame(self.frame_74)
        self.frame_109.setObjectName(u"frame_109")
        self.frame_109.setFrameShape(QFrame.NoFrame)
        self.frame_109.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_61 = QHBoxLayout(self.frame_109)
        self.horizontalLayout_61.setObjectName(u"horizontalLayout_61")
        self.label_13 = QLabel(self.frame_109)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_61.addWidget(self.label_13)

        self.horizon_info = QPushButton(self.frame_109)
        self.horizon_info.setObjectName(u"horizon_info")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.horizon_info.setIcon(icon)
        self.horizon_info.setIconSize(QSize(24, 24))
        self.horizon_info.setFlat(True)

        self.horizontalLayout_61.addWidget(self.horizon_info, 0, Qt.AlignLeft)


        self.verticalLayout_9.addWidget(self.frame_109, 0, Qt.AlignTop)

        self.frame_124 = QFrame(self.frame_74)
        self.frame_124.setObjectName(u"frame_124")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_124.sizePolicy().hasHeightForWidth())
        self.frame_124.setSizePolicy(sizePolicy1)
        self.frame_124.setFrameShape(QFrame.NoFrame)
        self.frame_124.setFrameShadow(QFrame.Raised)
        self.state_layout = QVBoxLayout(self.frame_124)
        self.state_layout.setObjectName(u"state_layout")
        self.state_layout.setContentsMargins(0, 15, 0, 0)

        self.verticalLayout_9.addWidget(self.frame_124)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_3)


        self.horizontalLayout_35.addWidget(self.frame_74)

        self.frame_64 = QFrame(self.frame_11)
        self.frame_64.setObjectName(u"frame_64")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_64.sizePolicy().hasHeightForWidth())
        self.frame_64.setSizePolicy(sizePolicy2)
        self.frame_64.setFrameShape(QFrame.NoFrame)
        self.frame_64.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_64)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scrollArea = QScrollArea(self.frame_64)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 364, 477))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_17 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_17.setObjectName(u"label_17")

        self.verticalLayout_3.addWidget(self.label_17)

        self.frame_116 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_116.setObjectName(u"frame_116")
        self.frame_116.setFrameShape(QFrame.NoFrame)
        self.frame_116.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_68 = QHBoxLayout(self.frame_116)
        self.horizontalLayout_68.setObjectName(u"horizontalLayout_68")
        self.horizontalLayout_68.setContentsMargins(0, 0, 0, 0)
        self.state_select_3 = QComboBox(self.frame_116)
        self.state_select_3.addItem("")
        self.state_select_3.addItem("")
        self.state_select_3.setObjectName(u"state_select_3")

        self.horizontalLayout_68.addWidget(self.state_select_3)

        self.horizontalLayout_68.setStretch(0, 1)

        self.verticalLayout_3.addWidget(self.frame_116)

        self.label_31 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_31.setObjectName(u"label_31")

        self.verticalLayout_3.addWidget(self.label_31)

        self.frame_118 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_118.setObjectName(u"frame_118")
        self.frame_118.setFrameShape(QFrame.NoFrame)
        self.frame_118.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_70 = QHBoxLayout(self.frame_118)
        self.horizontalLayout_70.setSpacing(6)
        self.horizontalLayout_70.setObjectName(u"horizontalLayout_70")
        self.horizontalLayout_70.setContentsMargins(0, 0, 0, 0)
        self.start_year_horizon_3 = QComboBox(self.frame_118)
        self.start_year_horizon_3.addItem("")
        self.start_year_horizon_3.setObjectName(u"start_year_horizon_3")

        self.horizontalLayout_70.addWidget(self.start_year_horizon_3)

        self.horizontalLayout_70.setStretch(0, 1)

        self.verticalLayout_3.addWidget(self.frame_118)

        self.label_46 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_46.setObjectName(u"label_46")

        self.verticalLayout_3.addWidget(self.label_46)

        self.frame_13 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.NoFrame)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.end_year_horizon_3 = QComboBox(self.frame_13)
        self.end_year_horizon_3.addItem("")
        self.end_year_horizon_3.setObjectName(u"end_year_horizon_3")

        self.horizontalLayout_7.addWidget(self.end_year_horizon_3)

        self.horizontalLayout_7.setStretch(0, 1)

        self.verticalLayout_3.addWidget(self.frame_13)

        self.label_32 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_32.setObjectName(u"label_32")

        self.verticalLayout_3.addWidget(self.label_32)

        self.frame_115 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_115.setObjectName(u"frame_115")
        self.frame_115.setFrameShape(QFrame.NoFrame)
        self.frame_115.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_67 = QHBoxLayout(self.frame_115)
        self.horizontalLayout_67.setObjectName(u"horizontalLayout_67")
        self.horizontalLayout_67.setContentsMargins(0, 0, 0, 0)
        self.rps_percentage_3 = QComboBox(self.frame_115)
        self.rps_percentage_3.addItem("")
        self.rps_percentage_3.setObjectName(u"rps_percentage_3")

        self.horizontalLayout_67.addWidget(self.rps_percentage_3)

        self.rps_80_year_3 = QComboBox(self.frame_115)
        self.rps_80_year_3.addItem("")
        self.rps_80_year_3.setObjectName(u"rps_80_year_3")

        self.horizontalLayout_67.addWidget(self.rps_80_year_3)

        self.add_rps_target_3 = QPushButton(self.frame_115)
        self.add_rps_target_3.setObjectName(u"add_rps_target_3")
        self.add_rps_target_3.setFlat(True)

        self.horizontalLayout_67.addWidget(self.add_rps_target_3)

        self.horizontalLayout_67.setStretch(0, 1)
        self.horizontalLayout_67.setStretch(1, 1)
        self.horizontalLayout_67.setStretch(2, 1)

        self.verticalLayout_3.addWidget(self.frame_115)

        self.rps_target_display_3 = QTextBrowser(self.scrollAreaWidgetContents_3)
        self.rps_target_display_3.setObjectName(u"rps_target_display_3")
        sizePolicy2.setHeightForWidth(self.rps_target_display_3.sizePolicy().hasHeightForWidth())
        self.rps_target_display_3.setSizePolicy(sizePolicy2)
        self.rps_target_display_3.setStyleSheet(u"background: transparent;\n"
"border: none;")

        self.verticalLayout_3.addWidget(self.rps_target_display_3)

        self.label_30 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_30.setObjectName(u"label_30")

        self.verticalLayout_3.addWidget(self.label_30)

        self.frame_117 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_117.setObjectName(u"frame_117")
        self.frame_117.setFrameShape(QFrame.NoFrame)
        self.frame_117.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_69 = QHBoxLayout(self.frame_117)
        self.horizontalLayout_69.setObjectName(u"horizontalLayout_69")
        self.horizontalLayout_69.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.frame_117)

        self.frame_36 = QFrame(self.scrollAreaWidgetContents_3)
        self.frame_36.setObjectName(u"frame_36")
        self.frame_36.setFrameShape(QFrame.NoFrame)
        self.frame_36.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_36)
        self.horizontalLayout_18.setSpacing(0)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.frame_36)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)

        self.horizontalLayout.addWidget(self.scrollArea)


        self.horizontalLayout_35.addWidget(self.frame_64)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_35.addItem(self.horizontalSpacer)

        self.horizontalLayout_35.setStretch(0, 2)
        self.horizontalLayout_35.setStretch(1, 3)
        self.horizontalLayout_35.setStretch(2, 1)

        self.verticalLayout_40.addWidget(self.frame_11)

        self.frame = QFrame(self.frame_8)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 150))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_40.addWidget(self.frame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_40.addItem(self.verticalSpacer)


        self.horizontalLayout_5.addWidget(self.frame_8)


        self.verticalLayout_11.addWidget(self.frame_9)

        self.time_info = QFrame(self.frame_6)
        self.time_info.setObjectName(u"time_info")
        sizePolicy.setHeightForWidth(self.time_info.sizePolicy().hasHeightForWidth())
        self.time_info.setSizePolicy(sizePolicy)
        self.time_info.setFrameShape(QFrame.NoFrame)
        self.time_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.time_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.time_info)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setMinimumSize(QSize(0, 150))
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.hide_time = QPushButton(self.time_info)
        self.hide_time.setObjectName(u"hide_time")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.hide_time.setIcon(icon1)
        self.hide_time.setIconSize(QSize(24, 24))
        self.hide_time.setFlat(True)

        self.verticalLayout_2.addWidget(self.hide_time, 0, Qt.AlignHCenter)


        self.verticalLayout_11.addWidget(self.time_info)


        self.verticalLayout.addWidget(self.frame_6)

        self.frame_10 = QFrame(time_scope_widget)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.NoFrame)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.horizon_save = QPushButton(self.frame_10)
        self.horizon_save.setObjectName(u"horizon_save")
        self.horizon_save.setMaximumSize(QSize(0, 0))

        self.horizontalLayout_4.addWidget(self.horizon_save, 0, Qt.AlignHCenter)

        self.rps_year_80_store = QPushButton(self.frame_10)
        self.rps_year_80_store.setObjectName(u"rps_year_80_store")
        self.rps_year_80_store.setFlat(True)

        self.horizontalLayout_4.addWidget(self.rps_year_80_store, 0, Qt.AlignHCenter)


        self.verticalLayout.addWidget(self.frame_10)


        self.retranslateUi(time_scope_widget)

        QMetaObject.connectSlotsByName(time_scope_widget)
    # setupUi

    def retranslateUi(self, time_scope_widget):
        time_scope_widget.setWindowTitle(QCoreApplication.translate("time_scope_widget", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("time_scope_widget", u"Data Collection", None))
        self.label_13.setText(QCoreApplication.translate("time_scope_widget", u"Time Scope", None))
        self.horizon_info.setText("")
        self.label_17.setText(QCoreApplication.translate("time_scope_widget", u" State Selection:", None))
        self.state_select_3.setItemText(0, QCoreApplication.translate("time_scope_widget", u"Select State", None))
        self.state_select_3.setItemText(1, QCoreApplication.translate("time_scope_widget", u"Other", None))

        self.label_31.setText(QCoreApplication.translate("time_scope_widget", u" Time Horizon Start Year:", None))
        self.start_year_horizon_3.setItemText(0, QCoreApplication.translate("time_scope_widget", u"Select Start Year", None))

        self.label_46.setText(QCoreApplication.translate("time_scope_widget", u"Time Horizon End Year:", None))
        self.end_year_horizon_3.setItemText(0, QCoreApplication.translate("time_scope_widget", u"Select End Year", None))

        self.label_32.setText(QCoreApplication.translate("time_scope_widget", u" RPS Targets:", None))
        self.rps_percentage_3.setItemText(0, QCoreApplication.translate("time_scope_widget", u"Target %", None))

        self.rps_80_year_3.setItemText(0, QCoreApplication.translate("time_scope_widget", u"% Goal Year", None))

        self.add_rps_target_3.setText(QCoreApplication.translate("time_scope_widget", u"Add Target", None))
        self.label_30.setText("")
        self.textBrowser.setHtml(QCoreApplication.translate("time_scope_widget", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">Please select the state, time period, and Renewable Portfolio Standard (RPS) targets of the simulation. Upon selection of the state, RPS and Clean Energy Standard (CES) targets will populate. This data was gathered from the Berkely Lab Energy and Markets Policy U.S. State Renewables Portfolio and Clean Energy Standards 2024 Update which can be accessed at  ht"
                        "tps://emp.lbl.gov/publications/us-state-renewables-portfolio-clean-0. Additional state specific policy can be accessed at </span><span style=\" font-family:'Segoe UI'; font-size:9pt;\">https://gesdb.sandia.gov/policy.html.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\"><br /><br /></span></p></body></html>", None))
        self.hide_time.setText("")
        self.horizon_save.setText(QCoreApplication.translate("time_scope_widget", u"Save", None))
        self.rps_year_80_store.setText(QCoreApplication.translate("time_scope_widget", u"Next", None))
    # retranslateUi

