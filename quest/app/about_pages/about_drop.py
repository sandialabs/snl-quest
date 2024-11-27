from PySide6.QtWidgets import (
    QWidget,
)

from quest.app.about_pages.ui.ui_about_class import Ui_about_container


class about_apps(QWidget, Ui_about_container):
    """A page that displays information about quest"""
    def __init__(self):
        """sets up the ui file to show in the application"""
        super().__init__()
#           Set up the ui

        self.setupUi(self)
