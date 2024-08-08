# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'data_visiedLwe.ui'
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
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QProgressBar,
    QPushButton, QSizePolicy, QStackedWidget, QTextBrowser,
    QVBoxLayout, QWidget)
import quest.resources_rc

class Ui_data_v(object):
    def setupUi(self, data_v):
        if not data_v.objectName():
            data_v.setObjectName(u"data_v")
        data_v.resize(1444, 856)
        self.verticalLayout = QVBoxLayout(data_v)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.data_entry = QStackedWidget(data_v)
        self.data_entry.setObjectName(u"data_entry")
        self.stream_app = QWidget()
        self.stream_app.setObjectName(u"stream_app")
        self.verticalLayout_3 = QVBoxLayout(self.stream_app)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame = QFrame(self.stream_app)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.frame_2)
        self.frame_5.setObjectName(u"frame_5")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_5)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.pyg_view = QWebEngineView(self.frame_5)
        self.pyg_view.setObjectName(u"pyg_view")
        self.pyg_view.setUrl(QUrl(u"about:blank"))

        self.verticalLayout_4.addWidget(self.pyg_view)


        self.verticalLayout_2.addWidget(self.frame_5)

        self.verticalLayout_2.setStretch(0, 10)

        self.horizontalLayout.addWidget(self.frame_2)

        self.horizontalLayout.setStretch(0, 2)

        self.verticalLayout_3.addWidget(self.frame)

        self.data_entry.addWidget(self.stream_app)
        self.data_welcome = QWidget()
        self.data_welcome.setObjectName(u"data_welcome")
        self.verticalLayout_6 = QVBoxLayout(self.data_welcome)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.textBrowser = QTextBrowser(self.data_welcome)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"background-color: transparent;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_6.addWidget(self.textBrowser)

        self.frame_3 = QFrame(self.data_welcome)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_3)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame_6 = QFrame(self.frame_3)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_6)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.data_vis_install_button = QPushButton(self.frame_6)
        self.data_vis_install_button.setObjectName(u"data_vis_install_button")
        self.data_vis_install_button.setMinimumSize(QSize(100, 28))
        self.data_vis_install_button.setMaximumSize(QSize(100, 16777215))
        self.data_vis_install_button.setStyleSheet(u"")
        self.data_vis_install_button.setIconSize(QSize(16, 16))
        self.data_vis_install_button.setCheckable(True)
        self.data_vis_install_button.setChecked(False)
        self.data_vis_install_button.setFlat(True)

        self.verticalLayout_7.addWidget(self.data_vis_install_button)

        self.progess = QFrame(self.frame_6)
        self.progess.setObjectName(u"progess")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.progess.sizePolicy().hasHeightForWidth())
        self.progess.setSizePolicy(sizePolicy1)
        self.progess.setMinimumSize(QSize(0, 8))
        self.progess.setStyleSheet(u"")
        self.progess.setFrameShape(QFrame.NoFrame)
        self.progess.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.progess)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.gpt_progress_bar = QProgressBar(self.progess)
        self.gpt_progress_bar.setObjectName(u"gpt_progress_bar")
        sizePolicy1.setHeightForWidth(self.gpt_progress_bar.sizePolicy().hasHeightForWidth())
        self.gpt_progress_bar.setSizePolicy(sizePolicy1)
        self.gpt_progress_bar.setMinimumSize(QSize(0, 4))
        self.gpt_progress_bar.setStyleSheet(u"QProgressBar {\n"
"	min-height: 4px;\n"
"	max-height: 4px;\n"
"	border-radius: 2px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    border-radius: 2px;\n"
"    background-color: rgb(129, 194, 65);\n"
"}")
        self.gpt_progress_bar.setValue(50)
        self.gpt_progress_bar.setTextVisible(False)
        self.gpt_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_11.addWidget(self.gpt_progress_bar)


        self.verticalLayout_7.addWidget(self.progess)


        self.verticalLayout_5.addWidget(self.frame_6, 0, Qt.AlignHCenter)


        self.verticalLayout_6.addWidget(self.frame_3)

        self.data_entry.addWidget(self.data_welcome)

        self.verticalLayout.addWidget(self.data_entry)


        self.retranslateUi(data_v)

        self.data_entry.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(data_v)
    # setupUi

    def retranslateUi(self, data_v):
        data_v.setWindowTitle(QCoreApplication.translate("data_v", u"Form", None))
        self.textBrowser.setHtml(QCoreApplication.translate("data_v", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:26pt; font-weight:700;\">QuESt-GPT </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:700;\">AI-powered tool for data analysis and visualization</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; mar"
                        "gin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:26pt; font-weight:700;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-lef"
                        "t:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt;\">This application helps users analyze and visualize their dataset (in CSV files). The application utilizes Large Language Models (LLMs) to translate users queries into python codes for performing data analysis and visualization. Currently, GPT4 models (OpenAI's API: https://openai.com/product) and codellama2 model (Replicate's API: https://replicate.com/) are used within the application.  </span></p></body></html>", None))
        self.data_vis_install_button.setText(QCoreApplication.translate("data_v", u"Continue", None))
    # retranslateUi

