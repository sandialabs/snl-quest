import sys
from math import cos, sin
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor

class prog_dots(QWidget):
    def __init__(self):
        super().__init__()
        self.dots_radius = 10
        self.dots_count = 8
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(50)  # Faster update for smoother animation

    def update_position(self):
        self.angle += 5  # Smaller angle increment for smoother animation
        if self.angle >= 360:
            self.angle = 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 50

        for i in range(self.dots_count):
            angle_offset = (self.angle + i * (360 // self.dots_count)) % 360
            radian = angle_offset * 3.14159 / 180
            dot_x = center_x + radius * cos(radian)
            dot_y = center_y + radius * sin(radian)
            scale_factor = 1 + 0.5 * sin(radian)
            dot_radius = self.dots_radius * scale_factor
            opacity = 0.5 + 0.5 * sin(radian)
            painter.setBrush(QColor(129, 194, 65, int(255 * opacity)))
            painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius, dot_radius * 2, dot_radius * 2)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thinking Dots Animation")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.thinking_dots_widget = prog_dots()
        self.layout.addWidget(self.thinking_dots_widget)

        self.start_button = QPushButton("Start Animation")
        self.start_button.clicked.connect(self.start_animation)
        self.layout.addWidget(self.start_button)

    def start_animation(self):
        self.thinking_dots_widget.timer.start(50)

if __name__ == "__main__":
    from math import cos, sin
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
