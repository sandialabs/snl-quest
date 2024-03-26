# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about_stackAYEDjG.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy, QStackedWidget,
    QTextBrowser, QVBoxLayout, QWidget)
import resources_rc

class Ui_help_land(object):
    def setupUi(self, help_land):
        if not help_land.objectName():
            help_land.setObjectName(u"help_land")
        help_land.resize(1083, 649)
        self.verticalLayout = QVBoxLayout(help_land)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.help_widge = QStackedWidget(help_land)
        self.help_widge.setObjectName(u"help_widge")
        self.quest_help_home = QWidget()
        self.quest_help_home.setObjectName(u"quest_help_home")
        self.verticalLayout_2 = QVBoxLayout(self.quest_help_home)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.frame = QFrame(self.quest_help_home)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"")
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_4)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.ack_push = QPushButton(self.frame_4)
        self.ack_push.setObjectName(u"ack_push")
        self.ack_push.setStyleSheet(u"font: 600 18pt \"Segoe UI\";")
        self.ack_push.setFlat(True)

        self.verticalLayout_9.addWidget(self.ack_push)


        self.horizontalLayout_2.addWidget(self.frame_4, 0, Qt.AlignHCenter)

        self.frame_7 = QFrame(self.frame)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"")
        self.frame_7.setFrameShape(QFrame.NoFrame)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame_7)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.get_push = QPushButton(self.frame_7)
        self.get_push.setObjectName(u"get_push")
        self.get_push.setStyleSheet(u"font: 600 18pt \"Segoe UI\";")
        self.get_push.setFlat(True)

        self.verticalLayout_8.addWidget(self.get_push)


        self.horizontalLayout_2.addWidget(self.frame_7, 0, Qt.AlignHCenter)

        self.frame_5 = QFrame(self.frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setStyleSheet(u"")
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.who_push = QPushButton(self.frame_5)
        self.who_push.setObjectName(u"who_push")
        self.who_push.setStyleSheet(u"font: 600 18pt \"Segoe UI\";")
        self.who_push.setFlat(True)

        self.verticalLayout_7.addWidget(self.who_push)


        self.horizontalLayout_2.addWidget(self.frame_5, 0, Qt.AlignHCenter)


        self.gridLayout_2.addWidget(self.frame, 2, 0, 1, 1)

        self.frame_2 = QFrame(self.quest_help_home)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy1)
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"font: 800 26pt \"Segoe UI\";")

        self.verticalLayout_4.addWidget(self.label_7)


        self.gridLayout_2.addWidget(self.frame_2, 0, 0, 1, 1, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frame_3 = QFrame(self.quest_help_home)
        self.frame_3.setObjectName(u"frame_3")
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame_3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_6 = QFrame(self.frame_3)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setStyleSheet(u"")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_6)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.what_push = QPushButton(self.frame_6)
        self.what_push.setObjectName(u"what_push")
        self.what_push.setStyleSheet(u"\n"
"font: 600 18pt \"Segoe UI\";")
        self.what_push.setFlat(True)

        self.verticalLayout_5.addWidget(self.what_push)


        self.horizontalLayout.addWidget(self.frame_6, 0, Qt.AlignHCenter)

        self.frame_8 = QFrame(self.frame_3)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setStyleSheet(u"")
        self.frame_8.setFrameShape(QFrame.NoFrame)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_8)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.inst_push = QPushButton(self.frame_8)
        self.inst_push.setObjectName(u"inst_push")
        self.inst_push.setStyleSheet(u"font: 600 18pt \"Segoe UI\";")
        self.inst_push.setFlat(True)

        self.verticalLayout_6.addWidget(self.inst_push)


        self.horizontalLayout.addWidget(self.frame_8, 0, Qt.AlignHCenter)

        self.frame_9 = QFrame(self.frame_3)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setStyleSheet(u"")
        self.frame_9.setFrameShape(QFrame.NoFrame)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_9)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.doc_push = QPushButton(self.frame_9)
        self.doc_push.setObjectName(u"doc_push")
        self.doc_push.setStyleSheet(u"font: 600 18pt \"Segoe UI\";")
        self.doc_push.setFlat(True)

        self.verticalLayout_3.addWidget(self.doc_push)


        self.horizontalLayout.addWidget(self.frame_9, 0, Qt.AlignHCenter)


        self.gridLayout_2.addWidget(self.frame_3, 1, 0, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_2)

        self.help_widge.addWidget(self.quest_help_home)
        self.acknowledge_page = QWidget()
        self.acknowledge_page.setObjectName(u"acknowledge_page")
        self.verticalLayout_13 = QVBoxLayout(self.acknowledge_page)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_11 = QLabel(self.acknowledge_page)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setStyleSheet(u"font: 20pt \"Segoe UI\";")

        self.verticalLayout_13.addWidget(self.label_11)

        self.textBrowser_4 = QTextBrowser(self.acknowledge_page)
        self.textBrowser_4.setObjectName(u"textBrowser_4")

        self.verticalLayout_13.addWidget(self.textBrowser_4)

        self.ack_back = QPushButton(self.acknowledge_page)
        self.ack_back.setObjectName(u"ack_back")
        self.ack_back.setFlat(True)

        self.verticalLayout_13.addWidget(self.ack_back, 0, Qt.AlignHCenter)

        self.help_widge.addWidget(self.acknowledge_page)
        self.getting_help = QWidget()
        self.getting_help.setObjectName(u"getting_help")
        self.verticalLayout_14 = QVBoxLayout(self.getting_help)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_12 = QLabel(self.getting_help)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"font: 20pt \"Segoe UI\";")

        self.verticalLayout_14.addWidget(self.label_12)

        self.textBrowser_5 = QTextBrowser(self.getting_help)
        self.textBrowser_5.setObjectName(u"textBrowser_5")

        self.verticalLayout_14.addWidget(self.textBrowser_5)

        self.help_back = QPushButton(self.getting_help)
        self.help_back.setObjectName(u"help_back")
        self.help_back.setFlat(True)

        self.verticalLayout_14.addWidget(self.help_back, 0, Qt.AlignHCenter)

        self.help_widge.addWidget(self.getting_help)
        self.users_page = QWidget()
        self.users_page.setObjectName(u"users_page")
        self.verticalLayout_15 = QVBoxLayout(self.users_page)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.label_13 = QLabel(self.users_page)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setStyleSheet(u"font: 20pt \"Segoe UI\";")

        self.verticalLayout_15.addWidget(self.label_13)

        self.textBrowser_6 = QTextBrowser(self.users_page)
        self.textBrowser_6.setObjectName(u"textBrowser_6")

        self.verticalLayout_15.addWidget(self.textBrowser_6)

        self.use_back = QPushButton(self.users_page)
        self.use_back.setObjectName(u"use_back")
        self.use_back.setFlat(True)

        self.verticalLayout_15.addWidget(self.use_back, 0, Qt.AlignHCenter)

        self.help_widge.addWidget(self.users_page)
        self.docs_page = QWidget()
        self.docs_page.setObjectName(u"docs_page")
        self.verticalLayout_12 = QVBoxLayout(self.docs_page)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_10 = QLabel(self.docs_page)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setStyleSheet(u"font: 20pt \"Segoe UI\";")

        self.verticalLayout_12.addWidget(self.label_10)

        self.textBrowser_3 = QTextBrowser(self.docs_page)
        self.textBrowser_3.setObjectName(u"textBrowser_3")

        self.verticalLayout_12.addWidget(self.textBrowser_3)

        self.docs_back = QPushButton(self.docs_page)
        self.docs_back.setObjectName(u"docs_back")
        self.docs_back.setFlat(True)

        self.verticalLayout_12.addWidget(self.docs_back, 0, Qt.AlignHCenter)

        self.help_widge.addWidget(self.docs_page)
        self.install_apps_page = QWidget()
        self.install_apps_page.setObjectName(u"install_apps_page")
        self.verticalLayout_11 = QVBoxLayout(self.install_apps_page)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_9 = QLabel(self.install_apps_page)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setStyleSheet(u"font: 20pt \"Segoe UI\";\n"
"background: transparent")

        self.verticalLayout_11.addWidget(self.label_9)

        self.textBrowser_2 = QTextBrowser(self.install_apps_page)
        self.textBrowser_2.setObjectName(u"textBrowser_2")

        self.verticalLayout_11.addWidget(self.textBrowser_2)

        self.inst_back = QPushButton(self.install_apps_page)
        self.inst_back.setObjectName(u"inst_back")
        self.inst_back.setFlat(True)

        self.verticalLayout_11.addWidget(self.inst_back, 0, Qt.AlignHCenter)

        self.help_widge.addWidget(self.install_apps_page)
        self.what_is_quest = QWidget()
        self.what_is_quest.setObjectName(u"what_is_quest")
        self.verticalLayout_10 = QVBoxLayout(self.what_is_quest)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_8 = QLabel(self.what_is_quest)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setStyleSheet(u"font: 20pt \"Segoe UI\";")

        self.verticalLayout_10.addWidget(self.label_8)

        self.textBrowser = QTextBrowser(self.what_is_quest)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout_10.addWidget(self.textBrowser)

        self.what_back = QPushButton(self.what_is_quest)
        self.what_back.setObjectName(u"what_back")
        self.what_back.setFlat(True)

        self.verticalLayout_10.addWidget(self.what_back, 0, Qt.AlignHCenter)

        self.help_widge.addWidget(self.what_is_quest)

        self.gridLayout.addWidget(self.help_widge, 0, 0, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.frame_11 = QFrame(help_land)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy2)
        self.frame_11.setMaximumSize(QSize(16777215, 75))
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.quest_logo = QPushButton(self.frame_11)
        self.quest_logo.setObjectName(u"quest_logo")
        self.quest_logo.setStyleSheet(u"QPushButton:hover{border: none;}")
        icon = QIcon()
        icon.addFile(u":/logos/images/logo/Quest_Logo_RGB.png", QSize(), QIcon.Normal, QIcon.Off)
        self.quest_logo.setIcon(icon)
        self.quest_logo.setIconSize(QSize(100, 100))
        self.quest_logo.setFlat(True)

        self.horizontalLayout_3.addWidget(self.quest_logo)

        self.snl_logo = QPushButton(self.frame_11)
        self.snl_logo.setObjectName(u"snl_logo")
        self.snl_logo.setStyleSheet(u"QPushButton:hover{border: none;}")
        icon1 = QIcon()
        icon1.addFile(u":/logos/images/logo/SNL_Stacked_Black_Blue.jpg", QSize(), QIcon.Normal, QIcon.Off)
        self.snl_logo.setIcon(icon1)
        self.snl_logo.setIconSize(QSize(100, 100))
        self.snl_logo.setFlat(True)

        self.horizontalLayout_3.addWidget(self.snl_logo)

        self.doe_logo = QPushButton(self.frame_11)
        self.doe_logo.setObjectName(u"doe_logo")
        self.doe_logo.setStyleSheet(u"QPushButton:hover{border: none;}")
        icon2 = QIcon()
        icon2.addFile(u":/logos/images/logo/New_DOE_Logo_Color.jpg", QSize(), QIcon.Normal, QIcon.Off)
        self.doe_logo.setIcon(icon2)
        self.doe_logo.setIconSize(QSize(100, 100))
        self.doe_logo.setFlat(True)

        self.horizontalLayout_3.addWidget(self.doe_logo)


        self.verticalLayout.addWidget(self.frame_11)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(help_land)

        self.help_widge.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(help_land)
    # setupUi

    def retranslateUi(self, help_land):
        help_land.setWindowTitle(QCoreApplication.translate("help_land", u"Form", None))
        self.ack_push.setText(QCoreApplication.translate("help_land", u"Acknowledgements", None))
        self.get_push.setText(QCoreApplication.translate("help_land", u"Getting Help", None))
        self.who_push.setText(QCoreApplication.translate("help_land", u"Who Uses QuESt?", None))
        self.label_7.setText(QCoreApplication.translate("help_land", u"QuESt Help Center", None))
        self.what_push.setText(QCoreApplication.translate("help_land", u"What is QuESt?", None))
        self.inst_push.setText(QCoreApplication.translate("help_land", u"Installing Apps", None))
