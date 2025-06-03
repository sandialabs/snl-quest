# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'file_loadAejAqu.ui'
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
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTextBrowser, QVBoxLayout, QWidget)
import afr.resources_rc

class Ui_file_loader(object):
    def setupUi(self, file_loader):
        if not file_loader.objectName():
            file_loader.setObjectName(u"file_loader")
        file_loader.resize(858, 908)
        self.verticalLayout = QVBoxLayout(file_loader)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.frame_24 = QFrame(file_loader)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setFrameShape(QFrame.NoFrame)
        self.frame_24.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.frame_24)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.label_5 = QLabel(self.frame_24)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_19.addWidget(self.label_5)

        self.frame_25 = QFrame(self.frame_24)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setFrameShape(QFrame.NoFrame)
        self.frame_25.setFrameShadow(QFrame.Raised)
        self.verticalLayout_20 = QVBoxLayout(self.frame_25)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.frame_26 = QFrame(self.frame_25)
        self.frame_26.setObjectName(u"frame_26")
        self.frame_26.setFrameShape(QFrame.NoFrame)
        self.frame_26.setFrameShadow(QFrame.Raised)
        self.verticalLayout_58 = QVBoxLayout(self.frame_26)
        self.verticalLayout_58.setObjectName(u"verticalLayout_58")
        self.frame_100 = QFrame(self.frame_26)
        self.frame_100.setObjectName(u"frame_100")
        self.frame_100.setFrameShape(QFrame.NoFrame)
        self.frame_100.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_54 = QHBoxLayout(self.frame_100)
        self.horizontalLayout_54.setObjectName(u"horizontalLayout_54")
        self.frame_101 = QFrame(self.frame_100)
        self.frame_101.setObjectName(u"frame_101")
        self.frame_101.setFrameShape(QFrame.NoFrame)
        self.frame_101.setFrameShadow(QFrame.Raised)
        self.verticalLayout_57 = QVBoxLayout(self.frame_101)
        self.verticalLayout_57.setObjectName(u"verticalLayout_57")
        self.frame_17 = QFrame(self.frame_101)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setFrameShape(QFrame.NoFrame)
        self.frame_17.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_42 = QHBoxLayout(self.frame_17)
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.label_21 = QLabel(self.frame_17)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.horizontalLayout_42.addWidget(self.label_21)

        self.pushButton_4 = QPushButton(self.frame_17)
        self.pushButton_4.setObjectName(u"pushButton_4")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/help_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.pushButton_4.setIcon(icon)
        self.pushButton_4.setIconSize(QSize(24, 24))
        self.pushButton_4.setFlat(True)

        self.horizontalLayout_42.addWidget(self.pushButton_4, 0, Qt.AlignLeft)


        self.verticalLayout_57.addWidget(self.frame_17)

        self.frame_125 = QFrame(self.frame_101)
        self.frame_125.setObjectName(u"frame_125")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_125.sizePolicy().hasHeightForWidth())
        self.frame_125.setSizePolicy(sizePolicy)
        self.frame_125.setFrameShape(QFrame.NoFrame)
        self.frame_125.setFrameShadow(QFrame.Raised)
        self.block_drop_lay = QVBoxLayout(self.frame_125)
        self.block_drop_lay.setObjectName(u"block_drop_lay")

        self.verticalLayout_57.addWidget(self.frame_125)


        self.horizontalLayout_54.addWidget(self.frame_101)

        self.frame_102 = QFrame(self.frame_100)
        self.frame_102.setObjectName(u"frame_102")
        self.frame_102.setFrameShape(QFrame.NoFrame)
        self.frame_102.setFrameShadow(QFrame.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_102)
        self.verticalLayout_17.setSpacing(15)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_50 = QLabel(self.frame_102)
        self.label_50.setObjectName(u"label_50")

        self.verticalLayout_17.addWidget(self.label_50)

        self.frame_54 = QFrame(self.frame_102)
        self.frame_54.setObjectName(u"frame_54")
        self.frame_54.setFrameShape(QFrame.NoFrame)
        self.frame_54.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_36 = QHBoxLayout(self.frame_54)
        self.horizontalLayout_36.setSpacing(6)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.horizontalLayout_36.setContentsMargins(0, 0, 0, 0)
        self.file_input_sys = QLineEdit(self.frame_54)
        self.file_input_sys.setObjectName(u"file_input_sys")

        self.horizontalLayout_36.addWidget(self.file_input_sys)

        self.file_input_sys_store = QPushButton(self.frame_54)
        self.file_input_sys_store.setObjectName(u"file_input_sys_store")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/folder_open_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.file_input_sys_store.setIcon(icon1)
        self.file_input_sys_store.setIconSize(QSize(24, 24))
        self.file_input_sys_store.setCheckable(False)
        self.file_input_sys_store.setFlat(True)

        self.horizontalLayout_36.addWidget(self.file_input_sys_store)

        self.horizontalLayout_36.setStretch(0, 5)

        self.verticalLayout_17.addWidget(self.frame_54)

        self.label_51 = QLabel(self.frame_102)
        self.label_51.setObjectName(u"label_51")

        self.verticalLayout_17.addWidget(self.label_51)

        self.frame_55 = QFrame(self.frame_102)
        self.frame_55.setObjectName(u"frame_55")
        self.frame_55.setFrameShape(QFrame.NoFrame)
        self.frame_55.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_37 = QHBoxLayout(self.frame_55)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalLayout_37.setContentsMargins(0, 0, 0, 0)
        self.file_input_inso = QLineEdit(self.frame_55)
        self.file_input_inso.setObjectName(u"file_input_inso")

        self.horizontalLayout_37.addWidget(self.file_input_inso)

        self.file_input_inso_store = QPushButton(self.frame_55)
        self.file_input_inso_store.setObjectName(u"file_input_inso_store")
        self.file_input_inso_store.setIcon(icon1)
        self.file_input_inso_store.setIconSize(QSize(24, 24))
        self.file_input_inso_store.setCheckable(False)
        self.file_input_inso_store.setFlat(True)

        self.horizontalLayout_37.addWidget(self.file_input_inso_store)

        self.horizontalLayout_37.setStretch(0, 5)

        self.verticalLayout_17.addWidget(self.frame_55)

        self.label_52 = QLabel(self.frame_102)
        self.label_52.setObjectName(u"label_52")

        self.verticalLayout_17.addWidget(self.label_52)

        self.frame_27 = QFrame(self.frame_102)
        self.frame_27.setObjectName(u"frame_27")
        self.frame_27.setFrameShape(QFrame.NoFrame)
        self.frame_27.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.frame_27)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.file_input_wind = QLineEdit(self.frame_27)
        self.file_input_wind.setObjectName(u"file_input_wind")

        self.horizontalLayout_13.addWidget(self.file_input_wind)

        self.file_input_wind_store = QPushButton(self.frame_27)
        self.file_input_wind_store.setObjectName(u"file_input_wind_store")
        self.file_input_wind_store.setIcon(icon1)
        self.file_input_wind_store.setIconSize(QSize(24, 24))
        self.file_input_wind_store.setCheckable(False)
        self.file_input_wind_store.setFlat(True)

        self.horizontalLayout_13.addWidget(self.file_input_wind_store)

        self.horizontalLayout_13.setStretch(0, 5)

        self.verticalLayout_17.addWidget(self.frame_27)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_17.addItem(self.verticalSpacer_8)


        self.horizontalLayout_54.addWidget(self.frame_102)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_54.addItem(self.horizontalSpacer)

        self.horizontalLayout_54.setStretch(0, 2)
        self.horizontalLayout_54.setStretch(1, 3)
        self.horizontalLayout_54.setStretch(2, 1)

        self.verticalLayout_58.addWidget(self.frame_100)


        self.verticalLayout_20.addWidget(self.frame_26)


        self.verticalLayout_19.addWidget(self.frame_25)

        self.file_info = QFrame(self.frame_24)
        self.file_info.setObjectName(u"file_info")
        self.file_info.setMaximumSize(QSize(16777215, 16777215))
        self.file_info.setFrameShape(QFrame.NoFrame)
        self.file_info.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.file_info)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.file_info)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_2.addWidget(self.textBrowser)

        self.file_hide = QPushButton(self.file_info)
        self.file_hide.setObjectName(u"file_hide")
        icon2 = QIcon()
        icon2.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.file_hide.setIcon(icon2)
        self.file_hide.setIconSize(QSize(24, 24))
        self.file_hide.setFlat(True)

        self.verticalLayout_2.addWidget(self.file_hide, 0, Qt.AlignHCenter)


        self.verticalLayout_19.addWidget(self.file_info)


        self.verticalLayout.addWidget(self.frame_24)

        self.frame_58 = QFrame(file_loader)
        self.frame_58.setObjectName(u"frame_58")
        self.frame_58.setFrameShape(QFrame.NoFrame)
        self.frame_58.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_29 = QHBoxLayout(self.frame_58)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalSpacer_16 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_29.addItem(self.horizontalSpacer_16)

        self.data_path_store = QPushButton(self.frame_58)
        self.data_path_store.setObjectName(u"data_path_store")
        self.data_path_store.setMaximumSize(QSize(0, 0))

        self.horizontalLayout_29.addWidget(self.data_path_store)

        self.results_next = QPushButton(self.frame_58)
        self.results_next.setObjectName(u"results_next")
        self.results_next.setFlat(True)

        self.horizontalLayout_29.addWidget(self.results_next)


        self.verticalLayout.addWidget(self.frame_58)


        self.retranslateUi(file_loader)

        QMetaObject.connectSlotsByName(file_loader)
    # setupUi

    def retranslateUi(self, file_loader):
        file_loader.setWindowTitle(QCoreApplication.translate("file_loader", u"Form", None))
        self.label_5.setText(QCoreApplication.translate("file_loader", u"Data Collection", None))
        self.label_21.setText(QCoreApplication.translate("file_loader", u"Data Import", None))
        self.pushButton_4.setText("")
        self.label_50.setText(QCoreApplication.translate("file_loader", u" System Load Data:", None))
        self.file_input_sys.setText("")
        self.file_input_sys.setPlaceholderText(QCoreApplication.translate("file_loader", u"path/to/system_load.csv", None))
        self.file_input_sys_store.setText("")
        self.label_51.setText(QCoreApplication.translate("file_loader", u"Insolation Data:", None))
        self.file_input_inso.setText("")
        self.file_input_inso.setPlaceholderText(QCoreApplication.translate("file_loader", u"path/to/insolation.csv", None))
        self.file_input_inso_store.setText("")
        self.label_52.setText(QCoreApplication.translate("file_loader", u"Wind Data:", None))
        self.file_input_wind.setText("")
        self.file_input_wind.setPlaceholderText(QCoreApplication.translate("file_loader", u"path/to/wind_data.csv", None))
        self.file_input_wind_store.setText("")
        self.textBrowser.setHtml(QCoreApplication.translate("file_loader", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Please select the data files to use in the simulation. The required files to upload are system load, sample insolation, and sample wind. The files should be formatted as .csv in the following style.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent"
                        ":0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">The system wide load data should follow this format:<br /></span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Header Row</span>: The first row of your CSV file should contain the following column headers: <span style=\" font-family:'Courier New';\">year</span>, <span style=\" font-family:'Courier New';\">month</span>, <span style=\" font-family:'Courier New';\">day</span>, <span style=\" font-family:'Courier New';\">hour</span>, <span style=\" font-family:'Courier New';\">system_wid"
                        "e</span></li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Data Rows</span>: Each subsequent row should represent a data entry corresponding to the headers. For example, a row might look like this: <span style=\" font-family:'Courier New';\">2020, 1, 1, 0, 100</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Year</span>: The year of the data entry, e.g., <span style=\" font-family:'Courier New';\">2020</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Month</span>: The month of the data entry, e.g., 1 for Ja"
                        "nuary.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Day</span>: The day of the data entry, e.g., <span style=\" font-family:'Courier New';\">1</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Hour</span>: The hour of the data entry, e.g., <span style=\" font-family:'Courier New';\">0</span> for midnight.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">System-wide</span>: System-wide load value.</li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:"
                        "0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">The insolation data should follow this format:<br /></span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Header Row</span>: The first row of your CSV file should contain the following column headers: <span style=\" font-family:'Courier New';\">year</span>, <span style=\" font-family:'Courier New';\">month</span>, <span style=\" font-family:'Courier New';\">day</span>, <span style=\" font-family:'Courier New';\">hour</span>, <span style=\" font-family:'Courier New"
                        "';\">insolation_pu</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Data Rows</span>: Each subsequent row should represent a data entry corresponding to the headers. For example: <span style=\" font-family:'Courier New';\">2021, 1, 1, 00, 0.85</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Year</span>: The year of the data entry, e.g., <span style=\" font-family:'Courier New';\">2021</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Month</span>: The month of the data entry, e.g., <span style=\" f"
                        "ont-family:'Courier New';\">1</span> for January.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Day</span>: The day of the data entry, e.g., <span style=\" font-family:'Courier New';\">1</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Hour</span>: The hour of the data entry, e.g., <span style=\" font-family:'Courier New';\">0</span> for midnight.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Insolation_pu</span>: The per-unit insolation value, representing the per-unit ouput power.</li></ul>\n"
"<p style=\""
                        "-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">The wind data should follow this format:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Header Row</span>: The first row of your CSV file should contain the following colu"
                        "mn headers: <span style=\" font-family:'Courier New';\">year</span>, <span style=\" font-family:'Courier New';\">month</span>, <span style=\" font-family:'Courier New';\">day</span>, <span style=\" font-family:'Courier New';\">hour</span>, <span style=\" font-family:'Courier New';\">wind_power_pu</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Data Rows</span>: Each subsequent row should represent a data entry corresponding to the headers. For example, a row might look like this: <span style=\" font-family:'Courier New';\">2021, 1, 1, 1, 1.0000</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Year</span>: The year of the data entry, e.g., <span style=\" font-family:'C"
                        "ourier New';\">2021</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Month</span>: The month of the data entry, e.g., <span style=\" font-family:'Courier New';\">1</span> for January.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Day</span>: The day of the data entry, e.g., <span style=\" font-family:'Courier New';\">1</span>.</li>\n"
"<li style=\" font-family:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Hour</span>: The hour of the data entry, e.g., <span style=\" font-family:'Courier New';\">1</span> for 1 AM.</li>\n"
"<li style=\" font-f"
                        "amily:'Segoe UI'; font-size:9pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Wind_power_pu</span>: The per-unit wind power value, representing the wind power generated.</li></ul></body></html>", None))
        self.file_hide.setText("")
        self.data_path_store.setText(QCoreApplication.translate("file_loader", u"Save", None))
        self.results_next.setText(QCoreApplication.translate("file_loader", u"Next", None))
    # retranslateUi

