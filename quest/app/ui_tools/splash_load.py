from PySide6.QtWidgets import (
    QMainWindow,
)
from quest.app.splash_screen.ui.ui_splash import Ui_SplashScreen


class splash(QMainWindow, Ui_SplashScreen):
    """A splash screen for booting the app."""

    def __init__(self):
        """Initialize the ui."""
        super().__init__()
#           Set up the ui

        self.setupUi(self)
