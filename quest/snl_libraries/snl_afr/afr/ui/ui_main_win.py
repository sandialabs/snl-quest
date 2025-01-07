# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_winjuUZlW.ui'
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
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QTextBrowser, QVBoxLayout,
    QWidget)
import afr.resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(973, 673)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.centralwidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(8, 8, 0, 0)
        self.label_53 = QLabel(self.frame_2)
        self.label_53.setObjectName(u"label_53")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_53.sizePolicy().hasHeightForWidth())
        self.label_53.setSizePolicy(sizePolicy)
        self.label_53.setMaximumSize(QSize(20, 32))
        self.label_53.setPixmap(QPixmap(u":/logo/images/logo/Quest_Q_RGB.png"))
        self.label_53.setScaledContents(True)

        self.horizontalLayout_2.addWidget(self.label_53)

        self.label_23 = QLabel(self.frame_2)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setStyleSheet(u"font: 12pt \"Segoe UI\";")

        self.horizontalLayout_2.addWidget(self.label_23)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.mini = QPushButton(self.frame_2)
        self.mini.setObjectName(u"mini")
        icon = QIcon()
        icon.addFile(u":/dark_icon/images/dark_icon/remove_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.mini.setIcon(icon)
        self.mini.setIconSize(QSize(24, 24))
        self.mini.setFlat(True)

        self.horizontalLayout_2.addWidget(self.mini)

        self.maxi = QPushButton(self.frame_2)
        self.maxi.setObjectName(u"maxi")
        icon1 = QIcon()
        icon1.addFile(u":/dark_icon/images/dark_icon/open_in_new_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.maxi.setIcon(icon1)
        self.maxi.setIconSize(QSize(24, 24))
        self.maxi.setFlat(True)

        self.horizontalLayout_2.addWidget(self.maxi)

        self.exit = QPushButton(self.frame_2)
        self.exit.setObjectName(u"exit")
        icon2 = QIcon()
        icon2.addFile(u":/dark_icon/images/dark_icon/close_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.exit.setIcon(icon2)
        self.exit.setIconSize(QSize(24, 24))
        self.exit.setFlat(True)

        self.horizontalLayout_2.addWidget(self.exit)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setStyleSheet(u"")
        self.frame_4.setFrameShape(QFrame.NoFrame)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_4)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 8, 0)
        self.back_button = QPushButton(self.frame_4)
        self.back_button.setObjectName(u"back_button")
        icon3 = QIcon()
        icon3.addFile(u":/dark_icon/images/dark_icon/arrow_back_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.back_button.setIcon(icon3)
        self.back_button.setIconSize(QSize(24, 24))
        self.back_button.setFlat(True)

        self.verticalLayout_2.addWidget(self.back_button)

        self.home_button = QPushButton(self.frame_4)
        self.home_button.setObjectName(u"home_button")
        icon4 = QIcon()
        icon4.addFile(u":/dark_icon/images/dark_icon/home_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.home_button.setIcon(icon4)
        self.home_button.setIconSize(QSize(24, 24))
        self.home_button.setFlat(True)

        self.verticalLayout_2.addWidget(self.home_button)

        self.settings_button = QPushButton(self.frame_4)
        self.settings_button.setObjectName(u"settings_button")
        icon5 = QIcon()
        icon5.addFile(u":/dark_icon/images/dark_icon/settings_24dp_FILL0_wght200_GRAD0_opsz24.png", QSize(), QIcon.Normal, QIcon.Off)
        self.settings_button.setIcon(icon5)
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFlat(True)

        self.verticalLayout_2.addWidget(self.settings_button)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.frame_4)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.NoFrame)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.frame_3)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.welcome = QWidget()
        self.welcome.setObjectName(u"welcome")
        self.verticalLayout_5 = QVBoxLayout(self.welcome)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frame_5 = QFrame(self.welcome)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.NoFrame)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_5)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_28 = QFrame(self.frame_5)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setFrameShape(QFrame.NoFrame)
        self.frame_28.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_14 = QHBoxLayout(self.frame_28)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.frame_29 = QFrame(self.frame_28)
        self.frame_29.setObjectName(u"frame_29")
        self.frame_29.setFrameShape(QFrame.NoFrame)
        self.frame_29.setFrameShadow(QFrame.Raised)
        self.verticalLayout_24 = QVBoxLayout(self.frame_29)
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 60, 0, 0)
        self.frame_31 = QFrame(self.frame_29)
        self.frame_31.setObjectName(u"frame_31")
        self.frame_31.setFrameShape(QFrame.NoFrame)
        self.frame_31.setFrameShadow(QFrame.Raised)
        self.verticalLayout_25 = QVBoxLayout(self.frame_31)
        self.verticalLayout_25.setSpacing(0)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(0, 0, 0, -1)

        self.verticalLayout_24.addWidget(self.frame_31, 0, Qt.AlignLeft|Qt.AlignTop)

        self.textBrowser_2 = QTextBrowser(self.frame_29)
        self.textBrowser_2.setObjectName(u"textBrowser_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.textBrowser_2.sizePolicy().hasHeightForWidth())
        self.textBrowser_2.setSizePolicy(sizePolicy2)
        self.textBrowser_2.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser_2.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_24.addWidget(self.textBrowser_2)

        self.textBrowser = QTextBrowser(self.frame_29)
        self.textBrowser.setObjectName(u"textBrowser")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy3)
        self.textBrowser.setStyleSheet(u"background-color:transparent;\n"
"border: none;")
        self.textBrowser.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_24.addWidget(self.textBrowser)

        self.frame_32 = QFrame(self.frame_29)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setFrameShape(QFrame.NoFrame)
        self.frame_32.setFrameShadow(QFrame.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.frame_32)
        self.verticalLayout_26.setSpacing(0)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")

        self.verticalLayout_24.addWidget(self.frame_32)


        self.horizontalLayout_14.addWidget(self.frame_29)

        self.frame_30 = QFrame(self.frame_28)
        self.frame_30.setObjectName(u"frame_30")
        sizePolicy1.setHeightForWidth(self.frame_30.sizePolicy().hasHeightForWidth())
        self.frame_30.setSizePolicy(sizePolicy1)
        self.frame_30.setMaximumSize(QSize(400, 16777215))
        self.frame_30.setStyleSheet(u"")
        self.frame_30.setFrameShape(QFrame.NoFrame)
        self.frame_30.setFrameShadow(QFrame.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_30)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")

        self.horizontalLayout_14.addWidget(self.frame_30)

        self.horizontalLayout_14.setStretch(0, 3)
        self.horizontalLayout_14.setStretch(1, 2)

        self.verticalLayout_4.addWidget(self.frame_28)

        self.frame_6 = QFrame(self.frame_5)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.NoFrame)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 9)
        self.frame_7 = QFrame(self.frame_6)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.NoFrame)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_3.addWidget(self.frame_7)

        self.start_wiz = QPushButton(self.frame_6)
        self.start_wiz.setObjectName(u"start_wiz")
        self.start_wiz.setFlat(True)

        self.horizontalLayout_3.addWidget(self.start_wiz, 0, Qt.AlignLeft)

        self.horizontalLayout_3.setStretch(0, 4)
        self.horizontalLayout_3.setStretch(1, 5)

        self.verticalLayout_4.addWidget(self.frame_6)


        self.verticalLayout_5.addWidget(self.frame_5)

        self.stackedWidget.addWidget(self.welcome)
        self.loader_page = QWidget()
        self.loader_page.setObjectName(u"loader_page")
        self.verticalLayout_22 = QVBoxLayout(self.loader_page)
        self.verticalLayout_22.setSpacing(0)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(0, 0, 0, 0)
        self.file_load_layout = QVBoxLayout()
        self.file_load_layout.setSpacing(0)
        self.file_load_layout.setObjectName(u"file_load_layout")

        self.verticalLayout_22.addLayout(self.file_load_layout)

        self.stackedWidget.addWidget(self.loader_page)
        self.time_page = QWidget()
        self.time_page.setObjectName(u"time_page")
        self.verticalLayout_6 = QVBoxLayout(self.time_page)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.time_layout = QVBoxLayout()
        self.time_layout.setSpacing(0)
        self.time_layout.setObjectName(u"time_layout")

        self.verticalLayout_6.addLayout(self.time_layout)

        self.stackedWidget.addWidget(self.time_page)
        self.storage_page = QWidget()
        self.storage_page.setObjectName(u"storage_page")
        self.verticalLayout_30 = QVBoxLayout(self.storage_page)
        self.verticalLayout_30.setSpacing(0)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.eff_layout = QVBoxLayout()
        self.eff_layout.setSpacing(0)
        self.eff_layout.setObjectName(u"eff_layout")

        self.verticalLayout_30.addLayout(self.eff_layout)

        self.stackedWidget.addWidget(self.storage_page)
        self.cap_page = QWidget()
        self.cap_page.setObjectName(u"cap_page")
        self.verticalLayout_7 = QVBoxLayout(self.cap_page)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.cap_layout = QVBoxLayout()
        self.cap_layout.setSpacing(0)
        self.cap_layout.setObjectName(u"cap_layout")

        self.verticalLayout_7.addLayout(self.cap_layout)

        self.stackedWidget.addWidget(self.cap_page)
        self.cost_page = QWidget()
        self.cost_page.setObjectName(u"cost_page")
        self.verticalLayout_18 = QVBoxLayout(self.cost_page)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.cost_scenario_layout = QVBoxLayout()
        self.cost_scenario_layout.setSpacing(0)
        self.cost_scenario_layout.setObjectName(u"cost_scenario_layout")

        self.verticalLayout_18.addLayout(self.cost_scenario_layout)

        self.stackedWidget.addWidget(self.cost_page)
        self.plan_page = QWidget()
        self.plan_page.setObjectName(u"plan_page")
        self.verticalLayout_13 = QVBoxLayout(self.plan_page)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.cap_plan_layout = QVBoxLayout()
        self.cap_plan_layout.setSpacing(0)
        self.cap_plan_layout.setObjectName(u"cap_plan_layout")

        self.verticalLayout_13.addLayout(self.cap_plan_layout)

        self.stackedWidget.addWidget(self.plan_page)
        self.results_viewer = QWidget()
        self.results_viewer.setObjectName(u"results_viewer")
        self.verticalLayout_8 = QVBoxLayout(self.results_viewer)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.process_layout = QVBoxLayout()
        self.process_layout.setSpacing(0)
        self.process_layout.setObjectName(u"process_layout")

        self.verticalLayout_8.addLayout(self.process_layout)

        self.stackedWidget.addWidget(self.results_viewer)
        self.results = QWidget()
        self.results.setObjectName(u"results")
        self.verticalLayout_61 = QVBoxLayout(self.results)
        self.verticalLayout_61.setSpacing(0)
        self.verticalLayout_61.setObjectName(u"verticalLayout_61")
        self.verticalLayout_61.setContentsMargins(0, 0, 0, 0)
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_layout.setSpacing(0)
        self.dashboard_layout.setObjectName(u"dashboard_layout")

        self.verticalLayout_61.addLayout(self.dashboard_layout)

        self.stackedWidget.addWidget(self.results)
        self.settings_page = QWidget()
        self.settings_page.setObjectName(u"settings_page")
        self.verticalLayout_21 = QVBoxLayout(self.settings_page)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.label = QLabel(self.settings_page)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_21.addWidget(self.label)

        self.stackedWidget.addWidget(self.settings_page)
        self.cost_page_2 = QWidget()
        self.cost_page_2.setObjectName(u"cost_page_2")
        self.verticalLayout_36 = QVBoxLayout(self.cost_page_2)
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.frame_23 = QFrame(self.cost_page_2)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setFrameShape(QFrame.NoFrame)
        self.frame_23.setFrameShadow(QFrame.Raised)
        self.verticalLayout_34 = QVBoxLayout(self.frame_23)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.label_11 = QLabel(self.frame_23)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_34.addWidget(self.label_11)

        self.frame_36 = QFrame(self.frame_23)
        self.frame_36.setObjectName(u"frame_36")
        self.frame_36.setFrameShape(QFrame.StyledPanel)
        self.frame_36.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_36)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.frame_37 = QFrame(self.frame_36)
        self.frame_37.setObjectName(u"frame_37")
        self.frame_37.setFrameShape(QFrame.StyledPanel)
        self.frame_37.setFrameShadow(QFrame.Raised)
        self.verticalLayout_51 = QVBoxLayout(self.frame_37)
        self.verticalLayout_51.setObjectName(u"verticalLayout_51")
        self.textBrowser_7 = QTextBrowser(self.frame_37)
        self.textBrowser_7.setObjectName(u"textBrowser_7")

        self.verticalLayout_51.addWidget(self.textBrowser_7)

        self.frame_91 = QFrame(self.frame_37)
        self.frame_91.setObjectName(u"frame_91")
        self.frame_91.setFrameShape(QFrame.StyledPanel)
        self.frame_91.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_52 = QHBoxLayout(self.frame_91)
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.frame_92 = QFrame(self.frame_91)
        self.frame_92.setObjectName(u"frame_92")
        self.frame_92.setFrameShape(QFrame.StyledPanel)
        self.frame_92.setFrameShadow(QFrame.Raised)
        self.verticalLayout_35 = QVBoxLayout(self.frame_92)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.label_18 = QLabel(self.frame_92)
        self.label_18.setObjectName(u"label_18")
        self.label_18.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.verticalLayout_35.addWidget(self.label_18, 0, Qt.AlignLeft|Qt.AlignTop)


        self.horizontalLayout_52.addWidget(self.frame_92)

        self.frame_93 = QFrame(self.frame_91)
        self.frame_93.setObjectName(u"frame_93")
        self.frame_93.setFrameShape(QFrame.StyledPanel)
        self.frame_93.setFrameShadow(QFrame.Raised)
        self.verticalLayout_50 = QVBoxLayout(self.frame_93)
        self.verticalLayout_50.setSpacing(12)
        self.verticalLayout_50.setObjectName(u"verticalLayout_50")
        self.verticalLayout_50.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_52.addWidget(self.frame_93)

        self.horizontalLayout_52.setStretch(0, 2)
        self.horizontalLayout_52.setStretch(1, 5)

        self.verticalLayout_51.addWidget(self.frame_91)


        self.horizontalLayout_11.addWidget(self.frame_37)


        self.verticalLayout_34.addWidget(self.frame_36)


        self.verticalLayout_36.addWidget(self.frame_23)

        self.frame_47 = QFrame(self.cost_page_2)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setFrameShape(QFrame.StyledPanel)
        self.frame_47.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_21 = QHBoxLayout(self.frame_47)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_10)

        self.next_6 = QPushButton(self.frame_47)
        self.next_6.setObjectName(u"next_6")

        self.horizontalLayout_21.addWidget(self.next_6)


        self.verticalLayout_36.addWidget(self.frame_47)

        self.stackedWidget.addWidget(self.cost_page_2)
        self.plan_page_2 = QWidget()
        self.plan_page_2.setObjectName(u"plan_page_2")
        self.verticalLayout_39 = QVBoxLayout(self.plan_page_2)
        self.verticalLayout_39.setObjectName(u"verticalLayout_39")
        self.frame_42 = QFrame(self.plan_page_2)
        self.frame_42.setObjectName(u"frame_42")
        self.frame_42.setFrameShape(QFrame.StyledPanel)
        self.frame_42.setFrameShadow(QFrame.Raised)
        self.verticalLayout_37 = QVBoxLayout(self.frame_42)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.label_12 = QLabel(self.frame_42)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_37.addWidget(self.label_12)

        self.frame_45 = QFrame(self.frame_42)
        self.frame_45.setObjectName(u"frame_45")
        self.frame_45.setFrameShape(QFrame.StyledPanel)
        self.frame_45.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_23 = QHBoxLayout(self.frame_45)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.frame_77 = QFrame(self.frame_45)
        self.frame_77.setObjectName(u"frame_77")
        self.frame_77.setFrameShape(QFrame.StyledPanel)
        self.frame_77.setFrameShadow(QFrame.Raised)
        self.verticalLayout_56 = QVBoxLayout(self.frame_77)
        self.verticalLayout_56.setObjectName(u"verticalLayout_56")
        self.textBrowser_12 = QTextBrowser(self.frame_77)
        self.textBrowser_12.setObjectName(u"textBrowser_12")

        self.verticalLayout_56.addWidget(self.textBrowser_12)

        self.frame_97 = QFrame(self.frame_77)
        self.frame_97.setObjectName(u"frame_97")
        self.frame_97.setFrameShape(QFrame.StyledPanel)
        self.frame_97.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_53 = QHBoxLayout(self.frame_97)
        self.horizontalLayout_53.setObjectName(u"horizontalLayout_53")
        self.frame_98 = QFrame(self.frame_97)
        self.frame_98.setObjectName(u"frame_98")
        self.frame_98.setFrameShape(QFrame.StyledPanel)
        self.frame_98.setFrameShadow(QFrame.Raised)
        self.verticalLayout_38 = QVBoxLayout(self.frame_98)
        self.verticalLayout_38.setSpacing(0)
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.verticalLayout_38.setContentsMargins(0, -1, -1, -1)
        self.label_20 = QLabel(self.frame_98)
        self.label_20.setObjectName(u"label_20")
        self.label_20.setStyleSheet(u"font: 700 12pt \"Segoe UI\";")

        self.verticalLayout_38.addWidget(self.label_20, 0, Qt.AlignLeft|Qt.AlignTop)


        self.horizontalLayout_53.addWidget(self.frame_98)

        self.frame_99 = QFrame(self.frame_97)
        self.frame_99.setObjectName(u"frame_99")
        self.frame_99.setFrameShape(QFrame.StyledPanel)
        self.frame_99.setFrameShadow(QFrame.Raised)
        self.verticalLayout_55 = QVBoxLayout(self.frame_99)
        self.verticalLayout_55.setSpacing(12)
        self.verticalLayout_55.setObjectName(u"verticalLayout_55")
        self.label_49 = QLabel(self.frame_99)
        self.label_49.setObjectName(u"label_49")

        self.verticalLayout_55.addWidget(self.label_49)

        self.frame_81 = QFrame(self.frame_99)
        self.frame_81.setObjectName(u"frame_81")
        self.frame_81.setFrameShape(QFrame.StyledPanel)
        self.frame_81.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_56 = QHBoxLayout(self.frame_81)
        self.horizontalLayout_56.setSpacing(0)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.horizontalLayout_56.setContentsMargins(0, 0, 0, 0)
        self.coal_cap_input = QLineEdit(self.frame_81)
        self.coal_cap_input.setObjectName(u"coal_cap_input")

        self.horizontalLayout_56.addWidget(self.coal_cap_input)

        self.coal_cap_input_store = QPushButton(self.frame_81)
        self.coal_cap_input_store.setObjectName(u"coal_cap_input_store")
        self.coal_cap_input_store.setMaximumSize(QSize(0, 0))
        self.coal_cap_input_store.setFlat(True)

        self.horizontalLayout_56.addWidget(self.coal_cap_input_store)


        self.verticalLayout_55.addWidget(self.frame_81)

        self.label_48 = QLabel(self.frame_99)
        self.label_48.setObjectName(u"label_48")

        self.verticalLayout_55.addWidget(self.label_48)

        self.frame_82 = QFrame(self.frame_99)
        self.frame_82.setObjectName(u"frame_82")
        self.frame_82.setFrameShape(QFrame.StyledPanel)
        self.frame_82.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_57 = QHBoxLayout(self.frame_82)
        self.horizontalLayout_57.setSpacing(0)
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.horizontalLayout_57.setContentsMargins(0, 0, 0, 0)
        self.nucl_cap_input = QLineEdit(self.frame_82)
        self.nucl_cap_input.setObjectName(u"nucl_cap_input")

        self.horizontalLayout_57.addWidget(self.nucl_cap_input)

        self.nucl_cap_input_store = QPushButton(self.frame_82)
        self.nucl_cap_input_store.setObjectName(u"nucl_cap_input_store")
        self.nucl_cap_input_store.setMaximumSize(QSize(0, 0))
        self.nucl_cap_input_store.setFlat(True)

        self.horizontalLayout_57.addWidget(self.nucl_cap_input_store)


        self.verticalLayout_55.addWidget(self.frame_82)

        self.label_47 = QLabel(self.frame_99)
        self.label_47.setObjectName(u"label_47")

        self.verticalLayout_55.addWidget(self.label_47)

        self.frame_83 = QFrame(self.frame_99)
        self.frame_83.setObjectName(u"frame_83")
        self.frame_83.setFrameShape(QFrame.StyledPanel)
        self.frame_83.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_27 = QHBoxLayout(self.frame_83)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.bio_cap_input = QLineEdit(self.frame_83)
        self.bio_cap_input.setObjectName(u"bio_cap_input")

        self.horizontalLayout_27.addWidget(self.bio_cap_input)


        self.verticalLayout_55.addWidget(self.frame_83)


        self.horizontalLayout_53.addWidget(self.frame_99)

        self.horizontalLayout_53.setStretch(0, 2)
        self.horizontalLayout_53.setStretch(1, 5)

        self.verticalLayout_56.addWidget(self.frame_97)


        self.horizontalLayout_23.addWidget(self.frame_77)


        self.verticalLayout_37.addWidget(self.frame_45)


        self.verticalLayout_39.addWidget(self.frame_42)

        self.frame_53 = QFrame(self.plan_page_2)
        self.frame_53.setObjectName(u"frame_53")
        self.frame_53.setFrameShape(QFrame.StyledPanel)
        self.frame_53.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_28 = QHBoxLayout(self.frame_53)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalSpacer_15 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_28.addItem(self.horizontalSpacer_15)

        self.bio_cap_input_store = QPushButton(self.frame_53)
        self.bio_cap_input_store.setObjectName(u"bio_cap_input_store")

        self.horizontalLayout_28.addWidget(self.bio_cap_input_store)

        self.next_8 = QPushButton(self.frame_53)
        self.next_8.setObjectName(u"next_8")

        self.horizontalLayout_28.addWidget(self.next_8)


        self.verticalLayout_39.addWidget(self.frame_53)

        self.stackedWidget.addWidget(self.plan_page_2)
        self.state_page = QWidget()
        self.state_page.setObjectName(u"state_page")
        self.verticalLayout_63 = QVBoxLayout(self.state_page)
        self.verticalLayout_63.setObjectName(u"verticalLayout_63")
        self.frame_104 = QFrame(self.state_page)
        self.frame_104.setObjectName(u"frame_104")
        self.frame_104.setFrameShape(QFrame.StyledPanel)
        self.frame_104.setFrameShadow(QFrame.Raised)
        self.verticalLayout_59 = QVBoxLayout(self.frame_104)
        self.verticalLayout_59.setObjectName(u"verticalLayout_59")
        self.label_22 = QLabel(self.frame_104)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setStyleSheet(u"font: 24pt \"Segoe UI\";")

        self.verticalLayout_59.addWidget(self.label_22)

        self.frame_105 = QFrame(self.frame_104)
        self.frame_105.setObjectName(u"frame_105")
        self.frame_105.setFrameShape(QFrame.StyledPanel)
        self.frame_105.setFrameShadow(QFrame.Raised)
        self.verticalLayout_60 = QVBoxLayout(self.frame_105)
        self.verticalLayout_60.setObjectName(u"verticalLayout_60")

        self.verticalLayout_59.addWidget(self.frame_105)

        self.verticalLayout_59.setStretch(1, 1)

        self.verticalLayout_63.addWidget(self.frame_104)

        self.next_time = QPushButton(self.state_page)
        self.next_time.setObjectName(u"next_time")

        self.verticalLayout_63.addWidget(self.next_time, 0, Qt.AlignRight)

        self.stackedWidget.addWidget(self.state_page)

        self.verticalLayout_3.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.frame_3)


        self.verticalLayout.addWidget(self.frame)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_53.setText("")
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"QuESt Analysis for Regulators", None))
#if QT_CONFIG(tooltip)
        self.mini.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Minimize</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.mini.setText("")
