# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app_templategSKvQd.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QProgressBar,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)
import quest.resources_rc

class Ui_fformat(object):
    def setupUi(self, fformat):
        if not fformat.objectName():
            fformat.setObjectName(u"fformat")
        fformat.resize(400, 300)
        fformat.setStyleSheet(u"")
        self.horizontalLayout = QHBoxLayout(fformat)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.app_search = QFrame(fformat)
        self.app_search.setObjectName(u"app_search")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.app_search.sizePolicy().hasHeightForWidth())
        self.app_search.setSizePolicy(sizePolicy)
        self.app_search.setMinimumSize(QSize(180, 250))
        self.app_search.setStyleSheet(u"")
        self.app_search.setFrameShape(QFrame.NoFrame)
        self.app_search.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.app_search)
        self.verticalLayout_19.setSpacing(0)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(3, 3, 3, 3)
        self.app_image = QFrame(self.app_search)
        self.app_image.setObjectName(u"app_image")
        self.app_image.setStyleSheet(u"")
        self.app_image.setFrameShape(QFrame.NoFrame)
        self.app_image.setFrameShadow(QFrame.Raised)

        self.verticalLayout_19.addWidget(self.app_image)

        self.app_control_5 = QFrame(self.app_search)
        self.app_control_5.setObjectName(u"app_control_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.app_control_5.sizePolicy().hasHeightForWidth())
        self.app_control_5.setSizePolicy(sizePolicy1)
        self.app_control_5.setMinimumSize(QSize(0, 40))
        self.app_control_5.setStyleSheet(u"")
        self.app_control_5.setFrameShape(QFrame.NoFrame)
        self.app_control_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_28 = QHBoxLayout(self.app_control_5)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.about_button = QPushButton(self.app_control_5)
        self.about_button.setObjectName(u"about_button")
        sizePolicy.setHeightForWidth(self.about_button.sizePolicy().hasHeightForWidth())
        self.about_button.setSizePolicy(sizePolicy)
        self.about_button.setMinimumSize(QSize(28, 28))
        self.about_button.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u":/icon/images/icons/info_FILL0_wght200_GRAD0_opsz48(1).svg", QSize(), QIcon.Normal, QIcon.Off)
        self.about_button.setIcon(icon)
        self.about_button.setIconSize(QSize(28, 28))
        self.about_button.setCheckable(False)
        self.about_button.setFlat(True)

        self.horizontalLayout_28.addWidget(self.about_button)

        self.install_button = QPushButton(self.app_control_5)
        self.install_button.setObjectName(u"install_button")
        sizePolicy.setHeightForWidth(self.install_button.sizePolicy().hasHeightForWidth())
        self.install_button.setSizePolicy(sizePolicy)
        self.install_button.setMinimumSize(QSize(85, 28))
        self.install_button.setStyleSheet(u"")
        self.install_button.setIconSize(QSize(16, 16))
        self.install_button.setCheckable(True)
        self.install_button.setChecked(False)
        self.install_button.setFlat(True)

        self.horizontalLayout_28.addWidget(self.install_button)

        self.setting_button = QPushButton(self.app_control_5)
        self.setting_button.setObjectName(u"setting_button")
        sizePolicy.setHeightForWidth(self.setting_button.sizePolicy().hasHeightForWidth())
        self.setting_button.setSizePolicy(sizePolicy)
        self.setting_button.setMinimumSize(QSize(28, 28))
        self.setting_button.setStyleSheet(u"QPushButton::menu-indicator{width:0px;}")
        icon1 = QIcon()
        icon1.addFile(u":/icon/images/icons/settings_FILL0_wght200_GRAD0_opsz48.png", QSize(), QIcon.Normal, QIcon.Off)
        self.setting_button.setIcon(icon1)
        self.setting_button.setIconSize(QSize(28, 28))
        self.setting_button.setCheckable(False)

        self.horizontalLayout_28.addWidget(self.setting_button)


        self.verticalLayout_19.addWidget(self.app_control_5)

        self.progess_5 = QFrame(self.app_search)
        self.progess_5.setObjectName(u"progess_5")
        sizePolicy1.setHeightForWidth(self.progess_5.sizePolicy().hasHeightForWidth())
        self.progess_5.setSizePolicy(sizePolicy1)
        self.progess_5.setMinimumSize(QSize(0, 8))
        self.progess_5.setStyleSheet(u"")
        self.progess_5.setFrameShape(QFrame.NoFrame)
        self.progess_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_20 = QVBoxLayout(self.progess_5)
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar(self.progess_5)
        self.progress_bar.setObjectName(u"progress_bar")
        sizePolicy1.setHeightForWidth(self.progress_bar.sizePolicy().hasHeightForWidth())
        self.progress_bar.setSizePolicy(sizePolicy1)
        self.progress_bar.setMinimumSize(QSize(0, 4))
        self.progress_bar.setStyleSheet(u"QProgressBar {\n"
"	min-height: 4px;\n"
"	max-height: 4px;\n"
"	border-radius: 2px;\n"
"}\n"
"QProgressBar::chunk {\n"
"    border-radius: 2px;\n"
"    background-color: rgb(129, 194, 65);\n"
"}")
        self.progress_bar.setValue(50)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setInvertedAppearance(False)

        self.verticalLayout_20.addWidget(self.progress_bar)


        self.verticalLayout_19.addWidget(self.progess_5)


        self.horizontalLayout.addWidget(self.app_search)


        self.retranslateUi(fformat)

        QMetaObject.connectSlotsByName(fformat)
    # setupUi

    def retranslateUi(self, fformat):
        fformat.setWindowTitle(QCoreApplication.translate("fformat", u"Form", None))
        self.about_button.setText("")
        self.install_button.setText(QCoreApplication.translate("fformat", u"Install", None))
        self.setting_button.setText("")
    # retranslateUi

