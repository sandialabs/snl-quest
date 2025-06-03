# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'effiJaTpDA.ui'
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
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox,
    QTextBrowser, QVBoxLayout, QWidget)
import afr.resources_rc

class Ui_eff_widget(object):
    def setupUi(self, eff_widget):
        if not eff_widget.objectName():
            eff_widget.setObjectName(u"eff_widget")
        eff_widget.resize(780, 664)
        self.verticalLayout = QVBoxLayout(eff_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame_56 = QFrame(eff_widget)
        self.frame_56.setObjectName(u"frame_56")
        self.frame_56.setFrameShape(QFrame.NoFrame)
        self.frame_56.setFrameShadow(QFrame.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.frame_56)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.label_8 = QLabel(self.frame_56)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_27.addWidget(self.label_8)

        self.frame_57 = QFrame(self.frame_56)
        self.frame_57.setObjectName(u"frame_57")
        self.frame_57.setFrameShape(QFrame.NoFrame)
        self.frame_57.setFrameShadow(QFrame.Raised)
        self.verticalLayout_48 = QVBoxLayout(self.frame_57)
        self.verticalLayout_48.setObjectName(u"verticalLayout_48")
        self.frame_65 = QFrame(self.frame_57)
        self.frame_65.setObjectName(u"frame_65")
        self.frame_65.setFrameShape(QFrame.NoFrame)
        self.frame_65.setFrameShadow(QFrame.Raised)
        self.verticalLayout_29 = QVBoxLayout(self.frame_65)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")

        self.verticalLayout_48.addWidget(self.frame_65)

        self.frame_85 = QFrame(self.frame_57)
        self.frame_85.setObjectName(u"frame_85")
        self.frame_85.setFrameShape(QFrame.NoFrame)
        self.frame_85.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_85)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_86 = QFrame(self.frame_85)
        self.frame_86.setObjectName(u"frame_86")
        self.frame_86.setFrameShape(QFrame.NoFrame)
        self.frame_86.setFrameShadow(QFrame.Raised)
        self.verticalLayout_62 = QVBoxLayout(self.frame_86)
        self.verticalLayout_62.setSpacing(20)
        self.verticalLayout_62.setObjectName(u"verticalLayout_62")
        self.frame_110 = QFrame(self.frame_86)
        self.frame_110.setObjectName(u"frame_110")
        self.frame_110.setFrameShape(QFrame.NoFrame)
        self.frame_110.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_66 = QHBoxLayout(self.frame_110)
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.label_16 = QLabel(self.frame_110)
        self.label_16.setObjectName(u"label_16")
        self.label_16.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_66.addWidget(self.label_16)

        self.pushButton = QPushButton(self.frame_110)
        self.pushButton.setObjectName(u"pushButton")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QSize(24, 24))
        self.pushButton.setFlat(True)

        self.horizontalLayout_66.addWidget(self.pushButton, 0, Qt.AlignLeft)


        self.verticalLayout_62.addWidget(self.frame_110)

        self.verticalSpacer_4 = QSpacerItem(20, 329, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_62.addItem(self.verticalSpacer_4)


        self.horizontalLayout_2.addWidget(self.frame_86)

        self.frame_87 = QFrame(self.frame_85)
        self.frame_87.setObjectName(u"frame_87")
        self.frame_87.setFrameShape(QFrame.NoFrame)
        self.frame_87.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_87)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.frame_87)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 436, 722))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.name_label = QLabel(self.scrollAreaWidgetContents)
        self.name_label.setObjectName(u"name_label")

        self.verticalLayout_3.addWidget(self.name_label)

        self.frame_8 = QFrame(self.scrollAreaWidgetContents)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.NoFrame)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.name_input = QLineEdit(self.frame_8)
        self.name_input.setObjectName(u"name_input")

        self.horizontalLayout_10.addWidget(self.name_input)


        self.verticalLayout_3.addWidget(self.frame_8)

        self.label_36 = QLabel(self.scrollAreaWidgetContents)
        self.label_36.setObjectName(u"label_36")

        self.verticalLayout_3.addWidget(self.label_36)

        self.frame = QFrame(self.scrollAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.eff_slide = QSlider(self.frame)
        self.eff_slide.setObjectName(u"eff_slide")
        self.eff_slide.setMaximum(9999)
        self.eff_slide.setOrientation(Qt.Horizontal)

        self.horizontalLayout_3.addWidget(self.eff_slide)


        self.verticalLayout_3.addWidget(self.frame)

        self.frame_66 = QFrame(self.scrollAreaWidgetContents)
        self.frame_66.setObjectName(u"frame_66")
        self.frame_66.setFrameShape(QFrame.NoFrame)
        self.frame_66.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_44 = QHBoxLayout(self.frame_66)
        self.horizontalLayout_44.setSpacing(0)
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.horizontalLayout_44.setContentsMargins(0, 0, 0, 0)
        self.es4_eff_input_store = QPushButton(self.frame_66)
        self.es4_eff_input_store.setObjectName(u"es4_eff_input_store")
        self.es4_eff_input_store.setMaximumSize(QSize(0, 0))
        self.es4_eff_input_store.setFlat(True)

        self.horizontalLayout_44.addWidget(self.es4_eff_input_store)


        self.verticalLayout_3.addWidget(self.frame_66)

        self.eff_edit = QLineEdit(self.scrollAreaWidgetContents)
        self.eff_edit.setObjectName(u"eff_edit")
        self.eff_edit.setStyleSheet(u"background-color: transparent")
        self.eff_edit.setFrame(False)
        self.eff_edit.setCursorPosition(0)

        self.verticalLayout_3.addWidget(self.eff_edit)

        self.label_35 = QLabel(self.scrollAreaWidgetContents)
        self.label_35.setObjectName(u"label_35")

        self.verticalLayout_3.addWidget(self.label_35)

        self.frame_2 = QFrame(self.scrollAreaWidgetContents)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.deg_slide = QSlider(self.frame_2)
        self.deg_slide.setObjectName(u"deg_slide")
        self.deg_slide.setMaximum(9999)
        self.deg_slide.setOrientation(Qt.Horizontal)

        self.horizontalLayout_4.addWidget(self.deg_slide)


        self.verticalLayout_3.addWidget(self.frame_2)

        self.frame_67 = QFrame(self.scrollAreaWidgetContents)
        self.frame_67.setObjectName(u"frame_67")
        self.frame_67.setFrameShape(QFrame.NoFrame)
        self.frame_67.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_45 = QHBoxLayout(self.frame_67)
        self.horizontalLayout_45.setSpacing(0)
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.horizontalLayout_45.setContentsMargins(0, 0, 0, 0)
        self.es36_eff_input_store = QPushButton(self.frame_67)
        self.es36_eff_input_store.setObjectName(u"es36_eff_input_store")
        self.es36_eff_input_store.setMaximumSize(QSize(0, 0))
        self.es36_eff_input_store.setFlat(True)

        self.horizontalLayout_45.addWidget(self.es36_eff_input_store)


        self.verticalLayout_3.addWidget(self.frame_67)

        self.deg_edit = QLineEdit(self.scrollAreaWidgetContents)
        self.deg_edit.setObjectName(u"deg_edit")
        self.deg_edit.setStyleSheet(u"background-color: transparent")
        self.deg_edit.setFrame(False)

        self.verticalLayout_3.addWidget(self.deg_edit)

        self.label_34 = QLabel(self.scrollAreaWidgetContents)
        self.label_34.setObjectName(u"label_34")

        self.verticalLayout_3.addWidget(self.label_34)

        self.frame_3 = QFrame(self.scrollAreaWidgetContents)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.eol_slide = QSlider(self.frame_3)
        self.eol_slide.setObjectName(u"eol_slide")
        self.eol_slide.setMaximum(9999)
        self.eol_slide.setOrientation(Qt.Horizontal)

        self.horizontalLayout_5.addWidget(self.eol_slide)


        self.verticalLayout_3.addWidget(self.frame_3)

        self.frame_68 = QFrame(self.scrollAreaWidgetContents)
        self.frame_68.setObjectName(u"frame_68")
        self.frame_68.setFrameShape(QFrame.NoFrame)
        self.frame_68.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_46 = QHBoxLayout(self.frame_68)
        self.horizontalLayout_46.setSpacing(0)
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.horizontalLayout_46.setContentsMargins(0, 0, 0, 0)
        self.es100_eff_input_store = QPushButton(self.frame_68)
        self.es100_eff_input_store.setObjectName(u"es100_eff_input_store")
        self.es100_eff_input_store.setMaximumSize(QSize(0, 0))
        self.es100_eff_input_store.setFlat(True)

        self.horizontalLayout_46.addWidget(self.es100_eff_input_store)


        self.verticalLayout_3.addWidget(self.frame_68)

        self.eol_edit = QLineEdit(self.scrollAreaWidgetContents)
        self.eol_edit.setObjectName(u"eol_edit")
        self.eol_edit.setStyleSheet(u"background-color: transparent")
        self.eol_edit.setFrame(False)

        self.verticalLayout_3.addWidget(self.eol_edit)

        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.verticalLayout_3.addWidget(self.label)

        self.frame_6 = QFrame(self.scrollAreaWidgetContents)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.frame_6.setLineWidth(1)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_8.setSpacing(6)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.frame_6)

        self.dur_box = QSpinBox(self.scrollAreaWidgetContents)
        self.dur_box.setObjectName(u"dur_box")
        self.dur_box.setMaximum(1000)

        self.verticalLayout_3.addWidget(self.dur_box)

        self.label_37 = QLabel(self.scrollAreaWidgetContents)
        self.label_37.setObjectName(u"label_37")

        self.verticalLayout_3.addWidget(self.label_37)

        self.frame_7 = QFrame(self.scrollAreaWidgetContents)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.NoFrame)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, -1, 0, 0)
        self.cycle_box = QComboBox(self.frame_7)
        self.cycle_box.addItem("")
        self.cycle_box.addItem("")
        self.cycle_box.addItem("")
        self.cycle_box.addItem("")
        self.cycle_box.setObjectName(u"cycle_box")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cycle_box.sizePolicy().hasHeightForWidth())
        self.cycle_box.setSizePolicy(sizePolicy)

        self.horizontalLayout_9.addWidget(self.cycle_box)


        self.verticalLayout_3.addWidget(self.frame_7)

        self.frame_5 = QFrame(self.scrollAreaWidgetContents)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addWidget(self.frame_5)

        self.frame_4 = QFrame(self.scrollAreaWidgetContents)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"")
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.frame_9 = QFrame(self.frame_4)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setStyleSheet(u"")
        self.frame_9.setFrameShape(QFrame.NoFrame)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer)

        self.set_storage = QPushButton(self.frame_9)
        self.set_storage.setObjectName(u"set_storage")
        self.set_storage.setStyleSheet(u"")
        self.set_storage.setFlat(True)

        self.horizontalLayout_11.addWidget(self.set_storage)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_2)


        self.horizontalLayout_6.addWidget(self.frame_9)


        self.verticalLayout_3.addWidget(self.frame_4)

        self.storage_list = QTextBrowser(self.scrollAreaWidgetContents)
        self.storage_list.setObjectName(u"storage_list")
        self.storage_list.setStyleSheet(u"        background-color: transparent; \n"
"        border: none;\n"
"        color: #d4d4d4;  ")
        self.storage_list.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_3.addWidget(self.storage_list)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)


        self.horizontalLayout_2.addWidget(self.frame_87)


        self.verticalLayout_48.addWidget(self.frame_85)


        self.verticalLayout_27.addWidget(self.frame_57)


        self.verticalLayout.addWidget(self.frame_56)

        self.store_info = QFrame(eff_widget)
        self.store_info.setObjectName(u"store_info")
        self.store_info.setFrameShape(QFrame.NoFrame)
        self.store_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.store_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.store_info)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.hide_store = QPushButton(self.store_info)
        self.hide_store.setObjectName(u"hide_store")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.hide_store.setIcon(icon1)
        self.hide_store.setIconSize(QSize(24, 24))
        self.hide_store.setFlat(True)

        self.verticalLayout_2.addWidget(self.hide_store, 0, Qt.AlignHCenter)


        self.verticalLayout.addWidget(self.store_info)

        self.frame_46 = QFrame(eff_widget)
        self.frame_46.setObjectName(u"frame_46")
        self.frame_46.setStyleSheet(u"")
        self.frame_46.setFrameShape(QFrame.NoFrame)
        self.frame_46.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.frame_46)
        self.horizontalLayout_20.setSpacing(0)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_20.addItem(self.horizontalSpacer_8)

        self.es_save = QPushButton(self.frame_46)
        self.es_save.setObjectName(u"es_save")
        self.es_save.setMaximumSize(QSize(0, 0))

        self.horizontalLayout_20.addWidget(self.es_save)

        self.next_4 = QPushButton(self.frame_46)
        self.next_4.setObjectName(u"next_4")
        self.next_4.setFlat(True)

        self.horizontalLayout_20.addWidget(self.next_4)


        self.verticalLayout.addWidget(self.frame_46)


        self.retranslateUi(eff_widget)

        QMetaObject.connectSlotsByName(eff_widget)
    # setupUi

    def retranslateUi(self, eff_widget):
        eff_widget.setWindowTitle(QCoreApplication.translate("eff_widget", u"Form", None))
        self.label_8.setText(QCoreApplication.translate("eff_widget", u"Data Collection", None))
        self.label_16.setText(QCoreApplication.translate("eff_widget", u"Storage Devices", None))
        self.pushButton.setText("")
        self.name_label.setText(QCoreApplication.translate("eff_widget", u"Device Name:", None))
        self.name_input.setText(QCoreApplication.translate("eff_widget", u"4 Hour Lithium Ion", None))
        self.label_36.setText(QCoreApplication.translate("eff_widget", u"Storage Efficiency:", None))
        self.es4_eff_input_store.setText("")
        self.eff_edit.setText("")
        self.label_35.setText(QCoreApplication.translate("eff_widget", u"Storage Degradation Rate:", None))
        self.es36_eff_input_store.setText("")
        self.label_34.setText(QCoreApplication.translate("eff_widget", u"Storage End of Life:", None))
        self.es100_eff_input_store.setText("")
        self.label.setText(QCoreApplication.translate("eff_widget", u"Duration:", None))
        self.label_37.setText(QCoreApplication.translate("eff_widget", u"Storage Cycling", None))
        self.cycle_box.setItemText(0, QCoreApplication.translate("eff_widget", u"Weekly", None))
        self.cycle_box.setItemText(1, QCoreApplication.translate("eff_widget", u"Monthly", None))
        self.cycle_box.setItemText(2, QCoreApplication.translate("eff_widget", u"Seasonal", None))
        self.cycle_box.setItemText(3, QCoreApplication.translate("eff_widget", u"Annual", None))

        self.set_storage.setText(QCoreApplication.translate("eff_widget", u"Set", None))
        self.textBrowser.setHtml(QCoreApplication.translate("eff_widget", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Please set candidate storage technologies:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:"
                        "0px;\">Round trip efficiency relates the amount of charged energy that will be usable for discharge</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Storage degradation rate is the percent capacity loss annually</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Storage end of life is the target percentage of initial capacity that will cause the technology to be retired</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Storage duration is the ratio of energy capacity to power capacity of the technology</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; "
                        "margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The cycling of the storage device indicates over what time period the net charging must be zero</li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Upon pressing the Set button, these devices will be added to the available buildout options of the simulation.</span></p></body></html>", None))
        self.hide_store.setText("")
        self.es_save.setText(QCoreApplication.translate("eff_widget", u"Save", None))
        self.next_4.setText(QCoreApplication.translate("eff_widget", u"Next", None))
    # retranslateUi

