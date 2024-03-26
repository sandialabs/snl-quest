from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

import sys

darkPalette = QPalette()
darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
darkPalette.setColor(QPalette.WindowText, Qt.white)
darkPalette.setColor(
    QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127)
)
darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
darkPalette.setColor(QPalette.ToolTipBase, Qt.white)
darkPalette.setColor(QPalette.ToolTipText, Qt.white)
darkPalette.setColor(QPalette.Text, Qt.white)
darkPalette.setColor(
    QPalette.Disabled, QPalette.Text, QColor(127, 127, 127)
)
darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
darkPalette.setColor(QPalette.ButtonText, Qt.white)
darkPalette.setColor(
    QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127)
)
darkPalette.setColor(QPalette.BrightText, Qt.red)
darkPalette.setColor(QPalette.Link, QColor(42, 130, 218))
darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
darkPalette.setColor(
    QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80)
)
darkPalette.setColor(QPalette.HighlightedText, Qt.white)
darkPalette.setColor(
    QPalette.Disabled,
    QPalette.HighlightedText,
    QColor(127, 127, 127),
)

app = QApplication(sys.argv)
app.setPalette(darkPalette)

w = QMainWindow()  # Replace with your QMainWindow instance.
w.show()

app.exec()
