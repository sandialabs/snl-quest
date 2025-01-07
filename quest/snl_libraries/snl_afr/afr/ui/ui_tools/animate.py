import sys
import random
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QBrush

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.circles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # Update every 50 ms

    def add_circle(self):
        width, height = self.width(), self.height()
        max_circle_radius = 60
        min_circle_radius = 10
        radius = random.randint(min_circle_radius, max_circle_radius)
        
        # Ensure the width is greater than twice the maximum circle radius
        if width > 2 * max_circle_radius:
            x = random.randint(radius, width - radius)
        else:
            x = width // 2  # Center the circle if the width is too small

        y = height + radius  # Start below the bottom edge
        color = random.choice(["#115f9a", "#1984c5", "#22a7f0", "#48b5c4", "#76c68f", "#a6d75b", "#c9e52f", "#d0ee11", "#d0f400"])
        self.circles.append({'x': x, 'y': y, 'radius': radius, 'color': color})

    def update_animation(self):
        width, height = self.width(), self.height()
        # Move circles upwards
        for circle in self.circles:
            circle['y'] -= 5  # Move up by 5 pixels
        # Remove circles that are out of the view
        self.circles = [circle for circle in self.circles if circle['y'] + circle['radius'] > 0]
        # Add new circles
        if random.random() < 0.07:  # Add a new circle with a 7% chance
            self.add_circle()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor('#1e1e1e'))  # Background color
        for circle in self.circles:
            painter.setBrush(QBrush(QColor(circle['color'])))
            painter.setPen(QColor(circle['color']))
            painter.drawEllipse(QRect(circle['x'] - circle['radius'], circle['y'] - circle['radius'], 2 * circle['radius'], 2 * circle['radius']))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create an instance of the AnimatedBackground widget
    animated_background = AnimatedBackground()
    animated_background.show()

    sys.exit(app.exec())
