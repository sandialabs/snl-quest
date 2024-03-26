# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'home_pageBrZPJE.ui'
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
    QLineEdit, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QStackedWidget, QTextBrowser, QVBoxLayout,
    QWidget)
import resources_rc
import resources_rc

class Ui_home_page(object):
    def setupUi(self, home_page):
        if not home_page.objectName():
            home_page.setObjectName(u"home_page")
        home_page.resize(1112, 787)
        home_page.setStyleSheet(u"")
        self.horizontalLayout = QHBoxLayout(home_page)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.home_frame = QFrame(home_page)
        self.home_frame.setObjectName(u"home_frame")
        self.home_frame.setFrameShape(QFrame.StyledPanel)
        self.home_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.home_frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_9 = QFrame(self.home_frame)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setStyleSheet(u"")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_9)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.home_page_frame = QFrame(self.frame_9)
        self.home_page_frame.setObjectName(u"home_page_frame")
        self.home_page_frame.setStyleSheet(u"")
        self.home_page_frame.setFrameShape(QFrame.StyledPanel)
        self.home_page_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.home_page_frame)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.home_page_scroll = QScrollArea(self.home_page_frame)
        self.home_page_scroll.setObjectName(u"home_page_scroll")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.home_page_scroll.sizePolicy().hasHeightForWidth())
        self.home_page_scroll.setSizePolicy(sizePolicy)
        self.home_page_scroll.setStyleSheet(u"")
        self.home_page_scroll.setFrameShape(QFrame.NoFrame)
        self.home_page_scroll.setFrameShadow(QFrame.Plain)
        self.home_page_scroll.setLineWidth(0)
        self.home_page_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.home_page_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.home_page_scroll.setWidgetResizable(True)
        self.home_pace_content = QWidget()
        self.home_pace_content.setObjectName(u"home_pace_content")
        self.home_pace_content.setGeometry(QRect(0, 0, 1071, 782))
        self.home_pace_content.setStyleSheet(u"")
        self.verticalLayout_8 = QVBoxLayout(self.home_pace_content)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.home_apps = QFrame(self.home_pace_content)
        self.home_apps.setObjectName(u"home_apps")
        self.home_apps.setStyleSheet(u"")
        self.home_apps.setFrameShape(QFrame.StyledPanel)
        self.home_apps.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.home_apps)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tech_app = QFrame(self.home_apps)
        self.tech_app.setObjectName(u"tech_app")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tech_app.sizePolicy().hasHeightForWidth())
        self.tech_app.setSizePolicy(sizePolicy1)
        self.tech_app.setMinimumSize(QSize(180, 250))
        self.tech_app.setStyleSheet(u"")
        self.tech_app.setFrameShape(QFrame.StyledPanel)
        self.tech_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_22 = QVBoxLayout(self.tech_app)
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(9, 9, 9, 9)
        self.app_info_7 = QFrame(self.tech_app)
        self.app_info_7.setObjectName(u"app_info_7")
        self.app_info_7.setStyleSheet(u"image: url(:/logos/images/logo/Quest_Tech_Logo_RGB.png);")
        self.app_info_7.setFrameShape(QFrame.StyledPanel)
        self.app_info_7.setFrameShadow(QFrame.Raised)

        self.verticalLayout_22.addWidget(self.app_info_7)

        self.app_control_7 = QFrame(self.tech_app)
        self.app_control_7.setObjectName(u"app_control_7")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.app_control_7.sizePolicy().hasHeightForWidth())
        self.app_control_7.setSizePolicy(sizePolicy2)
        self.app_control_7.setMinimumSize(QSize(0, 40))
        self.app_control_7.setStyleSheet(u"")
        self.app_control_7.setFrameShape(QFrame.StyledPanel)
        self.app_control_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.app_control_7)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.app_about_button_7 = QPushButton(self.app_control_7)
        self.app_about_button_7.setObjectName(u"app_about_button_7")
        sizePolicy1.setHeightForWidth(self.app_about_button_7.sizePolicy().hasHeightForWidth())
        self.app_about_button_7.setSizePolicy(sizePolicy1)
        self.app_about_button_7.setMinimumSize(QSize(28, 28))
        self.app_about_button_7.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u":/icon/images/icons/info_FILL0_wght200_GRAD0_opsz48(1).svg", QSize(), QIcon.Normal, QIcon.Off)
        self.app_about_button_7.setIcon(icon)
        self.app_about_button_7.setIconSize(QSize(28, 28))
        self.app_about_button_7.setCheckable(False)
        self.app_about_button_7.setFlat(True)

        self.horizontalLayout_15.addWidget(self.app_about_button_7)

        self.tech_selection_install_button = QPushButton(self.app_control_7)
        self.tech_selection_install_button.setObjectName(u"tech_selection_install_button")
        self.tech_selection_install_button.setMinimumSize(QSize(0, 28))
        self.tech_selection_install_button.setStyleSheet(u"")
        self.tech_selection_install_button.setIconSize(QSize(16, 16))
        self.tech_selection_install_button.setCheckable(True)
        self.tech_selection_install_button.setFlat(True)

        self.horizontalLayout_15.addWidget(self.tech_selection_install_button)

        self.app_setting_button_7 = QPushButton(self.app_control_7)
        self.app_setting_button_7.setObjectName(u"app_setting_button_7")
        sizePolicy1.setHeightForWidth(self.app_setting_button_7.sizePolicy().hasHeightForWidth())
        self.app_setting_button_7.setSizePolicy(sizePolicy1)
        self.app_setting_button_7.setMinimumSize(QSize(28, 28))
        self.app_setting_button_7.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/icon/images/icons/settings_FILL0_wght200_GRAD0_opsz48.png", QSize(), QIcon.Normal, QIcon.Off)
        self.app_setting_button_7.setIcon(icon1)
        self.app_setting_button_7.setIconSize(QSize(28, 28))
        self.app_setting_button_7.setCheckable(False)

        self.horizontalLayout_15.addWidget(self.app_setting_button_7)


        self.verticalLayout_22.addWidget(self.app_control_7)

        self.progess_7 = QFrame(self.tech_app)
        self.progess_7.setObjectName(u"progess_7")
        sizePolicy2.setHeightForWidth(self.progess_7.sizePolicy().hasHeightForWidth())
        self.progess_7.setSizePolicy(sizePolicy2)
        self.progess_7.setMinimumSize(QSize(0, 8))
        self.progess_7.setStyleSheet(u"")
        self.progess_7.setFrameShape(QFrame.StyledPanel)
        self.progess_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.progess_7)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.tech_progress_bar = QProgressBar(self.progess_7)
        self.tech_progress_bar.setObjectName(u"tech_progress_bar")
        sizePolicy2.setHeightForWidth(self.tech_progress_bar.sizePolicy().hasHeightForWidth())
        self.tech_progress_bar.setSizePolicy(sizePolicy2)
        self.tech_progress_bar.setMinimumSize(QSize(0, 0))
        self.tech_progress_bar.setStyleSheet(u"")
        self.tech_progress_bar.setValue(50)
        self.tech_progress_bar.setTextVisible(False)
        self.tech_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_23.addWidget(self.tech_progress_bar)


        self.verticalLayout_22.addWidget(self.progess_7)


        self.gridLayout.addWidget(self.tech_app, 0, 0, 1, 1)

        self.eval_app = QFrame(self.home_apps)
        self.eval_app.setObjectName(u"eval_app")
        sizePolicy1.setHeightForWidth(self.eval_app.sizePolicy().hasHeightForWidth())
        self.eval_app.setSizePolicy(sizePolicy1)
        self.eval_app.setMinimumSize(QSize(180, 250))
        self.eval_app.setStyleSheet(u"")
        self.eval_app.setFrameShape(QFrame.StyledPanel)
        self.eval_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.eval_app)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(9, 9, 9, 9)
        self.app_info_2 = QFrame(self.eval_app)
        self.app_info_2.setObjectName(u"app_info_2")
        self.app_info_2.setStyleSheet(u"image: url(:/logos/images/logo/Quest_EvaluationLogo_RGB.png);\n"
"")
        self.app_info_2.setFrameShape(QFrame.StyledPanel)
        self.app_info_2.setFrameShadow(QFrame.Raised)

        self.verticalLayout_12.addWidget(self.app_info_2)

        self.app_control_2 = QFrame(self.eval_app)
        self.app_control_2.setObjectName(u"app_control_2")
        sizePolicy2.setHeightForWidth(self.app_control_2.sizePolicy().hasHeightForWidth())
        self.app_control_2.setSizePolicy(sizePolicy2)
        self.app_control_2.setMinimumSize(QSize(0, 40))
        self.app_control_2.setStyleSheet(u"")
        self.app_control_2.setFrameShape(QFrame.StyledPanel)
        self.app_control_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.app_control_2)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.app_about_button_2 = QPushButton(self.app_control_2)
        self.app_about_button_2.setObjectName(u"app_about_button_2")
        sizePolicy1.setHeightForWidth(self.app_about_button_2.sizePolicy().hasHeightForWidth())
        self.app_about_button_2.setSizePolicy(sizePolicy1)
        self.app_about_button_2.setMinimumSize(QSize(28, 28))
        self.app_about_button_2.setStyleSheet(u"")
        self.app_about_button_2.setIcon(icon)
        self.app_about_button_2.setIconSize(QSize(28, 28))
        self.app_about_button_2.setCheckable(False)
        self.app_about_button_2.setFlat(True)

        self.horizontalLayout_10.addWidget(self.app_about_button_2)

        self.evaluation_install_button = QPushButton(self.app_control_2)
        self.evaluation_install_button.setObjectName(u"evaluation_install_button")
        self.evaluation_install_button.setMinimumSize(QSize(0, 28))
        self.evaluation_install_button.setStyleSheet(u"")
        self.evaluation_install_button.setIconSize(QSize(16, 16))
        self.evaluation_install_button.setCheckable(True)
        self.evaluation_install_button.setFlat(True)

        self.horizontalLayout_10.addWidget(self.evaluation_install_button)

        self.app_setting_button_2 = QPushButton(self.app_control_2)
        self.app_setting_button_2.setObjectName(u"app_setting_button_2")
        sizePolicy1.setHeightForWidth(self.app_setting_button_2.sizePolicy().hasHeightForWidth())
        self.app_setting_button_2.setSizePolicy(sizePolicy1)
        self.app_setting_button_2.setMinimumSize(QSize(28, 28))
        self.app_setting_button_2.setStyleSheet(u"")
        self.app_setting_button_2.setIcon(icon1)
        self.app_setting_button_2.setIconSize(QSize(28, 28))
        self.app_setting_button_2.setCheckable(False)

        self.horizontalLayout_10.addWidget(self.app_setting_button_2)


        self.verticalLayout_12.addWidget(self.app_control_2)

        self.progess_2 = QFrame(self.eval_app)
        self.progess_2.setObjectName(u"progess_2")
        sizePolicy2.setHeightForWidth(self.progess_2.sizePolicy().hasHeightForWidth())
        self.progess_2.setSizePolicy(sizePolicy2)
        self.progess_2.setMinimumSize(QSize(0, 8))
        self.progess_2.setStyleSheet(u"")
        self.progess_2.setFrameShape(QFrame.StyledPanel)
        self.progess_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.progess_2)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.eval_progress_bar = QProgressBar(self.progess_2)
        self.eval_progress_bar.setObjectName(u"eval_progress_bar")
        sizePolicy2.setHeightForWidth(self.eval_progress_bar.sizePolicy().hasHeightForWidth())
        self.eval_progress_bar.setSizePolicy(sizePolicy2)
        self.eval_progress_bar.setMinimumSize(QSize(0, 0))
        self.eval_progress_bar.setStyleSheet(u"")
        self.eval_progress_bar.setValue(50)
        self.eval_progress_bar.setTextVisible(False)
        self.eval_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_13.addWidget(self.eval_progress_bar)


        self.verticalLayout_12.addWidget(self.progess_2)


        self.gridLayout.addWidget(self.eval_app, 0, 1, 1, 1)

        self.perf_app = QFrame(self.home_apps)
        self.perf_app.setObjectName(u"perf_app")
        sizePolicy1.setHeightForWidth(self.perf_app.sizePolicy().hasHeightForWidth())
        self.perf_app.setSizePolicy(sizePolicy1)
        self.perf_app.setMinimumSize(QSize(180, 250))
        self.perf_app.setStyleSheet(u"")
        self.perf_app.setFrameShape(QFrame.StyledPanel)
        self.perf_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_24 = QVBoxLayout(self.perf_app)
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(9, 9, 9, 9)
        self.app_info_8 = QFrame(self.perf_app)
        self.app_info_8.setObjectName(u"app_info_8")
        self.app_info_8.setStyleSheet(u"image: url(:/logos/images/logo/Quest_Perf_Logo_RGB.png);")
        self.app_info_8.setFrameShape(QFrame.StyledPanel)
        self.app_info_8.setFrameShadow(QFrame.Raised)

        self.verticalLayout_24.addWidget(self.app_info_8)

        self.app_control_8 = QFrame(self.perf_app)
        self.app_control_8.setObjectName(u"app_control_8")
        sizePolicy2.setHeightForWidth(self.app_control_8.sizePolicy().hasHeightForWidth())
        self.app_control_8.setSizePolicy(sizePolicy2)
        self.app_control_8.setMinimumSize(QSize(0, 40))
        self.app_control_8.setStyleSheet(u"")
        self.app_control_8.setFrameShape(QFrame.StyledPanel)
        self.app_control_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_16 = QHBoxLayout(self.app_control_8)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.app_about_button_8 = QPushButton(self.app_control_8)
        self.app_about_button_8.setObjectName(u"app_about_button_8")
        sizePolicy1.setHeightForWidth(self.app_about_button_8.sizePolicy().hasHeightForWidth())
        self.app_about_button_8.setSizePolicy(sizePolicy1)
        self.app_about_button_8.setMinimumSize(QSize(28, 28))
        self.app_about_button_8.setStyleSheet(u"")
        self.app_about_button_8.setIcon(icon)
        self.app_about_button_8.setIconSize(QSize(28, 28))
        self.app_about_button_8.setCheckable(False)
        self.app_about_button_8.setFlat(True)

        self.horizontalLayout_16.addWidget(self.app_about_button_8)

        self.performance_install_button = QPushButton(self.app_control_8)
        self.performance_install_button.setObjectName(u"performance_install_button")
        self.performance_install_button.setMinimumSize(QSize(0, 28))
        self.performance_install_button.setStyleSheet(u"")
        self.performance_install_button.setIconSize(QSize(16, 16))
        self.performance_install_button.setCheckable(True)
        self.performance_install_button.setFlat(True)

        self.horizontalLayout_16.addWidget(self.performance_install_button)

        self.app_setting_button_8 = QPushButton(self.app_control_8)
        self.app_setting_button_8.setObjectName(u"app_setting_button_8")
        sizePolicy1.setHeightForWidth(self.app_setting_button_8.sizePolicy().hasHeightForWidth())
        self.app_setting_button_8.setSizePolicy(sizePolicy1)
        self.app_setting_button_8.setMinimumSize(QSize(28, 28))
        self.app_setting_button_8.setStyleSheet(u"")
        self.app_setting_button_8.setIcon(icon1)
        self.app_setting_button_8.setIconSize(QSize(28, 28))
        self.app_setting_button_8.setCheckable(False)

        self.horizontalLayout_16.addWidget(self.app_setting_button_8)


        self.verticalLayout_24.addWidget(self.app_control_8)

        self.progess_8 = QFrame(self.perf_app)
        self.progess_8.setObjectName(u"progess_8")
        sizePolicy2.setHeightForWidth(self.progess_8.sizePolicy().hasHeightForWidth())
        self.progess_8.setSizePolicy(sizePolicy2)
        self.progess_8.setMinimumSize(QSize(0, 8))
        self.progess_8.setStyleSheet(u"")
        self.progess_8.setFrameShape(QFrame.StyledPanel)
        self.progess_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_25 = QVBoxLayout(self.progess_8)
        self.verticalLayout_25.setSpacing(0)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.perf_progress_bar = QProgressBar(self.progess_8)
        self.perf_progress_bar.setObjectName(u"perf_progress_bar")
        sizePolicy2.setHeightForWidth(self.perf_progress_bar.sizePolicy().hasHeightForWidth())
        self.perf_progress_bar.setSizePolicy(sizePolicy2)
        self.perf_progress_bar.setMinimumSize(QSize(0, 0))
        self.perf_progress_bar.setStyleSheet(u"")
        self.perf_progress_bar.setValue(50)
        self.perf_progress_bar.setTextVisible(False)
        self.perf_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_25.addWidget(self.perf_progress_bar)


        self.verticalLayout_24.addWidget(self.progess_8)


        self.gridLayout.addWidget(self.perf_app, 0, 2, 1, 1)

        self.btm_app = QFrame(self.home_apps)
        self.btm_app.setObjectName(u"btm_app")
        sizePolicy1.setHeightForWidth(self.btm_app.sizePolicy().hasHeightForWidth())
        self.btm_app.setSizePolicy(sizePolicy1)
        self.btm_app.setMinimumSize(QSize(180, 250))
        self.btm_app.setStyleSheet(u"")
        self.btm_app.setFrameShape(QFrame.NoFrame)
        self.btm_app.setFrameShadow(QFrame.Plain)
        self.btm_app.setLineWidth(1)
        self.verticalLayout_14 = QVBoxLayout(self.btm_app)
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(9, 9, 9, 9)
        self.app_info_3 = QFrame(self.btm_app)
        self.app_info_3.setObjectName(u"app_info_3")
        self.app_info_3.setStyleSheet(u"image: url(:/logos/images/logo/Quest_BTN_Logo_RGB.png);")
        self.app_info_3.setFrameShape(QFrame.StyledPanel)
        self.app_info_3.setFrameShadow(QFrame.Raised)

        self.verticalLayout_14.addWidget(self.app_info_3)

        self.app_control_3 = QFrame(self.btm_app)
        self.app_control_3.setObjectName(u"app_control_3")
        sizePolicy2.setHeightForWidth(self.app_control_3.sizePolicy().hasHeightForWidth())
        self.app_control_3.setSizePolicy(sizePolicy2)
        self.app_control_3.setMinimumSize(QSize(0, 40))
        self.app_control_3.setStyleSheet(u"")
        self.app_control_3.setFrameShape(QFrame.StyledPanel)
        self.app_control_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.app_control_3)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.app_about_button_3 = QPushButton(self.app_control_3)
        self.app_about_button_3.setObjectName(u"app_about_button_3")
        sizePolicy1.setHeightForWidth(self.app_about_button_3.sizePolicy().hasHeightForWidth())
        self.app_about_button_3.setSizePolicy(sizePolicy1)
        self.app_about_button_3.setMinimumSize(QSize(28, 28))
        self.app_about_button_3.setStyleSheet(u"")
        self.app_about_button_3.setIcon(icon)
        self.app_about_button_3.setIconSize(QSize(28, 28))
        self.app_about_button_3.setCheckable(False)
        self.app_about_button_3.setFlat(True)

        self.horizontalLayout_11.addWidget(self.app_about_button_3)

        self.behind_the_meter_install_button = QPushButton(self.app_control_3)
        self.behind_the_meter_install_button.setObjectName(u"behind_the_meter_install_button")
        self.behind_the_meter_install_button.setMinimumSize(QSize(0, 28))
        self.behind_the_meter_install_button.setStyleSheet(u"")
        self.behind_the_meter_install_button.setIconSize(QSize(16, 16))
        self.behind_the_meter_install_button.setCheckable(True)
        self.behind_the_meter_install_button.setFlat(True)

        self.horizontalLayout_11.addWidget(self.behind_the_meter_install_button)

        self.app_setting_button_3 = QPushButton(self.app_control_3)
        self.app_setting_button_3.setObjectName(u"app_setting_button_3")
        sizePolicy1.setHeightForWidth(self.app_setting_button_3.sizePolicy().hasHeightForWidth())
        self.app_setting_button_3.setSizePolicy(sizePolicy1)
        self.app_setting_button_3.setMinimumSize(QSize(28, 28))
        self.app_setting_button_3.setStyleSheet(u"")
        self.app_setting_button_3.setIcon(icon1)
        self.app_setting_button_3.setIconSize(QSize(28, 28))
        self.app_setting_button_3.setCheckable(False)

        self.horizontalLayout_11.addWidget(self.app_setting_button_3)


        self.verticalLayout_14.addWidget(self.app_control_3)

        self.progess_3 = QFrame(self.btm_app)
        self.progess_3.setObjectName(u"progess_3")
        sizePolicy2.setHeightForWidth(self.progess_3.sizePolicy().hasHeightForWidth())
        self.progess_3.setSizePolicy(sizePolicy2)
        self.progess_3.setMinimumSize(QSize(0, 8))
        self.progess_3.setStyleSheet(u"")
        self.progess_3.setFrameShape(QFrame.StyledPanel)
        self.progess_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.progess_3)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.behind_progress_bar = QProgressBar(self.progess_3)
        self.behind_progress_bar.setObjectName(u"behind_progress_bar")
        sizePolicy2.setHeightForWidth(self.behind_progress_bar.sizePolicy().hasHeightForWidth())
        self.behind_progress_bar.setSizePolicy(sizePolicy2)
        self.behind_progress_bar.setMinimumSize(QSize(0, 0))
        self.behind_progress_bar.setStyleSheet(u"")
        self.behind_progress_bar.setValue(50)
        self.behind_progress_bar.setTextVisible(False)
        self.behind_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_15.addWidget(self.behind_progress_bar)


        self.verticalLayout_14.addWidget(self.progess_3)


        self.gridLayout.addWidget(self.btm_app, 0, 3, 1, 1)

        self.micr_app = QFrame(self.home_apps)
        self.micr_app.setObjectName(u"micr_app")
        sizePolicy1.setHeightForWidth(self.micr_app.sizePolicy().hasHeightForWidth())
        self.micr_app.setSizePolicy(sizePolicy1)
        self.micr_app.setMinimumSize(QSize(180, 250))
        self.micr_app.setStyleSheet(u"")
        self.micr_app.setFrameShape(QFrame.StyledPanel)
        self.micr_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.micr_app)
        self.verticalLayout_28.setSpacing(0)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(9, 9, 9, 9)
        self.app_info_10 = QFrame(self.micr_app)
        self.app_info_10.setObjectName(u"app_info_10")
        self.app_info_10.setStyleSheet(u"image: url(:/logos/images/logo/Quest_Microgrid_Logo_RGB.png);")
        self.app_info_10.setFrameShape(QFrame.StyledPanel)
        self.app_info_10.setFrameShadow(QFrame.Raised)

        self.verticalLayout_28.addWidget(self.app_info_10)

        self.app_control_10 = QFrame(self.micr_app)
        self.app_control_10.setObjectName(u"app_control_10")
        sizePolicy2.setHeightForWidth(self.app_control_10.sizePolicy().hasHeightForWidth())
        self.app_control_10.setSizePolicy(sizePolicy2)
        self.app_control_10.setMinimumSize(QSize(0, 40))
        self.app_control_10.setStyleSheet(u"")
        self.app_control_10.setFrameShape(QFrame.StyledPanel)
        self.app_control_10.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.app_control_10)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.app_about_button_10 = QPushButton(self.app_control_10)
        self.app_about_button_10.setObjectName(u"app_about_button_10")
        sizePolicy1.setHeightForWidth(self.app_about_button_10.sizePolicy().hasHeightForWidth())
        self.app_about_button_10.setSizePolicy(sizePolicy1)
        self.app_about_button_10.setMinimumSize(QSize(28, 28))
        self.app_about_button_10.setStyleSheet(u"")
        self.app_about_button_10.setIcon(icon)
        self.app_about_button_10.setIconSize(QSize(28, 28))
        self.app_about_button_10.setCheckable(False)
        self.app_about_button_10.setFlat(True)

        self.horizontalLayout_18.addWidget(self.app_about_button_10)

        self.microgrid_install_button = QPushButton(self.app_control_10)
        self.microgrid_install_button.setObjectName(u"microgrid_install_button")
        self.microgrid_install_button.setMinimumSize(QSize(0, 28))
        self.microgrid_install_button.setStyleSheet(u"")
        self.microgrid_install_button.setIconSize(QSize(16, 16))
        self.microgrid_install_button.setCheckable(True)
        self.microgrid_install_button.setFlat(True)

        self.horizontalLayout_18.addWidget(self.microgrid_install_button)

        self.app_setting_button_10 = QPushButton(self.app_control_10)
        self.app_setting_button_10.setObjectName(u"app_setting_button_10")
        sizePolicy1.setHeightForWidth(self.app_setting_button_10.sizePolicy().hasHeightForWidth())
        self.app_setting_button_10.setSizePolicy(sizePolicy1)
        self.app_setting_button_10.setMinimumSize(QSize(28, 28))
        self.app_setting_button_10.setStyleSheet(u"")
        self.app_setting_button_10.setIcon(icon1)
        self.app_setting_button_10.setIconSize(QSize(28, 28))
        self.app_setting_button_10.setCheckable(False)

        self.horizontalLayout_18.addWidget(self.app_setting_button_10)


        self.verticalLayout_28.addWidget(self.app_control_10)

        self.microProgressBar = QFrame(self.micr_app)
        self.microProgressBar.setObjectName(u"microProgressBar")
        sizePolicy2.setHeightForWidth(self.microProgressBar.sizePolicy().hasHeightForWidth())
        self.microProgressBar.setSizePolicy(sizePolicy2)
        self.microProgressBar.setMinimumSize(QSize(0, 8))
        self.microProgressBar.setStyleSheet(u"")
        self.microProgressBar.setFrameShape(QFrame.StyledPanel)
        self.microProgressBar.setFrameShadow(QFrame.Raised)
        self.verticalLayout_29 = QVBoxLayout(self.microProgressBar)
        self.verticalLayout_29.setSpacing(0)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.verticalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.micro_progress_bar = QProgressBar(self.microProgressBar)
        self.micro_progress_bar.setObjectName(u"micro_progress_bar")
        sizePolicy2.setHeightForWidth(self.micro_progress_bar.sizePolicy().hasHeightForWidth())
        self.micro_progress_bar.setSizePolicy(sizePolicy2)
        self.micro_progress_bar.setMinimumSize(QSize(0, 0))
        self.micro_progress_bar.setStyleSheet(u"")
        self.micro_progress_bar.setValue(50)
        self.micro_progress_bar.setTextVisible(False)
        self.micro_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_29.addWidget(self.micro_progress_bar)


        self.verticalLayout_28.addWidget(self.microProgressBar)


        self.gridLayout.addWidget(self.micr_app, 1, 0, 1, 1)

        self.quest_gpt = QFrame(self.home_apps)
        self.quest_gpt.setObjectName(u"quest_gpt")
        sizePolicy1.setHeightForWidth(self.quest_gpt.sizePolicy().hasHeightForWidth())
        self.quest_gpt.setSizePolicy(sizePolicy1)
        self.quest_gpt.setMinimumSize(QSize(180, 250))
        self.quest_gpt.setStyleSheet(u"QFrame{background-color: rgb(226, 235, 242);\n"
"}\n"
"#quest_gpt.QFrame:hover{\n"
"	background-color: rgb(216, 228, 238);\n"
"}")
        self.quest_gpt.setFrameShape(QFrame.StyledPanel)
        self.quest_gpt.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.quest_gpt)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(9, 9, 9, 9)
        self.app_info = QFrame(self.quest_gpt)
        self.app_info.setObjectName(u"app_info")
        self.app_info.setStyleSheet(u"image: url(:/logos/images/logo/Quest_Logo_RGB - GPT.png);")
        self.app_info.setFrameShape(QFrame.StyledPanel)
        self.app_info.setFrameShadow(QFrame.Raised)

        self.verticalLayout_10.addWidget(self.app_info)

        self.app_control = QFrame(self.quest_gpt)
        self.app_control.setObjectName(u"app_control")
        sizePolicy2.setHeightForWidth(self.app_control.sizePolicy().hasHeightForWidth())
        self.app_control.setSizePolicy(sizePolicy2)
        self.app_control.setMinimumSize(QSize(0, 40))
        self.app_control.setFrameShape(QFrame.StyledPanel)
        self.app_control.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.app_control)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.app_about_button = QPushButton(self.app_control)
        self.app_about_button.setObjectName(u"app_about_button")
        sizePolicy1.setHeightForWidth(self.app_about_button.sizePolicy().hasHeightForWidth())
        self.app_about_button.setSizePolicy(sizePolicy1)
        self.app_about_button.setMinimumSize(QSize(28, 28))
        self.app_about_button.setIcon(icon)
        self.app_about_button.setIconSize(QSize(28, 28))
        self.app_about_button.setCheckable(False)
        self.app_about_button.setFlat(True)

        self.horizontalLayout_9.addWidget(self.app_about_button)

        self.quest_gpt_install_button = QPushButton(self.app_control)
        self.quest_gpt_install_button.setObjectName(u"quest_gpt_install_button")
        self.quest_gpt_install_button.setMinimumSize(QSize(0, 28))
        self.quest_gpt_install_button.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	color:white;\n"