#if QT_CONFIG(tooltip)
        self.doc_push.setToolTip(QCoreApplication.translate("help_land", u"<html><head/><body><p><span style=\" font-size:9pt; font-weight:400;\">Under Construction</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.doc_push.setText(QCoreApplication.translate("help_land", u"Examples", None))
        self.label_11.setText(QCoreApplication.translate("help_land", u"Acknowledgements", None))
        self.textBrowser_4.setHtml(QCoreApplication.translate("help_land", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">QuESt is developed by the </span><span style=\" font-size:14pt; text-decoration: underline;\">Energy Storage Tehcnology and Systems</span><span style=\" font-size:14pt;\"> and </span><span style=\" font-size:14pt; text-decoration: underline;\">Electric Power Systems Research</span><span style=\" font-size:14pt;\"> departments at </span><span style=\" font-size:14pt; te"
                        "xt-decoration: underline;\">Sandia National Laboratories</span><span style=\" font-size:14pt;\">.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">The developers would like to thank </span><span style=\" font-size:14pt; font-weight:700;\">Dr. Imre Gyuk</span><span style=\" font-size:14pt;\"> at the Energy Storage Program at the U.S. Department of Energy for funding the development of theis software.</span></p></body></html>", None))
        self.ack_back.setText(QCoreApplication.translate("help_land", u"Go Back", None))
        self.label_12.setText(QCoreApplication.translate("help_land", u"Getting Help", None))
        self.textBrowser_5.setHtml(QCoreApplication.translate("help_land", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">For issues and feedback we would appreciate it if you could use the &quot;Issues&quot; feature of this repository. This helps others join the discussion and helps us keep track of and document issues.</span></p>\n"
"<h3 style=\" margin-top:14px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a name=\"user-content-email\""
                        "></a><span style=\" font-size:14pt; font-weight:700;\">E</span><span style=\" font-size:14pt; font-weight:700;\">mail</span></h3>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Entity account </span><span style=\" font-family:'Courier New'; font-size:14pt;\">@sandia.gov: snl-quest</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Project maintainer (Tu Nguyen) </span><span style=\" font-family:'Courier New'; font-size:14pt;\">@sandia.gov: tunguy</span></p></body></html>", None))
        self.help_back.setText(QCoreApplication.translate("help_land", u"Go Back", None))
        self.label_13.setText(QCoreApplication.translate("help_land", u"Who Uses Quest?", None))
        self.textBrowser_6.setHtml(QCoreApplication.translate("help_land", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">The software is designed to be used by anyone with an interest in performing analysis of energy storage or its applications without having to create their own models or write their own code. It\u2019s designed to be easy to use out of the box but also modifiable by the savvy user if they so choose. The software is intended to be used as a platform for running simulatio"
                        "ns, obtaining results, and using the information to inform planning decisions.</span></p></body></html>", None))
        self.use_back.setText(QCoreApplication.translate("help_land", u"Go Back", None))
        self.label_10.setText(QCoreApplication.translate("help_land", u"Examples", None))
        self.textBrowser_3.setHtml(QCoreApplication.translate("help_land", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">This page is under construction.</span></p></body></html>", None))
        self.docs_back.setText(QCoreApplication.translate("help_land", u"Go Back", None))
        self.label_9.setText(QCoreApplication.translate("help_land", u"Installing Apps", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("help_land", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Available applications can be installed with the click of a button. Each application will be installed into an independent environment to improve version control of libraries. After the installation is completed the install button will be updated to a launch button. The user will then be able to launch applications from the home page.</span></p></body></html>", None))
        self.inst_back.setText(QCoreApplication.translate("help_land", u"Go Back", None))
        self.label_8.setText(QCoreApplication.translate("help_land", u"What is Quest?", None))
        self.textBrowser.setHtml(QCoreApplication.translate("help_land", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">QuESt 2.0</span><span style=\" font-size:14pt;\"> is an evolved version of the original QuESt, an open-source Python software designed for energy storage (ES) analytics. It transforms into a platform providing centralized access to multiple tools and improved data analytics, aiming to simplify ES analysis and democratize access to these tools. </span"
                        "></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Currently, QuESt 2.0 includes three main components: </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">1.</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">The QuESt App Hub</span><span style=\" font-size:14pt;\"> operates similarly to an app store, offering access points to a multitude of applications. Currently, various energy storage analytics tools have been available on QuESt App hub. For example: </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Symbol'; font-size:14pt;\">\u00b7"
                        "</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt Data Manager</span><span style=\" font-size:14pt;\"> manages the acquisition of data. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Symbol'; font-size:14pt;\">\u00b7</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt Valuation</span><span style=\" font-size:14pt;\"> estimates the potential revenue generated by energy storage systems when providing ancillary services in the electricity markets. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Symbol'; font-size:14pt;\">\u00b7</span><span styl"
                        "e=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt BTM (Behind-The-Meter) c</span><span style=\" font-size:14pt;\">alculates the cost savings for time-of-use and net energy metering customers utilizing behind-the-meter energy storage systems. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Symbol'; font-size:14pt;\">\u00b7</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt Technology Selection</span><span style=\" font-size:14pt;\"> supports in selecting the appropriate energy storage technology based on specific applications and requirements. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0p"
                        "x;\"><span style=\" font-family:'Symbol'; font-size:14pt;\">\u00b7</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt Performance</span><span style=\" font-size:14pt;\"> evaluates the performance of energy storage systems in different climatic conditions. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Symbol'; font-size:14pt;\">\u00b7</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt Microgrid </span><span style=\" font-size:14pt;\">supports microgrid design and simulation considering energy storage as a key component. </span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><s"
                        "pan style=\" font-size:14pt;\">It has been designed with key features to improve user experience and application management: </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">User-Friendly Access</span>: Users can easily find and install applications that suit their specific needs. </li>\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Isolated Environments</span>: Upon installation, each application creates an isolated environment. This ensures that applications run independently, preventing conflicts, and enhancing stability. </li>\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:0px; margin-bottom:12px; marg"
                        "in-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Simultaneous Operation</span>: Multiple applications can be installed and operated simultaneously, allowing users to leverage different tools without interference. </li></ul>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">2.</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">The QuESt Workspace</span><span style=\" font-size:14pt;\"> provides an integrated environment where users can create workflows by assembling multiple applications into a coherent process. It enhances the platform's usability and efficiency through several mechanisms: </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li "
                        "style=\" font-size:14pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Integration of Applications</span>: Users can create work processes that integrate multiple apps by assembling pipelines using plugin extensions. This modular approach allows for the flexible composition of analytics workflows tailored to specific needs. </li>\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Workflow Management</span>: The workspace supports the selection, assembly, connection, and post-processing of data and tools. This structured approach streamlines the analytics process, from data preparation to visualization, making it easier to manage and understand. </li></ul>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-in"
                        "dent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">3.</span><span style=\" font-family:'Times New Roman'; font-size:14pt;\">\u00a0\u00a0\u00a0\u00a0\u00a0\u00a0 </span><span style=\" font-size:14pt; font-weight:700;\">QuESt GPT</span><span style=\" font-size:14pt;\"> represents a leap forward in data analytics within the platform, utilizing generative AI (specifically Large Language Models, or LLM) for data characterization and visualization: </span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Data Insights</span>: Users can select datasets and ask questions about the data, with QuESt GPT providing insights based on the data's characteristics. This interaction model simplifies complex data analysis, making it accessible to users without deep t"
                        "echnical expertise. </li>\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:0px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Utilization of LLMs</span>: By leveraging advanced open-source LLMs such as OpenAi\u2019sGPT4 and Meta\u2019s Llama2, QuESt GPT can perform sophisticated data analytics tasks, such as characterizing and visualizing large datasets. This enables users to gain deeper insights from their data, supporting more informed decision-making at no costs. </li></ul></body></html>", None))
        self.what_back.setText(QCoreApplication.translate("help_land", u"Go Back", None))
        self.quest_logo.setText("")
        self.snl_logo.setText("")
        self.doe_logo.setText("")
    # retranslateUi

