from PySide6.QtCore import Qt, Signal, QObject, QEvent, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QWidget, QLabel, QHBoxLayout, QPushButton

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: transparent;")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel("QuESt 2.0")
        self.title_label.setStyleSheet("color: white; padding-left: 10px;")
        layout.addWidget(self.title_label)

        self.minimize_button = QPushButton("-")
        self.minimize_button.setFixedSize(QSize(30, 30))
        self.minimize_button.setStyleSheet("background-color: transparent; color: white; border: none;")
        self.minimize_button.clicked.connect(self.minimize)
        layout.addWidget(self.minimize_button)

        self.setLayout(layout)

    def minimize(self):
        self.window().showMinimized()

class CustomSplashScreen(QSplashScreen):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        # Override default window flags to remove Qt.WindowStaysOnTopHint
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # Create a container widget to hold the title bar and splash screen content
        self.container = QWidget(self)
        self.container.setGeometry(self.rect())

        # Create a vertical layout for the container
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 60)
        layout.setSpacing(0)

        # Add the custom title bar to the layout
        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)

        # Add the splash screen content (pixmap) to the layout
        self.splash_content = QLabel(self)
        self.splash_content.setPixmap(pixmap)
       # self.splash_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.splash_content)

    def mousePressEvent(self, event):
        # Ignore mouse press events to prevent the splash screen from appearing frozen
        event.ignore()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                self.hide()  # Hide the splash screen when minimized

    def showNormal(self):
        self.setWindowState(Qt.WindowNoState)
        self.show()

class SplashScreenUpdater(QObject):
    update_message = Signal(str)

    def __init__(self, splash):
        super().__init__()
        self.splash = splash
        self.update_message.connect(self.show_message)

    def show_message(self, message):
        # Display the message at the bottom center with white color
        self.splash.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
