import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QToolTip
from PySide6.QtGui import QPainter, QColor, QPen, QMouseEvent
from PySide6.QtCore import QRectF, Qt, QPointF
import math

class CircularGraphicWidget(QWidget):
    """Base class for the pie charts"""
    def __init__(self, data, names=None, colors=None, parent=None):
        super().__init__(parent)
        self.data = self.normalize_data(data)
        self.names = names if names else []
        self.colors = colors if colors else [
            "#b30000", "#7c1158", "#4421af", "#1a53ff", "#0d88e6",
            "#00b7c7", "#5ad45a", "#8be04e", "#ebdc78"
        ]  # Provided colors
        self.alt_colors = [
            "#115f9a", "#1984c5", "#22a7f0", "#48b5c4", "#76c68f",
            "#a6d75b", "#c9e52f", "#d0ee11", "#d0f400"
        ]
        self.setMinimumSize(200, 200)
        self.hovered_index = -1
        self.setMouseTracking(True)  # Enable mouse tracking

    def normalize_data(self, data):

        try:
            total = sum(data)
            normal_data = [value * 100 / total for value in data]
        except Exception as e:
            print(e)
            print("Something wrong with normalization of data.")
        else:
            return normal_data

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            size = min(self.width(), self.height())
            rect = QRectF((self.width() - size) / 2, (self.height() - size) / 2, size, size).adjusted(20, 20, -20, -20)
            start_angle = 0
            spacing = 6  # Space between sections

            total = sum(self.data)

            for i, value in enumerate(self.data):
                span_angle = 360 * (value / total)
                color = self.colors[i % len(self.colors)]  # Cycle through colors if there are more data points than colors
                painter.setBrush(QColor(color).lighter(150) if i == self.hovered_index else QColor(color))
                painter.drawPie(rect.adjusted(spacing, spacing, -spacing, -spacing), int(start_angle * 16), int(span_angle * 16))
                start_angle += span_angle

            # Draw the larger center circle for a donut effect
            painter.setBrush(QColor("#1e1e1e"))
            painter.drawEllipse(rect.adjusted(30, 30, -30, -30))
        except:
            pass

    def mouseMoveEvent(self, event):
        pos = event.position()
        size = min(self.width(), self.height())
        center = QPointF(self.width() / 2, self.height() / 2)
        outer_radius = (size) / 1.3  # Adjusted outer radius based on widget size
        inner_radius = outer_radius * 0.3  # Inner radius of the donut hole

        # Check if the mouse position is within the outer radius but outside the inner radius
        distance = (pos - center).manhattanLength()
        if inner_radius < distance <= outer_radius:
            angle = self.calculate_angle(pos)
            self.hovered_index = self.get_segment_index(angle)
            if self.hovered_index != -1:
                value = self.data[self.hovered_index]
                name = self.names[self.hovered_index] if self.names else f"Category {self.hovered_index + 1}"
                QToolTip.showText(event.globalPosition().toPoint(), f"{name}: {value:.2f}%")
            else:
                QToolTip.hideText()
        else:
            self.hovered_index = -1
            QToolTip.hideText()
        self.update()

    def leaveEvent(self, event):
        self.hovered_index = -1
        QToolTip.hideText()
        self.update()

    def calculate_angle(self, pos):
        center = QPointF(self.width() / 2, self.height() / 2)
        delta = pos - center
        angle = math.degrees(math.atan2(delta.y(), delta.x()))
        fixed_angle = -1*angle
        return (fixed_angle + 360) % 360

    def get_segment_index(self, angle):
        start_angle = 0
        total = sum(self.data)
        for i, value in enumerate(self.data):
            span_angle = 360 * (value / total)
            if start_angle <= angle < start_angle + span_angle:
                return i
            start_angle += span_angle
        return -1
    
    def update(self):
        """Refresh the widget when the data changes."""
        self.repaint()

    def update_data(self, data):
        """Update the data and refresh the widget."""
        self.data = self.normalize_data(data)
        self.repaint()

class LegendWidget(QWidget):
    def __init__(self, names, colors, parent=None):
        super().__init__(parent)
        self.names = names
        self.colors = colors
        self.setMinimumSize(170, 0)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i, name in enumerate(self.names):
            color = self.colors[i % len(self.colors)]
            painter.setBrush(QColor(color))
            painter.drawRect(10, 30 * i + 10, 20, 20)
            painter.drawText(40, 30 * i + 25, name)

    def update(self):
        """Repaint when necessary"""
        self.repaint()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    data1 = [30, 20, 50, 10, 40, 15, 25, 35, 45, 5]  # Example data for the pie chart
    names1 = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]  # Example names for the legend

    # Example custom colors
    custom_colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#800000", "#008000", "#000080", "#808000"]

    window = QWidget()
    layout = QHBoxLayout(window)

    pie_chart1 = CircularGraphicWidget(data1, names1, custom_colors)  # Pass custom colors
    legend1 = LegendWidget(names1, pie_chart1.colors)

    layout.addWidget(pie_chart1)
    layout.addWidget(legend1)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())