"	background-color: rgb(40, 84, 113);\n"
"	padding-left: 0px;\n"
"	border-radius:4px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	border: 2px solid rgb(129, 194, 65);\n"
"	border-radius: 4px;\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(129, 194, 65);\n"
"	border-radius: 4px;\n"
"}\n"
"QPushButton:checked {	\n"
"	background-color: rgb(129, 194, 65);\n"
"	border-radius: 4px;\n"
"}\n"
"")
        self.quest_gpt_install_button.setIconSize(QSize(16, 16))
        self.quest_gpt_install_button.setCheckable(True)
        self.quest_gpt_install_button.setChecked(False)
        self.quest_gpt_install_button.setFlat(True)

        self.horizontalLayout_9.addWidget(self.quest_gpt_install_button)

        self.app_setting_button = QPushButton(self.app_control)
        self.app_setting_button.setObjectName(u"app_setting_button")
        sizePolicy1.setHeightForWidth(self.app_setting_button.sizePolicy().hasHeightForWidth())
        self.app_setting_button.setSizePolicy(sizePolicy1)
        self.app_setting_button.setMinimumSize(QSize(28, 28))
        self.app_setting_button.setStyleSheet(u"QPushButton::menu-indicator{width:0px;}")
        self.app_setting_button.setIcon(icon1)
        self.app_setting_button.setIconSize(QSize(28, 28))
        self.app_setting_button.setCheckable(False)

        self.horizontalLayout_9.addWidget(self.app_setting_button)


        self.verticalLayout_10.addWidget(self.app_control)

        self.progess = QFrame(self.quest_gpt)
        self.progess.setObjectName(u"progess")
        sizePolicy2.setHeightForWidth(self.progess.sizePolicy().hasHeightForWidth())
        self.progess.setSizePolicy(sizePolicy2)
        self.progess.setMinimumSize(QSize(0, 8))
        self.progess.setStyleSheet(u"background-color: rgb(226, 235, 242);")
        self.progess.setFrameShape(QFrame.StyledPanel)
        self.progess.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.progess)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.quest_gpt_progress_bar = QProgressBar(self.progess)
        self.quest_gpt_progress_bar.setObjectName(u"quest_gpt_progress_bar")
        sizePolicy2.setHeightForWidth(self.quest_gpt_progress_bar.sizePolicy().hasHeightForWidth())
        self.quest_gpt_progress_bar.setSizePolicy(sizePolicy2)
        self.quest_gpt_progress_bar.setMinimumSize(QSize(0, 4))
        self.quest_gpt_progress_bar.setStyleSheet(u"QProgressBar {\n"
"	min-height: 4px;\n"
"	max-height: 4px;\n"
"	border-radius: 2px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    border-radius: 2px;\n"
"    background-color: rgb(129, 194, 65);\n"
"}")
        self.quest_gpt_progress_bar.setValue(50)
        self.quest_gpt_progress_bar.setTextVisible(False)
        self.quest_gpt_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_11.addWidget(self.quest_gpt_progress_bar)


        self.verticalLayout_10.addWidget(self.progess)


        self.gridLayout.addWidget(self.quest_gpt, 1, 1, 1, 1)

        self.data_app = QFrame(self.home_apps)
        self.data_app.setObjectName(u"data_app")
        sizePolicy1.setHeightForWidth(self.data_app.sizePolicy().hasHeightForWidth())
        self.data_app.setSizePolicy(sizePolicy1)
        self.data_app.setMinimumSize(QSize(180, 250))
        self.data_app.setStyleSheet(u"QFrame{background-color: rgb(226, 235, 242);\n"
"}\n"
"#data_app.QFrame:hover{\n"
"	background-color: rgb(216, 228, 238);\n"
"}")
        self.data_app.setFrameShape(QFrame.StyledPanel)
        self.data_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.data_app)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(9, 9, 9, 9)
        self.app_info_4 = QFrame(self.data_app)
        self.app_info_4.setObjectName(u"app_info_4")
        self.app_info_4.setStyleSheet(u"image: url(:/icon/images/logo/Quest_Datamanager_Logo_RGB.png);")
        self.app_info_4.setFrameShape(QFrame.StyledPanel)
        self.app_info_4.setFrameShadow(QFrame.Raised)

        self.verticalLayout_16.addWidget(self.app_info_4)

        self.app_control_4 = QFrame(self.data_app)
        self.app_control_4.setObjectName(u"app_control_4")
        sizePolicy2.setHeightForWidth(self.app_control_4.sizePolicy().hasHeightForWidth())
        self.app_control_4.setSizePolicy(sizePolicy2)
        self.app_control_4.setMinimumSize(QSize(0, 40))
        self.app_control_4.setFrameShape(QFrame.StyledPanel)
        self.app_control_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_27 = QHBoxLayout(self.app_control_4)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.app_about_button_4 = QPushButton(self.app_control_4)
        self.app_about_button_4.setObjectName(u"app_about_button_4")
        sizePolicy1.setHeightForWidth(self.app_about_button_4.sizePolicy().hasHeightForWidth())
        self.app_about_button_4.setSizePolicy(sizePolicy1)
        self.app_about_button_4.setMinimumSize(QSize(28, 28))
        self.app_about_button_4.setIcon(icon)
        self.app_about_button_4.setIconSize(QSize(28, 28))
        self.app_about_button_4.setCheckable(False)
        self.app_about_button_4.setFlat(True)

        self.horizontalLayout_27.addWidget(self.app_about_button_4)

        self.manager_install_button = QPushButton(self.app_control_4)
        self.manager_install_button.setObjectName(u"manager_install_button")
        self.manager_install_button.setMinimumSize(QSize(0, 28))
        self.manager_install_button.setStyleSheet(u"QPushButton {	\n"
"	border: none;\n"
"	color:white;\n"
"	background-color: rgb(40, 84, 113);\n"
"	padding-left: 0px;\n"
"	border-radius:4px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"	border: 2px solid rgb(129, 194, 65);\n"
"	border-radius: 4px;\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(129, 194, 65);\n"
"	border-radius: 4px;\n"
"}\n"
"QPushButton:checked {	\n"
"	background-color: rgb(129, 194, 65);\n"
"	border-radius: 4px;\n"
"}\n"
"")
        self.manager_install_button.setIconSize(QSize(16, 16))
        self.manager_install_button.setCheckable(True)
        self.manager_install_button.setChecked(False)
        self.manager_install_button.setFlat(True)

        self.horizontalLayout_27.addWidget(self.manager_install_button)

        self.app_setting_button_4 = QPushButton(self.app_control_4)
        self.app_setting_button_4.setObjectName(u"app_setting_button_4")
        sizePolicy1.setHeightForWidth(self.app_setting_button_4.sizePolicy().hasHeightForWidth())
        self.app_setting_button_4.setSizePolicy(sizePolicy1)
        self.app_setting_button_4.setMinimumSize(QSize(28, 28))
        self.app_setting_button_4.setStyleSheet(u"QPushButton::menu-indicator{width:0px;}")
        self.app_setting_button_4.setIcon(icon1)
        self.app_setting_button_4.setIconSize(QSize(28, 28))
        self.app_setting_button_4.setCheckable(False)

        self.horizontalLayout_27.addWidget(self.app_setting_button_4)


        self.verticalLayout_16.addWidget(self.app_control_4)

        self.progess_4 = QFrame(self.data_app)
        self.progess_4.setObjectName(u"progess_4")
        sizePolicy2.setHeightForWidth(self.progess_4.sizePolicy().hasHeightForWidth())
        self.progess_4.setSizePolicy(sizePolicy2)
        self.progess_4.setMinimumSize(QSize(0, 8))
        self.progess_4.setStyleSheet(u"background-color: rgb(226, 235, 242);")
        self.progess_4.setFrameShape(QFrame.StyledPanel)
        self.progess_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.progess_4)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.data_progress_bar = QProgressBar(self.progess_4)
        self.data_progress_bar.setObjectName(u"data_progress_bar")
        sizePolicy2.setHeightForWidth(self.data_progress_bar.sizePolicy().hasHeightForWidth())
        self.data_progress_bar.setSizePolicy(sizePolicy2)
        self.data_progress_bar.setMinimumSize(QSize(0, 4))
        self.data_progress_bar.setStyleSheet(u"QProgressBar {\n"
"	min-height: 4px;\n"
"	max-height: 4px;\n"
"	border-radius: 2px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    border-radius: 2px;\n"
"    background-color: rgb(129, 194, 65);\n"
"}")
        self.data_progress_bar.setValue(50)
        self.data_progress_bar.setTextVisible(False)
        self.data_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_18.addWidget(self.data_progress_bar)


        self.verticalLayout_16.addWidget(self.progess_4)


        self.gridLayout.addWidget(self.data_app, 1, 2, 1, 1)

        self.eq_app = QFrame(self.home_apps)
        self.eq_app.setObjectName(u"eq_app")
        sizePolicy1.setHeightForWidth(self.eq_app.sizePolicy().hasHeightForWidth())
        self.eq_app.setSizePolicy(sizePolicy1)
        self.eq_app.setMinimumSize(QSize(180, 250))
        self.eq_app.setStyleSheet(u"")
        self.eq_app.setFrameShape(QFrame.StyledPanel)
        self.eq_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.eq_app)
        self.verticalLayout_26.setSpacing(0)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(9, 9, 9, 9)
        self.app_info_9 = QFrame(self.eq_app)
        self.app_info_9.setObjectName(u"app_info_9")
        self.app_info_9.setStyleSheet(u"image: url(:/logos/images/logo/Quest_Equity_Logo_RGB.png);")
        self.app_info_9.setFrameShape(QFrame.StyledPanel)
        self.app_info_9.setFrameShadow(QFrame.Raised)

        self.verticalLayout_26.addWidget(self.app_info_9)

        self.app_control_9 = QFrame(self.eq_app)
        self.app_control_9.setObjectName(u"app_control_9")
        sizePolicy2.setHeightForWidth(self.app_control_9.sizePolicy().hasHeightForWidth())
        self.app_control_9.setSizePolicy(sizePolicy2)
        self.app_control_9.setMinimumSize(QSize(0, 40))
        self.app_control_9.setStyleSheet(u"")
        self.app_control_9.setFrameShape(QFrame.StyledPanel)
        self.app_control_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.app_control_9)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.app_about_button_9 = QPushButton(self.app_control_9)
        self.app_about_button_9.setObjectName(u"app_about_button_9")
        sizePolicy1.setHeightForWidth(self.app_about_button_9.sizePolicy().hasHeightForWidth())
        self.app_about_button_9.setSizePolicy(sizePolicy1)
        self.app_about_button_9.setMinimumSize(QSize(28, 28))
        self.app_about_button_9.setStyleSheet(u"")
        self.app_about_button_9.setIcon(icon)
        self.app_about_button_9.setIconSize(QSize(28, 28))
        self.app_about_button_9.setCheckable(False)
        self.app_about_button_9.setFlat(True)

        self.horizontalLayout_17.addWidget(self.app_about_button_9)

        self.equity_install_button = QPushButton(self.app_control_9)
        self.equity_install_button.setObjectName(u"equity_install_button")
        self.equity_install_button.setMinimumSize(QSize(0, 28))
        self.equity_install_button.setStyleSheet(u"")
        self.equity_install_button.setIconSize(QSize(16, 16))
        self.equity_install_button.setCheckable(True)
        self.equity_install_button.setFlat(True)

        self.horizontalLayout_17.addWidget(self.equity_install_button)

        self.app_setting_button_9 = QPushButton(self.app_control_9)
        self.app_setting_button_9.setObjectName(u"app_setting_button_9")
        sizePolicy1.setHeightForWidth(self.app_setting_button_9.sizePolicy().hasHeightForWidth())
        self.app_setting_button_9.setSizePolicy(sizePolicy1)
        self.app_setting_button_9.setMinimumSize(QSize(28, 28))
        self.app_setting_button_9.setStyleSheet(u"")
        self.app_setting_button_9.setIcon(icon1)
        self.app_setting_button_9.setIconSize(QSize(28, 28))
        self.app_setting_button_9.setCheckable(False)

        self.horizontalLayout_17.addWidget(self.app_setting_button_9)


        self.verticalLayout_26.addWidget(self.app_control_9)

        self.progess_9 = QFrame(self.eq_app)
        self.progess_9.setObjectName(u"progess_9")
        sizePolicy2.setHeightForWidth(self.progess_9.sizePolicy().hasHeightForWidth())
        self.progess_9.setSizePolicy(sizePolicy2)
        self.progess_9.setMinimumSize(QSize(0, 8))
        self.progess_9.setStyleSheet(u"")
        self.progess_9.setFrameShape(QFrame.StyledPanel)
        self.progess_9.setFrameShadow(QFrame.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.progess_9)
        self.verticalLayout_27.setSpacing(0)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.verticalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.energy_progress_bar = QProgressBar(self.progess_9)
        self.energy_progress_bar.setObjectName(u"energy_progress_bar")
        sizePolicy2.setHeightForWidth(self.energy_progress_bar.sizePolicy().hasHeightForWidth())
        self.energy_progress_bar.setSizePolicy(sizePolicy2)
        self.energy_progress_bar.setMinimumSize(QSize(0, 0))
        self.energy_progress_bar.setStyleSheet(u"")
        self.energy_progress_bar.setValue(50)
        self.energy_progress_bar.setTextVisible(False)
        self.energy_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_27.addWidget(self.energy_progress_bar)


        self.verticalLayout_26.addWidget(self.progess_9)


        self.gridLayout.addWidget(self.eq_app, 1, 3, 1, 1)

        self.plan_app = QFrame(self.home_apps)
        self.plan_app.setObjectName(u"plan_app")
        sizePolicy1.setHeightForWidth(self.plan_app.sizePolicy().hasHeightForWidth())
        self.plan_app.setSizePolicy(sizePolicy1)
        self.plan_app.setMinimumSize(QSize(180, 250))
        self.plan_app.setStyleSheet(u"")
        self.plan_app.setFrameShape(QFrame.StyledPanel)
        self.plan_app.setFrameShadow(QFrame.Raised)
        self.verticalLayout_30 = QVBoxLayout(self.plan_app)
        self.verticalLayout_30.setSpacing(0)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(9, 9, 9, 9)
        self.app_info_11 = QFrame(self.plan_app)
        self.app_info_11.setObjectName(u"app_info_11")
        self.app_info_11.setStyleSheet(u"image: url(:/logos/images/logo/Quest_Planning_Logo_RGB.png);")
        self.app_info_11.setFrameShape(QFrame.StyledPanel)
        self.app_info_11.setFrameShadow(QFrame.Raised)

        self.verticalLayout_30.addWidget(self.app_info_11)

        self.app_control_11 = QFrame(self.plan_app)
        self.app_control_11.setObjectName(u"app_control_11")
        sizePolicy2.setHeightForWidth(self.app_control_11.sizePolicy().hasHeightForWidth())
        self.app_control_11.setSizePolicy(sizePolicy2)
        self.app_control_11.setMinimumSize(QSize(0, 40))
        self.app_control_11.setStyleSheet(u"")
        self.app_control_11.setFrameShape(QFrame.StyledPanel)
        self.app_control_11.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.app_control_11)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.app_about_button_11 = QPushButton(self.app_control_11)
        self.app_about_button_11.setObjectName(u"app_about_button_11")
        sizePolicy1.setHeightForWidth(self.app_about_button_11.sizePolicy().hasHeightForWidth())
        self.app_about_button_11.setSizePolicy(sizePolicy1)
        self.app_about_button_11.setMinimumSize(QSize(28, 28))
        self.app_about_button_11.setStyleSheet(u"")
        self.app_about_button_11.setIcon(icon)
        self.app_about_button_11.setIconSize(QSize(28, 28))
        self.app_about_button_11.setCheckable(False)
        self.app_about_button_11.setFlat(True)

        self.horizontalLayout_19.addWidget(self.app_about_button_11)

        self.planning_install_button = QPushButton(self.app_control_11)
        self.planning_install_button.setObjectName(u"planning_install_button")
        self.planning_install_button.setMinimumSize(QSize(0, 28))
        self.planning_install_button.setStyleSheet(u"")
        self.planning_install_button.setIconSize(QSize(16, 16))
        self.planning_install_button.setCheckable(True)
        self.planning_install_button.setFlat(True)

        self.horizontalLayout_19.addWidget(self.planning_install_button)

        self.app_setting_button_11 = QPushButton(self.app_control_11)
        self.app_setting_button_11.setObjectName(u"app_setting_button_11")
        sizePolicy1.setHeightForWidth(self.app_setting_button_11.sizePolicy().hasHeightForWidth())
        self.app_setting_button_11.setSizePolicy(sizePolicy1)
        self.app_setting_button_11.setMinimumSize(QSize(28, 28))
        self.app_setting_button_11.setStyleSheet(u"")
        self.app_setting_button_11.setIcon(icon1)
        self.app_setting_button_11.setIconSize(QSize(28, 28))
        self.app_setting_button_11.setCheckable(False)

        self.horizontalLayout_19.addWidget(self.app_setting_button_11)


        self.verticalLayout_30.addWidget(self.app_control_11)

        self.progess_11 = QFrame(self.plan_app)
        self.progess_11.setObjectName(u"progess_11")
        sizePolicy2.setHeightForWidth(self.progess_11.sizePolicy().hasHeightForWidth())
        self.progess_11.setSizePolicy(sizePolicy2)
        self.progess_11.setMinimumSize(QSize(0, 8))
        self.progess_11.setStyleSheet(u"")
        self.progess_11.setFrameShape(QFrame.StyledPanel)
        self.progess_11.setFrameShadow(QFrame.Raised)
        self.verticalLayout_31 = QVBoxLayout(self.progess_11)
        self.verticalLayout_31.setSpacing(0)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.verticalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.plan_progress_bar = QProgressBar(self.progess_11)
        self.plan_progress_bar.setObjectName(u"plan_progress_bar")
        sizePolicy2.setHeightForWidth(self.plan_progress_bar.sizePolicy().hasHeightForWidth())
        self.plan_progress_bar.setSizePolicy(sizePolicy2)
        self.plan_progress_bar.setMinimumSize(QSize(0, 0))
        self.plan_progress_bar.setStyleSheet(u"")
        self.plan_progress_bar.setValue(50)
        self.plan_progress_bar.setTextVisible(False)
        self.plan_progress_bar.setInvertedAppearance(False)

        self.verticalLayout_31.addWidget(self.plan_progress_bar)


        self.verticalLayout_30.addWidget(self.progess_11)


        self.gridLayout.addWidget(self.plan_app, 2, 0, 1, 1)


        self.verticalLayout_8.addWidget(self.home_apps)

        self.home_page_scroll.setWidget(self.home_pace_content)

        self.verticalLayout_7.addWidget(self.home_page_scroll)


        self.verticalLayout_2.addWidget(self.home_page_frame)

        self.about_info = QFrame(self.frame_9)
        self.about_info.setObjectName(u"about_info")
        self.about_info.setMinimumSize(QSize(0, 0))
        self.about_info.setMaximumSize(QSize(16777215, 0))
        self.about_info.setFrameShape(QFrame.StyledPanel)
        self.about_info.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_43 = QHBoxLayout(self.about_info)
        self.horizontalLayout_43.setSpacing(0)
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.horizontalLayout_43.setContentsMargins(0, 0, 0, 0)
        self.about_info_cont = QFrame(self.about_info)
        self.about_info_cont.setObjectName(u"about_info_cont")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.about_info_cont.sizePolicy().hasHeightForWidth())
        self.about_info_cont.setSizePolicy(sizePolicy3)
        self.about_info_cont.setMinimumSize(QSize(0, 0))
        self.about_info_cont.setMaximumSize(QSize(16777215, 16777215))
        self.about_info_cont.setFrameShape(QFrame.StyledPanel)
        self.about_info_cont.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.about_info_cont)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.about_info_cont)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_2)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.about_info_container = QFrame(self.frame_2)
        self.about_info_container.setObjectName(u"about_info_container")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.about_info_container.sizePolicy().hasHeightForWidth())
        self.about_info_container.setSizePolicy(sizePolicy4)
        self.about_info_container.setMinimumSize(QSize(0, 0))
        self.about_info_container.setMaximumSize(QSize(16777215, 16777215))
        self.about_info_container.setStyleSheet(u"")
        self.about_info_container.setFrameShape(QFrame.StyledPanel)
        self.about_info_container.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.about_info_container)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.about_info_container)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1063, 71))
        self.scrollAreaWidgetContents.setStyleSheet(u"")
        self.horizontalLayout_3 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget_2 = QStackedWidget(self.scrollAreaWidgetContents)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")
        self.stackedWidget_2.setStyleSheet(u"")
        self.about_data = QWidget()
        self.about_data.setObjectName(u"about_data")
        self.about_data.setStyleSheet(u"")
        self.horizontalLayout_12 = QHBoxLayout(self.about_data)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.textBrowser = QTextBrowser(self.about_data)
        self.textBrowser.setObjectName(u"textBrowser")
        self.textBrowser.setStyleSheet(u"")

        self.horizontalLayout_12.addWidget(self.textBrowser)

        self.stackedWidget_2.addWidget(self.about_data)
        self.about_tech = QWidget()
        self.about_tech.setObjectName(u"about_tech")
        self.horizontalLayout_13 = QHBoxLayout(self.about_tech)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_2 = QTextBrowser(self.about_tech)
        self.textBrowser_2.setObjectName(u"textBrowser_2")

        self.horizontalLayout_13.addWidget(self.textBrowser_2)

        self.stackedWidget_2.addWidget(self.about_tech)
        self.about_eval = QWidget()
        self.about_eval.setObjectName(u"about_eval")
        self.horizontalLayout_14 = QHBoxLayout(self.about_eval)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_3 = QTextBrowser(self.about_eval)
        self.textBrowser_3.setObjectName(u"textBrowser_3")

        self.horizontalLayout_14.addWidget(self.textBrowser_3)

        self.stackedWidget_2.addWidget(self.about_eval)
        self.about_btm = QWidget()
        self.about_btm.setObjectName(u"about_btm")
        self.about_btm.setStyleSheet(u"")
        self.horizontalLayout_20 = QHBoxLayout(self.about_btm)
        self.horizontalLayout_20.setSpacing(0)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_4 = QTextBrowser(self.about_btm)
        self.textBrowser_4.setObjectName(u"textBrowser_4")
        self.textBrowser_4.setStyleSheet(u"")

        self.horizontalLayout_20.addWidget(self.textBrowser_4)

        self.stackedWidget_2.addWidget(self.about_btm)
        self.about_perf = QWidget()
        self.about_perf.setObjectName(u"about_perf")
        self.horizontalLayout_21 = QHBoxLayout(self.about_perf)
        self.horizontalLayout_21.setSpacing(0)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_5 = QTextBrowser(self.about_perf)
        self.textBrowser_5.setObjectName(u"textBrowser_5")

        self.horizontalLayout_21.addWidget(self.textBrowser_5)

        self.stackedWidget_2.addWidget(self.about_perf)
        self.about_energy = QWidget()
        self.about_energy.setObjectName(u"about_energy")
        self.horizontalLayout_22 = QHBoxLayout(self.about_energy)
        self.horizontalLayout_22.setSpacing(0)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_6 = QTextBrowser(self.about_energy)
        self.textBrowser_6.setObjectName(u"textBrowser_6")

        self.horizontalLayout_22.addWidget(self.textBrowser_6)

        self.stackedWidget_2.addWidget(self.about_energy)
        self.about_micro = QWidget()
        self.about_micro.setObjectName(u"about_micro")
        self.horizontalLayout_23 = QHBoxLayout(self.about_micro)
        self.horizontalLayout_23.setSpacing(0)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_7 = QTextBrowser(self.about_micro)
        self.textBrowser_7.setObjectName(u"textBrowser_7")

        self.horizontalLayout_23.addWidget(self.textBrowser_7)

        self.stackedWidget_2.addWidget(self.about_micro)
        self.about_plan = QWidget()
        self.about_plan.setObjectName(u"about_plan")
        self.horizontalLayout_24 = QHBoxLayout(self.about_plan)
        self.horizontalLayout_24.setSpacing(0)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_8 = QTextBrowser(self.about_plan)
        self.textBrowser_8.setObjectName(u"textBrowser_8")

        self.horizontalLayout_24.addWidget(self.textBrowser_8)

        self.stackedWidget_2.addWidget(self.about_plan)
        self.about_quest = QWidget()
        self.about_quest.setObjectName(u"about_quest")
        self.horizontalLayout_25 = QHBoxLayout(self.about_quest)
        self.horizontalLayout_25.setSpacing(0)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_9 = QTextBrowser(self.about_quest)
        self.textBrowser_9.setObjectName(u"textBrowser_9")

        self.horizontalLayout_25.addWidget(self.textBrowser_9)

        self.stackedWidget_2.addWidget(self.about_quest)
        self.about_manager = QWidget()
        self.about_manager.setObjectName(u"about_manager")
        self.horizontalLayout_26 = QHBoxLayout(self.about_manager)
        self.horizontalLayout_26.setSpacing(0)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.textBrowser_10 = QTextBrowser(self.about_manager)
        self.textBrowser_10.setObjectName(u"textBrowser_10")

        self.horizontalLayout_26.addWidget(self.textBrowser_10)

        self.stackedWidget_2.addWidget(self.about_manager)

        self.horizontalLayout_3.addWidget(self.stackedWidget_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_9.addWidget(self.scrollArea)

        self.about_hide = QPushButton(self.about_info_container)
        self.about_hide.setObjectName(u"about_hide")
        sizePolicy1.setHeightForWidth(self.about_hide.sizePolicy().hasHeightForWidth())
        self.about_hide.setSizePolicy(sizePolicy1)
        self.about_hide.setMouseTracking(True)
        self.about_hide.setAutoFillBackground(False)
        self.about_hide.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u":/icon/images/icons/remove_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.about_hide.setIcon(icon2)
        self.about_hide.setFlat(True)

        self.verticalLayout_9.addWidget(self.about_hide, 0, Qt.AlignHCenter)


        self.verticalLayout_17.addWidget(self.about_info_container)


        self.horizontalLayout_2.addWidget(self.frame_2)


        self.horizontalLayout_43.addWidget(self.about_info_cont)


        self.verticalLayout_2.addWidget(self.about_info)

        self.lineEdit = QLineEdit(self.frame_9)
        self.lineEdit.setObjectName(u"lineEdit")
        sizePolicy1.setHeightForWidth(self.lineEdit.sizePolicy().hasHeightForWidth())
        self.lineEdit.setSizePolicy(sizePolicy1)
        self.lineEdit.setMinimumSize(QSize(480, 0))
        self.lineEdit.setStyleSheet(u"border: 0.5px solid gray;\n"
"border-radius: 2px;\n"
"background-image: url(:/icon/images/icons/search_FILL0_wght200_GRAD0_opsz24.png);\n"
"background-repeat: no-repeat;\n"
"background-position: right;\n"
"\n"
"selection-color: black;")
        self.lineEdit.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.lineEdit.setFrame(True)
        self.lineEdit.setClearButtonEnabled(False)

        self.verticalLayout_2.addWidget(self.lineEdit, 0, Qt.AlignHCenter)


        self.verticalLayout.addWidget(self.frame_9)


        self.horizontalLayout.addWidget(self.home_frame)


        self.retranslateUi(home_page)

        self.stackedWidget_2.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(home_page)
    # setupUi

    def retranslateUi(self, home_page):
        home_page.setWindowTitle(QCoreApplication.translate("home_page", u"Form", None))
        self.app_about_button_7.setText("")
        self.tech_selection_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_7.setText("")
        self.app_about_button_2.setText("")
        self.evaluation_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_2.setText("")
        self.app_about_button_8.setText("")
        self.performance_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_8.setText("")
        self.app_about_button_3.setText("")
        self.behind_the_meter_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_3.setText("")
        self.app_about_button_10.setText("")
        self.microgrid_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_10.setText("")
        self.app_about_button.setText("")
        self.quest_gpt_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button.setText("")
        self.app_about_button_4.setText("")
        self.manager_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_4.setText("")
        self.app_about_button_9.setText("")
        self.equity_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_9.setText("")
        self.app_about_button_11.setText("")
        self.planning_install_button.setText(QCoreApplication.translate("home_page", u"Install", None))
        self.app_setting_button_11.setText("")
        self.textBrowser.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:26pt; font-weight:700;\">QuESt-GPT </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:18pt; font-weight:700;\">AI-powered tool for data analysis and visualization</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; m"
                        "argin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:26pt; font-weight:700;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt;\">This application helps users analyze and visualize their dataset (in CSV files). The application utilizes Large Language Models (LLMs) to translate users queries into python codes for performing data analysis and visualization. Currently, GPT4 models (OpenAI's API: https://openai.com/product) and codellama2 model (Replicate's API: https://replicate.com/) are used within the application.  </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:16pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</spa"
                        "n></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Tu Nguyen tunguy@sandia.gov</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p></body></html>", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Technology Selection</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\""
                        " font-size:14pt;\">An application for identifying the energy storage technologies most suitable for a given project. This tool is based on multiple parameters that characterize each storage technology; the technologies that do not satisfy the minimum application requirements are filtered out and the remaining technologies are ranked to indicate their compatibility to the desired project.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Tu Nguyen tunguy@sandia.gov</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0"
                        "px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p></body></html>", None))
        self.textBrowser_3.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Valuation</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\""
                        ">An application for energy storage valuation, an analysis where the maximum revenue of a hypothetical energy storage device is estimated using historical market data. This is done by determining the sequence of state of charge management actions that optimize revenue generation, assuming perfect foresight of the historical data. QuESt Valuation is aimed at optimizing value stacking for ISO/RTO services such as energy arbitrage and frequency regulation.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Tu Nguyen tunguy@sandia.go"
                        "v</span></p></body></html>", None))
        self.textBrowser_4.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt BTM</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\""
                        ">A collection of tools for behind-the-meter (BTM) energy storage systems:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">*Estimate cost savings for time-of-use and/or net-metering customers</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Tu Nguyen tunguy@sandia.gov</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; t"
                        "ext-indent:0px; font-size:11pt;\"><br /></p></body></html>", None))
        self.textBrowser_5.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Performance</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:700;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style="
                        "\" font-size:14pt;\">An application for analyzing battery energy storage system performance due to parasitic heating, ventilation, and air conditioning loads. This tool leverages the building simulation tool EnergyPlus to model the energy consumption of a particular battery housing.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Walker Olis wolis@sandia.gov</span></p></body></html>", None))
        self.textBrowser_6.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Energy Equity</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-s"
                        "ize:14pt;\">An application for assessing energy equity and environmental justice of energy storage projects. This application currently has the powerplant replacement wizard that estimates the health and climate benefits of substituting a powerplant with energy storage and PV. It then calculates the county level benefits to estimate how much the project would impact disadvantaged communities and people with low incomes.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">David Rosewater dmrose@sandia.gov</span></p></body></html>", None))
        self.textBrowser_7.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Microgrid</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:"
                        "14pt;\">The QuESt Microgrid app is a Discrete Event Simulator for evaluating energy storage systems connected to electrical power distribution systems.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">John Eddy jpeddy@sandia.gov</span></p></body></html>", None))
        self.textBrowser_8.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Planning</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:1"
                        "4pt;\">This app is still in development and will be released to the QuESt platform soon.</span></p></body></html>", None))
        self.textBrowser_9.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">About Quest</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt;\">placeholder</"
                        "span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0;"
                        " text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; "
                        "margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p></body></html>", None))
        self.textBrowser_10.setHtml(QCoreApplication.translate("home_page", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:22pt; font-weight:700;\">QuESt Data Manager</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14p"
                        "t;\">An application for acquiring data from open sources. Data selected for download is acquired in a format and structure compatible with other QuESt applications. Data that can be acquired includes:</span></p>\n"
"<ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\">\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:12px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Independent system operators (ISOs) and regional transmission organization (RTOs) market and operations data</li>\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">U.S. utility rate structures (tariffs)</li>\n"
"<li style=\" font-size:14pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Commercial or residential building load profiles</li>\n"
"<li style=\" font-size:1"
                        "4pt;\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Photovoltaic (PV) power profiles</li></ul>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:700;\">Contact</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">Tu Nguyen tunguy@sandia.gov</span></p></body></html>", None))
        self.about_hide.setText("")
#if QT_CONFIG(tooltip)
        self.lineEdit.setToolTip(QCoreApplication.translate("home_page", u"Search", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit.setText("")
        self.lineEdit.setPlaceholderText("")
    # retranslateUi