#if QT_CONFIG(tooltip)
        self.maxi.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Maximize</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.maxi.setText("")
#if QT_CONFIG(tooltip)
        self.exit.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Exit</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.exit.setText("")
#if QT_CONFIG(tooltip)
        self.back_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Back</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.back_button.setText("")
#if QT_CONFIG(tooltip)
        self.home_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Home</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.home_button.setText("")
#if QT_CONFIG(tooltip)
        self.settings_button.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Settings</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.settings_button.setText("")
        self.textBrowser_2.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:24pt; font-weight:700;\">Analyze the impact of energy storage, PV, and wind deployment on capacity and decarbonization goals</span></p></body></html>", None))
        self.textBrowser.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-blo"
                        "ck-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:16pt; font-weight:700;\">Features</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:11pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:11pt;\">*Provides high level energy generation analysis over several years</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:11pt;\">*Determines cost optimal investments in Energy Storage, Wind and PV</span></p>\n"
""
                        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:11pt;\">*Balances system wide energy on a daily scale</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:11pt;\">*Customize ES mix with durations of up to 1000 hours</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:11pt;\">*Considers ES and PV degradation and end of life</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:11pt;\">*Set RPS targets</span></p></body></html>", None))
        self.start_wiz.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Data Collection", None))
        self.textBrowser_7.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:14pt;\">Cost Scenarios</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Description</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; "
                        "text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">**Example Inputs:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'Segoe UI'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">ES 4 Cost: 500000</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">ES 36 Cost: 250000</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">ES 100 Cost: 125000</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -q"
                        "t-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">ES 1000 Cost: 50000</span></p></body></html>", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Cost Scenarios", None))
        self.next_6.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Data Collection", None))
        self.textBrowser_12.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'.AppleSystemUIFont'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:14pt;\">Planned Capacity</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Description</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0"
                        "; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">**Example Inputs</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Coal Capacity: 200, 200, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Nuclear Capacity: 372, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312, 312</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'Segoe UI'; font-size:9pt;\">Bio Capacity: 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11</span></p></body></html>", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Capacity Planning", None))
        self.label_49.setText(QCoreApplication.translate("MainWindow", u" Coal Capacity:", None))
        self.coal_cap_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Coal Capacity...", None))
        self.coal_cap_input_store.setText("")
        self.label_48.setText(QCoreApplication.translate("MainWindow", u" Nuclear Capacity:", None))
        self.nucl_cap_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Nuclear Capacity...", None))
        self.nucl_cap_input_store.setText("")
        self.label_47.setText(QCoreApplication.translate("MainWindow", u" Bio Capacity:", None))
        self.bio_cap_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Bio Capacity...", None))
        self.bio_cap_input_store.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.next_8.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"State Selection", None))
        self.next_time.setText(QCoreApplication.translate("MainWindow", u"Next", None))
    # retranslateUi

