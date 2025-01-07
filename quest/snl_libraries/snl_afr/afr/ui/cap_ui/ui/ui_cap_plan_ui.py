# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cap_plan_uiVOBpvs.ui'
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
    QVBoxLayout, QWidget)
import afr.resources_rc

class Ui_cap_planning(object):
    def setupUi(self, cap_planning):
        if not cap_planning.objectName():
            cap_planning.setObjectName(u"cap_planning")
        cap_planning.resize(777, 747)
        self.verticalLayout = QVBoxLayout(cap_planning)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_40 = QFrame(cap_planning)
        self.frame_40.setObjectName(u"frame_40")
        self.frame_40.setFrameShape(QFrame.NoFrame)
        self.frame_40.setFrameShadow(QFrame.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.frame_40)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.label_9 = QLabel(self.frame_40)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_28.addWidget(self.label_9)

        self.frame_41 = QFrame(self.frame_40)
        self.frame_41.setObjectName(u"frame_41")
        self.frame_41.setFrameShape(QFrame.NoFrame)
        self.frame_41.setFrameShadow(QFrame.Raised)
        self.verticalLayout_54 = QVBoxLayout(self.frame_41)
        self.verticalLayout_54.setObjectName(u"verticalLayout_54")
        self.frame_94 = QFrame(self.frame_41)
        self.frame_94.setObjectName(u"frame_94")
        self.frame_94.setFrameShape(QFrame.NoFrame)
        self.frame_94.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_22 = QHBoxLayout(self.frame_94)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(-1, 0, -1, -1)
        self.frame_95 = QFrame(self.frame_94)
        self.frame_95.setObjectName(u"frame_95")
        self.frame_95.setFrameShape(QFrame.NoFrame)
        self.frame_95.setFrameShadow(QFrame.Raised)
        self.verticalLayout_52 = QVBoxLayout(self.frame_95)
        self.verticalLayout_52.setObjectName(u"verticalLayout_52")
        self.verticalLayout_52.setContentsMargins(-1, 9, -1, -1)
        self.frame_22 = QFrame(self.frame_95)
        self.frame_22.setObjectName(u"frame_22")
        self.frame_22.setFrameShape(QFrame.NoFrame)
        self.frame_22.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_43 = QHBoxLayout(self.frame_22)
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.label_19 = QLabel(self.frame_22)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_43.addWidget(self.label_19, 0, Qt.AlignTop)

        self.frame_2 = QFrame(self.frame_22)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_2)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.frame_2)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.pushButton_5 = QPushButton(self.frame)
        self.pushButton_5.setObjectName(u"pushButton_5")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_5.setIcon(icon)
        self.pushButton_5.setIconSize(QSize(24, 24))
        self.pushButton_5.setFlat(True)

        self.verticalLayout_3.addWidget(self.pushButton_5)

        self.cap_table_loader = QPushButton(self.frame)
        self.cap_table_loader.setObjectName(u"cap_table_loader")
        self.cap_table_loader.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/folder_open_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.cap_table_loader.setIcon(icon1)
        self.cap_table_loader.setIconSize(QSize(24, 24))
        self.cap_table_loader.setFlat(True)

        self.verticalLayout_3.addWidget(self.cap_table_loader)

        self.cap_csv_save = QPushButton(self.frame)
        self.cap_csv_save.setObjectName(u"cap_csv_save")
        icon2 = QIcon()
        icon2.addFile(u":/dark_icon/images/dark_icon/save_24dp_D4D4D4_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.cap_csv_save.setIcon(icon2)
        self.cap_csv_save.setIconSize(QSize(24, 24))
        self.cap_csv_save.setFlat(True)

        self.verticalLayout_3.addWidget(self.cap_csv_save)


        self.horizontalLayout.addWidget(self.frame)

        self.frame_3 = QFrame(self.frame_2)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_3)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"background-color:transparent;")
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_4)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_4.addWidget(self.frame_4)

        self.frame_5 = QFrame(self.frame_3)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_5)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_4.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame_3)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_6)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_4.addWidget(self.frame_6)


        self.horizontalLayout.addWidget(self.frame_3)


        self.horizontalLayout_43.addWidget(self.frame_2)

        self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_43.addItem(self.horizontalSpacer_29)


        self.verticalLayout_52.addWidget(self.frame_22)


        self.horizontalLayout_22.addWidget(self.frame_95)

        self.horizontalLayout_22.setStretch(0, 2)

        self.verticalLayout_54.addWidget(self.frame_94)


        self.verticalLayout_28.addWidget(self.frame_41)

        self.frame_39 = QFrame(self.frame_40)
        self.frame_39.setObjectName(u"frame_39")
        self.frame_39.setFrameShape(QFrame.NoFrame)
        self.frame_39.setFrameShadow(QFrame.Plain)
        self.table_layout = QVBoxLayout(self.frame_39)
        self.table_layout.setObjectName(u"table_layout")
        self.label_10 = QLabel(self.frame_39)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMaximumSize(QSize(0, 0))

        self.table_layout.addWidget(self.label_10)


        self.verticalLayout_28.addWidget(self.frame_39)

        self.cap_info = QFrame(self.frame_40)
        self.cap_info.setObjectName(u"cap_info")
        self.cap_info.setFrameShape(QFrame.NoFrame)
        self.cap_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.cap_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.cap_info)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.hide_cap = QPushButton(self.cap_info)
        self.hide_cap.setObjectName(u"hide_cap")
        icon3 = QIcon()
        icon3.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.hide_cap.setIcon(icon3)
        self.hide_cap.setIconSize(QSize(24, 24))
        self.hide_cap.setFlat(True)

        self.verticalLayout_2.addWidget(self.hide_cap, 0, Qt.AlignHCenter)


        self.verticalLayout_28.addWidget(self.cap_info)


        self.verticalLayout.addWidget(self.frame_40)

        self.frame_48 = QFrame(cap_planning)
        self.frame_48.setObjectName(u"frame_48")
        self.frame_48.setFrameShape(QFrame.NoFrame)
        self.frame_48.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_24 = QHBoxLayout(self.frame_48)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_24.addItem(self.horizontalSpacer_12)

        self.cc_cap_input_store = QPushButton(self.frame_48)
        self.cc_cap_input_store.setObjectName(u"cc_cap_input_store")
        self.cc_cap_input_store.setMaximumSize(QSize(0, 0))

        self.horizontalLayout_24.addWidget(self.cc_cap_input_store, 0, Qt.AlignBottom)

        self.next_7 = QPushButton(self.frame_48)
        self.next_7.setObjectName(u"next_7")
        self.next_7.setFlat(True)

        self.horizontalLayout_24.addWidget(self.next_7, 0, Qt.AlignBottom)


        self.verticalLayout.addWidget(self.frame_48)


        self.retranslateUi(cap_planning)

        QMetaObject.connectSlotsByName(cap_planning)
    # setupUi

    def retranslateUi(self, cap_planning):
        cap_planning.setWindowTitle(QCoreApplication.translate("cap_planning", u"Form", None))
        self.label_9.setText(QCoreApplication.translate("cap_planning", u"Data Collection", None))
        self.label_19.setText(QCoreApplication.translate("cap_planning", u"Capacity Planning", None))
        self.pushButton_5.setText("")
        self.cap_table_loader.setText("")
        self.cap_csv_save.setText("")
        self.label_10.setText("")
        self.textBrowser.setHtml(QCoreApplication.translate("cap_planning", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Please upload planned generation capacities via .csv file. Csv files should follow the this format:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:700;\" style=\" margin-top:12px; margin-bott"
                        "om:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Header Row: The first row of your CSV file should contain the following column headers: <span style=\" font-family:'Courier New';\">Category</span>, <span style=\" font-family:'Courier New';\">Type</span>, <span style=\" font-family:'Courier New';\">Capacity Factor</span>, <span style=\" font-family:'Courier New';\">2020</span>, <span style=\" font-family:'Courier New';\">2021</span>, <span style=\" font-family:'Courier New';\">2022</span>, etc.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Data Rows</span>: Each subsequent row should represent a data entry corresponding to the headers. For example, a row might look like this: <span style=\" font-family:'Courier New';\">Phyd, Clean, 0.37, 1, 0, 0, etc.</span></li>\n"
"<li style=\" font-family:'Segoe UI'; font-size"
                        ":9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Category</span>: The generation technology category, e.g., <span style=\" font-family:'Courier New';\">Combustion Turbine</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Type</span>: Whether the generation is considered a clean or dirty source of energy, e.g., <span style=\" font-family:'Courier New';\">Clean</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Capacity Factor</span>: The capacity factor of the energy source, e.g., <span style=\" font-family:'Courier New';\">0.37</span>.</li>\n"
"<li style=\" font-"
                        "family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Yearly Data</span>: The rated capacity in MW of each generation source for each year from <span style=\" font-family:'Courier New';\">2020</span> to <span style=\" font-family:'Courier New';\">20</span>xx e.g. <span style=\" font-family:'Courier New';\">999, 888, etc.</span></li></ul></body></html>", None))
        self.hide_cap.setText("")
        self.cc_cap_input_store.setText(QCoreApplication.translate("cap_planning", u"Save", None))
        self.next_7.setText(QCoreApplication.translate("cap_planning", u"Next", None))
    # retranslateUi

