from PySide6.QtWidgets import (
    QWidget,
)

from quest.app.home_page.ui.ui_app_template import Ui_fformat


class form_apps(QWidget, Ui_fformat):
    """
    The template to create homepage apps.

    This class sets up the UI for the home page and initializes the components
    defined in the UI file.
    """
    def __init__(self):
        """sets up the ui file to show in the application"""
        super().__init__()
#           Set up the ui

        self.setupUi(self)
