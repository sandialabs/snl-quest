from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush, QRadialGradient
import math

class indicate(QWidget):
    def __init__(self, parent=None, outer_radius=9, inner_radius=6, pulse_duration=1000):
        """
        Initializes the indicator widget with a pulsing gradient effect.
        :param parent: Parent widget.
        :param outer_radius: Outer radius of the donut in pixels.
        :param inner_radius: Inner radius of the donut in pixels.
        :param pulse_duration: Duration of one full pulse cycle in milliseconds.
        """
        super().__init__(parent)
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
        self.setFixedSize(outer_radius * 2, outer_radius * 2)  # Set fixed size for the widget

        # Pulse animation parameters
        self.pulse_duration = pulse_duration

        # Timer for pulsing effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(50)  # Update every 50 milliseconds

        self.pulse_progress = 0
        self.pulse_increment = 50 / pulse_duration  # Adjust speed of transition

    def update_pulse(self):
        """Update the pulse effect to create a smooth glowing donut."""
        self.pulse_progress += self.pulse_increment
        if self.pulse_progress > 1:
            self.pulse_progress = 0  # Reset the progress after a full cycle
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate the current intensity based on pulse progress
        intensity = 0.5 + 0.5 * math.sin(self.pulse_progress * 2 * math.pi)  # Smooth pulse from 0 to 1

        # Create a gradient for the donut
        gradient = QRadialGradient(self.outer_radius, self.outer_radius, self.outer_radius)
        gradient.setColorAt(0, QColor(230 * intensity, 255 * intensity, 230 * intensity))  # Light color
        gradient.setColorAt(1, QColor(80, 80, 80))  # Dark color
        
        # Set the brush for the donut
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)

        # Draw the outer circle (donut shape)
        painter.drawEllipse(0, 0, self.outer_radius * 2, self.outer_radius * 2)

        # Draw the inner circle (to create the hole of the donut)
        painter.setBrush(self.palette().window().color())  # Use background color to create the hole
        painter.drawEllipse(self.outer_radius - self.inner_radius, self.outer_radius - self.inner_radius,
                            self.inner_radius * 2, self.inner_radius * 2)

# Example usage:
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = indicate()
    window.show()
    sys.exit(app.exec())


